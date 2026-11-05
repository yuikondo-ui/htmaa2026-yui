---
title: Final Project
ref: HTMAA/FINAL
status: WIP
hero: img/final/final_teaser.mp4
summary: Clothes for digital selves. A tangible digital twin built from a person's own data, and clothes to choose what it shows.
---

## Overview

They are watching us. Big Data analytics and artificial intelligence (AI) draw non-intuitive and unverifiable inferences and predictions about the behaviors, preferences, and private lives of individuals. These inferences draw on highly diverse and feature-rich data of unpredictable value, and create new opportunities for discriminatory, biased, and invasive decision-making. Yet we are behind a one-way mirror: these inferences are not accessible or shown to us. [(Wachter, 2019)](https://journals.library.columbia.edu/index.php/CBLR/article/view/3424) What does it mean to make a choice when the options have been so carefully arranged for us in an invisible way? Is personal freedom possible on the Internet? [(Chayka, 2024)](https://www.kylechayka.com/filterworld)

I propose that we need a shield between us and AI. Right now our digital body is exposed. Just as we wear clothes to present chosen facets of ourselves, we also need clothes in the digital world. The sculpture represents your digital body, built from the traces you leave on platforms like YouTube, TikTok, Claude and elsewhere. A language model reads those traces and turns them into inferences: demographics, behavior, relationships, goals, interests, and the sensitive ones in between. Each inference becomes one panel of a modular shell around a body.

Undressed, the sculpture tells everything it knows about you. Put a piece of clothing on it and it speaks only from the facets you chose to show; take the clothing off and the rest comes back. Assembling and disassembling a sculpture made of your own data lets you think about this with your hands: what to show, what to hide, and to whom.

## Prototypes

### Prototype v4: Inference View

[Open in new tab ↗](files/week00/inference-view.html) (Nov 5 2026)

:::embed files/week00/inference-view.html | Inference View, prototype v4

### Prototype v3: Data Blocks

[Open in new tab ↗](files/week00/data-blocks.html) (Nov 4 2026)

:::embed files/week00/data-blocks.html | Data Blocks, prototype v3

### Prototype v2: Digital Mirror

[Open in new tab ↗](files/week00/acrylic-data-body.html) (Nov 2 2026)

:::embed files/week00/acrylic-data-body.html | Digital Mirror, prototype v2

### Prototype v1: Data Barbie

[Open in new tab ↗](files/week00/data-barbie.html) (Sep 25 2026)

:::embed files/week00/data-barbie.html | Data Barbie, prototype v1

## Open questions

<table class="oq">
<tr><th>Materials</th><td>Acrylic, so the LED light can shine through?
<ul>
<li>Frosted vs. clear: frosted spreads the light softly; clear shows engraved lines that catch the edge light.</li>
<li>Thickness vs. sensing: through 3 mm acrylic the touch signal almost disappears (34 → 37), so thinner sheets or electrodes on the inside surface may be needed.</li>
</ul></td></tr>
<tr><th>Shape of the sculpture</th><td>Two types:
<ul>
<li>Blocks (Week 6): the body split into a few larger blocks. Better suited for sensing touch: with step response, a few electrodes per block could tell where it's pressed, so there is no need to print and wire many panels.<br><img src="img/week06/img_7996.jpg" alt="Week 6: the life-size block figure, cut on the ShopBot from 27 flat parts" style="max-width:220px;display:block;margin:8px 0"><img src="img/final/data_blocks_view.jpg" alt="Prototype v3 Data Blocks: a standing figure made of transparent cubes, each with a white line drawing of a hand, an eye or a face inside" style="max-width:220px;display:block;margin:8px 0"></li>
<li>Panels (Week 3): many small triangles. Aesthetically more beautiful, and each panel can be one inference, but each needs its own sensor and LED.<br><img src="img/week03/proto3-print-b.jpg" alt="Week 3: the printed lattice figure with green triangle panels attached" style="max-width:220px;display:block;margin:8px 0"></li>
<li>In between: the panel look on the surface, but sensing per block underneath (e.g. 32 touch zones, like the prototype).</li>
</ul>
Size: life-size (about 170 cm) or smaller?</td></tr>
<tr><th>Input device</th><td>Capacitive sensing / step response?
<ul>
<li>If the body is made of blocks, step response (tx/rx) could work: one TX per block, several RX pads to find where it's pressed.</li>
<li>Problem: acrylic weakens the signal. Next: 1 MΩ, then 10 MΩ resistor, thinner acrylic, or the electrode closer to the surface.</li>
<li>How hard it's pressed: from the step response itself, or a few load cells in the base?</li>
</ul></td></tr>
<tr><th>Output device</th><td>Likely to be LED lights. LED tape?
<ul>
<li>Addressable LED tape (NeoPixel / WS2812) inside each block, so each zone can dim on its own: 100 / 60 / 25 / 0 %.</li>
<li>Needs a gap or diffuser between the LEDs and the acrylic, or the LEDs show as dots.</li>
<li>Power: up to about 60 mA per LED at full white, so count the LEDs before choosing the power supply.</li>
</ul></td></tr>
<tr><th>Interface</th><td>Projection mapping?
<ul>
<li>On a wall behind the sculpture: the data each inference was made from. Touching a panel zooms the wall to that inference.</li>
<li>Or directly onto the sculpture, as text on the body: each inference appears on the part of the body it describes. Could also project the viewer's own 3D-scanned body onto the sculpture, so it becomes their body.</li>
<li>What should the viewer see first: the body, the wall, or the words?</li>
</ul></td></tr>
<tr><th>Data</th><td>Whose data makes the inferences: fictional examples, or the viewer's own? Importing platform data takes days. Could I project the viewer's 3D scan onto the sculpture?</td></tr>
<tr><th>Panel ↔ inference</th><td>What is the relationship between the panel you touch and its inference? Why is this inference on this part of the body?<br><br>Ideas:
<ul>
<li>By body part: head = values and beliefs, chest = relationships and feelings, hands = interests and activities, legs = mobility and location.</li>
<li>By source: group by where it was inferred from (YouTube, TikTok, Claude) with a color or a face of the body.</li>
</ul></td></tr>
</table>

## Weekly log

### Week 0: Concept { .log-week }

My final project is clothes for the digital self: a tangible sculpture shaped like the user's face, its surface built from what their digital history says about them, and a set of clothes that act as a shield.

I made this proposal video with Claude:

:::video https://youtu.be/Wp1-sOIoUTU | Final project proposal, Week 0

#### Algorithmic Mirror

The idea grows out of the [Algorithmic Mirror](https://yuikondo.cargo.site/algorithmic-mirror-1), an interactive visualization tool that simulates the hidden profiling practices of social media platforms. It uses large-language-model sentence embeddings to reimagine how online activity might be categorized and interpreted ([overview video](https://youtu.be/LPDfGhzDFjs)).

Instead of a dashboard of metrics and metadata counts, the tool draws an explorable landscape: a speculative profile of a young person's digital traces. It does not uncover the platforms' actual models. It builds possible mirrors of algorithmic judgment, artificial reflections that show how an identity could be abstracted and rearranged through data.

![Algorithmic Mirror: one participant's landscape, by platform](img/week00/mirror_platforms.jpg)
*One participant's landscape across Netflix, TikTok and YouTube.*

Seeing the three platforms side by side was what struck participants first.

> "It made me reconsider how my interests are distributed across platforms. It's as if different personalities exist within each platform." (P2)

A time slider then replays the landscape month by month, so the participant watches their profile take shape ([temporal evolution video](https://youtu.be/v-dd-9q9w-k)).

> "When YouTube tries to understand what I like, my question is how would it try to track my interest over time and project new interests, or would it just take me as I currently am and give me exactly what I like?" (P9)

By turning opaque inferences into spatial metaphors, the mirror invites reflection on how children's online footprints are silently turned into profiles, and on how inhabiting such a mirror might change one's sense of self.

#### From mirror to clothes

With a mirror, we can only gaze at our own image. With clothes, we can shape how we present ourselves. How do we make clothes for our digital selves, so that we can choose what we present to AI systems?

#### Sketch and inspiration

![First sketch: clothes for digital selves](img/week00/sketch.jpg)
*The first sketch. A face-shaped mannequin under a shell of triangular panels, each panel one inference made from digital history. Digital traces → LLM → inferences → one inference per panel. Post-its: data portraits and data doubles, danah boyd's faceted identity, context collapse and time collapse, contextual integrity, and Monteiro et al. on when LLM inferences are acceptable.*

Artistic inspiration for fragmented selves across space and time:

:::cols natural
![Nerhol, Phases of Everything](img/week00/ref_nerhol.jpg)
*Nerhol, Phases of Everything. A portrait made from many photographs taken over minutes, carved as one block: one person, many moments, one face. [Source ↗](https://www.shashasha.co/en/book/phrase-of-everything)*
![Rineke Dijkstra, Still Moving](img/week00/ref_dijkstra.jpg)
*Rineke Dijkstra, Still Moving. Portraits of the same people returned to over years: the same person, a different self each time. [Source ↗](https://www.distanz.de/rineke-dijkstra/still-moving)*
![Satoshi Kon, Perfect Blue](img/week00/ref_perfect_blue.jpg)
*Satoshi Kon, Perfect Blue. A self shattered across a public image and a private one.*
:::

:::cols natural
![Artistic inspiration board](img/week00/board_artistic.jpg)
*Artistic references: Daniel Rozin's mechanical mirrors, the Photorythms portraits at the Media Lab, Perfect Blue and its fragmented self, Hirano Keiichirō's novel Honshin (A Man), and a pair of mirrored figures.*
![Paper inspiration board](img/week00/board_papers.jpg)
*Papers and concepts: AugTwin and Twins on accountable digital twins, danah boyd's Faceted Id/entity (MIT MAS thesis, 2002), Monteiro et al., When Are LLM Inferences Acceptable? (2026), and the sensitive-inference dashboard from our own preprint. Concepts: contextual integrity, time collapse, context collapse, Goffman's performance.*
:::

### Week 1: Modular clothes (laser cutting) { .log-week }

I first thought of printing the user's inferences as cards, so that users could sort them by hand and slip them into pockets on the clothes. Learning about construction kits changed that: I want assembling the clothes from parts to be intuitive in itself. So I looked at modular clothes, which can be taken apart and put back together without sewing ([definition](https://www.sciencedirect.com/science/article/pii/S0921344924000892)), and at ANREALAGE's Spring/Summer 2022 collection "Dimension" ([source](https://www.tokyoweekender.com/art_and_culture/fashion/anrealage-japanese-fashion/)).

![A board of modular clothing references: garments with detachable parts, user prototypes and modular pieces](img/final/w1-modular-inspiration.jpg)
*Inspiration for modular clothes.*

![The Week 1 construction kit, assembled and sprayed](img/final/w1-skirt-kit.jpg)
*The output: a press-fit construction kit for a skirt in plywood. [Week 1 ↗](weeks/week01.html)*

I am not satisfied with the usability of the assembly: it took me two hours to put together. So I plan to explore more intuitive joints and shapes. This kit also only makes a skirt, and I want users to be able to assemble the parts in different ways, into pants or a dress as well.

### Week 2: A map of poetry words (embedded programming) { .log-week }

In Week 2, I focused on learning the basics of electronics, as I had no background in it. As a side project, I explored a map visualization of poetry words. On the internet we get lost: everything is zoomed in, and we have little spatial sense of how words relate. So I thought the XIAO-based QPad could be an interesting device for exploring a map of words.

![The Kigo pad: a map of seasonal poetry words on the QPad's screen](img/week02/kigopad.jpg)
*The Kigo pad. [Week 2 ↗](weeks/week02.html)*

### Week 3: Body sculpture (3D printing) { .log-week }

#### Exploring shapes

In Week 3, I wanted to explore what the final shape of a digital self could look like, using the 3D printer.

I was inspired by ANREALAGE's Spring/Summer 2027 collection "SKIN": how their clothes can change with LED panels, and how numbers were used to stand for the body.

![Stills from ANREALAGE's SKIN collection: garments lit with LED panels and covered in projected green numbers](img/final/w3-anrealage-skin.jpg)
*ANREALAGE, SS27 "SKIN".*

Building on my struggles with the Week 1 construction kit, I also looked at joint design from [Nervous System](https://n-e-r-v-o-u-s.com/projects/).

![Nervous System's Kinematics pieces: bracelets, flat sheets of joined triangles, a necklace and a dress](img/final/w3-nervous-system-joints.jpg)
*Nervous System's jointed pieces.*

I also thought it could be fun to explore not just clothes but sculpture, especially Jaume Plensa's *Alchemist* and Antony Gormley's figures.

![A board of body sculptures: Jaume Plensa's figures made of letters and numbers, and Antony Gormley's bodies made of blocks, lines and wire](img/final/w3-plensa-gormley.jpg)
*Jaume Plensa and Antony Gormley.*

Then I explored how the body sculpture itself could be taken apart and put back together.

![The two printed figures still in green supports](img/week03/body-tree-vs-normal.jpg)
*Printing the body with two kinds of supports.*

:::cols natural
![The gray lattice figure with its supports removed](img/week03/body-supports-removed.jpg)
*After removing the supports.*
![A figure with green triangle panels attached](img/week03/proto3-print-b.jpg)
*Panels that make up the body. [Week 3 ↗](weeks/week03.html)*
:::

#### Projection mapping?

After this, I asked myself: does the sculpture actually need to be assembled and disassembled? Talking with Quentin during office hours, I thought it could also be interesting to explore touch sensing and projection mapping. Could we project how algorithms see you onto your own face, or onto the clothes you are wearing?

![A board of projection mapping references: faces with projected makeup and patterns, and dancers with projected faces](img/final/w3-projection-mapping.jpg)
*Projection mapping onto faces and bodies.*

#### Making it personal (data processing)

I want viewers to relate to their own body, not to a random person's, so that they think about their own digital selves rather than a hypothetical one.

But uploading data from platforms is slow. In the Algorithmic Mirror project, it took three days to a week. Yet [PimEyes](https://pimeyes.com/en) can find where my face appears online almost instantly. Then I found [I-XRAY](https://anhphu.org/i-xray), a project that uses smart glasses to look up a stranger's name, work and interests from their face in real time, using only public data. Its code is not public, but its data processing could be interesting to explore.

For the body shape, this paper could also be useful: it scans a body in about 3 minutes and turns it into an avatar.

- Kondo et al., [Instant Skinned Gaussian Avatars for Web, Mobile and VR Applications](https://dl.acm.org/doi/10.1145/3694907.3765954)

Yoichi Ochiai used this technology in his Expo 2025 Osaka pavilion, *null²*: visitors scan their face, voice and body to make a digital copy of themselves, and inside the mirrored pavilion they talk with their own digital body as it deforms and moves on its own. I will explore this more.

![Stills from null²: a scanned figure reflected endlessly in a mirrored room](img/final/w3-null2-ochiai.jpg)
*Yoichi Ochiai, null², Expo 2025 Osaka.*

#### Whom do we present our digital selves to?

My idea is to think about self-presentation in the digital age. But imagining how to present yourself to algorithms is probably too abstract. So I thought, what if you imagine dying, and presenting yourself to the people who are still alive? Imagine your life can be quantified, and the people close to you can make avatars or agents of you and talk to them, as in Hirano Keiichirō's novel [*Honshin*](https://books.bunshun.jp/articles/-/6444), where a son has a virtual figure of his late mother made.

When others can make avatars of us, do we still own our own body? How are our memories mediated through algorithms?

Papers:

- Öhman and Floridi, [The Political Economy of Death in the Age of Information: A Critical Approach to the Digital Afterlife Industry](https://philarchive.org/rec/HMATPE) (2017)
- Sas and Whittaker, [Design for Forgetting: Disposing of Digital Possessions after a Breakup](https://eprints.lancs.ac.uk/id/eprint/60831) (CHI 2013)
- Albers et al., [Dying, Death, and the Afterlife in Human-Computer Interaction. A Scoping Review](https://doi.org/10.1145/3544548.3581199) (CHI 2023)

Quietly, I'm slightly against [TeleAbsence](https://news.mit.edu/2025/teleabsence-poetic-encounters-past-0502). They say we die twice: once when our body dies, and again when we are forgotten. But what if we actually want to die and be forgotten? How can our last wishes be respected? Did Max Brod betray Kafka when he published his writings, even though Kafka was so negative about them and did not want them published? How can we control how we are perceived and remembered? Do we even desire to be immortal?

> Let us call the gesture of Bettina and Laura the gesture of longing for immortality. Bettina, who aspires to grand immortality, wishes to say: I refuse to die with this day and its cares, I wish to transcend myself, to be a part of history, because history is eternal memory. Laura, though she only aspires to small immortality, wants the same: to transcend herself and the unhappy moment in which she lives to do "something" to make everyone who has known her remember her.

*Milan Kundera, Immortality (trans. Peter Kussi, 1991)*

So for participants, thinking about death, and designing a digital body that chooses how to be remembered and what to pass on to the next generation, could be an interesting prompt.

### Week 4 & 5: LED lights (electronics design / production) { .log-week }

In Week 4, I again focused on learning electronics, so I did not develop the concept much further.

I am making a Spotify album-art LED matrix, and learned how to send color information to a 64×64 LED matrix. This could be applied to changing the colors on the body sculpture based on how participants touch it.

![A 64×64 LED matrix showing album art, next to a CD player in a transparent case](img/final/w4-led-matrix.jpg)
*The LED matrix, and the transparent case I'd like the board to live in.*

![Notebook page tracing how a color signal travels to the matrix, and the five steps of drawing a frame](img/week04/sketch-hub75-color-signal.jpg)
*How color information reaches the LEDs. [Week 4 ↗](weeks/week04.html)*

### Week 6: Exploring the shape of the sculpture { .log-week }

In Week 6, I explored what shape the final sculpture should take. I 3D scanned my own body and abstracted it into a low-poly figure made of triangular panels.

![The life-size block figure standing in an elevator](img/week06/img_7996.jpg)
*A life-size figure based on my 3D body scan, cut on the ShopBot as 27 flat parts that slot together without glue or screws. [Week 6 ↗](weeks/week06.html)*

I also met [Judith Donath](https://en.wikipedia.org/wiki/Judith_Donath), whose work first inspired me to visualize digital selves three years ago. She is happy to keep talking with me :)

### Week 7: Input devices { .log-week }

For the sculpture, I'm thinking of a capacitive touch sensor in each panel, so I tested one through acrylic. On bare copper a touch was easy to see (the reading jumped from about 28 to 60), but through 3 mm of acrylic it only moved from 34 to 37, about the same as the noise. It needs a much larger resistor (1 MΩ, then 10 MΩ) to be sensitive enough to capture the touch.

## Use of AI

Claude helped me make the proposal video and the prototypes (Data Barbie and Digital Mirror), rendered the teaser video, and turned my notes in our shared doc into this page. The concept, the sketches and the writing are my own.
