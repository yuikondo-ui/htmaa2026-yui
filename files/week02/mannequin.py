#!/usr/bin/env python3
"""
mannequin.py — parametric waffle dress form for the laser cutter
HTMAA Week 2 · companion to modkit.py (same kerf/fit logic)

The body is an analytic torso: a stack of superellipse cross-sections whose
width/depth follow a measurement profile (hip → waist → bust → shoulder → neck).
Two families of slices (X planes, Y planes) are cut from the analytic body — no mesh,
no Slicer for Fusion 360. Each family can be tilted (tilt_x, tilt_y, degrees from
vertical) for the "angled slices" look; slots follow the actual intersection lines.

Slots: at each X∩Y intersection the X slice is slotted from the TOP and the
Y slice from the BOTTOM, each to the midpoint of the intersection segment.
Assemble: stand the X slices (slots open at the top), lower the Y slices onto them.

usage: python3 mannequin.py               -> out_mannequin/*.dxf, sheet.svg, preview.png
       python3 mannequin.py scale=0.4 thickness=1.7 pitch=12 tilt_x=15 tilt_y=-10
"""
import math, os, sys
import numpy as np
from scipy.interpolate import PchipInterpolator
import ezdxf
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely.affinity import translate

P = dict(
    scale      = 0.5,     # 1.0 = life size. 0.5 -> ~32 cm tall form
    thickness  = 4.0,     # cardboard mm
    kerf       = 0.20,
    fit        = -0.05,   # negative = tight
    pitch      = 20.0,    # spacing between parallel slices (mm, at output scale)
    tilt_x     = 0.0,     # deg: X family tilted about the Y axis (0 = vertical)
    tilt_y     = 0.0,     # deg: Y family tilted about the X axis
    raster     = 1.0,     # mm: sampling step for slice outlines
    n_exp      = 2.4,
    min_neck   = 14.0,
    min_span   = 25.0,    # mm: X∩Y intersections shorter than this get no slot
    min_rim    = 6.0,     # mm: material that must remain outside a slot    # mm: a slice thinner than this anywhere is dropped (fragile)     # superellipse exponent (2 = ellipse, higher = boxier)
    sheet_w    = 600, sheet_h = 400, margin = 5,
    # life-size measurements, mm. z = height above the hip cut (bottom of form)
    #            z     circumference   depth/width
    profile = [( 0,      940,  0.72),   # hip (flat bottom of the form)
               ( 90,     880,  0.72),   # high hip
               (200,     680,  0.68),   # waist
               (300,     760,  0.72),   # underbust
               (360,     880,  0.80),   # bust
               (430,     840,  0.62),   # upper chest
               (500,     860,  0.48),   # shoulders (wide, thin)
               (545,     380,  0.90),   # neck base
               (600,     360,  0.90)],  # neck top
)

def slot_w():
    return P["thickness"] + P["fit"] - P["kerf"]

# ---------------------------------------------------------------- body ---- #
def profile_funcs():
    z  = np.array([p[0] for p in P["profile"]]) * P["scale"]
    c  = np.array([p[1] for p in P["profile"]]) * P["scale"]
    r  = np.array([p[2] for p in P["profile"]])
    # superellipse perimeter ≈ ellipse perimeter (Ramanujan) — good enough for a form
    width = []
    for ci, ri in zip(c, r):
        # solve a from perimeter with b = ri*a : perimeter ≈ pi*(3(a+b) - sqrt((3a+b)(a+3b)))
        f = lambda a: math.pi * (3 * (a + ri * a) - math.sqrt((3 * a + ri * a) * (a + 3 * ri * a))) - ci
        lo, hi = 1.0, 1000.0
        for _ in range(60):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
        width.append(lo)
    a = PchipInterpolator(z, np.array(width))
    b = PchipInterpolator(z, np.array(width) * r)
    return a, b, z[0], z[-1]

