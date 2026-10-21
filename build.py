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
        vert = " vertical" if re.search(r"youtube\.com/shorts/", url) else ""   # Shorts are 9:16
        if yt:
            vid = yt.group(1)
            player = (f'<iframe src="https://www.youtube.com/embed/{vid}?autoplay=1&rel=0" title="{esc(title)}" '
                      f'allowfullscreen referrerpolicy="strict-origin-when-cross-origin" '
                      f'allow="autoplay; accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>')
            # poster + play button; the player is created on click (faster, and no error box while offline)
            return (f'<div class="embed video{vert}">{bar}'
                    f'<button class="yt" type="button" aria-label="Play {esc(title)}" '
                    f'onclick="this.outerHTML=this.dataset.player" data-player="{esc(player)}">'
                    f'<img src="https://i.ytimg.com/vi/{vid}/maxresdefault.jpg" alt="" loading="lazy" '
                    f'onerror="this.onerror=null;this.src=\'https://i.ytimg.com/vi/{vid}/hqdefault.jpg\'">'
                    f'<span class="yt-play"></span></button></div>\n')
        return (f'<div class="embed video{vert}">{bar}<iframe src="{esc(url)}" loading="lazy" title="{esc(title)}" allowfullscreen></iframe></div>\n')
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
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo:ital,wdth,wght@1,125,900&family=Geist:wght@100..900&family=Geist+Mono:wght@400..600&family=Inter+Tight:wght@100..900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}css/style.css">
<script>try{{if(localStorage.getItem("theme")==="dark")document.documentElement.setAttribute("data-theme","dark")}}catch(e){{}}</script>
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
    <a href="{r}projects.html"{a('projects')}><span class="box"></span>Projects</a>
  </nav>
  <span class="site-right">
    <button class="theme-toggle" type="button" aria-pressed="false" aria-label="Switch to dark mode" title="Dark / light"><svg class="i-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11z" fill="currentColor"/></svg><svg class="i-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.2" fill="currentColor"/><g stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6"/></g></svg></button>
    <a class="site-about" href="{r}about.html"{a('about')}>About</a>
  </span>
