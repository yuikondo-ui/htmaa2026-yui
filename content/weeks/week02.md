---
week: 02
date: 09/16
topics: [computer-controlled cutting](http://academy.cba.mit.edu/classes/computer_cutting/index.html)
recitation: [parametric design](https://pub.cba.mit.edu/alfonso.parra/HTMAA-CAD-Recitation/)
status: WIP
hero: img/week02/skirt_render.jpg
summary: A parametric press-fit kit for a modular acrylic skirt, a waffle-sliced cardboard mannequin to wear it, and what the laser taught me about kerf, fit and fire.
---

## Modular clothes

Modular garments are clothing that can be assembled and taken apart in pieces without sewing the pieces together ([definition](https://www.sciencedirect.com/science/article/pii/S0921344924000892)).

![Inspiration board: Refashion, Anrealage, Textile Studies, upcycled denim, modular pixel garments](img/week02/ref_board.jpg)
*Left to right: [Refashion](https://rebeccayelin.github.io/refashion/)'s fabric modules with reversible interfaces and its garment-pattern tool (Lin, Lukáč, Leake, UIST 2025); user prototypes; repurposed denim with grommet squares; modular pixel figures; [Textile Studies](https://rebeccayelin.github.io/encoding-decoding-constellations/#textile-studies), laser-cut lace on miniature mannequins, which is the visual target; a type-contour installation; the Refashion paper page; [Anrealage](https://www.thecuttingclass.com/a-modular-anrealage-silhouette-through-blocks/)'s block silhouettes.*

Three ideas run through these. Some garments are adjustable, where the wearer changes the shape, as in Lepore's drawstrings or Anrealage's blocks. Some are docked, where different materials are joined without sewing, as in sacai or Refashion. And some are modular in the strict sense, where one repeated piece makes the whole garment, as in Vogler's work, Variable Seams and Textile Studies.

:::cols
![Issey Miyake, triangulated white garment on the runway](img/week02/ref_issey_miyake.jpg)
*Issey Miyake. One folded triangle repeated over the whole body; the surface is the structure. [Source ↗](https://www.isseymiyake.com/)*
![Ilaria Lepore, Hiroi Trousers](img/week02/ref_hiroi_trousers.jpg)
*Lepore's Hiroi Trousers: oversized nylon with drawstrings that the wearer tightens or opens to change the silhouette. Adjustable. [Source ↗](https://www.ilarialepore.com/products/hiroi-trousers)*
![Kuon vintage boro patchwork pullover](img/week02/ref_kuon.jpg)
*Kuon's boro patchwork pullover: pieces of old indigo cloth joined into one garment. Modular by repair. [Source ↗](https://kuon.tokyo/ja/products/vintage-boro-patchwork-pullover-shirt)*
:::

Links: [Hiroi Trousers](https://www.ilarialepore.com/products/hiroi-trousers) · [sacai](https://ragtag-global.com/blogs/the-ragtag-journal/sacai-hybrid-style) · [modular tote](https://www.youtube.com/watch?v=u8fJbSVdQxA) · [Refashion](https://rebeccayelin.github.io/refashion/) · [Anrealage](https://www.youtube.com/watch?v=rTy9v-6TNmQ) / [blocks](https://www.thecuttingclass.com/a-modular-anrealage-silhouette-through-blocks/) · [Textile Studies](https://rebeccayelin.github.io/encoding-decoding-constellations/#textile-studies) · [Kuon](https://kuon.tokyo/ja/products/vintage-boro-patchwork-pullover-shirt) · [Vogler, Modular Fashion](https://medium.com/@CarolinVogler/modular-fashion-c98306c820a9) · [Vogler, Fabricating human shapes](https://medium.com/@CarolinVogler/fabricating-human-shapes-6854cb14aef7) · [Variable Seams](https://www.variableseams.com/)

Inspired by these, I decided to use acrylic, where the laser kerf actually matters, joined with press-fit connectors, plus a cardboard mannequin to wear it at tabletop scale like the Textile Studies pieces. So the plan became a modular skirt in acrylic and a mannequin to put it on.

I also built an interactive prototype of the mannequin and skirt in Three.js. Every slider is a real cut parameter, and the whole thing is a single file with no build step.

:::embed files/week02/week02_preview_en.html | Interactive prototype: mannequin and skirt (Three.js)

## The triangle kit

I started with panels made from triangles, written in Python with Claude as `modkit.py`.

![Kit parts: tri, tile, half, dart, connectors](img/week02/kit_parts.jpg)
*The kit. `tri` is an equilateral triangle with slots on every edge; `tile`, `half` and `dart` are a square, a half square and a trapezoid, where the dart gives curvature by its shape; `con_0` is a straight connector for coplanar panels and `con_<angle>` an angled one that sets the dihedral angle between panels; `fit_test` is a strip of slots stepping 0.1 mm around the material thickness.*

The generator is Python with shapely and ezdxf, and writes a DXF with CUT and ENGRAVE layers.

:::source files/week02/modkit.py

Triangles because a surface made of squares can only be flat or bent one way. Triangles are the smallest piece that can tile a curved surface: change the angle between neighbouring triangles and the surface curves. A triangle also cannot change shape once its three edges are fixed, so an assembled triangle mesh is stiff without extra bracing.

Slots on the edges and a separate connector because two rigid acrylic sheets cannot hook into each other the way felt can. Vogler's tab-and-slot only works because felt bends. So the panels carry only slots, and a small connector bridges two of them. That makes every panel identical and every edge identical, so any panel fits anywhere, which is what reconfigurable needs. The connector also carries the angle: a straight one gives a flat surface, an angled one folds it.

Everything is a parameter because the kit was designed in cardboard numbers and cut in acrylic. Only `thickness` and `fit` changed; the geometry followed.

## Rebuilding the panel in Fusion 360

To understand the logic I rebuilt the panel and connector in Fusion 360 by myself, fully parametric. I gave myself one rule for the whole build: never type a number into a dimension, only a parameter name or an expression.

### Parameters

I started with the parameters (Modify → Change Parameters → User Parameters).

| name | unit | expression | note |
|---|---|---|---|
| `thickness` | mm | 3 | acrylic (measure the real sheet) |
| `kerf` | mm | 0.15 | laser cut width |
| `fit` | mm | −0.05 | negative = tighter |
| `slot_w` | mm | `thickness + fit - kerf` | drawn slot width, 2.80 |
| `W` | mm | 40 | triangle edge |
| `n_slots` | No Units | 2 | must be unitless or Pattern's Quantity rejects it |
| `slot_pitch` | mm | `W / (n_slots + 1)` | 13.333 |
| `slot_d` | mm | 5 | insertion depth |
| `corner_r` | mm | 1.5 | |
| `con_gap` | mm | 1.5 | gap between joined panels |
| `con_height` | mm | 12 | fin height |
| `con_len` | mm | `2 * slot_d + con_gap` | 11.5 |

### Panel

The triangle is an inscribed polygon with three sides, centred on the origin, in a sketch on XY. I dimensioned one edge and typed `W`; it shows as `fx: 40.00` once linked. One vertex sits on the Y axis so the base is horizontal and the centroid is the origin, which the circular pattern needs later.

Then one slot on the base: a two-point rectangle standing on the base line, with three dimensions and one constraint. The width is `slot_w` (2.80). The top edge to the base is `slot_d` (5.00), which fixes both depth and vertical position. The right edge to the Y axis is `slot_pitch / 2 - slot_w / 2` (5.267); the dimension is edge-based, so half the width has to be subtracted, and with `slot_pitch / 2` alone the pair comes out asymmetric. The bottom-left corner is coincident with the base line. Lines turn black when fully constrained; blue means they can still move.

The second slot on the same edge is a rectangular pattern of the slot's four lines, window-selected so the base line is not caught, along the base line, with distribution set to Spacing, quantity `n_slots` and distance `slot_pitch`. Two things went wrong first: `n_slots` stayed red until I changed its unit to No Units, and with Extent instead of Spacing the copy landed on the Y axis, because Extent means total length.

:::cols natural
![Sketch: triangle with one fully dimensioned slot](img/week02/fusion_01_slot_dimensions.jpg)
*The triangle with one fully constrained slot. Every dimension is a parameter or an expression.*
![Rectangular Pattern dialog](img/week02/fusion_02_rect_pattern.jpg)
*The rectangular pattern that puts the second slot on the base edge.*
:::

The other two edges come from a circular pattern of the six slot lines about the centroid, full, quantity 3. The slots rotate 120° with the triangle, so they stay perpendicular to every edge. A rectangular pattern can only translate, which is why this step needs the circular one. Then extrude by `thickness`, selecting only the big triangular profile. My first attempt selected the six small slot profiles instead, which would have extruded six little bars.

Finally a fillet of `corner_r` on the three corners, and optionally 0.3–0.5 mm on the slot roots, where acrylic cracks.

### Connector

The connector `con_0` lives in the same file, because parameters are per file in Fusion; the document is in Part Design mode, so it is a second body rather than a component. It is a centre rectangle of `con_len` × `con_height` in a new sketch on XY, away from the panel. A slot at the right end is `slot_d` horizontal by `slot_w` vertical, with its top-right corner coincident with the body's right edge and its top edge `(con_height - slot_w) / 2` from the body top, which centres it without the origin. The same at the left end, or a mirror. Then extrude the H-shaped profile by `thickness` as a New Body; Join would fuse it to the panel. The result is an H on its side: two 5 mm slots from the ends, a 1.5 mm neck (`con_gap`), and 4.6 mm rails top and bottom.

To check the assembly I moved the connector body with M: rotate 90° so it stands, rotate 90° again about one of its thickness edges so its length runs perpendicular to the panel edge, then drag until the slot bottoms meet. That took three wrong orientations. The test that finally worked: seen from the top, the connector must read as a 2.8 mm line sticking 6.5 mm past the edge.

:::cols natural
![Wrong profile selection](img/week02/fusion_03_extrude_wrong.jpg)
*Wrong: the six slot profiles are selected in blue. The right pick is the one large face.*
![Finished panel body](img/week02/fusion_04_panel.jpg)
*The finished panel body after the fillet.*
![Connector inserted in a panel slot](img/week02/fusion_05_connector_inserted.jpg)
*The connector seated in a panel slot.*
:::

Parameters live per file, so panel and connector belong in the same file. Quantity fields need a unitless parameter. Coincident is point-to-curve; line-to-line is Collinear. Extrude selects profiles, so pick the big face, because the slots are separate profiles. And slot positions must be symmetric about the edge midpoint, because the neighbouring panel sees the edge reversed.

## Kerf and fit

### Characterizing the laser (group)

Before cutting anything of my own, we characterized the lab's xTool machines as a group: power and speed on cardboard and acrylic, then focus and kerf.

:::cols
![Cut test grid, xTool F1 Ultra, cardboard](img/week02/group_cut_test_f1ultra.jpg)
*Cut test on the xTool F1 Ultra. Power runs 50–100 % across the columns and speed 10–40 mm/s down the rows. Cardboard only cuts through in the bottom rows, at 15 mm/s or slower. Above that the line is scored, not cut, and at 100 % and 10 mm/s the edges char.*
![Score test grid, xTool P2, acrylic](img/week02/group_score_test_p2.jpg)
*Score test on the xTool P2 in orange acrylic: how visible a scored line is across 10–90 % power and 100–250 mm/s.*
:::

:::cols
![Focus test](img/week02/group_focus_test.jpg)
*The same circle cut at eight focus offsets. The crispest line marks the right height.*
![Kerf test](img/week02/group_kerf_test.jpg)
*Circles drawn with 0.0–0.7 mm of outward compensation. Dropping each cut-out disc back into its hole, the one that just fits gives the kerf.*
:::

![Name tags](img/week02/group_name_tags.jpg)
*Name tags.*

The laser burns a groove of width `kerf`, centred on the drawn line, so a slot comes out `kerf` wider than drawn. To get a physical slot of `thickness + fit`, the file has to draw it `kerf` narrower, which is where `slot_w = thickness + fit − kerf` comes from. `fit` is the design intent, negative for a press fit and positive for a slip fit; `kerf` is the machine's property. Only the difference `fit − kerf` reaches the file, so in practice either one can be adjusted.

### Test with acrylic

The first fit test was a strip with eight slots labelled −0.4 to +0.3 mm relative to the nominal 3.0 mm thickness. Every slot was loose, even −0.4. So the sheet was thinner than 3 mm, or the kerf wider than I had guessed, or both.

The second test shifted the range to −1.0 to −0.3, and −0.5 held. I cut panels and connectors at −0.5, and they would not go together at all. The strip only loads one joint, where a slot grips a piece of scrap. A real joint loads two at once, the panel gripping the connector and the connector gripping the panel, so it needs a looser number than the strip suggests.

For the third test, I cut three rows, each with two triangles and two connectors, all four parts cut at the same fit (−0.3, −0.2 and −0.1), with labels engraved so the parts could be matched after they dropped out of the sheet. The first attempt had no labels and the parts were impossible to tell apart. Panel slots at −0.2 and connector slots at −0.1 work. The panel and the connector come from the same sheet and still want different numbers, probably because the small connector heats and shrinks slightly. The generator now takes `fit` and `con_fit` separately.

:::cols tall
![Fit test strip](img/week02/fit_test_1.jpg)
*Fit test 1. All eight slots, down to −0.4 mm, were loose.*
![Fit test 3: labelled triangles and connectors](img/week02/fit_test_3.jpg)
*Fit test 3. Two triangles and two connectors per row, cut at the same fit, labels engraved. The −0.2 / −0.1 combination is the one that holds.*
:::

#### Fire

When I cut the acrylic at 80 % power and 20 mm/s, it caught fire. Two things probably came together: I had not removed the protective paper from the acrylic, and there was cardboard left on the bed from the mannequin test. The cardboard is most likely what burned. Next time I will clean the bed before running any job. And once something catches fire, stop immediately, with the emergency stop or pause, and put it out with the fire blanket.

![Parts from the cut that caught fire](img/week02/fire_parts.jpg)
*The parts from the cut that caught fire, paper still on. The connectors are charred at the edges.*

The same file on a black sheet did not fit at all. Nominal 3 mm extruded acrylic ranges roughly 2.6–3.1 mm, and a 0.4 mm change is far larger than the 0.1 mm steps of the fit test. The rule is now: change sheet, measure its thickness with calipers, set `thickness`. `fit` and `kerf` stay. Regenerating takes seconds.

The small scale exposed a bug. Shrinking the skirt to 0.4 scale made the first-ring triangles pointy, with a 49° apex. With two slots per edge at one third and two thirds, the two slots near the apex crossed and cut the apex off as a loose fragment. The fix is one slot per edge for small triangles, which also halves the connector count, or bigger triangles for two slots. The generator now reports an error when slots intersect.

### Test with plywood

The acrylic ran out, so I switched to 3 mm plywood. At 90 % power and 30 mm/s the beam did not go through; the parts tore when I pushed them out of the sheet and the thin connector rails broke. At 90 % and 20 mm/s the cut went through and the parts dropped out on their own. The lesson is not to pry: if a part needs to be pushed out, cut again more slowly rather than force it.

The acrylic numbers did not transfer either. Rows at fit −0.3, −0.2 and −0.1 were all too tight for the plywood, so I cut a second strip at 0.0, +0.1, +0.2 and +0.3. Wood is more forgiving than acrylic, because it compresses instead of cracking, so the useful range is wider. Two changes went into this second strip: the slot roots are rounded (0.4 mm) so cracks do not start at the inner corners, and the connector height went from 12 to 14 mm so the rails are thicker. The result is +0.3 for both the panel slots and the connector slots. Final numbers: thickness 3, kerf 0.25, fit +0.3. Only the difference fit − kerf reaches the file, so kerf stays at the guessed value and fit carries the correction.

:::cols tall
![Plywood parts cut at 90 % / 30 mm/s](img/week02/broken_wood.jpg)
*90 % power, 30 mm/s: not through. Pressing the parts out broke the narrow sections.*
![Plywood fit test strips](img/week02/fit_test.jpg)
*The second fit test, 0.0 to +0.3, with rounded slot roots. Row 3 (+0.3) is the one that holds.*
:::

With the numbers confirmed, I cut the whole kit: 42 panels in six labelled shapes and the connectors.

:::cols tall
![Kit on the laser bed](img/week02/kit_1.jpg)
*The kit on the bed: panels labelled by ring and direction (1d, 1u, 2d …), connectors along the left edge.*
![Sorted parts](img/week02/kit_2.jpg)
*Sorted by label, connectors in a box.*
:::

Assembled, the first connectors were too weak in the middle. The designed neck, the material between the two slots, was 1.5 mm, but the laser burns 0.12 mm off each slot bottom, so it came out at 1.25 mm, and the part label was engraved right on top of it, thinning it further. Three fixes: the neck is now drawn kerf-wider so the physical neck equals the parameter, the label moved to the rail, and the neck went from 1.5 to 2.5 mm and then to 5 mm. The trade-off is a wider gap between panels, because the neck is the gap, so the assembled ring grows by about 14 × 3.5 mm per ring.

Three panels joined d–u–d curve as expected, and the first ring closes. But the neck was still too narrow: with two connectors on one edge, neither would seat at the centre.

:::cols tall
![Three panels joined](img/week02/assembly_1.jpg)
*Three panels, d–u–d, joined with the angled connectors. The surface curves.*
![The first ring assembled](img/week02/assembly_2.jpg)
*The first ring closed. The connectors sit off-centre because the neck is too narrow.*
:::

So I doubled the neck again, from 5 to 10 mm, and recut the connectors. Then it worked. The alignment is not perfect: the connector angles are not all the same, so the vertical edges between rings do not line up well yet. Then the time was up. I wanted to have fun with colours, so I sprayed the kit purple and gold.

:::cols tall
![Connectors with a 10 mm neck](img/week02/neck_10mm.jpg)
*The recut connectors with a 10 mm neck.*
![Two rings assembled](img/week02/assembly_3.jpg)
*Two rings assembled with the 10 mm connectors. The panels seat, but the vertical edges drift.*
![The kit sprayed purple and gold](img/week02/colored.jpg)
*The kit sprayed purple and gold.*
:::

## Next: joint and shape in one piece

The connector count is the weak point of the kit for a user. I want the joint and the shape combined. Vogler's module does this:

> by having the positive and negative shapes on opposite sides, every triangle can fold up and connect to itself … having slots enables you to connect multiple positives to the same negative and create a dynamic web … weaving parts through the triangular part in the middle can replace darts

Her module works because felt bends; a rigid acrylic tab cannot pass through a slot. For acrylic this needs a hook shape that rotates in, on puzzle or chainmail logic, or a hybrid: acrylic panels with flexure connectors cut from polypropylene or PETG, which would also let the skirt move like cloth instead of holding a fixed polyhedral shape. Next I will try Vogler's shape in felt, and PP flexure connectors on the current panels.

## Laser-cut nori

A side project, inspired by patterned nori with the asanoha (麻の葉) motif. I made the pattern file with Claude ([asanoha_nori.svg](img/week02/asanoha_nori.svg)), engraved asanoha and cut sakura into sheets of nori on the laser, and made onigiri with it.

:::cols
![Reference: asanoha patterned nori](img/week02/ref_nori_asanoha.jpg)
*The reference: laser-cut patterned nori for designer sushi. [Source ↗](https://www.designboom.com/design/lasercut-nori-for-designer-sushi/)*
![Engraved asanoha nori](img/week02/nori_asanoha_engraved.jpg)
*Asanoha engraved into a sheet of nori.*
![Sakura cut-outs in nori](img/week02/nori_sakura_cut.jpg)
*Sakura cut out of nori.*
![Onigiri wrapped in sakura nori](img/week02/nori_onigiri.jpg)
*Onigiri wrapped in the sakura nori.*
:::

Nori turns out to be a good engraving test material: thin, uniform, and the pattern appears immediately as a colour change. The cut version needs low power and a single pass; it lifts and curls if the bed fan is strong. And the laser toasts it as it goes, so the nori comes out of the machine smelling good.

## Files

Everything is under `files/week02/` in the [repo](https://github.com/yuikondo-ui/htmaa2026-yui/tree/main/files/week02). `modkit.py` is the panel and connector generator with the fit test; `skirt.py` the flared skirt with per-ring panels and connectors at the needed angles; `mannequin.py` the waffle mannequin. The cut files are zipped: [out_skirt.zip](files/week02/out_skirt.zip) (panels, connectors and the 600 × 400 sheet), [out_mannequin.zip](files/week02/out_mannequin.zip) (two sheets) and [fit_tests.zip](files/week02/fit_tests.zip). `week02_preview_en.html` is the interactive preview, a single file with no build step. `triangle.f3d` is the Fusion version of panel and connector, parametric. `asanoha_nori.svg` is the nori pattern.

## Use of AI

I used Claude (Fable 5.1) throughout the week in three roles. As a generator, it wrote `modkit.py`, `skirt.py`, `mannequin.py` and the Three.js preview from my descriptions and references, and we revised them together as tests came back: the apex bug, the separate panel and connector fit, the multi-sheet layout. I read the core functions and can explain the slot formula and the pattern logic; I did not write the geometry code. As a tutor, it walked me through the Fusion 360 panel and connector step by step and through each error (the unit of `n_slots`, Extent versus Spacing, Coincident versus Collinear, which profile to extrude); the build and the stumbles listed above are mine. As an editor, it drafted this page from my Obsidian notes, and I edited it. The inspiration list, the process log and the fit-test observations are my own.
