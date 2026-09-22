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
