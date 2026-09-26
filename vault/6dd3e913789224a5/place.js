/* fills a place page from PLACES using <body data-place="id"> */
(function(){
  var id = document.body.dataset.place, p = placeOf(id); if (!p) return;
  var f = floorOf(p.floor);
  document.title = p.name + ' — how to break into (almost) anywhere';
  document.querySelector('.place-head h1').textContent = p.name;
  var meta = document.querySelector('.meta');
  meta.textContent = p.date;
  var mm = document.querySelector('.minimap');
  mm.style.backgroundImage = 'url(../floors/' + p.floor + '.png)';
  var dot = document.createElement('a'); dot.className = 'dot'; dot.href = '../index.html#' + p.floor;
  /* the image is contain-fit; the box has the same aspect ratio, so fractions map directly */
  dot.style.left = (p.x*100) + '%'; dot.style.top = (p.y*100) + '%'; dot.title = "back to the map";
  mm.appendChild(dot);
})();

/* the header stays out of the way while the title is on screen, and comes in once you scroll to the photos */
(function(){
  var head = document.querySelector('.place-head'), top = document.querySelector('header.top');
  if (!head || !top || !('IntersectionObserver' in window)) return;
  new IntersectionObserver(function(es){ top.classList.toggle('hidden', es[0].isIntersecting); }, { threshold: 0.35 }).observe(head);
})();