def inside(x, y, z, a, b, z0, z1):
    n = P["n_exp"]
    if z < z0 or z > z1: return False
    A, B = float(a(z)), float(b(z))
    return (abs(x / A) ** n + abs(y / B) ** n) < 1

def plane_frame(family):
    """returns (normal, e_u, e_v) for a slice family. e_v is the in-plane 'up-ish' axis."""
    if family == "x":
        t = math.radians(P["tilt_x"])
        return np.array([math.cos(t), 0, -math.sin(t)]), np.array([0, 1.0, 0]), np.array([math.sin(t), 0, math.cos(t)])
    t = math.radians(P["tilt_y"])
    return np.array([0, math.cos(t), -math.sin(t)]), np.array([1.0, 0, 0]), np.array([0, math.sin(t), math.cos(t)])

def slice_outline(family, d, a, b, z0, z1, R):
    """raster the plane n·p = d over (u,v) and contour the inside mask -> polygon in plane coords"""
    import contourpy
    n, eu, ev = plane_frame(family)
    step = P["raster"]
    us = np.arange(-R, R + step, step); vs = np.arange(-R, R * 1.4 + step, step)   # v may run higher (tilt)
    U, V = np.meshgrid(us, vs)
    px = d * n[0] + U * eu[0] + V * ev[0]
    py = d * n[1] + U * eu[1] + V * ev[1]
    pz = d * n[2] + U * eu[2] + V * ev[2]
    zc = np.clip(pz, z0, z1)
    A, B = a(zc), b(zc)
    e = P["n_exp"]
    F = 1 - (np.abs(px / A) ** e + np.abs(py / B) ** e)
    F[(pz < z0) | (pz > z1)] = -1
    gen = contourpy.contour_generator(us, vs, F)
    polys = [Polygon(c) for c in gen.lines(0.0) if len(c) >= 4]
    polys = [p.buffer(0) for p in polys if p.is_valid or True]
    polys = [p for p in polys if p.area > 50]
    if not polys: return None
    return unary_union(polys)

def to3d(family, d, pts):
    n, eu, ev = plane_frame(family)
    return [tuple(d * n + u * eu + v * ev) for u, v in pts]

def to2d(family, d, p):
    n, eu, ev = plane_frame(family)
    p = np.asarray(p) - d * n
    return float(p @ eu), float(p @ ev)

def intersection_segment(dx, dy, a, b, z0, z1, R):
    """3D segment where plane X(dx) ∩ plane Y(dy) passes through the body"""
    n1, _, _ = plane_frame("x"); n2, _, _ = plane_frame("y")
    l = np.cross(n1, n2); l /= np.linalg.norm(l)
    if l[2] < 0: l = -l                                   # point 'up'
    # a point on the line: solve [n1;n2;l]·p = [dx,dy,0]
    M = np.vstack([n1, n2, l]); p0 = np.linalg.solve(M, np.array([dx, dy, 0.0]))
    ts = np.arange(-R * 2, R * 2 + (z1 - z0), 1.0)
    ins = [t for t in ts if inside(*(p0 + t * l), a, b, z0, z1)]
    if len(ins) < 2: return None
    return p0 + ins[0] * l, p0 + ins[-1] * l

def slot(family, d, p_lo, p_hi, from_top):
    """slot polygon in plane coords: from the segment midpoint to one end (+5 mm overshoot)"""
    from shapely.geometry import LineString
    sw = slot_w()
    lo, hi = np.asarray(p_lo), np.asarray(p_hi)
    mid = (lo + hi) / 2
    end = hi if from_top else lo
    end = end + (end - mid) / (np.linalg.norm(end - mid) + 1e-9) * 5
    seg = LineString([to2d(family, d, mid), to2d(family, d, end)])
    return seg.buffer(sw / 2, cap_style=2)

