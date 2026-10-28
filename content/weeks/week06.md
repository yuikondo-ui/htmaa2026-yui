---
week: 06
date: 10/21
title: Computer-controlled machining
topics: [computer-controlled machining](http://academy.cba.mit.edu/classes/computer_machining/index.html)
recitation: CAM (Computer-Aided Manufacturing)
status: WIP
hero: img/week06/img_7996.jpg
summary: A life-size figure based on my 3D body scan, cut on the ShopBot as 27 flat parts that slot together without glue or screws.
---

## Assignment

Design, mill and assemble something big (about meter scale) on the ShopBot.

## What I made

A 170 cm tall sculpture of my body. It started from a 3D scan of me and became 27 flat wooden parts, including the base and an internal support, all cut from one sheet. The parts join with tabs and slots, so the figure slides together like a puzzle without separate connectors or ties.

:::cols natural
![The assembled 170 cm wooden figure standing against a wall](img/week06/img_7989.jpg)
*Assembled.*
![The sculpture standing in a freight elevator](img/week06/img_7996_2.jpg)
*In the elevator.*
:::

## Process

### Inspiration

I was inspired by Antony Gormley's [*Small Blockworks*](https://www.antonygormley.com/works/sculpture/series/small-blockworks). He tries to convey the feeling of a body with as few cast iron blocks as possible, stacked on top of or beside each other. The standing figures use cantilevers instead of the stability of a column, so the unstable build reflects a mental state and turns bodily sensation into structure.

:::cols natural
![Three works by Antony Gormley: a drawing of a body in a grid, a standing figure of stacked blocks, and a crouching figure made of a metal mesh](img/week06/gormley_refs.jpg)
*Works by Antony Gormley.*
![A human figure made of stacked dark blocks](img/week06/inspiration_blocks.jpg)
*A Blockworks figure, the reference that started the idea.*
:::

### 3D scanning

Joseph helped me scan my whole body. Then I imported the scan into Blender and also tried reducing the mesh to a few large triangles.

:::cols natural
![The 3D body scan in the scanning software](img/week06/scan_v.jpg)
*The scan.*
![The body scan imported into Blender](img/week06/blender_import_v.jpg)
*In Blender.*
![The scan reduced to a low-poly mesh of large triangles in Blender](img/week06/triangles_c.jpg)
*Reduced to triangles.*
:::

### Blocks in Blender

I used Geometry Nodes to turn the body into abstract blocks:

Group Input → Mesh to Volume → Distribute Points in Volume → Instance on Points (Cube) → Group Output

![The Geometry Nodes graph: Mesh to Volume, Distribute Points in Volume, Cube, Instance on Points](img/week06/nodes_uniform.jpg)

Next I added a Random Value node to the scale of the cubes, so each block gets a different size.

![The Geometry Nodes graph with a Random Value node feeding the instance scale](img/week06/nodes_random.jpg)

:::cols natural
![The body made of same-size cubes](img/week06/blocks_uniform.jpg)
*Same-size cubes.*
![The body made of cubes with random sizes](img/week06/blocks_random.jpg)
*Random sizes.*
![The randomized block figure from another angle](img/week06/blocks_result.jpg)
*Another angle.*
:::

The result did not follow the body accurately, so I went back to the original scan to clean it first. I tried using OpenAI to clean the scanned file. Then I realized that blocks are not what a CNC machine is good at. It cuts flat sheets, so the sculpture should be made of panels.

### From blocks to panels

I looked at different types of sculpture again, especially faceted ones like [Enzyme Design's *Sculptures Facette*](https://www.enzyme-design.com/en/realisations/view/19/sculptures-facette).

To explore how to turn my body scan into a sculpture made from flat, CNC-cut panels, I gave my scan to GPT Astra as a reference, and it generated an illustration of a faceted body.

![Front, side and three-quarter views of a faceted standing figure](img/week06/faceted_concept.jpg)
*First concept: a faceted figure with 49 parts.*

I brought this concept to a TA session with Quentin. He suggested two ways to connect and stabilize the panels: 3D-printed joints, or threading string through the structure and tensioning it.

At that stage the design had 49 parts. I was worried that assembling so many angled panels would be difficult. I wanted the construction to feel more like assembling a puzzle, with the connections built into the wooden parts themselves.

I looked for other references and found this arrangement of solid blocks and open spaces.

![Five figures made of flat solid blocks with open gaps between them](img/week06/inspiration_solid_open.jpg)
*Solid blocks and open spaces.*

### 27-part puzzle design

Working with GPT Astra, I used my body scan as a reference for a new design with 27 wooden parts, including the base and internal support. We built an interactive tool (running locally) to preview the sculpture and arrange the parts on a single sheet, then I imported the geometry into Fusion for CAM setup.

The final design is about 170 cm tall. The joints use integral tabs and slots, so the parts slide together without separate connectors or ties.

:::cols natural
![The interactive tool: sculpture preview on the left, sheet layout on the right](img/week06/puzzle_tool_c.jpg)
*The preview and layout tool.*
![All 27 parts nested on one sheet in Fusion](img/week06/design_27parts_c.jpg)
*The parts nested on one sheet in Fusion.*
:::

### CAM setup in Fusion

Following the [CBA ShopBot guide](https://docs.google.com/document/u/0/d/1-rF9PmoOsOtS0qZ2KEEdkcyEs0x8U_7F7Ub0gUat6TE/mobilebasic), I set up the stock and work coordinate system in Fusion. I matched the axis directions to the ShopBot (the X+ and Z+ arrows on the machine), selected a stock corner as the XY reference, and set Z zero at the top surface of the material.

:::cols natural narrow
![The X+ and Z+ axis arrows marked on the ShopBot frame](img/week06/img_7972.jpg)
*Axis directions on the ShopBot.*
:::

My first plan was to use both a downcut and an upcut end mill. I made **four CAM operations** in two ShopBot files:

| Planned tool | Operation | Purpose |
|---|---|---|
| Downcut | 01 — Internal contours | Cut the internal openings to 0.2 in (5.08 mm) deep. |
| Downcut | 02 — Outside contours | Cut the outer profiles of the parts to the same depth. |
| Upcut | 03 — Internal contours | Continue the internal cuts to the bottom of the sheet. |
| Upcut | 04 — Outside contours | Finish the outer cuts, leaving holding tabs. |

The idea was to get a clean top edge from the downcut bit, then finish the cuts with the upcut bit for better chip evacuation. I added holding tabs to keep the parts and larger cutouts attached to the sheet during through-cutting, used the recommended multiple depths (0.18 in per pass), and simulated each file in Fusion.

In the end I decided to use the **downcut bit for all four operations** and exported them together as one ShopBot file.

When I simulated the whole job, it was going to take 52 minutes. It was already 8:30 pm, so I removed the multiple depths, which brought it down to 32 minutes.

:::cols natural
![The contour toolpaths of all four operations on the sheet in Fusion](img/week06/cam_downcut_c.jpg)
*All four operations with the downcut bit.*
![Fusion simulation of the full toolpath on the green stock](img/week06/cam_sim_c.jpg)
*Simulation after removing multiple depths: 32 minutes.*
:::

### Cutting

I ran the job, but it did not cut all the way through.

<div class="cols" markdown="1">
<figure><video src="img/week06/img_7976.mp4" controls muted loop playsinline preload="metadata" style="width:100%;aspect-ratio:3/4;object-fit:cover;background:#000"></video><figcaption>The ShopBot cutting.</figcaption></figure>
<figure><img src="img/week06/img_7979.jpg" alt="The cut sheet with the parts' outlines visible but still attached" style="aspect-ratio:3/4;object-fit:cover"><figcaption>Not through.</figcaption></figure>
</div>

Setting the final depth exactly at the stock bottom did not cut through everywhere. Michal helped me change the bottom offset: I set **Bottom Height to Stock bottom −0.04 in**, so the tool goes about 1.02 mm below the modeled sheet bottom, into the sacrificial board, and ran the cut again. Is it working…?!

:::cols natural
![Fusion's Heights settings with Bottom Height offset −0.04 in](img/week06/cam_offset_panel.jpg)
*Bottom Height: Stock bottom, −0.04 in.*
![Watching the ShopBot run the second pass](img/week06/img_7983.jpg)
*Second pass.*
:::

Yes, it went through!

:::cols natural narrow
![The sheet with clean through-cuts](img/week06/img_7984.jpg)
*Through.*
:::

### Cleaning and assembly

I cut the holding tabs and cleaned up the edges of the wood, and got these parts.

:::cols natural
![Sanding a part with an oscillating tool](img/week06/img_7985.jpg)
*Cleaning the edges.*
![The first parts stacked on a table](img/week06/img_7986.jpg)
*Test-fitting the first parts.*
![All the parts laid out on a table](img/week06/img_7988.jpg)
*All the parts.*
:::

Then I assembled them!

:::cols natural
![The assembled figure against the wall](img/week06/img_7989.jpg)
![The sculpture standing in a freight elevator](img/week06/img_7996_2.jpg)
:::

## What I learned

- A CNC router cuts flat sheets, so the design has to start from panels, not from 3D blocks.
- Fewer parts and joints built into the wood made the assembly much easier than separate connectors would have.
- Setting the bottom height exactly at the stock bottom is not enough to cut through. A small negative offset (−0.04 in) into the sacrificial board fixed it.
- Removing multiple depths saved 20 minutes, but it puts more load on the tool in one pass.

## Use of AI

I used GPT Astra to generate the faceted body illustration from my scan, and to design the 27-part version with me. Together we built the interactive tool to preview the sculpture and lay out the parts on one sheet. I also tried using OpenAI to clean the scanned file. The scanning, the Blender block studies, the CAM setup in Fusion, the cutting and the assembly are my own. I used Claude Opus 5.5 to turn my notes into this page and to lay out the photos, and I edited it.

## Files

- Body scan (STL, 96 MB) — too large for the class repo, so it is not included here.
- [Blender block study](files/week06/abstractblocks.blend)
- [Low-poly triangle body](files/week06/triangles.stl)
- [Final ShopBot file, all downcut](files/week06/sculpture_total_0835.sbp)
- [ShopBot file with the −0.04 in bottom offset](files/week06/updated_yui.sbp)