</header>
"""

def footer(depth=0):
    """Three columns on the same grid as the index rows: email | LinkedIn | back to top. No rules."""
    mail = f'<a href="mailto:{esc(SITE["email"])}">{esc(SITE["email"])}</a>' if SITE["email"] else ""
    li = f'<a href="{esc(SITE["linkedin"])}" target="_blank" rel="noopener">LinkedIn</a>' if SITE["linkedin"] else ""
    return f"""<footer class="site-footer">
  <div class="col col-wide">{mail}</div>
  <div class="col">{li}</div>
  <div class="col col-top"><a href="#" class="to-top" aria-label="Back to top" onclick="window.scrollTo({{top:0,behavior:'smooth'}});return false;">&#x2191;</a></div>
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
        # a week counts as "not started" while it still has the template summary or (almost) no prose
        words = re.sub(r"^#.*$", "", body, flags=re.M).split()
        meta["started"] = not meta.get("summary", "").startswith("One line about") and len(words) > 40
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
def project_page(meta, depth, label, prev_link, next_link, active="", intro=""):
    body_html, toc = md_to_html(meta["body"])
    body_html = placeholder_imgs(fix_paths(body_html, depth), depth)
    # Cover: full-width image, dark overlay, the title repeated in big white type, label bottom-left.
    cover_title = (meta.get("title") or meta.get("topics_text") or label)
    cover_title = re.sub(r"\s*,\s*", "\u2003", cover_title).upper()   # no commas, all caps, em-space between topics
    hero_src = ((meta["hero"] if re.match(r"https?://", meta["hero"]) else "../" * depth + meta["hero"])
                if meta.get("hero") else "")
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
    return (head(f"{label} — {meta['title'] or meta.get('topics_text','')}", depth, cover_page=True) + header(depth, active) + f"""
<main class="project">
  {cover}
  <div class="project-body">
    {side}
    <article class="content">
{intro}{body_html}
    </article>
  </div>
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
  // Cover: scale one title line to the cover width (like the banner), shown once.
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
    var fs=Math.max(Math.min(fit*0.6, 120), Math.min(window.innerWidth*0.04, 40));  // about 60% of full width
    c.style.fontSize=fs+'px';one.style.display='block';one.style.whiteSpace='';
    var n=1;  // one title line (was repeated to fill the cover)
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
        f'  <a class="row{"" if m["started"] else " todo"}" href="weeks/{m["slug"]}.html"><span class="c1"><span class="wk">Week {esc(m["num"])}</span></span>'
        f'<span class="c2">{esc(m["topics_text"] or "Ref. " + m["ref"])}</span><span class="c3">{status_tag(m)}</span></a>\n' for m in weeks)
    if final:
        rows += (f'  <a class="row todo" href="final.html"><span class="c1"><span class="wk">Final</span></span>'
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
    """About: the sea (a slowly turning kaleidoscope of the ocean photo) fills the left half;
    the name, contact links and a narrow photo/places/poem column sit beside the text on the right.
    content/about.md = text, then a line with only `---`, then the side column (HTML). No footer."""
    if not about: return
    body = re.sub(r"\n---\s*$", "", about["body"].rstrip())
    parts = [p for p in re.split(r"\n---\s*\n", body, maxsplit=1) if p.strip()]
    text = fix_paths(md_to_html(parts[0])[0], 0)
    side = fix_paths(md_to_html(parts[1])[0], 0) if len(parts) > 1 else ""
    sea = esc(about.get("sea", "https://freight.cargo.site/w/1024/t/webgl/i/S2109509132541966905311695168092/graham-pengelly-xyh54DGiOwY-unsplash.jpg"))
    page = f"""
<main class="about about-sea">
  <div class="sea" aria-hidden="true"><canvas id="sea" data-src="{sea}"></canvas></div>
  <section class="about-panel">
    <div class="about-cols">
      <aside class="about-aside">{side}</aside>
      <div class="about-text">{text}</div>
    </div>
  </section>
</main>
<script>
// The sea: a port of Cargo's "kaleidoscope" backdrop (WebGL), with the settings the old site used
// (Cargo defaults: 18 slices, zoom 217, rotations 61° / -148°, speed -8, centre 21/66, mirrored, mouse drift).
(function(){{
  var cv=document.getElementById('sea');if(!cv)return;
  var gl=cv.getContext('webgl')||cv.getContext('experimental-webgl');
  var src=cv.getAttribute('data-src');
  if(!gl){{cv.parentNode.style.background='url('+src+') center/cover';return;}}
  var S={{slices:18,zoom:2.17,base1:61*Math.PI/180,speed1:-8/10000*50,base2:-148*Math.PI/180,speed2:-8/10000*50,cx:.21,cy:.66}};
  var still=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  var VS='attribute vec2 p;void main(){{gl_Position=vec4(p,0.,1.);}}';
  var FS=['precision highp float;uniform sampler2D tex;uniform float time,sliceAngle,base1,speed1,base2,speed2;',
    'uniform vec2 zoom,resolution,aspect,center,mouse;',
    'void main(){{vec2 pos0=-aspect+2.*gl_FragCoord.xy/resolution*aspect;float r=length(pos0);',
    'float ang=atan(pos0.y,pos0.x)+base1;float s=mod(ang+time*speed1,sliceAngle*2.);if(s>sliceAngle)s=2.*sliceAngle-s;',
    'float r2=base2+time*speed2;vec2 rot=vec2(sin(r2),cos(r2));vec2 pos=vec2(cos(s),sin(s))*r+center;',
    'gl_FragColor=texture2D(tex,vec2(pos.x*rot.y+pos.y*rot.x,pos.y*rot.y-pos.x*rot.x)*zoom+mouse,-1.);}}'].join('');
  function sh(t,c){{var o=gl.createShader(t);gl.shaderSource(o,c);gl.compileShader(o);return o;}}
  var pr=gl.createProgram();gl.attachShader(pr,sh(gl.VERTEX_SHADER,VS));gl.attachShader(pr,sh(gl.FRAGMENT_SHADER,FS));gl.linkProgram(pr);gl.useProgram(pr);
  var buf=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buf);
  gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,-1,1,1,-1,1]),gl.STATIC_DRAW);
  var lp=gl.getAttribLocation(pr,'p');gl.enableVertexAttribArray(lp);gl.vertexAttribPointer(lp,2,gl.FLOAT,false,0,0);
  var U={{}};['time','sliceAngle','base1','speed1','base2','speed2','zoom','resolution','aspect','center','mouse'].forEach(function(n){{U[n]=gl.getUniformLocation(pr,n);}});
  var ratio=1,ready=false,t0=performance.now(),mx=0,my=0,px=-1,py=-1;
  var img=new Image();img.crossOrigin='';
  img.onload=function(){{
    function p2(x){{var n=1;while(n<x)n*=2;return n;}}
    var c=document.createElement('canvas');c.width=p2(img.width);c.height=p2(img.height);   // WebGL1 wants power-of-two for mirrored repeat
    c.getContext('2d').drawImage(img,0,0,c.width,c.height);ratio=img.height/img.width;
    var tx=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,tx);
    gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,c);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR_MIPMAP_NEAREST);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.MIRRORED_REPEAT);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.MIRRORED_REPEAT);
    gl.generateMipmap(gl.TEXTURE_2D);ready=true;requestAnimationFrame(draw);
  }};
  img.onerror=function(){{cv.parentNode.style.background='url('+src+') center/cover';}};
  img.src=src;
  var k=Math.pow((S.zoom/5)*.35+(1-S.zoom/5),2);   // Cargo's mouse scaling
  window.addEventListener('mousemove',function(e){{mx=k*e.clientX;my=k*e.clientY;}},{{passive:true}});
  function draw(now){{
    if(!ready)return;
    var d=window.devicePixelRatio||1,r=cv.parentNode.getBoundingClientRect(),w=Math.round(r.width*d),h=Math.round(r.height*d);
    if(cv.width!==w||cv.height!==h){{cv.width=w;cv.height=h;gl.viewport(0,0,w,h);}}
    if(px<0){{px=mx;py=my;}}else{{px=mx*.2+px*.8;py=my*.2+py*.8;}}
    gl.uniform1f(U.time,still?0:(now-t0)/1000);gl.uniform1f(U.sliceAngle,Math.PI*2/S.slices);
    gl.uniform1f(U.base1,S.base1);gl.uniform1f(U.speed1,S.speed1);gl.uniform1f(U.base2,S.base2);gl.uniform1f(U.speed2,S.speed2);
    gl.uniform2f(U.zoom,1.5/S.zoom*ratio,1.5/S.zoom);gl.uniform2f(U.center,S.cx,S.cy);gl.uniform2f(U.mouse,px*.005,py*.005);
    gl.uniform2f(U.resolution,w,h);gl.uniform2f(U.aspect,w/h,1);
    gl.drawArrays(gl.TRIANGLES,0,6);
    if(!still)requestAnimationFrame(draw);
  }}
  window.addEventListener('resize',function(){{if(still)requestAnimationFrame(draw);}});
}})();
</script>
""" + footer()
    write("about.html", head("About") + header(0, "about") + page)

# ---------------------------------------------------------------- research projects
def load_projects():
    """content/projects/NN-slug.md — research projects (ported from yuikondo.cargo.site)."""
    out = []
    for p in sorted(glob.glob(os.path.join(CONTENT, "projects", "*.md"))):
        meta, body = parse_front(read(p))
        meta.setdefault("slug", re.sub(r"^\d+-", "", os.path.basename(p)[:-3]))
        meta.setdefault("title", meta["slug"]); meta.setdefault("ref", "PROJECT"); meta["body"] = body
        out.append(meta)
    return out

def project_intro(m):
    tags = "".join(f'<span class="tag">{esc(t.strip())}</span>' for t in m.get("tags", "").split(",") if t.strip())
    sub = f'<p class="proj-sub">{esc(m["subtitle"])}</p>' if m.get("subtitle") else ""
    venue = f'<p class="proj-venue">{esc(m.get("venue",""))}{" · " + esc(m["year"]) if m.get("year") else ""}</p>'
    return (f'<header class="proj-intro"><h1 class="proj-title">{esc(m["title"])}</h1>{sub}{venue}'
            f'<div class="tags">{tags}</div></header>\n')

def build_projects(projects):
    n = len(projects)
    for i, m in enumerate(projects):
        prev_ = (f'<a href="{projects[i-1]["slug"]}.html">← {esc(projects[i-1]["title"])}</a>' if i > 0
                 else '<a href="../projects.html">← Projects</a>')
        next_ = (f'<a href="{projects[i+1]["slug"]}.html">{esc(projects[i+1]["title"])} →</a>' if i < n - 1
                 else '<a href="../projects.html">Projects →</a>')
        label = m.get("year") or "Project"
        write(f"projects/{m['slug']}.html",
              project_page(m, 1, label, prev_, next_, active="projects", intro=project_intro(m)))
    rows = "".join(
        f'  <a class="row proj-row" href="projects/{esc(m["slug"])}.html"><span class="c1"><span class="wk">{esc(m["title"])}</span></span>'
        f'<span class="c2">{esc(m.get("summary",""))}</span><span class="c3">{esc(m.get("year",""))}</span></a>\n' for m in projects)
    cards = "".join(
        f'  <a class="card" href="projects/{esc(m["slug"])}.html"><img src="{esc(m.get("hero",""))}" alt="" loading="lazy" '
        f'onerror="this.onerror=null;this.src=\'img/placeholder.svg\'"><p class="caption"><span class="wk">{esc(m["title"])}</span>'
        f'<span class="card-venue">{esc(m.get("venue",""))}{" · " + esc(m["year"]) if m.get("year") else ""}</span></p><p class="card-desc">{esc(m.get("summary",""))}</p></a>\n' for m in projects)
    write("projects.html", head("Projects") + header(0, "projects") +
          f'<main class="grid-page">\n  <div class="grid">\n{cards}  </div>\n</main>\n' + footer())

# ---------------------------------------------------------------- main
def main():
    weeks = load_weeks()
    final = load_single("final.md", {"title": "Final Project", "ref": "HTMAA/FINAL"})
    about = load_single("about.md", {"title": "About"})
    build_weeks(weeks); build_final(final, weeks)
    build_index(weeks, final); build_grid(weeks, final); build_about(about)
    projects = load_projects(); build_projects(projects)
    print(f"built {len(weeks)} weeks" + (", final" if final else "") + (", about" if about else "") + f", {len(projects)} projects")

if __name__ == "__main__":
    main()
