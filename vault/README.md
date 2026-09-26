# vault — how to break into (almost) anywhere

Not linked from the main site. Type sizes follow the main site (--fs, Gridular name, Diatype/Geist body). Header right: "Map, HTMAA" — HTMAA goes back to the main site. Two doors in from the main site (js/site.js): click the red "How to make anything?" banner five times, or type `open` on any page. Both lead to `vault/`.

## Flow
1. `vault/index.html` — the password gate. Black page, big lowercase title, one underline. Wrong answers shake; no hints.
2. `vault/<16 hex>/index.html` — the Map. Dark; the cursor is a torch that reveals the Media Lab floor plan. Floors L G 2 3 4 5 6 bottom-left (also keys 0/L, G/1, 2–6, ↑↓; `#5` in the URL opens floor 5). Places you got into pulse green; click one to open its page.
3. `places/<id>.html` — one page per place: title, Where / When / How, the floor plan with the spot marked (links back to the map), then photo spreads.
4. `grid.html` (Index) lists every place; `information.html` is the about page.

## Adding a place
Everything comes from ONE list, `places.js`. Add an entry:

    { id:'e15-540', floor:'5', x:0.24, y:0.52,
      name:'E15-540', room:'E15-540, fifth level', date:'September 2026',
      how:'How I got in.', thumb:'img/01.jpg' },

`x, y` are fractions (0–1) of the floor image `floors/<floor>.png` (left→right, top→bottom). Then copy `places/e15-540.html`, rename it to `places/<id>.html`, change `data-place="<id>"` in `<body>`, and edit the photo spreads. The map marker, the index entry, the title, the meta and the mini-map are all filled in from `places.js`.

## Moving photos around (the easy way)
Open the place page, press **E**. Drag a photo to move it, drag the green corner to resize (height follows the photo), click to select and use ← → ↑ ↓ (shift = 5 rows), `[` `]` width, `r` rotate 90°, ⌫ remove. All photos sit on one long canvas, so drag them up and down as far as you like (the page scrolls when you drag near the edge). Photos can cross the fold but never overlap: while dragging a photo turns red over another one, and if you drop it there it jumps back. Press **S** to download the page with the new layout, and replace `places/<id>.html` with it. Press E again to leave edit mode.

By hand: each photo is `<figure data-box="row col width">` — row from the top (1 row = 1vw), col 1–24 (left page 1–12, right 13–24), width in columns. Height is worked out from the photo, so nothing is ever cropped. Add `data-rot="90"` (or 180 / 270) to turn a photo.

## Spreads
Each `<section class="spread">` is one two-page spread on a 24-column grid (left page = columns 1–12, right = 13–24). Presets: `L-full L-tall L-small L-low L-wide R-full R-tall R-wide R-small R-low R-big`, or your own `style="grid-area: row-start / col-start / row-end / col-end"` (rows are 1vw). Add `class="natural"` to avoid cropping. Place pages use `class="spread photos"` + `data-box` instead (above). Captions show on hover. Images ≤ ~130 KB (900 px, quality ~62) so forge accepts the push.

## Password
`python3 vault/setpass.py "new password"` — rewrites the hash in `index.html` and renames the gallery folder (the folder name is derived from the password, so it can't be read out of the source). Current: `sesame`. Case-insensitive.

## Floor plans
`floors/*.png` are cropped from MLMap-Print-2025-10-08.pdf (E14–E15), inverted, green. The E15 side of floors 5 and 6 is only an outline on the original map.
