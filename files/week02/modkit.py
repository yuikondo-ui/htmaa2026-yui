#!/usr/bin/env python3
"""
modkit.py — parametric press-fit construction kit for modular garments
HTMAA Week 2 (computer-controlled cutting)

Parts
  tri       : equilateral triangle panel (triangulated surfaces curve/drape)
  tile      : square panel, N slots per edge
  half      : W x W/2 panel
  dart      : trapezoid panel (top W, bottom W*dart_ratio) -> introduces curvature
  con_0     : straight connector (coplanar tiles)
  con_<deg> : angled connector -> dihedral between tiles (non-flat surfaces)
  fit_test  : strip of slots at varying width to calibrate kerf/fit

Every slot on every part shares one width, so any connector fits any panel.

usage:  python3 modkit.py               -> out/*.dxf, out/*.svg, out/sheet.dxf
        edit P below, or pass overrides: python3 modkit.py thickness=3 kerf=0.15
"""
import math, os, sys
import ezdxf
from shapely.geometry import Polygon, Point, MultiPoint, box
from shapely.geometry.polygon import orient
from shapely.affinity import rotate, translate
from shapely.ops import unary_union

# --------------------------------------------------------------------------- #
P = dict(
    thickness   = 4.0,    # mm  material thickness (cardboard ~4, acrylic 3)
    kerf        = 0.20,   # mm  measured with fit_test (cardboard ~0.2, acrylic ~0.15)
    fit         = -0.10,  # mm  panel slots: negative = tighter press-fit, 0 = slip fit
    con_fit     = None,   # mm  connector slots; None = same as fit (they can differ: panel and connector grip differently)
    W           = 60.0,   # mm  tile side length
    slots       = 2,      # slots per edge
    slot_depth  = 8.0,    # mm  how far a connector sinks into a panel
    con_height  = 18.0,   # mm  connector height (the "fin")
    con_gap     = 2.0,    # mm  space left between two joined panels
    dart_ratio  = 0.6,    # bottom/top width of the trapezoid panel
    angles      = [30, 60, 90],   # angled connectors to generate (deg)
    corner_r    = 2.0,    # mm  round outer corners (0 = sharp)
    counts      = dict(tri=12, tile=6, half=4, dart=4, con_0=20, con_30=6, con_60=6, con_90=6),
    sheet_w     = 600, sheet_h = 400, margin = 6,   # xTool bed-ish, mm
    fit_range   = [-0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3],   # slots on the fit_test strip
)

def slot_w(fit=None):
    """drawn slot width so that the *physical* slot = thickness + fit"""
    f = P["fit"] if fit is None else fit
    return P["thickness"] + f - P["kerf"]

def con_slot_w():
    return slot_w(P["fit"] if P["con_fit"] is None else P["con_fit"])

# --------------------------------------------------------------------------- #
def notched(poly, n_per_edge):
    """cut n perpendicular slots into every edge of a sharp convex polygon,
    then round the remaining outer corners"""
    sw, sd = slot_w(), P["slot_depth"]
    poly = orient(poly, 1.0)                      # CCW -> inward = left normal
    pts = list(poly.exterior.coords)[:-1]
    cutters = []
    for i in range(len(pts)):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
        ex, ey = x1 - x0, y1 - y0
        L = math.hypot(ex, ey)
        ang = math.degrees(math.atan2(ey, ex))
        for k in range(n_per_edge):
            t = (k + 1) / (n_per_edge + 1)
            cx, cy = x0 + ex * t, y0 + ey * t
            # rectangle along edge (width sw), extending inward sd and outward 1mm
            r = box(-sw / 2, -1.0, sw / 2, sd)          # local: +y = inward
            r = rotate(r, ang, origin=(0, 0))          # local +x -> edge dir, +y -> inward
            cutters.append(translate(r, cx, cy))
    return rounded(poly, P["corner_r"]).difference(unary_union(cutters))

def rounded(poly, r):
    return poly.buffer(-r).buffer(r, join_style=1) if r > 0 else poly

def tile():
    W = P["W"]
    return notched(box(0, 0, W, W), P["slots"])

def tri():
    W = P["W"]
    return notched(Polygon([(0, 0), (W, 0), (W / 2, W * math.sqrt(3) / 2)]), P["slots"])

def half():
    W = P["W"]
    return notched(box(0, 0, W, W / 2), P["slots"])

def dart():
    W, k = P["W"], P["dart_ratio"]
    dx = W * (1 - k) / 2
    poly = Polygon([(dx, 0), (W - dx, 0), (W, W), (0, W)])
    return notched(poly, P["slots"])

def connector(angle_deg=0):
    """two arms, each slot_depth+gap/2 long, meeting at the hinge line"""
    sw, sd, h, g = con_slot_w(), P["slot_depth"], P["con_height"], P["con_gap"]
    L = sd + g / 2
    def arm():
        a = box(0, -h / 2, L, h / 2)
        s = box(L - sd, -sw / 2, L + 1, sw / 2)   # slot enters from the far end
        return a.difference(s)
    a1 = rotate(arm(), 180 - angle_deg / 2, origin=(0, 0))   # points left-ish
    a2 = rotate(arm(), angle_deg / 2, origin=(0, 0))          # points right-ish
    # fill the inner wedge so the joint isn't a pinch point
    # fill the V-gap on the outer side of the hinge with a wedge
    ends = [(0, -h / 2), (0, h / 2)]
    corners = [rotate(Point(p), 180 - angle_deg / 2, origin=(0, 0)) for p in ends] + \
              [rotate(Point(p), angle_deg / 2, origin=(0, 0)) for p in ends] + [Point(0, 0)]
    hub = MultiPoint(corners).convex_hull if angle_deg else Polygon()
    c = unary_union([a1, a2, hub])
    return rounded(c, min(P["corner_r"], 1.0))

