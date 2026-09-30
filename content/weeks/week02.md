---
week: 02
date: 09/23
topics: [embedded programming](http://academy.cba.mit.edu/classes/embedded_programming/index.html)
recitation: electronics
status: WIP
hero: img/week02/kigopad.jpg
summary: Soldering Quentin's QPad for the first time, programming it in the Arduino IDE, and learning electronics from zero until the schematic and the datasheet finally made sense.
---
## Assignment 

• browse through the data sheet for a microcontroller
• write and test a program for an embedded system using a microcontrollet to interact (with input &/or output devices)  dand communicate (with wired or wireless connections)

# Learning electronics basic

I had no electronics knowledge and had not touched physics for ten years, so every word in the lecture was new to me. Before going further I wanted to understand the basics. I first watched [an introductory video](https://www.youtube.com/watch?v=nYuVSG89vg0). Then I gave the assignment and the class links to Claude and asked it to make a curriculum with quizzes for someone with no electronics background.

<!-- TODO: link English versions of the two study pages once they are public -->

I followed two sets of notes. The first, Embedded Bench Notes, goes from electricity basics (voltage, current, resistance, components and schematics) to digital logic and what is inside a microcontroller, then how code reaches the board, and finally inputs, outputs and communication (buttons and touch, LEDs, PWM, the OLED, serial and I2C). The second walks through the QPad schematic step by step: counting the parts, the XIAO pins, power and ground, net labels, the R4 and R5 pull-ups on SDA and SCL, and why the touch pads have no parts at all.

Following the curriculum, I drew the diagrams myself, and the vocabulary finally started to make sense.

:::cols
![Notebook sketch of the QPad power and I2C connections, with notes on M, J and R](img/week02/IMG_7410.jpg)
*My own drawing of how power and the SDA and SCL lines reach the OLED, with a note that M is a module, J a jack and R a resistor.*
![Whiteboard with a hand-drawn QPad diagram and notes on pull-up resistors](img/week02/IMG_7411.jpg)
*Testing myself on the whiteboard during a dinner break.*
:::

## Soldering the QPad

First, to learn basic soldering and embedded programming, we used the QPad, a teaching board that our TA Quentin designed. In the training he showed us how to assemble it: a microcontroller (the Seeed XIAO RP2040 module), an OLED display and six capacitive touch pads.

:::cols
![Quentin explaining the QPad to a group of students in the lab](img/week02/IMG_7316.jpg)
*Quentin walking us through the board before we started soldering.*
![Quentin holding up his phone with the QPad schematic](img/week02/IMG_7324.jpg)
*Quentin showing the QPad schematic on his phone: the XIAO pins on the left, with the six touch pads, SDA and SCL.*
:::

The README of the [QPad repository](https://forge.cba.mit.edu/quentin.bolsee/qpad-xiao) lists what the board needs.

> To assemble this board, you need: OLED module, xiao rp2040, resistors: 2x 10k, or anything in the 2-10k range, circuit board, 3D printed support (optional), 3D printed jig (optional).

![The QPad parts laid out: XIAO RP2040, OLED module, 3D-printed support, blue circuit board and the light blue jig](img/week02/items.jpg)
*Everything that goes into one QPad: the XIAO RP2040, the OLED module, the 3D-printed support, the bare board and the jig that holds it while soldering.*

The iron was set to 350°C, and we took turns trying it at the bench. Under the microscope I could see that the solder wire is hollow, with flux inside the core, and I could watch Quentin's joints form up close.

:::cols
![Microscope screen showing the tip of the flux-core solder wire](img/week02/IMG_7322.jpg)
*The flux-core solder wire under the microscope.*
![Microscope screen showing Quentin soldering a pin on the board](img/week02/IMG_7328.jpg)
*Watching Quentin solder under the microscope.*
![A tiny 1206 resistor on the bench](img/week02/IMG_7320.jpg)
*One 10k resistor in the 1206 size, about 3 mm long.*
:::

After the training I tried soldering on my own for the first time, following Quentin's [soldering guide](https://pub.cba.mit.edu/quentin.bolsee/qpad-page/soldering/). I struggled to melt the solder. It went everywhere, and I needed a flux pen to clean up the mess.

![The bare QPad board with the two 10k resistors R4 and R5 soldered next to the XIAO footprint](img/week02/IMG_7333.jpg)
*My first joints: R4 and R5 next to the XIAO footprint, with more solder than they needed.*

Quentin helped me fix it, and together we figured out that the thin conical tip I had started with made the solder much harder to melt. I switched to a larger tip and it worked much better.

:::cols
![The thin conical soldering tip](img/week02/IMG_2825.jpg)
*The thin tip I started with. It touches the joint at a single point, so heat moves into the pad slowly.*
![The larger chisel soldering tip](img/week02/IMG_2826.jpg)
*The larger tip I switched to. More contact area, so the pad heats up and the solder flows.*
:::

Then I followed the rest of the assembly guide and finished the board. It is not beautiful, but hopefully I will improve as the course goes on.

:::cols
![The finished QPad held in my hand, with the XIAO and the OLED soldered on](img/week02/IMG_7334.jpg)
*The finished QPad.*
![Selfie with classmates at the soldering bench](img/week02/IMG_2832.jpg)
*Soldering bench.*
:::

## Reading the datasheet

I read the [RP2040 datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf) to understand which GPIO pins can be I2C SDA and SCL, what voltage counts as HIGH, the value of the internal pull-up used by the touch pads, the bits and pins of the ADC, and how much current one pin can supply. It's over 600 pages so I only read the relevant parts. 

The pin locations (section 1.4.1) show the 56 legs of the chip. 

![RP2040 pinout for the QFN-56 package](img/week02/pin_location.png)
*RP2040 pin locations, datasheet section 1.4.1. Only GPIO26 to GPIO29 can also be ADC inputs.*

The GPIO function table (section 1.4.3) lists what each pin can become, F1 to F9. GPIO6 and GPIO7 can be I2C1 SDA and SCL, which is why the OLED is wired to D4 and D5. The touch pads only need plain HIGH and LOW (SIO), so they can go on any pin.

![RP2040 GPIO function select table](img/week02/gpio_functions.png)
*The GPIO function table, datasheet section 1.4.3.*

According to the IO electrical characteristics (section 5.5.3.4), any input above 2V is read as HIGH and anything below 0.8V as LOW. The input leakage current is at most 1 µA, which is why an input pin barely draws current and a pull-up resistor holds it at 3.3V.

![RP2040 digital IO characteristics table](img/week02/io_electrical_characteristics.png)
*Digital IO characteristics, datasheet section 5.5.3.4.*

## Programming in the Arduino IDE

Next I tested Quentin's [example code](https://forge.cba.mit.edu/quentin.bolsee/qpad-xiao/src/branch/main/code/Arduino). Following the Boards Manager instructions, I added the package URL in the IDE settings and installed the Arduino-Pico core, then selected Seeed XIAO RP2040 as the board. Getting my laptop to see the board took a few steps. I held the BOOT button while plugging it in, the red and blue lights came on, the IDE showed an unknown UF2 board, and after pressing the R (reset) button the correct port appeared.

I went through Quentin's four sketches one by one: [blink_RP2040](https://forge.cba.mit.edu/quentin.bolsee/qpad-xiao/src/branch/main/code/Arduino/blink_RP2040), [test_display_RP2040](https://forge.cba.mit.edu/quentin.bolsee/qpad-xiao/src/branch/main/code/Arduino/test_display_RP2040), [test_serial_RP2040](https://forge.cba.mit.edu/quentin.bolsee/qpad-xiao/src/branch/main/code/Arduino/test_serial_RP2040) and [test_touch_RP2040](https://forge.cba.mit.edu/quentin.bolsee/qpad-xiao/src/branch/main/code/Arduino/test_touch_RP2040).

:::cols
![The QPad plugged in over USB-C, with text on the OLED](img/week02/IMG_7337.jpg)
*The display sketch running on my board.*
![The OLED showing the text Yui is cool!](img/week02/IMG_7336.jpg)
*Changing the text in test_display to my own message.*
:::

The touch sketch prints one number per pad to the Serial Monitor. The number is how many times the loop runs before the pad charges up to HIGH, so it grows when a finger adds capacitance. The sketch counts a pad as touched when the number goes above 6. I tried it with my fingers and through a water bottle.

:::cols
![Serial Monitor showing six columns of touch values, with the second column around 70](img/week02/IMG_7406.jpg)
*Touching pad 1: its count rises to about 70 while the untouched pads stay at 0 or 1.*
![Serial Monitor showing touch values, with one column around 115 and another around 70](img/week02/IMG_7408.jpg)
*Two pads at once, one at about 115 and one at about 70.*
:::

# Writing and Testing the "Kigo Pad"

I wanted to use QPad for walking a saijiki, the seasonal word dictionary haiku poets use. The map is a grid of the 72 micro-seasons (七十二候) by the 7 traditional categories of season words, 504 cells in all. The OLED is a small window onto one cell of that map.

## Concept: a spatial understanding of words

One of my favorite things to do at a book cafe was to collect interesting books, then return them at the end of the day without looking up where they belonged. I had to explore the shelves myself to learn where each book lived, and each piece of knowledge became tied to a place. But on the internet we get lost. Everything is zoomed in, and we have very little sense of where one word sits in relation to others. Keisuke Matsuoka describes the shift from exploring to searching in his book "The Sociology of Google Maps":
> Rather than stepping outside their own bodies to grasp the whole in relative terms, people may have become absorbed in looking only at their current location and its surroundings, always with their own body as the reference point.

I thought the QPad could be an interesting device for exploring a map of words.
<!-- (Related ideas: topophilia, Bachelard's *The Poetics of Space*, and utamakura, the named places of classical Japanese poetry.) -->

So on the QPad, the pads are the controller for moving around the space. The OLED shows the word and where I am on the map. Four of the six pads are arrow keys. Left and right walk through time, one micro-season at a time from 立春 (start of spring) to 大寒 (greatest cold). Up and down change the angle, from weather to landscape, daily life, festivals, animals and plants. The other two pads zoom in and out.

<!-- TODO: link the project that used four pads as arrow keys and two for other functions to move pixel art -->

## Web prototype
Before touching the hardware I made a browser prototype with Claude that simulates the QPad and its OLED. It runs in any browser: [open the prototype](files/week03/kigo-pad/prototype.html). The arrow keys walk, `i` zooms in, `o` zooms out. The device has three zoom levels 
1. The middle one shows a single word, large. 
2. Zooming in shows its meaning and reading. 
3. Zooming out shows the place: a dot for where I am on the whole 72 × 7 map.

![Four OLED screens stacked: the word view for 春の海, its explanation, the place view with a dot on the map, and the word view for 東風解凍](files/week03/kigo-pad/tools/sim_device.png)
*Simulated OLED screens. From the top: the word, zoomed in to the explanation, zoomed out to the place, and the first micro-season.*

All the source is in [files/week03/kigo-pad](files/week03/kigo-pad/).

## Rendering Japanese on the OLED
The first hardware problem was making kanji readable on a 128 × 64 OLED. The Adafruit GFX font has no kanji, so I made a Python script ([make_font.py](files/week03/kigo-pad/tools/make_font.py)) with Claude Opus 4.8 to render only the characters the almanac actually uses into bitmaps: 209 kanji at 32 px in a Mincho typeface, and 104 kana at 16 px in a bold Gothic, because thin Mincho strokes disappear at small sizes. Together they take about 29 KB, which is small next to the 2 MB of flash on the XIAO. The test sketch [kigo_min.ino](files/week03/kigo-pad/firmware/kigo_min/kigo_min.ino) decodes each UTF-8 string, looks up each glyph and draws it pixel by pixel, stepping through all 72 micro-seasons every 2.5 seconds.

![東風解凍 in 32 px kanji with its reading はるかぜこおりをとく in 16 px kana, drawn as white pixels on black](files/week03/kigo-pad/tools/preview.png)
*The first micro-season, 東風解凍 (the east wind melts the ice), drawn back from the generated bitmaps at OLED resolution.*

## Touch Pad Scripts

With the fonts working, I wanted to move through the map with the six pads. From Quentin's `test_touch` example, I learned measuring capacitance by timing can be used as buttons. It drives the pad LOW to empty it, switch it to an input with a pull-up, and count how many loops pass before it charges back to HIGH. A finger adds capacitance, so a touched pad charges more slowly and the count climbs; anything past a small threshold counts as a touch. 

```cpp
// count how long a pad takes to charge back to HIGH — a finger makes it slower
int readTouch(int pin){
  pinMode(pin, OUTPUT); digitalWriteFast(pin, LOW);  // drain the pad
  delayMicroseconds(25);
  pinMode(pin, INPUT_PULLUP);                         // let it charge
  int t = 0; while (!digitalReadFast(pin) && t < TOUCH_TMAX) t++;
  return t;                                           // touched → larger count
}

Before mapping pads to directions I had to learn which physical pad was wired to which GPIO. I touched each one and noted which pin value rose, then drew the board as I hold it, with the OLED at the top:

┌──────────────────┬──────┬──────────────────────────────────────┐
│ pad on the board │ GPIO │                 role                 │
├──────────────────┼──────┼──────────────────────────────────────┤
│ top-left         │ 26   │ ↑ up (change category)               │
├──────────────────┼──────┼──────────────────────────────────────┤
│ bottom-left      │ 2    │ ↓ down                               │
├──────────────────┼──────┼──────────────────────────────────────┤
│ left             │ 27   │ ← left (walk back in time)           │
├──────────────────┼──────┼──────────────────────────────────────┤
│ right            │ 1    │ → right (walk forward)               │
├──────────────────┼──────┼──────────────────────────────────────┤
│ right pair       │ 4    │ q0 — tap to zoom in, hold to collect │
├──────────────────┼──────┼──────────────────────────────────────┤
│ right pair       │ 3    │ q5 — zoom out                        │
└──────────────────┴──────┴──────────────────────────────────────┘

//                    LEFT RIGHT UP DOWN q0 q5
int PAD_PIN[N_PAD] = {  27,   1, 26,  2,  4, 3 };
...
for (int i = 0; i < N_PAD; i++) {
  int v = readTouch(PAD_PIN[i]);
  touchPast[i] = touchNow[i];
  touchNow[i]  = (v > TOUCH_THRESHOLD);
  if (touchNow[i] && !touchPast[i]) { pressStart[i] = now; onPress(i); } // just pressed
  else if (!touchNow[i] && touchPast[i]) onRelease(i);                   // just released
}
// q0 held past 0.4 s → collect this word
if (touchNow[P_ZIN] && !q0Saved && now - pressStart[P_ZIN] >= HOLD_MS) { q0Saved = true; doSave(); }

:::video https://youtube.com/shorts/hCFWrETdXtQ?feature=share | Kigo pad

The full firmware is kigo_pad.ino (files/week03/kigo-pad/firmware/kigo_pad/kigo_pad.ino).

## Use of AI

I used Claude Opus 4.8. to build the two study pages and quizzes I learned from, and to answer my questions whenever a word did not make sense. The soldering, the testing and the drawings are my own. For the map for poets, I made the browser prototype, the font generation script and the firmware with Claude, starting from my own idea.
