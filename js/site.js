/* Site-wide interaction: link hover (mono switch) + anchored thumbnail previews.
   The hover state is managed in JS instead of CSS :hover because the hovered word changes
   width and can reflow out from under the cursor — with :hover that causes flicker. Here the
   state is kept while the pointer is inside EITHER the word's original box or its new box. */
(function () {
  var SEL = '.content a, .about a';
  var pv = document.createElement('img');
  pv.alt = ''; pv.setAttribute('aria-hidden', 'true');
  /* On About, the empty right column is the preview area; elsewhere a small thumbnail
     floats above the link. */
  var slot = document.querySelector('.about-side');
  pv.className = slot ? 'slot-preview' : 'link-preview';
  (slot || document.body).appendChild(pv);

  var active = null, boxes = [], mx = 0, my = 0;
  var PAD = 4;

  function rects(el) { return Array.prototype.slice.call(el.getClientRects()).map(function (r) {
    return { l: r.left - PAD, t: r.top - PAD, r: r.right + PAD, b: r.bottom + PAD }; }); }
  function inside(list, x, y) { return list.some(function (b) { return x >= b.l && x <= b.r && y >= b.t && y <= b.b; }); }

  function placePreview(a) {
    if (slot) {   // level with the hovered line, but never below the column's bottom
      var la = a.getBoundingClientRect(), ls = slot.getBoundingClientRect();
      pv.style.top = Math.round(Math.max(0, la.top - ls.top - 3)) + 'px';
      return;
    }
    var r = a.getBoundingClientRect(), w = pv.offsetWidth || 200, h = pv.offsetHeight || 130, gap = 6;
    var x = Math.min(r.left, window.innerWidth - w - 12), y = r.top - h - gap;
    if (y < 8) y = r.bottom + gap;
    pv.style.transform = 'translate(' + Math.round(x) + 'px,' + Math.round(y) + 'px)';
  }
  function open(a) {
    active = a; boxes = rects(a);                 // remember the box before the style changes
    a.classList.add('is-hover');
    boxes = boxes.concat(rects(a));               // and after
    var src = a.getAttribute('data-preview');
    if (src) {
      pv.src = src;
      var show = function () { if (active === a) { placePreview(a); pv.classList.add('show'); } };
      if (pv.complete && pv.naturalWidth) show(); else pv.onload = show;
    }
  }
  function close() {
    if (!active) return;
    active.classList.remove('is-hover'); active = null; boxes = [];
    pv.classList.remove('show');
  }

  document.addEventListener('mousemove', function (e) {
    mx = e.clientX; my = e.clientY;
    if (active) {
      if (!inside(boxes, mx, my) && !inside(rects(active), mx, my)) close();
      return;
    }
    var a = e.target.closest && e.target.closest(SEL);
    if (a) open(a);
  }, { passive: true });

  window.addEventListener('scroll', function () { if (active) { if (pv.classList.contains('show')) placePreview(active); if (!inside(rects(active), mx, my)) close(); } }, { passive: true });
  document.addEventListener('mouseleave', close);
})();

/* --- a door. click the banner five times (it tears a little more each time), or type "open" anywhere. --- */
(function () {
  var sc = document.querySelector('script[src$="js/site.js"]');
  var root = sc ? sc.getAttribute('src').replace(/js\/site\.js$/, '') : '';
  function go() { window.location.href = root + 'vault/'; }
  var NS = 'http://www.w3.org/2000/svg', n = 0, t = 0, cracks = [];

  /* a jagged line from top to bottom, around x (0–1 of the banner width) */
  function jag(x, w, h) {
    var pts = [], steps = 7 + Math.floor(Math.random() * 4), px = x * w;
    for (var i = 0; i <= steps; i++) {
      var y = (h / steps) * i, dx = (Math.random() - .5) * w * 0.05 + (i === 0 || i === steps ? 0 : 0);
      px += dx; pts.push([Math.max(4, Math.min(w - 4, px)), y]);
    }
    return pts;
  }
  function draw(banner, pts) {
    var svg = document.createElementNS(NS, 'svg'); svg.setAttribute('class', 'crack');
    svg.setAttribute('viewBox', '0 0 ' + banner.clientWidth + ' ' + banner.clientHeight); svg.setAttribute('preserveAspectRatio', 'none');
    var d = pts.map(function (p, i) { return (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1); }).join(' ');
    var lip = document.createElementNS(NS, 'path'); lip.setAttribute('d', d); lip.setAttribute('class', 'lip'); lip.setAttribute('transform', 'translate(2 0)');
    var p = document.createElementNS(NS, 'path'); p.setAttribute('d', d);
    svg.appendChild(lip); svg.appendChild(p); banner.appendChild(svg);
  }
  function tear(banner, pts) {
    var w = banner.clientWidth, h = banner.clientHeight;
    var line = pts.map(function (p) { return (p[0] / w * 100).toFixed(2) + '% ' + (p[1] / h * 100).toFixed(2) + '%'; });
    var left = 'polygon(0 0, ' + line.join(', ') + ', 0 100%)';
    var right = 'polygon(100% 0, ' + line.join(', ') + ', 100% 100%)';
    var m = banner.querySelector('.marquee');
    var tf = m ? getComputedStyle(m).transform : 'none';          /* freeze the marquee where it is */
    ['l', 'r'].forEach(function (side) {
      var piece = document.createElement('div'); piece.className = 'piece ' + side;
      piece.style.clipPath = side === 'l' ? left : right;
      var clone = m ? m.cloneNode(true) : null;
      if (clone) { clone.style.transform = tf; clone.style.animation = 'none'; piece.appendChild(clone); }
      banner.querySelectorAll('.crack').forEach(function (c) { piece.appendChild(c.cloneNode(true)); });
      banner.appendChild(piece);
    });
    banner.classList.add('torn');
    setTimeout(go, 700);
  }

  document.addEventListener('click', function (e) {
    var banner = e.target.closest && e.target.closest('.banner'); if (!banner) return;
    var now = Date.now(); if (now - t > 2500) { n = 0; cracks = []; banner.querySelectorAll('.crack').forEach(function (c) { c.remove(); }); } t = now;
    n++;
    var r = banner.getBoundingClientRect(), x = (e.clientX - r.left) / r.width;
    var pts = jag(x, banner.clientWidth, banner.clientHeight); cracks.push(pts); draw(banner, pts);
    banner.classList.remove('hit'); void banner.offsetWidth; banner.classList.add('hit');
    if (n >= 5) { n = 0; tear(banner, pts); }
  });

  var typed = '';
  document.addEventListener('keydown', function (e) {
    if (e.target && /INPUT|TEXTAREA/.test(e.target.tagName)) return;
    typed = (typed + e.key.toLowerCase()).slice(-4);
    if (typed === 'open') go();
  });
})();
