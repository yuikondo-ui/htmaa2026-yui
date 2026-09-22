# htmaa2026-yui

Yui Kondo's documentation site for *How to Make (Almost) Anything* (MIT MAS.863, Fall 2026).

**You write Markdown; `build.py` makes the site.** No framework — one Python script, one
CSS file. GitHub Actions rebuilds and deploys to GitHub Pages on every push to `main`.

## Layout

```
content/
  site.yml            name, banner text, email, repo link
  about.md            About page (two columns; split with a line containing only ---)
  final.md            Final project page
  weeks/weekNN.md     one file per week (01–15) — frontmatter + Markdown body
img/weekNN/           photos for that week (hero.jpg shows on the Grid + page top)
img/final/
files/weekNN/         design files (CAD, code, …)
css/style.css         all styling
build.py              Markdown → HTML
index.html grid.html about.html final.html weeks/*.html   ← generated, don't edit by hand
```

## Weekly routine

1. Drop photos into `img/weekNN/`. Keep them small (`sips -Z 1600 img/week01/*.jpg`).
2. Write `content/weeks/weekNN.md`. `##` headings become the left sidebar (見出し); `###` nest under them.
   Reference images as `img/weekNN/photo.jpg` — paths are fixed up for you.
3. Set `status: Done` in the frontmatter when finished.
4. Preview locally: `python3 build.py` then open `index.html`
   (first time: `pip install markdown`).
5. `git add -A && git commit -m "week NN" && git push` — Pages redeploys in ~1 minute.

### Week frontmatter

```
---
week: 03
date: 09/23
topics: [embedded programming](http://academy.cba.mit.edu/classes/embedded_programming/index.html)
recitation: electronics
status: WIP            # or Done
hero: img/week03/hero.jpg
summary: One line shown under the title.
---
```

`topics` (the class topics, with links) shows in the Index's middle column, the Grid caption
and the page's meta line. Optional `title:` adds your own name for the week to the page
heading (“Week 3 / title”); without it the heading is just “Week 3”.

## GitHub Pages setup (once)

Repo → Settings → Pages → *Build and deployment* → Source: **GitHub Actions**.
The workflow in `.github/workflows/pages.yml` does the rest.

## Fonts

| Use | Typeface | Status |
|-----|----------|--------|
| Name "Yui Kondo" in the header | **Gridular** (CoType Foundry, free, CC BY-ND 4.0) | Download from cotypefoundry.com/our-fonts/gridular and save as `fonts/Gridular-Regular.woff2` |
| Everything else | **ABC Diatype Variable** (ABC Dinamo, licensed) | Falls back to **Geist** (then Inter Tight) from Google Fonts unless `fonts/ABCDiatypeVariable.woff2` (+ `-Italic`) is present |
| Red banner | **ABC Diatype Extended Black Italic** | Falls back to **Archivo** Expanded Black Italic unless `fonts/ABCDiatypeExtended-BlackItalic.woff2` is present |

Until Gridular is added the name uses the body face. If your files are `.otf`/`.ttf`, either
change the `url(...)` in `css/style.css` or convert to woff2.
