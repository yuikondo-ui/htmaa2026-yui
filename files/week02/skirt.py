#!/usr/bin/env python3
"""
skirt.py — a flared skirt from the modkit system, one panel size per ring
HTMAA Week 2

Rings of triangles between concentric circles. Ring k sits between circle k
(radius r0 + k*flare) and circle k+1, H mm lower. Because the circles differ in
radius, the panels are isosceles: "up" panels have their base on circle k,
"down" panels on circle k+1; both share the same leg length L_k. Every edge
still carries 2 slots at 1/3 and 2/3, so any connector fits any edge, and both
panels sharing an edge see the same slot positions.

Connectors are generated at the dihedral angles the mesh actually needs,
rounded to `angle_step` degrees.

usage: python3 skirt.py                        -> out_skirt/
       python3 skirt.py r0=47 N=10 rings=3 flare=10 H=28 thickness=3 kerf=0.15 fit=0
"""
import math, os, sys
import numpy as np
from shapely.geometry import Polygon
from shapely.affinity import translate
import modkit
from modkit import notched, connector, write_dxf, write_svg, layout, slot_w, P as KP

S = dict(
    r0        = 47.0,   # waist radius, mm  (mannequin waist at scale 0.4 ≈ 45)
    N         = 10,     # triangles pointing up per ring (= down per ring)
    rings     = 3,
    flare     = 10.0,   # radius increase per ring, mm
    H         = 28.0,   # ring height, mm
    angle_step = 5,     # connector angles rounded to this
    spare     = 0.15,   # extra parts
)

def cli():
    for arg in sys.argv[1:]:
        k, v = arg.split("=", 1)
        if k in S: S[k] = type(S[k])(v)
        elif k in KP:
            KP[k] = float(v) if KP[k] is None else (type(KP[k])(v) if not isinstance(KP[k], (list, dict)) else eval(v))
        else: raise SystemExit(f"unknown parameter {k}")

def mesh():
    """vertices on circles, faces as index triples, with ring index and up/down tag"""
    N, R = S["N"], S["rings"]
    V = []          # (x, y, z)
    idx = {}
    for k in range(R + 1):
        r = S["r0"] + k * S["flare"]
        for i in range(N):
            a = (i + (k % 2) * 0.5) * 2 * math.pi / N
            idx[(k, i)] = len(V); V.append((r * math.cos(a), r * math.sin(a), -k * S["H"]))
    F = []          # (ia, ib, ic, ring, tag)
    for k in range(R):
        for i in range(N):
            A, B = idx[(k, i)], idx[(k, (i + 1) % N)]
            o = k % 2                                   # odd rings are half-step offset the other way
            C, D = idx[(k + 1, (i + o) % N)], idx[(k + 1, (i + o + 1) % N)]
            F.append((A, B, C, k, "d")); F.append((B, D, C, k, "u"))
    return np.array(V), F

def tri_lengths(V, f):
    a, b, c = V[f[0]], V[f[1]], V[f[2]]
    return np.linalg.norm(b - a), np.linalg.norm(c - b), np.linalg.norm(a - c)

def isosceles(base, leg):
    h = math.sqrt(max(leg ** 2 - (base / 2) ** 2, 0))
    return Polygon([(-base / 2, 0), (base / 2, 0), (0, h)])

def normal(V, f):
    a, b, c = V[f[0]], V[f[1]], V[f[2]]
    n = np.cross(b - a, c - a); n /= np.linalg.norm(n)
    cen = (a + b + c) / 3
    if np.dot(n, [cen[0], cen[1], 0]) < 0: n = -n
    return n

def main():
    cli()
    os.makedirs("out_skirt", exist_ok=True)
    V, F = mesh()
    N, R = S["N"], S["rings"]

    # --- panels: one shape per (ring, up/down)
    panels, counts, edge_len = {}, {}, {}
    for f in F:
        A, B, C, k, tag = f
        # "d" faces (A,B,C): base A-B on circle k, apex C.  "u" faces (B,D,C): base D-C on circle k+1, apex B
        if tag == "d":
            base, leg = np.linalg.norm(V[B] - V[A]), np.linalg.norm(V[C] - V[A])
        else:
            base, leg = np.linalg.norm(V[C] - V[B]), np.linalg.norm(V[B] - V[A])
        key = f"R{k+1}{tag}"
        panels[key] = (base, leg)
        counts[key] = counts.get(key, 0) + 1
    shapes = {}
    for key, (base, leg) in panels.items():
        if base < 3 * slot_w() + 2 * KP["slot_depth"]:
            print(f"  warning: {key} base {base:.1f} mm is too short for 2 slots")
        shapes[key] = notched(isosceles(base, leg), KP["slots"])
        if shapes[key].geom_type == "MultiPolygon":
            print(f"  ERROR: {key} slots intersect and cut the apex off — use fewer slots, bigger panels or shallower slot_depth")

    # --- connectors: dihedral per edge, rounded
    nrm = {i: normal(V, f) for i, f in enumerate(F)}
    edges = {}
    for i, f in enumerate(F):
        for a, b in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
            edges.setdefault(tuple(sorted((a, b))), []).append(i)
    angles = {}
    for e, fs in edges.items():
        if len(fs) != 2: continue
        d = math.degrees(math.acos(np.clip(np.dot(nrm[fs[0]], nrm[fs[1]]), -1, 1)))
        d = int(round(d / S["angle_step"]) * S["angle_step"])
        angles[d] = angles.get(d, 0) + KP["slots"]
    cons = {f"con_{a}": connector(a) for a in angles}

    # --- BOM
    print("panels:")
    for key in sorted(panels):
        b, l = panels[key]
        print(f"  {key}: base {b:.1f}  legs {l:.1f}  x{counts[key]}")
    print("connectors:")
    for a in sorted(angles): print(f"  con_{a}: x{angles[a]}")
    rim = 2 * math.pi * (S['r0'] + R * S['flare'])
    print(f"waist Ø {2*S['r0']:.0f} mm, hem Ø {2*(S['r0']+R*S['flare']):.0f} mm, length {R*S['H']:.0f} mm, "
          f"{len(F)} panels, {sum(angles.values())} connectors, slot drawn panel {slot_w():.2f} / connector {modkit.con_slot_w():.2f}")

    # --- files
    items = []
    for key, poly in shapes.items():
        b = poly.bounds; p = translate(poly, -b[0] + 2, -b[1] + 2)
        write_dxf([(p, 0, 0, key)], f"out_skirt/{key}.dxf")
        write_svg([(p, 0, 0, key)], f"out_skirt/{key}.svg", b[2] - b[0] + 4, b[3] - b[1] + 4)
        items += [(key, poly)] * math.ceil(counts[key] * (1 + S["spare"]))
    for key, poly in cons.items():
        b = poly.bounds; p = translate(poly, -b[0] + 2, -b[1] + 2)
        write_dxf([(p, 0, 0, None)], f"out_skirt/{key}.dxf")
        a = int(key.split("_")[1])
        items += [(key, poly)] * math.ceil(angles[a] * (1 + S["spare"]))
    items.sort(key=lambda it: -(it[1].bounds[3] - it[1].bounds[1]))
    sheets = layout(items)
    for i, placed in enumerate(sheets, 1):
        write_dxf(placed, f"out_skirt/sheet_{i}.dxf")        # ring labels are on the ENGRAVE layer
        write_svg(placed, f"out_skirt/sheet_{i}.svg", KP["sheet_w"], KP["sheet_h"])
    print(f"{len(items)} parts (incl. {int(S['spare']*100)}% spare) on {len(sheets)} sheet(s)")

if __name__ == "__main__":
    main()
