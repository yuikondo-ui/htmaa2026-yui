#!/usr/bin/env python3
"""
build.py — turn the Markdown in content/ into the static site.

    python3 build.py            # writes index.html, grid.html, about.html, final.html, weeks/*.html

Requires: pip install markdown   (that's the only dependency)

Content layout
--------------
content/weeks/weekNN.md   one file per week, frontmatter + markdown body
content/final.md          final project page (same format)
content/about.md          about page (two columns split at a line containing only `---`)
content/site.yml          name, banner text, footer links (simple key: value lines)

Frontmatter keys (between the `---` lines at the top of a week file):
  week: 01                       # zero-padded
  title: Press-fit lamp          # your own title for the week (shown as "Week N / title")
  ref: HTMAA/WK-01               # optional, shown in the middle column
  status: WIP | Done             # shows as [WIP] / [Done]
  topics: [introduction](url), [computer-aided design](url)   # markdown links; becomes the title
  recitation: [version control](url)                          # optional
  date: 09/09                                                 # optional
  hero: img/week01/hero.jpg      # optional; shown on Grid and at top of page
  summary: one-line description  # optional; shown under the title
  date: 2026-09-17               # optional

Headings: `##` becomes a sidebar entry, `###` a nested entry.
Images/links written as `img/...` or `files/...` work from any page (paths are fixed up).
"""
import os, re, sys, glob, html, json
try:
    import markdown
except ImportError:
    sys.exit("Missing dependency: run  pip install markdown")

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")

# ---------------------------------------------------------------- helpers
def read(p):
    with open(p, encoding="utf-8") as f: return f.read()

def write(rel, s):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: f.write(s)

