---
week: 07
date: 10/28
topics: [input devices](http://academy.cba.mit.edu/classes/input_devices/index.html)
recitation: Edge AI
title: input device
status: WIP
hero: img/week07/img_8216.jpg
summary: A step-response touch board on a XIAO RP2040, and a pressure sensor plan for an LED matrix you press to hide parts of your digital body.
---

## Assignment

Measure something: add a sensor to a microcontroller board that I designed and read it.

## What I made

I designed and milled a small XIAO RP2040 board that reads a copper electrode with step response (capacitive sensing) and drives an LED with four brightness steps. Touching the bare copper works. Through 3 mm of acrylic it does not.

<div class="cols" markdown="1">
<figure><img src="img/week07/img_8216.jpg" alt="The soldered XIAO board wired to a copper plate electrode with a small LED module on it, a hand resting on the plate" style="width:100%;aspect-ratio:3/4;object-fit:cover"><figcaption>The board, the copper electrode and the LED module.</figcaption></figure>
<figure><video src="img/week07/img_8191.mp4" controls muted loop playsinline preload="metadata" style="width:100%;aspect-ratio:3/4;object-fit:cover;background:#000"></video><figcaption>Touching the copper changes the LED brightness.</figcaption></figure>
</div>

This connects to my final project, a sculpture of my "digital self": a body made of triangular panels, where each panel stands for one thing an AI infers about me. When you press a triangle, that inference dims or disappears (100 → 60 → 25 → 0 %).


## Process

### Schematic

My first schematic had eight touch electrodes (T1–T8) on a 2×8 header. I simplified it to one electrode and one LED, so I could test whether sensing through acrylic works at all before making eight of them.

:::cols natural
![First KiCad schematic with eight touch inputs on a XIAO RP2040](img/week07/sch_v1_8touch.jpg)
*First version: eight electrodes.*
![Simplified KiCad schematic: one touch input, one LED with a 100 Ω resistor](img/week07/ss_1102_55703.jpg)
*Final version: one electrode and one LED.*
:::

| Ref | Part | Role |
|---|---|---|
| M1 | XIAO RP2040 (Fab module) | Microcontroller |
| J1 | 1×1 pin header | D0 → copper electrode (touch) |
| J2 | 1×2 pin header | D8 → LED inside the panel, and GND |
| R1 | 100 Ω (1206) | LED resistor |

ERC first complained that the power pins were not driven. Adding power flags fixed it.

![KiCad electrical rules check window with the power pin error](img/week07/ss_1102_55739_c.jpg)
*ERC: "Input Power pin not driven by any Output Power pins".*

### PCB layout

I set the net classes (track width and clearance) in Board Setup, placed the footprints and routed the board. DRC still showed warnings about the silkscreen and text height, which do not matter for milling.

:::cols natural
![KiCad Board Setup with the net class track widths](img/week07/ss_1102_61105.jpg)
*Board Setup: net classes.*
![The routed board in KiCad](img/week07/pcb_routed.jpg)
*Routed board.*
:::

:::cols natural
![KiCad design rules check window](img/week07/drc.jpg)
*DRC.*
![3D view of the board with the XIAO and two headers](img/week07/pcb_3d.jpg)
*3D view.*
:::

### Milling on the Carvera

I exported F.Cu and Edge.Cuts as PNG and made the toolpaths in mods.

:::cols natural medium
![mods PNG export settings](img/week07/mods.jpg)
*Exporting the PNG for mods.*
:::

The first boards had thin copper strips left between the traces. One side also came out badly because the board was lifted, so I taped the whole back and used auto-leveling. I also learned to export F.Cu and Edge.Cuts with the same settings, otherwise the outline does not line up.

:::cols natural narrow
![The milled touch board held between two fingers](img/week07/img_8185.jpg)
*The milled board.*
:::

### Reading the sensor

The code reads the electrode with the XIAO's internal pull-up (step response): it charges the pin and counts how long it takes to read HIGH, averaged over 128 samples. It keeps a slowly moving baseline, and each new touch moves the LED to the next brightness step.

:::code files/week07/touch_panel.ino | Touch panel (touch_panel.ino)

How it works:

- `readOnce()`: the pin is set to OUTPUT and LOW for 20 µs, which empties the electrode. Then it switches to INPUT_PULLUP, and the loop counts until the pin reads HIGH. A finger adds capacitance, so charging takes longer and the count goes up.
- `readSensor()`: averages 128 of those counts. This is `raw`.
- `setup()`: measures for a moment with no hand on the panel and saves the average as `base`.
- `loop()`: a touch starts when `raw` goes above `base + 8` and ends when it falls below `base + 4`, so it does not flicker. Each new touch moves the LED to the next level (100 → 60 → 25 → 0 %), and the LED fades to it. While nobody touches, `base` slowly follows `raw` to cancel drift.

<figure><video src="img/week07/serial_touch.mp4" controls muted loop playsinline preload="metadata" style="width:100%;max-width:640px;display:block;margin:0 auto;background:#000"></video><figcaption>Serial monitor: raw value, baseline, threshold and LED level.</figcaption></figure>

| Setup | Untouched | Touched | Difference |
|---|---|---|---|
| Copper only | 27–28 (noise 27–34) | about 60 | +32 |
| Through 3 mm acrylic | 34 | 37 | +3 |

On bare copper a touch is very clear. The acrylic alone raises the baseline (27 → 34), and through it the change is only +3, the same size as the noise. So with this setup I cannot detect a touch through 3 mm of acrylic. The next step for touch is an external 1 MΩ resistor from a send pin (D10), which should make the measurement more sensitive.

### Next steps: from touch to pressure

Then I decided to try it on the 64×64 LED matrix (Adafruit 4732, 192 mm) from week 5: a frosted acrylic plate floats in front of the matrix, and you press it. I planned to use **transmit-receive step response**, but I didn't have time to build it yet. Here is the plan:

- A copper ring on the back of the acrylic plate is the transmitter (TX), one wire for all corners.
- Each corner has a copper pad (RX) on a 3D-printed post, with 3 mm of soft foam on top.
- Pressing squeezes the foam, the TX–RX gap gets smaller and the signal gets bigger.
- The corner with the largest reading picks one of 4 zones, and the sum of the four readings gives 4 press levels.

![Diagram: four copper electrodes under the corners of the plate, the cross-section at one corner, and the four press levels](img/week07/press_4levels_stepresponse.jpg)
*4 zones × 4 press levels.*

### Case

I designed a case for the matrix and the sensor and printed it on the Prusa MK4S.

:::cols natural
![Cross-section at one corner of the case](img/week07/section.jpg)
*One corner: bezel, acrylic, foam and electrodes, spacer, matrix.*
![Back cover and easel foot](img/week07/back_cover_preview.jpg)
*Back cover for the wiring, and the foot that leans it back 15°.*
:::

| Part | Size (mm) | Notes |
|---|---|---|
| Body | 208 × 208 × 50 | holds the matrix on a 3 mm lip |
| Spacer | 195 × 195 × 25 | white, so it reflects the light; the four corner posts hold the electrodes |
| Bezel | 208 × 208 × 3 | keeps the plate from falling out, with 1 mm of play so it can sink |
| Back cover | 208 × 208 × 33 | wiring, driver board, cable exit at the bottom |
| Acrylic | 190 square + 194/168 ring | 3 mm, laser cut |

Printing notes: the 208 mm parts only just fit the 210 mm bed, so only an inner brim works. The first spacer print shook and lifted, so I slowed it down (gyroid infill, outer walls 60 mm/s, acceleration 2500, fan 40–70 %).

## Use of AI

I used Claude to answer KiCad questions, check my milling jobs, write the Arduino code, design the case (as Python scripts that output STLs), slice the G-code, and draw the illustrations and the sensing schematic. Claude also turned my notes and photos into this page. The board design, milling, soldering, measurements and the direction of the project are my own.

## Files

- [KiCad project and Gerbers](files/week07/input_device_kicad/)
- [touch_panel.ino](files/week07/touch_panel.ino) — one-electrode touch with 4 LED steps
- [txrx_test_1ch.ino](files/week07/txrx_test_1ch.ino) — first tx/rx test with one electrode pair
- [cap_press_4zone.ino](files/week07/cap_press_4zone.ino) — 4 zones × 4 press levels
- [cap_press_xy.ino](files/week07/cap_press_xy.ino) — x/y version
- [Sensing schematic (SVG)](files/week07/cap4-schematic.svg)
- [Case STLs and acrylic SVG](files/week07/case/)
