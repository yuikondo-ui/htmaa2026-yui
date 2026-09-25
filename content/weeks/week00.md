---
week: 00
date: 09/09
topics: [final project proposal & log](http://academy.cba.mit.edu/classes/principles_practices/index.html)
recitation: [version control and web development](https://pub.cba.mit.edu/863.26/site/recitations/version/index.html)
status: WIP
hero: img/week00/sketch.jpg
summary: Clothes for digital selves — a tangible digital twin built from a person's own data, and a doll-dressing game about what to show and what to hide.
---

## Overview

### Data Barbie

I want to propose the concept of Data Barbie: a dress-up activity in which the doll is your own data double. It starts from the traces a person leaves on YouTube, TikTok, Claude and elsewhere. A language model reads those traces and turns them into inferences: demographics, behaviour, relationships, goals, interests, and the sensitive ones in between. Each inference becomes one panel of a modular shell around a head shaped like the user's face.

Undressed, the doll tells everything it knows about you. Put a piece of clothing on it and it speaks only from the facets you chose to show; take the clothing off and the rest comes back. Which panels you cover, and for whom, is the game.

Children and adolescents rarely get to see their own inferred profile, let alone decide which parts of it face outward. Dressing and undressing a doll made of their own data lets them think about that with their hands: what to show, what to hide, and to whom.

## Prototypes

[Prototype v1 ↗](files/week00/data-barbie.html) (Sep 25 2026): a first version of the doll in the browser. Tap a facet to sew it into underwear, a shirt or a coat, then choose who is in the room. The doll speaks only from what is showing, and old inferences are drawn as old cloth.

## Week 0: Concept making

### Concept

Algorithms are looking at us, but we cannot stare back at the images they construct about us. My final project is clothes for the digital self: a tangible sculpture shaped like the user's face, its surface built from what their digital history says about them, and a set of clothes to dress it in. Undressed, the sculpture tells everything the data says. Dressed, it shows only the facets its owner chose.

:::video https://youtu.be/Wp1-sOIoUTU | Final project proposal, Week 0

### How it started: Algorithmic Mirror

The idea grows out of the [Algorithmic Mirror](https://algorithmicmirror.com/20250731-bright-lion-glf0) ([description](https://www.media.mit.edu/projects/algorithmic-mirror/overview/)), an interactive visualization tool that simulates the hidden profiling practices of social media platforms. I developed it with MIT Media Lab's Viral Communications group, [Oxford's Synthetic Society Lab](https://www.oii.ox.ac.uk/research/research-groups/synthetic-society-lab/) and [Oxford's Child-Centred AI Lab](https://oxfordccai.org/). It uses large-language-model sentence embeddings to reimagine how online activity might be categorized and interpreted.

:::video https://youtu.be/LPDfGhzDFjs | Algorithmic Mirror, overview

Instead of a dashboard of metrics and metadata counts, the tool draws an explorable landscape: a speculative profile of a young person's digital traces. It does not uncover the platforms' actual models. It builds possible mirrors of algorithmic judgment, artificial reflections that show how an identity could be abstracted and rearranged through data.

![Algorithmic Mirror: one participant's landscape, by platform](img/week00/mirror_platforms.jpg)
*One participant's landscape. Top: the Netflix self (red) and the TikTok self (purple). Bottom: the YouTube self (green), and all three together. The same topics, three different densities.*

Seeing the three platforms side by side was what struck participants first.

> "It made me reconsider how my interests are distributed across platforms. It's as if different personalities exist within each platform." (P2)

A time slider then replays the landscape month by month, so the participant watches their profile take shape.

:::video https://youtu.be/v-dd-9q9w-k | Algorithmic Mirror, temporal evolution

> "When YouTube tries to understand what I like, my question is how would it try to track my interest over time and project new interests, or would it just take me as I currently am and give me exactly what I like?" (P9)

By turning opaque inferences into spatial metaphors, the mirror invites reflection on how children's online footprints are silently turned into profiles, and on how inhabiting such a mirror might change one's sense of self.

### Motivation: tangible and playful

The mirror lives on a screen, and a screen is where the profiling already happens. I want to take it off the screen and make it something a child can hold and play with. Offline, we dress for the room we are in: one outfit for the office, another for friends, another for family. Online there is no room to read, because the room is the whole internet, so we walk in naked and disclose everything at once. Goffman called the two sides front stage and back stage; a flat data profile removes the distinction altogether. A tangible mirror can give it back, because clothes are the most familiar tool we have for deciding what to show.

### Sketch and inspiration

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


## Week 1: Laser cutting

I first thought of printing the user's inferences as cards, so that users could sort them by hand and slip them into pockets on the clothes. Learning about construction kits this week changed that: I want assembling the clothes from parts to be intuitive in itself. So I familiarised myself with modular clothes and took inspiration from fashion artists ([definition](https://www.sciencedirect.com/science/article/pii/S0921344924000892): modular garments are clothing items that can be disassembled and reassembled into multiple parts without sewing the parts together; sleeves or a collar are zipped or buttoned onto the main body).

:::cols natural
![Anrealage, Dimension, Spring/Summer 2022](img/week01/digital-clothes.jpg)
*Kunihiko Morinaga, Anrealage Spring/Summer 2022 collection "Dimension". Photo © Masaya Tanaka. [Source ↗](https://www.tokyoweekender.com/art_and_culture/fashion/anrealage-japanese-fashion/)*
![The Week 1 construction kit, assembled and sprayed](img/week01/colored.jpg)
*The output of Week 1: a press-fit construction kit for a skirt in plywood, two rings assembled, sprayed purple and gold.*
:::

The output was a [construction kit for a skirt](week01.html). I am not satisfied with the usability of the assembly: it took me two hours to put together. So I plan to explore more intuitive joints and shapes. This kit also only makes a skirt, and I want users to be able to assemble the parts in different ways, into pants or a dress as well.

## Files

The proposal video is on [YouTube](https://youtu.be/Wp1-sOIoUTU). The sketch and the inspiration boards are under `img/week00/`.