def parse_front(text):
    """Return (meta dict, body). Frontmatter = leading block between --- lines."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not m: return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, m.group(2)

def load_site():
    meta = {}
    p = os.path.join(CONTENT, "site.yml")
    if os.path.exists(p):
        for line in read(p).splitlines():
            if ":" in line and not line.strip().startswith("#"):
                k, v = line.split(":", 1); meta[k.strip()] = v.strip()
    meta.setdefault("name", "Yui Kondo")
    meta.setdefault("banner", "How to make anything?")
    meta.setdefault("year", "2026")
    meta.setdefault("email", "")
    meta.setdefault("repo", "")
    meta.setdefault("linkedin", "")
    meta.setdefault("course_url", "https://fab.cba.mit.edu/classes/863.26/")
    meta.setdefault("course_label", "MAS.863 · How to Make (Almost) Anything")
    return meta

SITE = load_site()

def blocks(body):
    """Expand the site's own block directives before markdown runs.

    :::cols … :::                      images (each followed by an *italic* caption) side by side
    :::embed files/x.html | Title      interactive page in a frame, with a Source toggle + open link
    :::source files/x.py               collapsible full source of a file in the repo
    :::video https://youtu.be/ID | Title   YouTube (or any embeddable) video, 16:9
    """
    body = re.sub(r"^:::cols([^\n]*)\n(.*?)^:::\s*$",
                  lambda m: f'<div class="cols{esc(m.group(1).rstrip())}" markdown="1">\n\n' + m.group(2) + '\n</div>\n',
                  body, flags=re.S | re.M)

    def embed(m):
        path, title = m.group(1).strip(), (m.group(2) or os.path.basename(m.group(1))).strip()
        full = os.path.join(ROOT, path)
        src = read(full) if os.path.exists(full) else ""
        return (f'<div class="embed">'
                f'<div class="embed-bar"><span class="embed-title">{esc(title)}</span>'
                f'<a class="embed-open" href="{esc(path)}" target="_blank" rel="noopener">Open in new tab ↗</a></div>'
                f'<iframe src="{esc(path)}" loading="lazy" title="{esc(title)}"></iframe>'
                f'<details class="src"><summary>Source <span class="muted">{esc(os.path.basename(path))} · '
                f'{src.count(chr(10)) + 1} lines</span></summary><pre><code>{esc(src)}</code></pre></details>'
                f'</div>\n')
    body = re.sub(r"^:::embed\s+(\S+)(?:\s*\|\s*(.+))?\s*$", embed, body, flags=re.M)

    def source(m):
        path = m.group(1).strip()
        full = os.path.join(ROOT, path)
        src = read(full) if os.path.exists(full) else "(file not found)"
        name = os.path.basename(path)
        return (f'<details class="src standalone"><summary><code>{esc(name)}</code> '
                f'<span class="muted">{src.count(chr(10)) + 1} lines · </span>'
                f'<a href="{esc(path)}" download>download</a></summary>'
                f'<pre><code>{esc(src)}</code></pre></details>\n')
    body = re.sub(r"^:::source\s+(\S+)\s*$", source, body, flags=re.M)

    def video(m):
        url, title = m.group(1).strip(), (m.group(2) or "Video").strip()
        yt = re.search(r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/))([\w-]{11})", url)
        bar = (f'<div class="embed-bar"><span class="embed-title">{esc(title)}</span>'
               f'<a class="embed-open" href="{esc(url)}" target="_blank" rel="noopener">Open in new tab ↗</a></div>')
        if yt:
            vid = yt.group(1)
            player = (f'<iframe src="https://www.youtube.com/embed/{vid}?autoplay=1&rel=0" title="{esc(title)}" '
                      f'allowfullscreen referrerpolicy="strict-origin-when-cross-origin" '
                      f'allow="autoplay; accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>')
            # poster + play button; the player is created on click (faster, and no error box while offline)
            return (f'<div class="embed video">{bar}'
                    f'<button class="yt" type="button" aria-label="Play {esc(title)}" '
                    f'onclick="this.outerHTML=this.dataset.player" data-player="{esc(player)}">'
                    f'<img src="https://i.ytimg.com/vi/{vid}/maxresdefault.jpg" alt="" loading="lazy" '
                    f'onerror="this.onerror=null;this.src=\'https://i.ytimg.com/vi/{vid}/hqdefault.jpg\'">'
                    f'<span class="yt-play"></span></button></div>\n')
        return (f'<div class="embed video">{bar}<iframe src="{esc(url)}" loading="lazy" title="{esc(title)}" allowfullscreen></iframe></div>\n')
    body = re.sub(r"^:::video\s+(\S+)(?:\s*\|\s*(.+))?\s*$", video, body, flags=re.M)
    return body

def figures(h):
    """<p><img></p> followed by <p><em>caption</em></p> becomes <figure> + <figcaption>."""
    pair = r"<img [^>]*>\s*(?:<em>(?:(?!</em>).)*</em>)?"
    def para(m):
        out = []
        for img, cap in re.findall(r"(<img [^>]*>)\s*(?:<em>((?:(?!</em>).)*)</em>)?", m.group(1), flags=re.S):
            out.append(f"<figure>{img}" + (f"<figcaption>{cap}</figcaption>" if cap else "") + "</figure>")
        return "\n".join(out)
    # a paragraph made only of images (each optionally followed by an *italic* caption)
    h = re.sub(rf"<p>((?:\s*{pair}\s*)+)</p>", para, h, flags=re.S)
    # caption in its own paragraph right after a lone image
    h = re.sub(r"<figure>(<img [^>]*>)</figure>\s*<p><em>((?:(?!</em>).)*)</em></p>",
               r"<figure>\1<figcaption>\2</figcaption></figure>", h, flags=re.S)
    return h

def md_to_html(body):
    """Convert markdown; return (html, toc list of (level, id, text))."""
    md = markdown.Markdown(extensions=["toc", "tables", "fenced_code", "attr_list", "sane_lists", "md_in_html"],
                           extension_configs={"toc": {"toc_depth": "2-3", "permalink": False}})
    out = figures(md.convert(blocks(body)))
    toc = []
    def walk(items, level):
        for it in items:
            toc.append((level, it["id"], it["name"]))
            walk(it.get("children", []), level + 1)
    walk(md.toc_tokens, 2)
    return out, toc

def fix_paths(h, depth):
    """Make img/ and files/ references work from a page `depth` folders deep."""
    if depth == 0: return h
    pre = "../" * depth
    return re.sub(r'(src|href|data-preview)="(img/|files/)', lambda m: f'{m.group(1)}="{pre}{m.group(2)}', h)

def placeholder_imgs(h, depth):
    """Missing images fall back to the dotted placeholder instead of a broken icon."""
    ph = "../" * depth + "img/placeholder.svg"
    return h.replace("<img ", f'<img onerror="this.onerror=null;this.src=\'{ph}\'" ')

def esc(s): return html.escape(s, quote=True)

def inline(md_text):
    """Render an inline markdown string (links, emphasis) without a wrapping <p>."""
    h = markdown.markdown(md_text)
    return re.sub(r"^<p>|</p>$", "", h.strip())

def week_label(m): return f"Week {m['num']}" if "num" in m else m.get("label", "")

# ---------------------------------------------------------------- chrome
def head(title, depth=0, cover_page=False):
    r = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — {esc(SITE['name'])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@1,125,900&family=Geist:wght@100..900&family=Geist+Mono:wght@400..600&family=Inter+Tight:wght@100..900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}css/style.css">
<script src="{r}js/site.js" defer></script>
</head>
<body{' class="has-cover"' if cover_page else ''}>
"""

