---
week: 04
date: 10/07
topics: [electronics design](http://academy.cba.mit.edu/classes/electronics_design/index.html)
recitation: EDA (Electronic Design Automation)
status: WIP
hero: img/week04/hero.jpg
summary: Designing my own board to drive a 64×64 LED matrix that shows Spotify album art, from a breadboard oscillator to a single-sided PCB with zero DRC errors.
---

## Idea

I came across a project that turns a 64×64 LED matrix into a display showing the album art of whatever I'm playing on Spotify ([video](https://www.youtube.com/watch?v=Imc0zfjhUTw), [code](https://github.com/tnarla/spotify-matrix)). The original project uses an off-the-shelf Adafruit RGB Matrix Bonnet on a Raspberry Pi. I wanted to design the embedded microcontroller board myself, from scratch.

As a reference for the enclosure, I like the KM5 CD player: it would be cool to put the board in a transparent box so you can see the board design.

:::cols
![A 64×64 LED matrix showing a grayscale album cover](img/week04/spotify-matrix-reference.png)
*The original project: album art on a 64×64 LED matrix.*
![A CD player in a transparent yellow case, with its circuit board and disc mechanism visible inside](img/week04/km5-cd-player.png)
*The KM5 CD player: the board shows through the case.*
:::

## Learning the basics on a breadboard

I had no background in electronics, so I started from the fundamentals. I bought a few beginner textbooks in Japanese to get familiar with the vocabulary of circuits, and watched some introductory videos:

- [Electronics fundamentals](https://youtu.be/SGvOmwZvhVk?si=WzMcevOVxclBdw-Q)
- [Digital electronics](https://youtu.be/pDELW2pIvWw?si=CADkYAXTZFjQhA2f)

![A page from a Japanese electronics textbook explaining a timer circuit, with a schematic of three LEDs and capacitors and a photo of the built circuit](img/week04/textbook-timer-circuit.jpg)
*One of the textbooks: a timer circuit where a capacitor works like a bucket filling with water.*

They didn't make much sense to me at first. So over the weekend I bought a breadboard and a basic electronics kit, and followed [this tutorial on transistors](https://www.youtube.com/watch?v=5vRAACeebjI&t=124s) to build an oscillating circuit.

<video src="img/week04/breadboard-oscillator.mp4" controls muted loop playsinline style="width:100%;border-radius:6px"></video>

*My oscillating circuit on the breadboard.*

Physically touching each component changed how I related to them. I got emotionally invested. Once I had built something that blinked, I wanted to understand *why* each part was there.

## First design: Raspberry Pi + XIAO RP2040

### Learning with Claude

I asked Claude how to turn the Spotify display idea into a board I designed myself, and what I would need to learn along the way. It made me a step-by-step course (Ohm's law, pull-up resistors, analog input, power protection, logic levels, HUB75, and finally KiCad), which I worked through first.

:::embed files/week04/bonnet-course.html | Bonnet course, made with Claude

The first plan was a custom "bonnet": a Raspberry Pi Zero 2 W for Wi-Fi and Spotify, a XIAO RP2040 for buttons and sensors, and two 74AHCT245 chips to boost the Pi's 3.3V signals to the 5V the matrix expects.

:::cols natural
![Hand-drawn power diagram: a 5V 4A AC adapter split to the LED matrix and to a screw terminal, then reverse protection, 5V power, and on to the Pi, the level shifters and the XIAO](img/week04/sketch-power-flow-v1.jpg)
*How power flows through the first design.*
![Hand-drawn information flow: Spotify over Wi-Fi into the Pi, through the J4 header and the level shifters U1 and U2, out the HUB75 connector to the LED matrix, with the XIAO and two buttons talking to the Pi over UART](img/week04/sketch-information-flow-v1.jpg)
*How information flows.*
:::

I didn't understand much of the diagram at first, but I built each block in KiCad one at a time. **Drawing the schematic myself was the most helpful part.** It made me picture how electricity actually flows through the board.

![KiCad schematic of a XIAO RP2040 with a tactile switch and a 10k pull-up resistor on pin D8](img/week04/firstattempt_kicad.png)
*My first block in KiCad: one button with a pull-up resistor.*

### Understanding power and signals

While drawing, I sketched my own diagrams to understand what each component was for, and how signals travel from the Pi to the matrix.

![A hand-drawn simplified schematic with notes on why each part is there: reverse polarity protection, the capacitor that fills dips when the Pi draws more current, pull-up resistors, and bypass capacitors next to each 245](img/week04/sketch-annotated-components-v1.jpg)
*Notes on what each component is for.*

### How color gets from the image to the LEDs

I also wanted to understand how the color information actually reaches a 64×64 matrix. The panel only lights two rows at a time (one in the top half, one in the bottom half), and switches between them faster than the eye can see:

1. **Choose a row pair.** Five address lines (A–E) select one of 32 row pairs (2⁵ = 32).
2. **Shift in the colors.** On every CLK pulse, six data lines (R1 G1 B1 for the top pixel, R2 G2 B2 for the bottom pixel) send one bit of color for one column. 64 pulses fill both rows.
3. **Latch and light.** LAT locks the row data in, and OE turns the LEDs on.
4. **Repeat for each bit.** Each LED can only be on or off, so color is made by repeating this for each bit of the 8-bit color value. Higher bits stay lit longer (weights 128, 64, … 1), and the eye adds up the light into 256 brightness levels per color.
5. **Move to the next row pair**, and redraw the whole frame 100+ times per second.

One full-color frame takes 32 × 64 × 8 = 16,384 clock pulses, and the panel has no memory of its own, so the controller has to keep sending them nonstop.

![Notebook page tracing the R1 signal from the Pi through J4, the level shifter and HUB75 to the matrix, next to the five steps of drawing a frame](img/week04/sketch-hub75-color-signal.jpg)
*Working out the signal path and the frame steps.*

### Checking the schematic

After finishing the schematic, I ran three checks:

- **Annotate** (Tools → Annotate Schematic) to give every part a unique reference (R1, R2, C1…)
- **ERC** (Inspect → Electrical Rules Checker) to catch unconnected pins and missing power sources
- **Footprints** (Tools → Assign Footprints) to make sure every symbol has the right physical shape

![The full first schematic in KiCad: XIAO RP2040, a 2×20 header for the Pi, two 74HCT245 level shifters, a HUB75 2×8 connector, power input with reverse protection, buttons and an LED](img/week04/schematic-v1-xiao-pi.png)
*The finished first schematic.*

### First PCB

When I sent the schematic to the PCB editor, the ratsnest (the thin lines showing what still needs to be connected) was a mess. The Pi's GPIO pins and the HUB75 connector's pins are in almost opposite orders, so on a single-sided board many traces would have had to cross.

![KiCad PCB editor with the Pi header, XIAO, level shifters and HUB75 connector placed, and blue ratsnest lines crossing all over the board](img/week04/pcb-v1-ratsnest.png)
*The first ratsnest.*

## Second design: Raspberry Pi Pico 2 W

### Office hours

During office hours, Dimitar suggested simplifying the design: drop the Raspberry Pi and use a single microcontroller with Wi-Fi instead. We also agreed to remove parts I didn't really need: the reverse-polarity protection, the Schottky diode, and the spare sensor sockets.

![The first overview diagram with the Pi, J4, Q1, D2 and sensor sockets crossed out, and notes about using a single board instead](img/week04/sketch-office-hours-simplify.jpg)
*Crossing out parts during office hours.*

We also checked whether the RGB panel could take 3.3V signals directly. Looking at the [Adafruit documentation](https://cdn-learn.adafruit.com/downloads/pdf/adafruit-matrixportal-s3.pdf), we confirmed that the panel runs on 5V, so I kept the level shifters to make sure the matrix reads the signals reliably.

![Schematic of the Adafruit MatrixPortal S3, with its level shifter section](img/week04/adafruit-matrixportal-s3-schematic.png)
*Adafruit's MatrixPortal S3 also uses level shifters between the ESP32-S3 and the HUB75 output.*

### Clarifying the requirements

After office hours, I wrote down exactly what the microcontroller needed:

1. **At least 14 GPIO pins**, since HUB75 uses 14 signal lines (ideally ~17, to also fit two buttons and a status LED)
2. **Wi-Fi**, to fetch the album art from Spotify

The XIAO boards in our inventory only have 11 GPIO pins, and the XIAO ESP32S3 Plus (20 pins) was out of stock everywhere. Dimitar suggested the **Raspberry Pi Pico 2 W**, which has Wi-Fi and 26 GPIO pins, and was available in the shop. A single Pico 2 W replaces both the Raspberry Pi and the XIAO from my first design. I then ordered the LED matrix and the other parts we didn't have.

### New schematic

I drew a simplified diagram of the new circuit and its signal flow:

![Hand-drawn simplified v2: AC adapter to the screw terminal, Pico, level shifters and HUB75, with the buttons, LED, and a list of changes from v1](img/week04/sketch-simplified-v2.jpg)
*Simplified v2, with the list of changes from the first design.*

Building on the first version, I ended up with this schematic. The HUB75 signals use consecutive pins (GP0–GP13), which makes it easier to drive the matrix with the RP2350's PIO later.

![KiCad schematic of the Pico 2 W with HUB75 signals on GP0–GP13, two 74HCT245 level shifters, a 2×8 HUB75 connector, a screw terminal with a 47µF capacitor, two buttons and an LED](img/week04/schematic-v2-pico.png)
*The second schematic.*

| Part | Role |
|---|---|
| Pico 2 W | Wi-Fi, Spotify, and all control |
| 74HCT245 × 2 | Boost the Pico's 3.3V signals to 5V for the matrix |
| HUB75 connector (2×8) | Cable to the LED matrix |
| Screw terminal + 47µF capacitor | 5V power input, smoothed |
| 0.1µF capacitors × 2 | Bypass capacitors for each 245 |
| 2 buttons + 10kΩ pull-ups | Next track / pause |
| LED + 1kΩ resistor | Status light for testing |

## PCB layout

### Untangling the crossing traces

My first placement still had traces crossing everywhere. When two chips face each other, their pin orders run in opposite directions, so the Pico's GP0 at the top ended up connected to the 245's channel at the bottom.

All eight channels of a 245 do the same job, so I went back to the schematic and reversed which 245 channel each signal uses. After updating the PCB, the traces lined up in parallel.

:::cols
![PCB editor with the level shifters and HUB75 connector on the left and the Pico on the right, ratsnest lines crossing in an X](img/week04/pcb-v2-crossing.png)
*Before: the lines cross.*
![PCB editor with the level shifters placed above and below the HUB75 connector, ratsnest lines running in parallel](img/week04/pcb-v2-parallel.png)
*After reversing the channels: the lines run in parallel.*
:::

### Fitting traces between connector pins

The HUB75 connector has two rows of pins, and on a single-sided board the inner row can only be reached by passing a trace *between* the outer pins. With the default pads, the gap was too narrow for a trace plus clearance. I shrank the copper pads to 1.27 mm (keeping the drill holes the same size), which opened up a 1.27 mm gap. It was enough for a 0.4 mm trace with 0.4 mm clearance on each side.

![KiCad footprint editor showing the 2×8 pin header with smaller square pads](img/week04/hub75-footprint-pads.png)
*Editing the HUB75 footprint's pads.*

### DRC: from 40 violations to zero

When I first ran the Design Rules Checker, I had 40 violations.

![Routed traces next to the Design Rules Checker listing clearance violations of 0.2668 mm against a 0.4064 mm minimum](img/week04/drc-40-violations.png)
*40 violations on the first run.*

I went through them one by one:

- **Misaligned components:** some parts had shifted slightly, so traces no longer met their pads cleanly.
- **Design rule violations:** traces too close to pads.
- **Isolated ground islands:** traces I had drawn early on cut the ground fill into separate pieces, so some GND pins weren't connected. I rerouted those traces to let the ground fill reach them.
- **Overlapping text:** some silkscreen labels overlapped, so I moved the components or their labels.

I kept fixing and re-running the check until there were no errors.

:::cols natural
![The Design Rules Checker showing 0 violations and 0 unconnected items, next to the routed board with a ground fill](img/week04/drc-zero.png)
*Zero violations, zero unconnected items.*
![3D view of the finished board: the Pico footprint, two level shifters, the HUB75 header, buttons, resistors and the screw terminal](img/week04/pcb-v2-3d.png)
*The board in KiCad's 3D viewer.*
:::

## Use of AI

I used Claude to make a step-by-step course on the electronics I needed for this board (the bonnet course above). It also helped me come up with the system diagram for the first design, then guided me through drawing the schematic in KiCad and fixing the errors along the way. I also used it to help me write up this page.

## Files

- [kicad-week03.kicad_sch](files/week04/kicad-week03/kicad-week03.kicad_sch): final schematic (Pico 2 W)
- [kicad-week03.kicad_pcb](files/week04/kicad-week03/kicad-week03.kicad_pcb): final PCB layout
- [kicad-week03.kicad_pro](files/week04/kicad-week03/kicad-week03.kicad_pro): KiCad project
- [kicad-week03.pdf](files/week04/kicad-week03/kicad-week03.pdf): schematic as PDF
- [kicad-week03-oct12.kicad_sch](files/week04/kicad-week03/kicad-week03-oct12.kicad_sch): first schematic (Raspberry Pi + XIAO RP2040)
- [bonnet-course.html](files/week04/bonnet-course.html): the course I worked through

Open the KiCad files in KiCad 10.
