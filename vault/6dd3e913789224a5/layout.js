/* layout.js — photo spreads with a built-in layout editor.
   Markup: <figure data-box="row col width" data-rot="90"><img src="…"></figure>   (data-rot optional: 90, 180 or 270)
     row   : 1… (1 row = 1vw)         col : 1–24 (left page 1–12, right 13–24, the fold is between 12 and 13)
     width : in columns (1–24)        height comes from the photo's own proportions, never cropped
   Photos should not overlap: a move that would land on another photo is refused (blink), a drag dropped on one jumps back,
   and a rotation that ends up on another photo turns red until you move it off.
   Edit mode: press E (or open the page with #edit). Drag to move, drag the corner to resize, click to select.
     arrows = nudge   [ ] = narrower / wider   r = rotate 90°
     backspace = remove from layout   S = download this page with the new layout (replace the file, done)
*/
(function () {
  var ROWCOL = 24;
  var spreads = function () { return Array.prototype.slice.call(document.querySelectorAll('.spread.photos')); };
  var figs = function () { return Array.prototype.slice.call(document.querySelectorAll('.spread.photos figure[data-box]')); };
  var colW = function () { return document.documentElement.clientWidth / ROWCOL; };
  var rowH = function () { return document.documentElement.clientWidth / 100; };

  function box(f) { var b = f.dataset.box.trim().split(/\s+/).map(Number); return { r: b[0] || 1, c: b[1] || 1, w: b[2] || 12 }; }
  function rowsOf(f, w) { return Math.ceil(w * (100 / ROWCOL) * ratio(f)); }
  function overlaps(f, b) {
    var h = rowsOf(f, b.w);
    return Array.prototype.some.call(f.parentNode.querySelectorAll('figure[data-box]'), function (o) {
      if (o === f) return false; var ob = box(o), oh = rowsOf(o, ob.w);
      return !(b.c + b.w <= ob.c || b.c >= ob.c + ob.w || b.r + h <= ob.r || b.r >= ob.r + oh);
    });
  }
  function bump(f) { f.classList.add('bump'); setTimeout(function () { f.classList.remove('bump'); }, 250); }
  function setBox(f, b, free) {
    b.w = Math.max(2, Math.min(ROWCOL, Math.round(b.w))); b.c = Math.max(1, Math.min(ROWCOL - b.w + 1, Math.round(b.c))); b.r = Math.max(1, Math.round(b.r));
    if (!free && !f.classList.contains('over') && overlaps(f, b)) { bump(f); return false; }
    f.dataset.box = b.r + ' ' + b.c + ' ' + b.w; apply(f); mark(f); return true;
  }
  /* a photo that sits on another one stays red until it is moved off */
  function mark(f) { f.classList.toggle('over', overlaps(f, box(f))); }
  function rot(f) { return (parseInt(f.dataset.rot || '0', 10) % 360 + 360) % 360; }
  function ratio(f) { var i = f.querySelector('img'), r = (i && i.naturalWidth) ? i.naturalHeight / i.naturalWidth : 0.75; return (rot(f) % 180) ? 1 / r : r; }
  function turn(f) {
    var i = f.querySelector('img'), d = rot(f);
    if (!d) { i.style.cssText = ''; f.dataset.rot = ''; f.removeAttribute('data-rot'); return; }
    requestAnimationFrame(function () {
      var W = f.clientWidth, H = f.clientHeight, swap = d % 180;
      i.style.cssText = 'position:absolute;left:50%;top:50%;width:' + (swap ? H : W) + 'px;height:' + (swap ? W : H) + 'px;transform:translate(-50%,-50%) rotate(' + d + 'deg);max-width:none';
    });
  }
  function apply(f) {
    var b = box(f), rows = rowsOf(f, b.w);
    f.style.gridArea = b.r + ' / ' + b.c + ' / span ' + rows + ' / ' + (b.c + b.w);
    turn(f);
  }
  function applyAll() { figs().forEach(apply); }
  applyAll();
  figs().forEach(function (f) { var i = f.querySelector('img'); if (i && !i.complete) i.addEventListener('load', function () { apply(f); }); });
  addEventListener('resize', applyAll);

  /* ---------------- editor ---------------- */
  var editing = false, sel = null, drag = null;
  var hud = document.createElement('div'); hud.id = 'layout-hud';
  hud.innerHTML = '<b>layout</b> drag anywhere (up and down too) · corner = resize · ← → ↑ ↓ (shift = 5) · [ ] width · r = rotate · ⌫ remove · <u>S = download page</u> · E = done';
  function toggle(on) {
    editing = on; document.body.classList.toggle('editing', on);
    if (on) { document.body.appendChild(hud); figs().forEach(prep); } else { hud.remove(); select(null); }
  }
  function prep(f) {
    if (f.querySelector('.rz')) return;
    var h = document.createElement('i'); h.className = 'rz'; f.appendChild(h);
    var l = document.createElement('i'); l.className = 'lbl'; f.appendChild(l); label(f);
  }
  function bottom(sp, except) { var r = 1; sp.querySelectorAll('figure[data-box]').forEach(function (o) { if (o !== except) { var ob = box(o); r = Math.max(r, ob.r + rowsOf(o, ob.w) + 2); } }); return r; }
  function label(f) { var l = f.querySelector('.lbl'); if (l) l.textContent = f.dataset.box; }
  function select(f) { if (sel) sel.classList.remove('sel'); sel = f; if (f) f.classList.add('sel'); }

  addEventListener('keydown', function (e) {
    if (/INPUT|TEXTAREA/.test(e.target.tagName)) return;
    if (e.key === 'e' || e.key === 'E') { toggle(!editing); return; }
    if (!editing) return;
    if (e.key === 's' || e.key === 'S') { download(); e.preventDefault(); return; }
    if (!sel) return;
    var b = box(sel), s = spreads(), i = s.indexOf(sel.parentNode);
    if (e.key === 'ArrowLeft') b.c--; else if (e.key === 'ArrowRight') b.c++;
    else if (e.key === 'ArrowUp') b.r -= e.shiftKey ? 5 : 1; else if (e.key === 'ArrowDown') b.r += e.shiftKey ? 5 : 1;
    else if (e.key === '[') b.w--; else if (e.key === ']') b.w++;
    else if (e.key === 'r' || e.key === 'R') { sel.dataset.rot = (rot(sel) + 90) % 360; if (!rot(sel)) sel.removeAttribute('data-rot'); apply(sel); mark(sel); label(sel); e.preventDefault(); return; }
    else if (e.key === 'n' && s[i + 1]) { s[i + 1].appendChild(sel); b.r = bottom(s[i + 1], sel); }
    else if (e.key === 'p' && s[i - 1]) { s[i - 1].appendChild(sel); b.r = bottom(s[i - 1], sel); }
    else if (e.key === '+') { var ns = document.createElement('section'); ns.className = 'spread photos'; sel.parentNode.after(ns); ns.appendChild(sel); b.r = 1; }
    else if (e.key === 'Backspace' || e.key === 'Delete') { var sp = sel.parentNode; sel.remove(); if (!sp.children.length) sp.remove(); select(null); return; }
    else return;
    e.preventDefault(); setBox(sel, b); label(sel);
  });

  document.addEventListener('pointerdown', function (e) {
    if (!editing) return;
    var f = e.target.closest && e.target.closest('.spread.photos figure[data-box]'); if (!f) return;
    e.preventDefault(); select(f);
    drag = { f: f, x: e.clientX, y: e.clientY + scrollY, lastX: e.clientX, lastY: e.clientY, b: box(f), resize: e.target.classList.contains('rz'), wasOver: f.classList.contains('over') };
  });
  function follow() {
    var dc = (drag.lastX - drag.x) / colW(), dr = (drag.lastY + scrollY - drag.y) / rowH(), b = drag.b;
    if (drag.resize) setBox(drag.f, { r: b.r, c: b.c, w: b.w + dc }, true);
    else setBox(drag.f, { r: b.r + dr, c: b.c + dc, w: b.w }, true);
    label(drag.f);
  }
  addEventListener('pointermove', function (e) {
    if (!drag) return;
    drag.lastX = e.clientX; drag.lastY = e.clientY; follow();
  });
  setInterval(function () { if (!drag || drag.resize || drag.lastY == null) return; var y = drag.lastY, H = innerHeight; if (y < 70) { scrollBy(0, -14); follow(); } else if (y > H - 70) { scrollBy(0, 14); follow(); } }, 16);
  addEventListener('pointerup', function () {
    if (!drag) return;
    if (!drag.wasOver && overlaps(drag.f, box(drag.f))) { setBox(drag.f, drag.b, true); bump(drag.f); }   /* landed on another photo: go back */
    mark(drag.f); label(drag.f); drag = null;
  });

  /* download the page with the new data-box values (inline grid-area is recomputed on load, so it is dropped) */
  function download() {
    var doc = document.documentElement.cloneNode(true);
    doc.querySelectorAll('#layout-hud, .rz, .lbl').forEach(function (n) { n.remove(); });
    doc.querySelectorAll('.spread.photos figure').forEach(function (f) { f.removeAttribute('style'); f.classList.remove('sel'); f.classList.remove('over'); f.classList.remove('bump'); if (!f.className) f.removeAttribute('class'); var i = f.querySelector('img'); if (i) i.removeAttribute('style'); });
    doc.querySelector('body').classList.remove('editing');
    /* place.js filled these in; empty them again so the file stays a template */
    var h = doc.querySelector('.place-head h1'); if (h) h.textContent = '';
    var m = doc.querySelector('.place-head .meta'); if (m) m.textContent = '';
    var mm = doc.querySelector('.minimap'); if (mm) { mm.removeAttribute('style'); mm.innerHTML = ''; }
    var pn = doc.querySelector('.prevnext'); if (pn) pn.innerHTML = '';
    var html = '<!doctype html>\n' + doc.outerHTML.replace(/<\/section>\s*<section/g, '</section>\n\n  <section');
    var a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([html], { type: 'text/html' }));
    a.download = location.pathname.split('/').pop() || 'page.html'; a.click();
  }

  if (location.hash === '#edit') toggle(true);
})();