def header(depth=0, active=""):
    r = "../" * depth
    a = lambda k: ' class="active"' if k == active else ""
    return f"""<header class="site-header">
  <a class="site-name" href="{r}index.html">{esc(SITE['name'])}</a>
  <nav class="site-nav">
    <a href="{r}index.html"{a('index')}><span class="box"></span>Index</a>
    <a href="{r}grid.html"{a('grid')}><span class="box"></span>Grid</a>
  </nav>
  <a class="site-about" href="{r}about.html"{a('about')}>About</a>
</header>
"""

def footer(depth=0):
    links = []
    if SITE["email"]:    links.append(f'<a href="mailto:{esc(SITE["email"])}">{esc(SITE["email"])}</a>')
    if SITE["linkedin"]: links.append(f'<a href="{esc(SITE["linkedin"])}">LinkedIn</a>')
    if SITE["repo"]:     links.append(f'<a href="{esc(SITE["repo"])}">GitHub</a>')
    return f"""<footer class="site-footer">
  <div class="col col-wide">{esc(SITE['name'])}, {esc(SITE['year'])}</div>
  <div class="col"><p>Contact:</p><p>{'<br>'.join(links)}</p></div>
</footer>
</body>
</html>
"""

def banner():
    """Red marquee. Two identical groups scroll -50% for a seamless loop; JS sets the
    duration from the measured width so the speed (px/s) is the same on every screen."""
    t = esc(SITE["banner"])
    group = "".join(f'<span class="mq-item">{t}</span>' for _ in range(3))
    return (f'<h1 class="banner" aria-label="{t}"><div class="marquee">'
            f'<div class="marquee-group">{group}</div>'
            f'<div class="marquee-group" aria-hidden="true">{group}</div>'
            f'</div></h1>\n'
            '<script>\n'
            '(function(){var m=document.querySelector(".marquee");if(!m)return;\n'
            ' function fit(){var w=m.scrollWidth/2;m.style.setProperty("--mq-dur",(w/110).toFixed(2)+"s");}\n'
            ' fit();window.addEventListener("resize",fit);if(document.fonts)document.fonts.ready.then(fit);})();\n'
            '</script>\n')

def status_tag(meta):
    s = meta.get("status", "WIP")
    return f'<span class="status status-{s.lower()}">[{esc(s)}]</span>'

