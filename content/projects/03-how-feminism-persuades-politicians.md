---
slug: how-feminism-persuades-politicians
title: How Feminism Persuades Politicians
subtitle: Impact of gender diversity on politicians' attention to gender equality on Japanese Twitter
venue: Waseda University | Bachelor's Thesis
year: 2023
tags: Digital Activism, Feminism, Filter Bubble, Japanese Twitter, Social Network Analysis, Natural Language Processing, Causal Inference
hero: https://freight.cargo.site/w/1600/i/D2113043088954557682239319794268/feminism.png
summary: An algorithmic glass ceiling: how gender homophily on Japanese Twitter limits women's influence on politicians.
---

## Overview

While social media platforms promise to **democratize discourse**, they often create **filter bubbles** that keep **underrepresented groups** from participating fully in political debates.

I examined the existence of an **algorithmic glass ceiling** that **impeded women's visibility and influence** on Japanese social media. Using NLP and network analysis, I found 60% higher engagement in same-gender interactions on gender equality discussions on Twitter, suggesting algorithmic homophily. This created **echo chambers** — women-only discussions about gender equality received 4x less politicians' attention compared to gender-balanced conversations, **limiting the ability to express their views and effect change.**

**Preprint:** [How Feminism Persuades Politicians: Impact of Gender Diversity on Politicians' Attention to Gender Equality on Japanese Twitter](https://drive.google.com/file/d/1BSQtOHvlN8SEvk21phUbgbOoqm4SBvrX/view?usp=sharing)

## Background

![](https://freight.cargo.site/w/1200/i/N2113058106153760184005937554012/flying-object-2V-h3Srx8q4-unsplash.jpg)

Historically, marginalised groups have fewer chances to interact with the dominant public, limiting their ability to advocate for their interests and share their experiences. While social media platforms have provided new channels for expression, their recommendation systems often **reinforce existing social divisions through filter bubbles** — algorithmic echo chambers that limit exposure to diverse perspectives.

This raises a critical question: **Can marginalized groups affect political discourse when their discourse remains largely confined to isolated community clusters?**

## Objectives

![](https://freight.cargo.site/w/1200/i/K2113088537083375795999694611036/jene-stephaniuk-XyvAQGLIms4-unsplash.jpg)

I explore these research questions:

- **RQ1:** To what extent do discussions about gender inequality in Japan occur across gender boundaries versus within same-gender groups?
- **RQ2:** What factors influence the success of gender equality advocacy in gaining attention from Japanese lawmakers and affecting policy changes? What role does group **homogeneity/heterogeneity** play in the effectiveness of social movements?

To address RQ2, I expanded upon Tilly's (1994) **WUNC** framework (Worthiness, Unity, Numbers, and Commitment) — a model for evaluating social movement success that was later quantified by Freelon et al. (2018). I enhanced this framework by incorporating a new metric of participant **'diversity'**, as it fosters a wider range of information, enhances problem-solving and tactical innovation, and increases the democratic legitimacy of social movements.

## Methodology

![](https://freight.cargo.site/w/1200/i/A2113175538108086674937815458396/marten-bjork-FVtG38Cjc_k-unsplash.jpg)

### RQ1: Gender Homophily in Gender Equality Discussions on Twitter

1. **Data Collection** — gathered 150,000 tweets and user information from accounts discussing gender equality in Python
2. **Gender Classification Analysis** — implemented natural language processing (NLP) techniques to predict users' gender based on their tweet content and profile information
3. **Interaction Network Visualization** — created network visualizations to analyze interaction patterns between different gender groups

### RQ2: Conditions to be Heard

Recognizing that politicians experience distinct, **personalized information environments** on social media, I analyzed **each politician's network of followers individually.** This approach allowed me to quantify these metrics (**Diversity** + Unity, Number, and Commitment) within each politician's unique information ecosystem, enabling an investigation of **how individual opinion formation dynamics** may vary across different political actors.

Data: July 1–31, 2022

1. **Data Collection**
    - Scraped Twitter accounts of politicians from official party websites
    - Extracted politicians' friend/following lists from Twitter
    - Identified and collected tweets discussing gender-related issues from politicians' network
    - Collected 1,000 tweets per user who discussed gender issues to identify their gender
2. **Natural Language Processing** — classified users' gender based on linguistic patterns and profile characteristics
3. **Social Movement Power Quantification** — measured the power (Diversity + UNC) of gender equality discussions in each politician's network
4. **Panel Data Analysis** — analyzed how Diversity + UNC metrics predict politicians' attention to gender equality issues

![](https://freight.cargo.site/w/1200/i/G2113148357992838940557211034204/Frame-25.png)
*Causal inference model: how (1) participant diversity, (2) message unity, (3) number of participants, and (4) user commitment to related gender equality affect politicians' opinions.*

## Findings

### Findings I: Gender Homophily in Gender Equality Discussions on Twitter

![](https://freight.cargo.site/w/1200/i/G2113157118019558151896501543516/graphfinal.png)
*Network visualisation: nodes represent gendered users, pink for women and blue for men. The links between nodes indicate interactions (e.g., retweets, replies).*

Users discussing gender equality tend to interact **1.6 times more with users of the same gender**, leading to gender-based clustering and limiting the diversity of perspectives.

This **homogeneous interaction** may restrict feminist perspectives, leading to an overemphasis on male domination and negative perceptions of the movement (Hooks, 2000). Including the perspectives of all genders is essential to avoiding this outcome (Wouters & Walgrave, 2017).

### Findings II: Impact of Gender Diversity on Politicians' Attention to Gender Equality

![](https://freight.cargo.site/w/1200/i/F2113182457703149652275141239388/Screenshot-2024-12-13-at-21.04.06.png)

Diversity has a significantly positive coefficient in Models (1), (5), (6), and (8), implying that higher levels of diversity increase the chance of attracting politicians' attention. Specifically, in column (6), a one standard deviation increase in diversity is associated with an increase of 0.57 log units in the expected number of gender-equality tweets. This finding is robust to the inclusion of time fixed-effects but not individual fixed-effects in both the daily and weekly panel data analyses.

## Conclusion

This research highlights challenges that marginalised groups face in engaging with the broader public, which limits the ability to express their views and effect change.

The findings identify a concerning feedback loop: **gender homophily** (as demonstrated in RQ1) limits marginalized groups' visibility and influence, while personalization algorithms may reinforce these divisions by creating additional barriers to cross-group connection. This algorithmic amplification of existing social divisions appears to particularly impact women and other marginalized groups, potentially making it more difficult for them to build the broad coalitions necessary for effective advocacy.

![](https://freight.cargo.site/w/1200/i/Z2113193866424063431274110083676/flying-object-qrPaii9-iQY-unsplash.jpg)