def ok(poly, label):
    """drop slices that are fragile: detached fragments or a bridge thinner than min_neck.
    Slots are ignored for the test (they are meant to be narrow)."""
    core = poly.buffer(P["thickness"]).buffer(-P["thickness"])       # close the slots
    thin = core.buffer(-P["min_neck"] / 2)
    if thin.is_empty or thin.geom_type == "MultiPolygon" or core.geom_type == "MultiPolygon":
        print(f"  dropped {label}: too thin / fragmented (raise pitch or lower min_neck to keep)")
        return False
    return True

# -------------------------------------------------------------- slices ---- #
def build():
    a, b, z0, z1 = profile_funcs()
    pitch = P["pitch"]
    amax = max(float(a(z)) for z in np.linspace(z0, z1, 200))
    bmax = max(float(b(z)) for z in np.linspace(z0, z1, 200))
    R = max(amax, bmax, z1 - z0) * 1.2
    # plane offsets: centred, spaced by pitch, wide enough to cover the tilted body
    def offsets(ext, tilt):
        span = ext + (z1 - z0) * abs(math.sin(math.radians(tilt))) / 2
        ds = np.arange(-span + pitch / 2, span, pitch); return ds - (ds[0] + ds[-1]) / 2
    xs = offsets(amax, P["tilt_x"]); ys = offsets(bmax, P["tilt_y"])
    # tilt shifts planes: offset d measured along the normal, which passes through (0,0,z_mid)
    zmid = (z0 + z1) / 2
    nx, _, _ = plane_frame("x"); ny, _, _ = plane_frame("y")
    xs = xs + nx[2] * zmid; ys = ys + ny[2] * zmid

    segs = {}
    for i, dx in enumerate(xs):
        for j, dy in enumerate(ys):
            seg = intersection_segment(dx, dy, a, b, z0, z1, R)
            if seg and np.linalg.norm(seg[1] - seg[0]) >= P["min_span"]:
                segs[(i, j)] = seg

    parts, frames = [], {}
    for fam, ds, other in (("x", xs, ys), ("y", ys, xs)):
        for i, d in enumerate(ds):
            label = f"{fam.upper()}{i+1}"
            poly = slice_outline(fam, d, a, b, z0, z1, R)
            if poly is None: continue
            cutters = []
            for j in range(len(other)):
                key = (i, j) if fam == "x" else (j, i)
                if key not in segs: continue
                c = slot(fam, d, segs[key][0], segs[key][1], from_top=(fam == "x"))
                test = poly.difference(unary_union(cutters + [c]))
                if test.geom_type == "MultiPolygon" or test.buffer(-P["min_rim"] / 2).geom_type == "MultiPolygon":
                    continue                                   # this slot would leave a fragile flap
                cutters.append(c)
            if len(cutters) < 2:
                print(f"  dropped {label}: fewer than 2 joints"); continue
            poly = poly.difference(unary_union(cutters))
            if ok(poly, label):
                parts.append((label, poly)); frames[label] = (fam, d)
    return parts, (frames, a, b, z0, z1)

# -------------------------------------------------------------- output ---- #
def rings(poly):
    polys = poly.geoms if poly.geom_type == "MultiPolygon" else [poly]
    for p in polys:
        yield list(p.exterior.coords)
        for i in p.interiors: yield list(i.coords)

def layout(parts):
    """shelf packing onto as many sheet_w x sheet_h sheets as needed -> list of sheets"""
    m, SW, SH = P["margin"], P["sheet_w"], P["sheet_h"]
    sheets, placed = [], []
    x, y, shelf = m, m, 0
    for label, poly in sorted(parts, key=lambda p: -(p[1].bounds[3] - p[1].bounds[1])):
        bx = poly.bounds; pw, ph = bx[2] - bx[0], bx[3] - bx[1]
        if x + pw > SW - m: x, y, shelf = m, y + shelf + m, 0
        if y + ph > SH - m:
            sheets.append(placed); placed = []; x, y, shelf = m, m, 0
        placed.append((label, translate(poly, x - bx[0], y - bx[1])))
        x += pw + m; shelf = max(shelf, ph)
    sheets.append(placed)
    return sheets