# ---------------------------------------------------------------- content loading
def load_weeks():
    weeks = []
    for p in sorted(glob.glob(os.path.join(CONTENT, "weeks", "*.md"))):
        meta, body = parse_front(read(p))
        meta.setdefault("week", re.sub(r"\D", "", os.path.basename(p)) or "00")
        meta["num"] = str(int(meta["week"]))
        meta["topics_text"] = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", meta.get("topics", ""))
        meta.setdefault("title", "")   # optional; page heading is "Week N" or "Week N / title"
        meta.setdefault("ref", f"HTMAA/WK-{meta['week']}")
        meta["slug"] = f"week{meta['week']}"
        meta["body"] = body
        weeks.append(meta)
    weeks.sort(key=lambda m: m["week"])
    return weeks

def load_single(name, defaults):
    p = os.path.join(CONTENT, name)
    if not os.path.exists(p): return None
    meta, body = parse_front(read(p))
    for k, v in defaults.items(): meta.setdefault(k, v)
    meta["body"] = body
    return meta

# ---------------------------------------------------------------- pages
def project_page(meta, depth, label, prev_link, next_link):
    body_html, toc = md_to_html(meta["body"])
    body_html = placeholder_imgs(fix_paths(body_html, depth), depth)
    # Cover: full-width image, dark overlay, the title repeated in big white type, label bottom-left.
    cover_title = (meta.get("title") or meta.get("topics_text") or label)
    cover_title = re.sub(r"\s*,\s*", "\u2003", cover_title).upper()   # no commas, all caps, em-space between topics
    hero_src = ("../" * depth + meta["hero"]) if meta.get("hero") else ""
    hero_img = (f'<img class="cover-img" src="{esc(hero_src)}" alt="" '
                f'onerror="this.closest(\'.cover\').classList.add(\'no-img\');this.remove()">') if hero_src else ""
    r = "../" * depth
    strip_item = (f'<span class="strip-item"><a href="{r}index.html">{esc(SITE["name"])}</a>'
                  f'<span class="sep">—</span><a href="https://www.media.mit.edu/">MIT Media Lab</a>, {esc(SITE["year"])}</span>')
    strip_group = f'<div class="strip-group">{strip_item * 4}</div>'
    cover = f"""<section class="cover{'' if hero_src else ' no-img'}">
    {hero_img}
    <div class="cover-title" data-title="{esc(cover_title)}" aria-hidden="true"><span>{esc(cover_title)}</span></div>
    <h2 class="cover-label">{esc(label)}<span class="sr">: {esc(cover_title)}</span></h2>
    <div class="cover-strip" aria-label="{esc(SITE['name'])} — MIT Media Lab, {esc(SITE['year'])}">
      <div class="strip-track">{strip_group}{strip_group}</div>
    </div>
  </section>
"""
    toc_html = "".join(
        f'<li class="lvl{lvl}"><a href="#{esc(i)}">{esc(t)}</a></li>' for lvl, i, t in toc)
    side = f"""<aside class="toc">
  <div class="toc-inner">
    <ul>{toc_html}</ul>
  </div>
</aside>""" if toc else '<aside class="toc"></aside>'
    date = f'<span>{esc(meta["date"])}</span>' if meta.get("date") else ""
    recit = f'<span class="recit">Recitation: {inline(meta["recitation"])}</span>' if meta.get("recitation") else ""
    title_part = f'<span class="slash"> / </span>{esc(meta["title"])}' if meta.get("title") else ""
    topics = (f'<span class="topics">{inline(meta["topics"])}</span>' if meta.get("topics")
              else f'<span>Ref. {esc(meta["ref"])}</span>')
    summary = f'<p class="lede">{esc(meta["summary"])}</p>' if meta.get("summary") else ""
    return (head(f"{label} — {meta['title'] or meta.get('topics_text','')}", depth, cover_page=True) + header(depth) + f"""
<main class="project">
  {cover}
  <div class="project-body">
    {side}
    <article class="content">
{body_html}
    </article>
  </div>
  <nav class="pager">{prev_link}{next_link}</nav>
</main>
<script>
// Highlight the sidebar entry for the section in view. The reference line sits a third of
// the way down the viewport; at the very bottom of the page the last entry wins.
(function(){{
  var links=[].slice.call(document.querySelectorAll('.toc a'));if(!links.length)return;
  var heads=links.map(function(a){{return document.getElementById(a.getAttribute('href').slice(1));}}).filter(Boolean);
  var pinned=null;   // set by a click; the spy stays off until the reader scrolls on their own
  function mark(cur){{links.forEach(function(a){{a.classList.toggle('active',a.getAttribute('href')==='#'+cur.id);}});}}
  function update(){{
    if(pinned)return;
    var line=window.scrollY+window.innerHeight*0.33,cur=heads[0];
    heads.forEach(function(h){{if(h.getBoundingClientRect().top+window.scrollY<=line)cur=h;}});
    if(window.innerHeight+window.scrollY>=document.documentElement.scrollHeight-2)cur=heads[heads.length-1];
    mark(cur);
  }}
  links.forEach(function(a){{a.addEventListener('click',function(){{
    var h=document.getElementById(a.getAttribute('href').slice(1));if(!h)return;
    pinned=h;mark(h);
  }});}});
  function unpin(){{pinned=null;update();}}
  window.addEventListener('wheel',unpin,{{passive:true}});window.addEventListener('touchstart',unpin,{{passive:true}});
  window.addEventListener('keydown',function(e){{if(/Arrow|Page|Home|End|Space/.test(e.key)||e.key===' ')unpin();}});
  window.addEventListener('scroll',update,{{passive:true}});window.addEventListener('resize',update);update();
  // Cover: scale one title line to the cover width (like the banner), then repeat it to fill the height.
  var c=document.querySelector('.cover-title');if(!c)return;
  function fill(){{
    var hd=document.querySelector('.site-header');
    c.parentNode.style.height=window.innerHeight+'px';
    var t=c.getAttribute('data-title');c.innerHTML='<span>'+t.replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</span>';
    var one=c.querySelector('span');one.style.display='inline-block';one.style.whiteSpace='nowrap';
    var base=100;c.style.fontSize=base+'px';
    var w=one.getBoundingClientRect().width||1;
    var cs=getComputedStyle(c),pad=parseFloat(cs.paddingLeft)+parseFloat(cs.paddingRight);
    var fit=base*(c.clientWidth-pad-6)/(w+0.04*base);
    var fs=Math.max(Math.min(fit, 200), Math.min(window.innerWidth*0.045, 72));
    c.style.fontSize=fs+'px';one.style.display='block';one.style.whiteSpace='';
    var lh=one.getBoundingClientRect().height||1,n=Math.max(1,Math.floor(c.clientHeight*0.72/lh));  // leave the lower part of the photo clear
    var html='';for(var i=0;i<n;i++)html+='<span>'+one.innerHTML+'</span>';c.innerHTML=html;
  }}
  fill();window.addEventListener('resize',fill);if(document.fonts)document.fonts.ready.then(fill);
  // Bottom strip: constant-speed marquee (~70 px/s).
  var tr=document.querySelector('.strip-track');
  function speed(){{if(tr)tr.style.setProperty('--strip-dur',(tr.scrollWidth/2/70).toFixed(2)+'s');}}
  speed();window.addEventListener('resize',speed);if(document.fonts)document.fonts.ready.then(speed);
  // Header: hidden while the cover is on screen, slides in once the reader scrolls past it.
  var hd=document.querySelector('.site-header'),cv=document.querySelector('.cover');
  function hdr(){{if(!hd||!cv)return;hd.classList.toggle('shown',window.scrollY>cv.offsetTop+cv.offsetHeight-hd.offsetHeight-8);}}
  hdr();window.addEventListener('scroll',hdr,{{passive:true}});
}})();
</script>
""" + footer(depth))

