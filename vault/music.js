/* background music for the vault: Suzanne Kraft — Flatiron (from "Talk From Home").
   Never starts on its own: it plays only after someone presses the ♪ bottom-right, then keeps playing across pages
   (and is remembered) until they press it again. The song is in three parts so the files stay small enough for forge. */
(function () {
  var base = (document.currentScript && document.currentScript.getAttribute('data-base')) || '';
  var PARTS = [base + 'audio/flatiron-1.m4a', base + 'audio/flatiron-2.m4a', base + 'audio/flatiron-3.m4a'];
  var LS = 'vault-music';
  var state = { on: false, part: 0, t: 0 };
  try { var saved = JSON.parse(localStorage.getItem(LS) || '{}'); for (var k in saved) state[k] = saved[k]; } catch (_) {}
  function save() { try { localStorage.setItem(LS, JSON.stringify({ on: state.on, part: state.part, t: state.t })); } catch (_) {} }

  var VOL = 0.8, fadeTimer = null;
  var audio = new Audio(); audio.preload = 'auto'; audio.volume = 0;
  /* the music never jumps in: it rises from silence over `secs` seconds */
  function fadeTo(target, secs) {
    clearInterval(fadeTimer); var from = audio.volume, steps = Math.max(1, Math.round(secs * 20)), i = 0;
    fadeTimer = setInterval(function () { i++; audio.volume = from + (target - from) * (i / steps); if (i >= steps) clearInterval(fadeTimer); }, secs * 1000 / steps);
  }
  var next = new Audio(); next.preload = 'auto';
  function load(part, t) {
    state.part = part % PARTS.length; audio.src = PARTS[state.part];
    if (t) { try { audio.currentTime = t; } catch (_) { audio.addEventListener('loadedmetadata', function once() { audio.currentTime = t; audio.removeEventListener('loadedmetadata', once); }); } }
    next.src = PARTS[(state.part + 1) % PARTS.length];
  }
  audio.addEventListener('ended', function () { load(state.part + 1, 0); audio.play().catch(function () {}); });
  audio.addEventListener('timeupdate', function () { state.t = audio.currentTime; });
  setInterval(save, 2000);
  addEventListener('pagehide', save);

  var ui = document.createElement('button'); ui.className = 'music'; ui.type = 'button';
  ui.innerHTML = '<span class="note">♪</span><span class="who">Suzanne Kraft — Flatiron</span>';
  function mount() { if (!ui.parentNode && document.body) document.body.appendChild(ui); render(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
  function render() {
    ui.classList.toggle('on', state.on && !audio.paused);
    ui.classList.toggle('blocked', state.on && audio.paused);
    ui.title = (state.on && !audio.paused) ? 'music off' : 'music on';
  }

  function play(secs) {
    if (!audio.src) load(state.part, state.t);
    audio.volume = 0;
    return audio.play().then(function () { state.on = true; save(); render(); fadeTo(VOL, secs || 4); }).catch(function () { render(); });
  }
  function stop() { fadeTo(0, 0.6); setTimeout(function () { audio.pause(); render(); }, 650); state.on = false; save(); render(); }
  ui.addEventListener('click', function () { if (state.on && !audio.paused) stop(); else play(3); });
  audio.addEventListener('play', render); audio.addEventListener('pause', render);

  window.VaultMusic = {
    start: function () { state.on = true; state.part = 0; state.t = 0; save(); load(0, 0); return play(10); },   /* not called anywhere now — music is opt-in via the ♪ */
    play: play, stop: stop
  };
  /* resume if it was on; a browser may refuse until the first tap — then the first tap anywhere starts it */
  if (state.on) {
    load(state.part, state.t); play(6);
    document.addEventListener('pointerdown', function once() { if (state.on && audio.paused) play(6); document.removeEventListener('pointerdown', once); });
  }
})();