def write_dxf(placed, path):
    doc = ezdxf.new("R2010", setup=True); doc.header["$INSUNITS"] = 4
    doc.layers.add("CUT", color=1); doc.layers.add("ENGRAVE", color=5)
    msp = doc.modelspace()
    for label, poly in placed:
        for ring in rings(poly):
            msp.add_lwpolyline(ring, close=True, dxfattribs={"layer": "CUT"})
        bx = poly.bounds
        msp.add_text(label, height=4, dxfattribs={"layer": "ENGRAVE"}).set_placement(
            ((bx[0] + bx[2]) / 2, bx[1] + 8), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
    doc.saveas(path)

def write_svg(placed, path, w, h):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">',
           f'<rect width="{w}" height="{h}" fill="white"/>']
    for label, poly in placed:
        for ring in rings(poly):
            d = "M " + " L ".join(f"{x:.2f},{h - y:.2f}" for x, y in ring) + " Z"
            out.append(f'<path d="{d}" fill="none" stroke="red" stroke-width="0.25"/>')
        bx = poly.bounds
        out.append(f'<text x="{(bx[0]+bx[2])/2:.1f}" y="{h-bx[1]-6:.1f}" font-size="4" text-anchor="middle" '
                   f'fill="blue" font-family="sans-serif">{label}</text>')
    out.append("</svg>"); open(path, "w").write("\n".join(out))

def preview(parts, geom, path):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    frames, a, b, z0, z1 = geom
    fig = plt.figure(figsize=(10, 7)); ax = fig.add_subplot(111, projection="3d")
    for label, poly in parts:
        fam, d = frames[label]
        polys = poly.geoms if poly.geom_type == "MultiPolygon" else [poly]
        for p in polys:
            verts = to3d(fam, d, list(p.exterior.coords))
            col = "#c9a877" if fam == "x" else "#8f6f47"
            ax.add_collection3d(Poly3DCollection([verts], facecolor=col, edgecolor="#3a2a10", linewidths=0.4, alpha=0.9))
    R = max(float(a(z1 * 0.6)), float(b(z1 * 0.6))) * 1.6
    ax.set_xlim(-R, R); ax.set_ylim(-R, R); ax.set_zlim(z0, z1)
    ax.set_box_aspect((1, 1, (z1 - z0) / (2 * R))); ax.view_init(14, -62); ax.set_axis_off()
    plt.tight_layout(); plt.savefig(path, dpi=150); plt.close()

def main():
    for arg in sys.argv[1:]:
        k, v = arg.split("="); P[k] = type(P[k])(v)
    os.makedirs("out_mannequin", exist_ok=True)
    parts, geom = build()
    sheets = layout(parts)
    for i, placed in enumerate(sheets, 1):
        write_dxf(placed, f"out_mannequin/sheet_{i}.dxf")
        write_svg(placed, f"out_mannequin/sheet_{i}.svg", P["sheet_w"], P["sheet_h"])
    for label, poly in parts:
        bx = poly.bounds
        write_dxf([(label, translate(poly, -bx[0] + 2, -bx[1] + 2))], f"out_mannequin/{label}.dxf")
    preview(parts, geom, "out_mannequin/preview.png")
    frames, a, b, z0, z1 = geom
    print(f"{sum(l[0]=='X' for l,_ in parts)} X-slices + {sum(l[0]=='Y' for l,_ in parts)} Y-slices, height {z1-z0:.0f} mm, "
          f"widest {2*max(float(a(z)) for z in np.linspace(z0,z1,200)):.0f} mm")
    print(f"slot drawn {slot_w():.2f} mm; {len(sheets)} sheet(s) of {P['sheet_w']} x {P['sheet_h']}")

if __name__ == "__main__":
    main()