def build_weeks(weeks):
    for i, m in enumerate(weeks):
        prev_ = (f'<a href="{weeks[i-1]["slug"]}.html">← Week {weeks[i-1]["num"]}</a>' if i > 0
                 else '<a href="../index.html">← Index</a>')
        next_ = (f'<a href="{weeks[i+1]["slug"]}.html">Week {weeks[i+1]["num"]} →</a>' if i < len(weeks)-1
                 else '<a href="../final.html">Final project →</a>')
        write(f"weeks/{m['slug']}.html", project_page(m, 1, f"Week {m['num']}", prev_, next_))

def build_final(final, weeks):
    if not final: return
    last = weeks[-1]["slug"] if weeks else "index"
    prev_ = f'<a href="weeks/{last}.html">← Week {weeks[-1]["num"]}</a>' if weeks else '<a href="index.html">← Index</a>'
    write("final.html", project_page(final, 0, "Final", prev_, '<a href="index.html">Index →</a>'))

def build_index(weeks, final):
    rows = "".join(
        f'  <a class="row" href="weeks/{m["slug"]}.html"><span class="c1"><span class="wk">Week {esc(m["num"])}</span></span>'
        f'<span class="c2">{esc(m["topics_text"] or "Ref. " + m["ref"])}</span><span class="c3">{status_tag(m)}</span></a>\n' for m in weeks)
    if final:
        rows += (f'  <a class="row" href="final.html"><span class="c1"><span class="wk">Final</span></span>'
                 f'<span class="c2">Ref. {esc(final["ref"])}</span><span class="c3">{status_tag(final)}</span></a>\n')
    write("index.html", head("Index") + header(0, "index") + banner() +
          f'\n<main class="index">\n{rows}</main>\n' + footer())

