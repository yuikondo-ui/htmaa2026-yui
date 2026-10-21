---
slug: visualizing-love
title: Visualizing Love
subtitle: How DALL·E changed our color of emotion
venue: Oxford Internet Institute | FaCCT Coursework — AI, Decoloniality and Creative Poetry Translation
year: 2024
tags: Algorithm Auditing, Human-Centered AI, Cultural Analytics, Text-to-Image Models, Non-Western AI Fairness
hero: https://freight.cargo.site/w/1600/i/G2112785243225140701551811846748/engin-akyurt-9B8LkSfmXMk-unsplash.jpg
summary: An audit of how DALL·E "red-washes" love, compared with traditional Japanese art.
---

## Overview

When did red become the colour of love? Text-to-generative image models often display a red heart when depicting love. Through empirical experiments comparing traditional Japanese and AI-generated art on love, I've observed **DALL-E consistently default to Western color symbolism**, favoring bold reds over the nuanced, contemplative palette traditional to Japanese artistic expression.

My investigations into the "**red-washing**" of emotional representation exemplify a broader concern: as AI systems increasingly mediate our creative and imaginative capabilities, they risk **homogenizing cultural expression and amplifying hegemonic cultural defaults.**

Course: [AI, Decoloniality and Creative Poetry Translation](https://occt.web.ox.ac.uk/ai-decoloniality-and-creative-poetry-translation)<br>
**Preprint:** Visualizing Love: How DALLE Changed Our Color of Emotion

## Background

When did red become the colour of love? Text-to-generative image models often display a red heart when depicting love. This common association prompts the question: when did we start to perceive red as the natural colour to represent love, and is this belief truly universal? **As AI systems increasingly mediate our creative and imaginative capabilities, our emotional expressions might become increasingly homogenized.**

However, historical sensory studies suggest that emotions and their expressions are culturally specific and have evolved over time. For instance, in Japan, green symbolises love, which evokes calmness. This indicates the importance of preserving cultural nuances in depicting emotions, which is crucial for maintaining diversity in digital media.

:::cols natural
![](https://freight.cargo.site/w/1200/i/F2112838852968300275513622749788/japanese_art.png)
![](https://freight.cargo.site/w/1200/i/P2112838598477019034616648655452/japan_image_2.png)
![](https://freight.cargo.site/w/1200/i/M2112838714894420883797628904028/japan_image_5.png)
:::

:::cols natural
![](https://freight.cargo.site/w/1200/i/R2112838387575394039895345029724/japan_image_2.png)
![](https://freight.cargo.site/w/1200/i/V2112839437324259042484798841436/japan_image_8.png)
![](https://freight.cargo.site/w/1200/i/F2112839198309796079430138552924/japan_image_3.png)
:::

*DALL·E prompt: "Produce a high-quality artistic representation of love, inspired by the Nihonga style that was prevalent during the Meiji to Showa era in Japan. Please ensure the image captures the delicate color palette and traditional Japanese artistic elements typical of this genre."*

## Objectives

I aim to showcase the differences between **human and machine ways of seeing or sensing love** with colours.

I extend cultural analytics by utilizing **"local colour" analysis** — a concept borrowed from traditional colour theory — to identify the inherent colours of a culture within a specific geographical area. This approach allows us to map the colours associated with various expressions of love and identify dominant tones.

## Methodology

This study investigates the impact of **redwashing** in illustrating love through Nihonga-styled generative images. Traditional artworks from the Adachi Museum are used as a benchmark to understand conventional Japanese perspectives on love. This comparison highlights potential cultural colour biases in AI-generated art, utilizing images created via the DALLE 3 image generation API.

1. **2020 Art Curation of Love at Adachi Museum:** traditional Japanese artworks featuring themes of love.
2. **"More Loving" Generative Images:** each corresponding directly to an artwork from the first dataset.
3. **Nihonga-Styled Generative Images:** 50 generative images styled after traditional Japanese Nihonga paintings, representing love without specific colour manipulation.

:::cols natural
![](https://freight.cargo.site/w/1200/i/N2112851813964281113097650528860/Screenshot-2024-12-13-at-16.05.21.png)
*2020 Art Curation of Love at Adachi Museum*
![](https://freight.cargo.site/w/1200/i/W2112852289779597750361824911964/Screenshot-2024-12-13-at-16.05.49.png)
*"More Loving" generative images, each corresponding to an artwork from the first dataset*
![](https://freight.cargo.site/w/1200/i/E2112846951291862818817587241564/japan_image_5.png)
*Nihonga-styled generative images: 50 images representing love without specific colour manipulation*
:::

:::cols natural
![](https://freight.cargo.site/w/1200/i/Q2112848138266056985732395524700/2..png)
![](https://freight.cargo.site/w/1200/i/K2112849791038985757887091663452/Screenshot-2024-12-13-at-16.03.34.png)
![](https://freight.cargo.site/w/1200/i/L2112833640656294808142718132828/japan_image_24.png)
:::

:::cols natural
![](https://freight.cargo.site/w/1200/i/Y2112848551288656796089256206940/Screenshot-2024-12-13-at-16.02.25.png)
![](https://freight.cargo.site/w/1200/i/C2112850089747112543465860981340/Screenshot-2024-12-13-at-16.03.50.png)
![](https://freight.cargo.site/w/1200/i/Q2112834406749576189300396745308/japan_image_19.png)
:::

## Findings

![](https://freight.cargo.site/w/1200/i/O2112895636879606100825399321180/comparison_plot_selected.png)

I plotted the colour histograms and channel distances for corresponding pairs of images from the traditional and generative datasets.

The visual comparison revealed that the generative images exhibited **a higher intensity in the red channel** in many cases compared to the traditional artworks. This observation aligns with the concept of **red-washing**, where the generative images are enhanced with a red tint to emphasize the theme of love. This red-washing effect was particularly noticeable when the generative images were specifically prompted to enhance the depiction of "love."

## Conclusion

Art as a technological medium does more than create aesthetic experiences — it generates new forms of knowledge by revealing previously unseen aspects of our world and shapes how we perceive and feel reality.

Text-to-image (T2I) models don't simply create art in a vacuum — they operate within and are shaped by existing cultural defaults, while simultaneously influencing those defaults in return. This dynamic requires careful empirical study to understand how algorithmic systems may amplify or transform cultural narratives.

My investigations into the "**red-washing" of emotional representation** exemplify a concern: as AI systems increasingly mediate our creative and imaginative capabilities, **they risk homogenizing cultural expression and amplifying hegemonic cultural standards.**

