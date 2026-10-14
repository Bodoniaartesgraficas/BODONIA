// Pinta los textos y la galería a partir de contenido.js, y después da vida a la galería y las ventanas.
const C = window.CONTENIDO;
const read = path => path.split('.').reduce((o, k) => (o == null ? o : o[k]), C);
function setText(el, value) {
  el.textContent = '';
  String(value).split('\n').forEach((line, i) => { if (i) el.appendChild(document.createElement('br')); el.appendChild(document.createTextNode(line)); });
}
document.title = C.pagina.titulo;
document.querySelectorAll('[data-texto]').forEach(el => { const v = read(el.dataset.texto); if (v != null) setText(el, v); });
const email = document.querySelector('#contact-email'); email.href = 'mailto:' + C.contacto.correo; email.textContent = C.contacto.correo;
const phone = document.querySelector('#contact-phone'); phone.href = 'tel:+34' + C.contacto.telefono.replace(/\D/g, ''); phone.textContent = C.contacto.telefono;
document.querySelector('#contact-map').href = C.contacto.mapa;
const servicesList = document.querySelector('#services-list');
C.servicios.lista.forEach(s => {
  const row = document.createElement('div'), dt = document.createElement('dt'), dd = document.createElement('dd');
  dt.textContent = s.nombre; row.append(dt); if (s.detalle) { dd.textContent = s.detalle; row.append(dd); } servicesList.appendChild(row);
});
const filasEl = document.querySelector('#filas');
const galleries = [];
const projects = [];
let n = 0;
C.filas.forEach((fila, fi) => {
  const section = document.createElement('section');
  section.className = 'works'; if (fi === 0) section.id = 'proyectos'; section.setAttribute('aria-label', fila.titulo);
  const label = document.createElement('p'); label.className = 'fila-titulo'; label.textContent = fila.titulo;
  const galleryEl = document.createElement('div');
  galleryEl.className = 'gallery'; galleryEl.tabIndex = 0;
  galleryEl.setAttribute('aria-label', fila.titulo + '. Galería horizontal: usa las flechas para recorrer los trabajos.');
  fila.proyectos.forEach(p => {
    const article = document.createElement('article');
    article.className = 'project'; article.dataset.title = p.titulo; article.dataset.type = p.tipo;
    article.dataset.full = p.completa || p.portada;
    const button = document.createElement('button');
    button.className = 'project-image'; button.setAttribute('aria-label', 'Abrir ' + p.titulo);
    const cover = document.createElement('img');
    cover.className = 'cover mockup'; cover.src = p.portada; cover.alt = p.titulo + ', ' + p.tipo.toLowerCase(); cover.draggable = false;
    if (p.encuadre) cover.style.objectPosition = p.encuadre;
    if (fi === 0 && n < 4) cover.fetchPriority = 'high'; else cover.loading = 'lazy';
    n++;
    button.appendChild(cover);
    if (p.detalle) {
      const detail = document.createElement('img');
      detail.className = 'alternate detalle'; detail.src = p.detalle; detail.alt = ''; detail.draggable = false; detail.loading = 'lazy';
      detail.setAttribute('aria-hidden', 'true');
      button.appendChild(detail);
    }
    article.appendChild(button); galleryEl.appendChild(article); projects.push(article);
  });
  section.append(label, galleryEl); filasEl.appendChild(section);
  galleries.push(galleryEl);
});

const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const visible = projects;
let selected = 0;
let dragged = false;
const projectDialog = document.querySelector('#project-dialog');

