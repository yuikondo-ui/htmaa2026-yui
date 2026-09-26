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

/* --- the door. hold the banner for a second and a half: the lights go out and the cursor becomes a torch.
       a keyhole hides bottom-left in the dark. click it, give the password, and the title appears, then the map.
       (typing "open" anywhere still takes you to the plain gate.) --- */
(function () {
  var sc = document.querySelector('script[src$="js/site.js"]');
  var root = sc ? sc.getAttribute('src').replace(/js\/site\.js$/, '') : '';
  var KEY = "f3c1f895fdb1ac14c19166f4d606f9c8be3805ec2d4596dbf344d75a8c41e3a6";   /* sha256 of the password — vault/setpass.py rewrites this */
  function go() { window.location.href = root + 'vault/'; }

  var dark = null, holdTimer = null;
  function lightsOut() {
    if (dark) return;
    dark = document.createElement('div'); dark.className = 'blackout';
    dark.innerHTML =
      '<div class="bo-torch"></div>' +
      '<div class="bo-key">' +
        '<svg class="keyhole" viewBox="0 0 24 34" aria-label="keyhole"><circle cx="12" cy="11" r="8"/><path d="M8 17 L4 32 L20 32 L16 17 Z"/></svg>' +
        '<form class="bo-form" autocomplete="off"><input type="password" placeholder="·······" autocapitalize="off" spellcheck="false"></form>' +
      '</div>' +
      '<div class="bo-splash"><h1>how to break into (almost) anywhere</h1></div>';
    document.body.appendChild(dark);
    document.documentElement.classList.add('lights-out');
    var key = dark.querySelector('.bo-key'), hole = dark.querySelector('.keyhole'),
        form = dark.querySelector('.bo-form'), input = form.querySelector('input'), splash = dark.querySelector('.bo-splash');
    var big = matchMedia('(hover:none)').matches, r = big ? (innerWidth < 700 ? 150 : 260) : 200;
    dark.style.setProperty('--r', r + 'px');
    function move(x, y) {
      dark.style.setProperty('--mx', x + 'px'); dark.style.setProperty('--my', y + 'px');
      var k = hole.getBoundingClientRect(), dx = x - (k.left + k.width / 2), dy = y - (k.top + k.height / 2);
      key.classList.toggle('lit', Math.sqrt(dx * dx + dy * dy) < r * 0.95);
    }
    dark.addEventListener('pointermove', function (e) { move(e.clientX, e.clientY); });
    dark.addEventListener('pointerdown', function (e) { move(e.clientX, e.clientY); });
    dark.addEventListener('touchmove', function (e) { var t = e.touches[0]; move(t.clientX, t.clientY); e.preventDefault(); }, { passive: false });
    move(innerWidth / 2, innerHeight / 2);
    hole.addEventListener('click', function (e) { e.preventDefault(); key.classList.add('open', 'lit'); setTimeout(function () { input.focus(); }, 60); });
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      var v = input.value.trim().toLowerCase(); if (!v) return;
      if (await sha256(v) === KEY) {
        var folder = (await sha256('door:' + v)).slice(0, 16);
        key.classList.add('gone'); splash.classList.add('show');
        setTimeout(function () { window.location.href = root + 'vault/' + folder + '/'; }, 1900);
      } else { input.value = ''; form.classList.remove('no'); void form.offsetWidth; form.classList.add('no'); }
    });
  }
  function lightsOn() {
    if (!dark) return;
    dark.classList.add('off'); document.documentElement.classList.remove('lights-out');
    var d = dark; dark = null; setTimeout(function () { d.remove(); }, 400);
  }
  function startHold(e) {
    var banner = e.target.closest && e.target.closest('.banner'); if (!banner || dark) return;
    banner.classList.add('holding');
    holdTimer = setTimeout(function () { banner.classList.remove('holding'); lightsOut(); }, 1500);
  }
  function endHold() { clearTimeout(holdTimer); holdTimer = null; document.querySelectorAll('.banner.holding').forEach(function (b) { b.classList.remove('holding'); }); }
  document.addEventListener('pointerdown', startHold);
  document.addEventListener('pointerup', endHold);
  document.addEventListener('pointercancel', endHold);
  document.addEventListener('contextmenu', function (e) { if (e.target.closest && e.target.closest('.banner')) e.preventDefault(); });
  document.addEventListener('keydown', function (e) { if (dark && e.key === 'Escape') lightsOn(); });
  /* coming back with the browser's back button: the page is restored from cache, so put the lights back on */
  window.addEventListener('pageshow', function () { if (dark) { var d = dark; dark = null; d.remove(); document.documentElement.classList.remove('lights-out'); } });
  window.addEventListener('pagehide', function () { if (dark) { var d = dark; dark = null; d.remove(); document.documentElement.classList.remove('lights-out'); } });

  var typed = '';
  document.addEventListener('keydown', function (e) {
    if (e.target && /INPUT|TEXTAREA/.test(e.target.tagName)) return;
    typed = (typed + e.key.toLowerCase()).slice(-4);
    if (typed === 'open') go();
  });

  async function sha256(s) {
    if (window.crypto && crypto.subtle) {
      try { var b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
            return Array.from(new Uint8Array(b)).map(function (x) { return x.toString(16).padStart(2, '0'); }).join(''); } catch (_) {}
    }
    return sha256js(s);
  }
  function sha256js(ascii){
    function rr(v,a){return (v>>>a)|(v<<(32-a));}
    var mathPow=Math.pow,maxWord=mathPow(2,32),i,j,result='',words=[],asciiBitLength=ascii.length*8,
        hash=sha256js.h=sha256js.h||[],k=sha256js.k=sha256js.k||[],primeCounter=k.length,isComposite={};
    for(var candidate=2;primeCounter<64;candidate++){ if(!isComposite[candidate]){ for(i=0;i<313;i+=candidate)isComposite[i]=candidate;
        hash[primeCounter]=(mathPow(candidate,.5)*maxWord)|0; k[primeCounter++]=(mathPow(candidate,1/3)*maxWord)|0; } }
    ascii=unescape(encodeURIComponent(ascii)); ascii+='\x80'; while(ascii.length%64-56)ascii+='\x00';
    for(i=0;i<ascii.length;i++){ j=ascii.charCodeAt(i); if(j>>8)return; words[i>>2]|=j<<((3-i)%4)*8; }
    words[words.length]=((asciiBitLength/maxWord)|0); words[words.length]=(asciiBitLength);
    for(j=0;j<words.length;){ var w=words.slice(j,j+=16),oldHash=hash; hash=hash.slice(0,8);
      for(i=0;i<64;i++){ var w15=w[i-15],w2=w[i-2],a=hash[0],e=hash[4],
          temp1=hash[7]+(rr(e,6)^rr(e,11)^rr(e,25))+((e&hash[5])^((~e)&hash[6]))+k[i]+(w[i]=(i<16)?w[i]:(w[i-16]+(rr(w15,7)^rr(w15,18)^(w15>>>3))+w[i-7]+(rr(w2,17)^rr(w2,19)^(w2>>>10)))|0),
          temp2=(rr(a,2)^rr(a,13)^rr(a,22))+((a&hash[1])^(a&hash[2])^(hash[1]&hash[2]));
        hash=[(temp1+temp2)|0].concat(hash); hash[4]=(hash[4]+temp1)|0; }
      for(i=0;i<8;i++)hash[i]=(hash[i]+oldHash[i])|0; }
    for(i=0;i<8;i++)for(j=3;j+1;j--){ var b=(hash[i]>>(j*8))&255; result+=((b<16)?0:'')+b.toString(16); }
    return result;
  }
})();