def build_grid(weeks, final):
    def card(href, img, cap):
        src = esc(img) if img else "img/placeholder.svg"
        return (f'  <a class="card" href="{href}"><img src="{src}" alt="" loading="lazy" '
                f'onerror="this.onerror=null;this.src=\'img/placeholder.svg\'">'
                f'<p class="caption">{cap}</p></a>\n')
    cards = "".join(card(f'weeks/{m["slug"]}.html', m.get("hero"),
                         f'<span class="wk">Week {esc(m["num"])}</span> {esc(m["topics_text"] or m["title"])}') for m in weeks)
    if final:
        cards += card("final.html", final.get("hero"), f'<span class="wk">Final</span> {esc(final["title"])}')
    write("grid.html", head("Grid") + header(0, "grid") +
          f'\n<main class="grid-page">\n  <div class="grid">\n{cards}  </div>\n</main>\n' + footer())

def build_about(about):
    if not about: return
    body = re.sub(r"\n---\s*$", "", about["body"].rstrip())        # ignore a trailing separator
    parts = [p for p in re.split(r"\n---\s*\n", body, maxsplit=1) if p.strip()]
    cls = ["about-main", "about-side"]
    cols = "".join(f'<div class="{cls[i]}">{fix_paths(md_to_html(p)[0], 0)}</div>' for i, p in enumerate(parts))
    cols = cols if len(parts) > 1 else cols + '<div class="about-side"></div>'
    write("about.html", head("About") + header(0, "about") +
          f'\n<main class="about">\n  <div class="two-col">{cols}</div>\n</main>\n' + footer())

# ---------------------------------------------------------------- main
def main():
    weeks = load_weeks()
    final = load_single("final.md", {"title": "Final Project", "ref": "HTMAA/FINAL"})
    about = load_single("about.md", {"title": "About"})
    build_weeks(weeks); build_final(final, weeks)
    build_index(weeks, final); build_grid(weeks, final); build_about(about)
    print(f"built {len(weeks)} weeks" + (", final" if final else "") + (", about" if about else ""))

if __name__ == "__main__":
    main()