def fit_test():
    """one strip, slots stepping fit from -0.4 to +0.3 mm around thickness"""
    t, k, sd = P["thickness"], P["kerf"], P["slot_depth"]
    fits = P.get("fit_range", [-0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3])
    pitch = 12
    strip = box(0, 0, pitch * len(fits) + 6, sd + 10)
    cutters = []
    for i, f in enumerate(fits):
        w = t + f - k
        x = 6 + pitch * i
        cutters.append(box(x - w / 2, sd + 10 - sd - 1, x + w / 2, sd + 11))
    return strip.difference(unary_union(cutters)), fits

# --------------------------------------------------------------------------- #
def rings(poly):
    if poly.geom_type == "MultiPolygon":
        poly = max(poly.geoms, key=lambda g: g.area)
    yield list(poly.exterior.coords)
    for i in poly.interiors:
        yield list(i.coords)

def write_dxf(parts, path):
    """parts: list of (polygon, dx, dy)"""
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4              # mm
    doc.layers.add("CUT", color=1)
    doc.layers.add("ENGRAVE", color=5)
    msp = doc.modelspace()
    for poly, dx, dy, label in parts:
        for ring in rings(translate(poly, dx, dy)):
            msp.add_lwpolyline(ring, close=True, dxfattribs={"layer": "CUT"})
        if label:
            b = translate(poly, dx, dy).bounds
            msp.add_text(label, height=3, dxfattribs={"layer": "ENGRAVE"}).set_placement(
                ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
    doc.saveas(path)

def write_svg(parts, path, w, h):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">',
           f'<rect width="{w}" height="{h}" fill="white"/>']
    for poly, dx, dy, label in parts:
        for ring in rings(translate(poly, dx, dy)):
            d = "M " + " L ".join(f"{x:.3f},{h - y:.3f}" for x, y in ring) + " Z"
            out.append(f'<path d="{d}" fill="none" stroke="red" stroke-width="0.2"/>')
        if label:
            b = translate(poly, dx, dy).bounds
            out.append(f'<text x="{(b[0]+b[2])/2:.1f}" y="{h-(b[1]+b[3])/2+1:.1f}" font-size="3" '
                       f'text-anchor="middle" fill="blue" font-family="sans-serif">{label}</text>')
    out.append("</svg>")
    open(path, "w").write("\n".join(out))

def layout(items):
    """shelf packing onto as many sheets as needed. items: list of (name, polygon) -> list of sheets"""
    m, SW, SH = P["margin"], P["sheet_w"], P["sheet_h"]
    x, y, shelf = m, m, 0
    sheets, placed = [], []
    for name, poly in items:
        b = poly.bounds
        pw, ph = b[2] - b[0], b[3] - b[1]
        if x + pw > SW - m:
            x, y, shelf = m, y + shelf + m, 0
        if y + ph > SH - m:
            sheets.append(placed); placed = []; x, y, shelf = m, m, 0
        placed.append((poly, x - b[0], y - b[1], name if name.startswith("R") else None))   # ring labels engraved
        x += pw + m
        shelf = max(shelf, ph)
    sheets.append(placed)
    return sheets

# --------------------------------------------------------------------------- #
def main():
    for arg in sys.argv[1:]:                       # cli overrides: key=value
        k, v = arg.split("=", 1)
        if P.get(k) is None: P[k] = float(v)
        else: P[k] = type(P[k])(v) if not isinstance(P[k], (list, dict)) else eval(v)
    os.makedirs("out", exist_ok=True)

    parts = {"tri": tri(), "tile": tile(), "half": half(), "dart": dart(), "con_0": connector(0)}
    for a in P["angles"]:
        parts[f"con_{a}"] = connector(a)

    # individual files (labelled)
    for name, poly in parts.items():
        b = poly.bounds
        p = translate(poly, -b[0] + 2, -b[1] + 2)
        write_dxf([(p, 0, 0, None)], f"out/{name}.dxf")
        write_svg([(p, 0, 0, None)], f"out/{name}.svg", b[2] - b[0] + 4, b[3] - b[1] + 4)

    ft, fits = fit_test()
    b = ft.bounds
    labels = [(box(0,0,0.01,0.01), 6 + 12 * i, 4, f"{f:+.1f}") for i, f in enumerate(fits)]
    write_dxf([(ft, 0, 0, None)] + labels, "out/fit_test.dxf")
    write_svg([(ft, 0, 0, None)] + labels, "out/fit_test.svg", b[2] + 2, b[3] + 2)

    # full sheet
    items = []
    for name, n in P["counts"].items():
        if name in parts:
            items += [(name, parts[name])] * n
    items.sort(key=lambda it: -(it[1].bounds[3] - it[1].bounds[1]))
    sheets = layout(items)
    for i, placed in enumerate(sheets, 1):
        write_dxf(placed, f"out/sheet_{i}.dxf")
        write_svg(placed, f"out/sheet_{i}.svg", P["sheet_w"], P["sheet_h"])

    print(f"slot width drawn = {slot_w():.2f} mm  (physical ≈ {P['thickness']+P['fit']:.2f} mm)")
    print(f"{len(items)} parts on {len(sheets)} sheet(s) of {P['sheet_w']} x {P['sheet_h']}")
    print("wrote out/" + ", ".join(sorted(os.listdir("out"))))

if __name__ == "__main__":
    main()