// Cada fila se desplaza sola: arrastrando, con las flechas del teclado o con el gesto horizontal del trackpad.
function initGallery(gallery, speed) {
  const cards = [...gallery.querySelectorAll('.project')];
  let drag = null, targetScroll = 0, animation = 0, paintFrame = 0;
  const photoLayers = cards.map(p => ({card:p, image:p.querySelector('.mockup')})).filter(p => p.image);
  function updatePhotos() {
    paintFrame = 0;
    const bounds = gallery.getBoundingClientRect();
    photoLayers.forEach(({card,image}) => {
      const rect = card.getBoundingClientRect();
      if (rect.right < bounds.left || rect.left > bounds.right) return;
      const offset = Math.max(-1, Math.min(1, (rect.left + rect.width / 2 - bounds.left - bounds.width / 2) / bounds.width));
      image.style.transform = reducedMotion.matches ? 'none' : `translate3d(${offset * -9}px,0,0) scale(1.045)`;
    });
  }
  function schedulePhotos() { if (!paintFrame) paintFrame = requestAnimationFrame(updatePhotos); }
  function stopMotion() { cancelAnimationFrame(animation); animation = 0; targetScroll = gallery.scrollLeft; }
  function move(amount, smooth = true) {
    if (!animation) targetScroll = gallery.scrollLeft;
    targetScroll = Math.max(0, Math.min(gallery.scrollWidth - gallery.clientWidth, targetScroll + amount));
    if (!smooth || reducedMotion.matches) { gallery.scrollLeft = targetScroll; return; }
    if (animation) return;
    let lastTime = performance.now();
    function frame(now) {
      const fraction = 1 - Math.exp(-Math.min(now - lastTime, 40) / 115);
      lastTime = now;
      const distance = targetScroll - gallery.scrollLeft;
      gallery.scrollLeft += distance * fraction;
      if (Math.abs(distance) > 2) animation = requestAnimationFrame(frame);
      else { gallery.scrollLeft = targetScroll; animation = 0; }
    }
    animation = requestAnimationFrame(frame);
  }
  function step(direction, smooth) { move(direction * (cards[0].offsetWidth + parseFloat(getComputedStyle(gallery).gap)), smooth); }
  gallery.addEventListener('scroll', schedulePhotos, {passive:true});
  window.addEventListener('resize', () => { stopMotion(); schedulePhotos(); });
  reducedMotion.addEventListener('change', () => { stopMotion(); photoLayers.forEach(({image}) => image.style.transform = 'none'); schedulePhotos(); });
  // La rueda del ratón baja la página; con Mayús recorre la fila.
  gallery.addEventListener('wheel', e => {
    if (!e.shiftKey || e.ctrlKey || document.querySelector('dialog[open]')) return;
    e.preventDefault();
    move((e.deltaX || e.deltaY) * (e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? gallery.clientWidth : 1));
  }, {passive:false});
  gallery.addEventListener('keydown', e => {
    if (!['ArrowRight','ArrowLeft','Home','End'].includes(e.key)) return;
    e.preventDefault(); stopMotion();
    if (e.key === 'Home') gallery.scrollLeft = 0;
    else if(e.key === 'End') gallery.scrollLeft = gallery.scrollWidth;
    else step(e.key === 'ArrowRight' ? 1 : -1, false);
  });
  gallery.addEventListener('pointerdown', e => {
    if (!e.isPrimary || drag) return;
    stopMotion(); dragged = false;
    if(e.pointerType !== 'mouse' || e.button !== 0) return;
    drag = {x:e.clientX,scroll:gallery.scrollLeft,id:e.pointerId,lastX:e.clientX,lastTime:performance.now(),velocity:0};
  });
  gallery.addEventListener('pointermove', e => {
    if(!drag) return;
    const delta = e.clientX-drag.x;
    if(Math.abs(delta)>5) { dragged = true; gallery.classList.add('dragging'); gallery.setPointerCapture(drag.id); }
    if(dragged) {
      const now = performance.now();
      const dt = Math.max(1, now - drag.lastTime);
      drag.velocity = (drag.lastX - e.clientX) / dt;
      drag.lastX = e.clientX; drag.lastTime = now;
      gallery.scrollLeft = drag.scroll-delta;
    }
  });
  function endDrag() { if(drag && gallery.hasPointerCapture(drag.id)) gallery.releasePointerCapture(drag.id); drag = null; gallery.classList.remove('dragging'); }
  gallery.addEventListener('pointerup', () => {
    const momentum = drag && dragged && performance.now()-drag.lastTime < 90 ? Math.max(-700,Math.min(700,drag.velocity*150)) : 0;
    endDrag();
    if(momentum && !reducedMotion.matches) move(momentum);
  });
  gallery.addEventListener('pointercancel',endDrag);
  gallery.addEventListener('lostpointercapture',endDrag);
  // Deslizamiento lento y continuo (de ida y vuelta); se detiene con el ratón encima, al arrastrar o con una ventana abierta.
  let pos = 0, dir = 1, last = 0, hold = 0, hovering = false, focused = false;
  gallery.addEventListener('pointerenter', e => { if (e.pointerType === 'mouse') hovering = true; });
  gallery.addEventListener('pointerleave', () => { hovering = false; });
  gallery.addEventListener('focusin', () => { focused = true; });
  gallery.addEventListener('focusout', () => { focused = false; });
  function drift(now) {
    const dt = Math.min(now - (last || now), 50) / 1000; last = now;
    const max = gallery.scrollWidth - gallery.clientWidth;
    if (animation || drag || hovering || focused || document.querySelector('dialog[open]') || reducedMotion.matches || max <= 0) { pos = gallery.scrollLeft; }
    else if (hold > 0) { hold -= dt; }
    else {
      if (Math.abs(gallery.scrollLeft - pos) > 1.5) pos = gallery.scrollLeft;
      pos += dir * speed * dt;
      if (pos >= max) { pos = max; dir = -1; hold = 1.5; } else if (pos <= 0) { pos = 0; dir = 1; hold = 1.5; }
      gallery.scrollLeft = pos;
    }
    requestAnimationFrame(drift);
  }
  requestAnimationFrame(drift);
  schedulePhotos();
  return { stop: stopMotion, toStart: smooth => { stopMotion(); move(-gallery.scrollLeft, smooth); dir = 1; hold = 1.5; } };
}
const controls = galleries.map((g, i) => initGallery(g, C.filas[i].velocidad || 20));
document.querySelector('.brand').addEventListener('click',e => {
  e.preventDefault(); controls.forEach(c => c.toStart(e.detail !== 0)); window.scrollTo({top:0, behavior: reducedMotion.matches ? 'auto' : 'smooth'});
});
function showDialog(dialog) {
  controls.forEach(c => c.stop());
  document.querySelectorAll('dialog[open]').forEach(d=>d.close());
  dialog.showModal();
}
document.querySelectorAll('[data-dialog]').forEach(button=>button.addEventListener('click',()=>showDialog(document.getElementById(button.dataset.dialog))));
document.querySelectorAll('dialog').forEach(dialog=>{
  dialog.querySelector('.close').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',e=>{
    const rect = dialog.getBoundingClientRect();
    if(e.target === dialog && (e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom)) dialog.close();
  });
});
function renderProject(index) {
  selected = (index + visible.length) % visible.length;
  const project = visible[selected];
  const name = project.dataset.title;
  document.querySelector('#project-title').textContent = name;
  document.querySelector('#project-type').textContent = project.dataset.type;
  const image = document.querySelector('#project-full');
  image.src = project.dataset.full;
  image.alt = `${name}: vista completa del trabajo`;
}
projects.forEach(project=>project.querySelector('button').addEventListener('click',e=>{
  if(dragged && e.detail) { dragged = false; return; }
  renderProject(visible.indexOf(project)); showDialog(projectDialog);
}));
document.querySelector('#project-prev').addEventListener('click',()=>renderProject(selected-1));
document.querySelector('#project-next').addEventListener('click',()=>renderProject(selected+1));
projectDialog.addEventListener('keydown',e=>{ if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();renderProject(selected+(e.key==='ArrowRight'?1:-1));} });
document.querySelector('#contact-form').addEventListener('submit',e=>{
  e.preventDefault();
  const form = e.currentTarget, status = document.querySelector('#form-status'), button = form.querySelector('button[type=submit]');
  button.disabled = true; status.textContent = C.formulario.enviando;
  fetch('/', {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body:new URLSearchParams(new FormData(form)).toString()})
    .then(r => { if(!r.ok) throw new Error(r.status); form.reset(); status.textContent = C.formulario.enviado; })
    .catch(() => { status.textContent = C.formulario.error; })
    .finally(() => { button.disabled = false; });
});

// Pantalla de carga con el logo: se retira cuando la página y las primeras fotos están listas.
(function () {
  const loader = document.querySelector('#loader');
  if (!loader) return;
  const firstImgs = [...document.querySelectorAll('#proyectos .gallery img.cover')].slice(0, 3);
  const ready = Promise.all(firstImgs.map(i => i.complete ? 0 : new Promise(r => { i.addEventListener('load', r); i.addEventListener('error', r); })));
  const minimum = new Promise(r => setTimeout(r, reducedMotion.matches ? 300 : 1400));
  Promise.race([Promise.all([ready, minimum]), new Promise(r => setTimeout(r, 6000))]).then(() => {
    loader.classList.add('hecho');
    setTimeout(() => loader.remove(), 700);
  });
})();
