---
week: 03
date: 09/30
topics: [3D scanning and printing](http://academy.cba.mit.edu/classes/scanning_printing/index.html)
recitation: AI agents
status: WIP
hero: img/week03/body-tree-vs-normal.jpg
summary: Three prototypes of a body you can take apart and put back together, from a mannequin covered in printed scales to a lattice figure with number panels.
---

## Prototype 1: a mannequin with scales

My first idea was 3D printing modular clothing: a garment made of pieces you can take off and rearrange. I looked at Yuima Nakazato's [TYPE-1](https://store.yuimanakazato.com/en/pages/type-1), [Refashion: Reconfigurable Garments via Modular Design](https://programs.sigchi.org/uist/2025/program/content/203866) from UIST '25, and the Kinematics dress. After seeing ANREALAGE's Autumn/Winter 2026–27 collection "GHOST", I thought each scale could be its own panel that comes off.

I designed the scales, the panels and a small mannequin for them to attach to with Claude Fable 5.1.

### Printing

I printed on the Bambu Lab H2S in my lab, in PLA (220°C nozzle, 65°C bed): the mannequin in white and the scales in purple. The mannequin could not be made subtractively. It is a hollow shell with a narrow neck and holes all around.

:::cols
![The white mannequin printing inside the Bambu H2S, with purple scales on the plate beside it](img/week03/vase-printing.jpg)
*The scales are on the same plate.*
![The H2S touchscreen at 76%, printing a plate named overnight_plate_h2s](img/week03/printer-screen.jpg)
*76% done, nozzle at 220°C, bed at 65°C.*
:::

I got these two errors when starting.

- **"Prime Tower is too close to others."** The prime tower is the waste tower the printer uses to purge between colors, and it was sitting next to the scales. Dragging it to an empty corner of the plate fixed it.
- **132 filament changes.** I first gave the scales three colors. Every layer of the first few millimeters then switched colors three or four times, and each change takes one to two minutes, so changes alone added about three hours. For a test print, I learned I should use as few colors as I can.

The printer also turned out to have only a 0.2 mm nozzle, so the whole print took 15 hours.

:::cols natural
![The white mannequin on a desk with loose purple scales beside it](img/week03/vase-and-scales.jpg)
*Off the plate.*
![Close-up of the support struts inside the mannequin's neck](img/week03/vase-neck-supports.jpg)
*Support had grown inside the neck, where it is hard to reach.*
![Two rows of purple scales clipped onto the mannequin](img/week03/vase-scales-attached.jpg)
*Two rows of scales attached.*
:::

The scales could not overlap. My friend Matt, who is an architect, suggested printing the panels flat, overlapping the scales while they are still a flat sheet, and only then assembling it into a 3D form.

:::cols natural narrow
![Sketch: the mannequin split into sections, scales with pins going into the holes, and the scales laid flat](img/week03/sketch-flat-scales.jpg)
*Matt's idea: lay the scales flat first, then assemble.*
:::

I also did not like how the mannequin and the clothes looked together. I wanted to explore joints the way Kinematics does, so I made a generator with GPT Astra to try different joints and sizes: [Kinematics joint generator](https://data-barbie-kinematics.yuikondobook.chatgpt.site/). I didn't end up printing these, but I would love to explore joints again.

![Nervous System's Kinematics bracelets, sheets, necklace and dress](img/week03/ref-kinematics.jpg)
*Nervous System's Kinematics pieces.*

## Prototype 2: a datafied body

I thought the way to show our digital selves could be not clothes but the body itself. I wondered how people could reconfigure the body with their own hands: first you see a body built by an algorithm, then you take it apart yourself, then you rebuild it. So I started looking at body sculptures and how they could stand for a datafied body.

On my way to the gym, I see Jaume Plensa's *Alchemist*, a seated figure made of numbers and mathematical symbols. It felt like a good picture of how algorithms see the human body: as numbers and characters. I was also drawn to Antony Gormley, who translates the body into abstract blocks or wires.

:::cols natural
![A sculpture of a seated figure made of white numbers and symbols, lit at night](img/week03/ref-alchemist.jpg)
*Jaume Plensa, Alchemist, at MIT.*
![A drawing by Antony Gormley: a dark figure built up from crossing lines](img/week03/ref-gormley-1.jpg)
*Antony Gormley: the body as lines,*
![A figure by Antony Gormley made of stacked dark blocks, leaning on a wall](img/week03/ref-gormley-2.jpg)
*as blocks,*
![A crouching figure by Antony Gormley made of welded steel rods](img/week03/ref-gormley-3.jpg)
*and as wire.*
:::

I was also inspired by ANREALAGE's Spring/Summer 2027 collection "SKIN": how their clothes can change with LED panels, and how numbers were used to stand for the body.

![Models in dresses covered in projected green numbers, standing in front of a wall of numbers](img/week03/ref-anrealage.jpg)
*ANREALAGE, SS27 "SKIN".*

Building on these, I decided the numbers should be panels you can attach to the body. I generated an image of that body with GPT Astra, but its lines were too thin to print, so I made a thicker kneeling version as the print file.

:::cols natural
![A black wireframe figure with green numbers inserted into it](img/week03/body-field-preview.jpg)
*The first body: too thin to print.*
![A thicker black lattice figure kneeling on a round base, with three green number panels on its chest](img/week03/kneeling-print-preview.jpg)
*The kneeling version I printed.*
:::

### Tree supports vs normal supports

The figure is fragile and needed support. I had one full day on the printer in my lab, so I printed it twice to compare the two support types in Bambu Studio:

- **Tree (organic)** grows branch-like arms that wrap around the model and hold overhangs from the side.
- **Normal (snug)** prints straight up, as a solid grid directly under each overhang.

For fine detail, tree is usually the better choice.

:::cols natural
![Bambu Studio preview of the figure with green tree supports branching around it](img/week03/slicer-tree.jpg)
*Tree (organic) in Bambu Studio.*
![Bambu Studio preview of the figure with green normal supports filling the space under it](img/week03/slicer-normal.jpg)
*Normal (snug) in Bambu Studio.*
:::

:::cols
![The two figures printing in the Bambu H2S, one in tree supports and one in normal supports](img/week03/body-printing.jpg)
*Both versions printing side by side.*
![The two figures on the build plate from above, with the small green number panels at the back](img/week03/body-on-plate.jpg)
*From above. The small green pieces at the back are the number panels.*
:::

![The two figures still wrapped in green supports: tree on the left, normal on the right](img/week03/body-tree-vs-normal.jpg)
*Tree supports (left) and normal supports (right). The normal supports enclosed almost the whole figure.*

### Removing the supports

I cut the tree supports away with flush cutters from the clamps bin.

:::cols
![A green bin of clamps, pliers and flush cutters](img/week03/clamps-bin.jpg)
*The tools.*
![Cutting a green support branch away from the gray lattice with red flush cutters](img/week03/removing-supports.jpg)
*Cutting the branches one by one, without breaking the lattice.*
:::

:::cols natural
![The gray lattice figure on a black background with a pile of green supports at its feet](img/week03/body-supports-removed.jpg)
*The figure with its supports removed.*
![Close-up of the lattice figure's chest, with green number panels clipped on](img/week03/body-closeup.jpg)
*The number panels attached to the body.*
:::

I liked this combination of colors. But the number panels still looked separate from the body. I wanted the panels to be the parts that make up the body, so that rearranging them becomes the body sculpture itself.

## Prototype 3: panels that make the body

I was inspired by ANREALAGE's 2022 collection, a figure whose whole surface is made of colored triangles, and thought it would be good if each panel could come off and go back on.

:::cols natural
![A figure in a long robe made of colored triangles, arms out](img/week03/proto3-look.jpg)
*The look I started from.*
![The same figure as a gray 3D mesh in Meshy](img/week03/proto3-meshy.jpg)
*Turned into a 3D model with Meshy 7.1 (about 2 million triangles).*
:::

This model has no grooves or pins to attach panels to the body, so with GPT Astra I thickened each line and added a hole to each panel so people can attach them.

When I laid the body down flat on the plate, it needed less support and the print took 4.5 hours.

![The figure printed lying down, held up by a row of tree supports](img/week03/proto3-printing.jpg)
*Printed lying down, on tree supports.*

But each panel is very small and delicate, so the supports were hard to remove. The joint worked for some of the panels, but I broke some parts, so it was hard to see what the whole thing looks like when it is assembled. The different triangle shapes look nice, but it takes forever to assemble. So the next step is to explore joints and simplify the triangles so it's feasible for people to play with the sculpture. I also want to test the resin printer.

:::cols natural
![The gray figure with arms out, standing against a dark background with its supports removed](img/week03/proto3-print-a.jpg)
*After removing the supports.*
![The same figure with some green triangle panels attached](img/week03/proto3-print-b.jpg)
*With some of the green panels attached.*
:::

## Use of AI

I used Claude Fable 5.1 to design the scales, the panels and the mannequin, and GPT Astra to build the Kinematics joint generator and to generate the image and 3D print file for prototype 2. I used Meshy to turn the image for prototype 3 into a 3D model.

## Files

- Body_150mm_for_resin_or_PLA.3mf — final print file for prototype 3 (Bambu Studio project, 8.6 MB). It is too large for the class repo, so it is not included here.
