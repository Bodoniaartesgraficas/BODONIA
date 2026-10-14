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
  dt.textContent = s.nombre; dd.textContent = s.detalle; row.append(dt, dd); servicesList.appendChild(row);
});
const galleryEl = document.querySelector('#gallery');
C.proyectos.forEach((p, i) => {
  const article = document.createElement('article');
  article.className = 'project'; article.dataset.title = p.titulo; article.dataset.type = p.tipo;
  article.dataset.full = p.completa || p.portada;
  const button = document.createElement('button');
  button.className = 'project-image'; button.setAttribute('aria-label', 'Abrir ' + p.titulo);
  const cover = document.createElement('img');
  cover.className = 'cover mockup'; cover.src = p.portada; cover.alt = p.titulo + ', ' + p.tipo.toLowerCase(); cover.draggable = false;
  if (p.encuadre) cover.style.objectPosition = p.encuadre;
  if (i < 4) cover.fetchPriority = 'high'; else cover.loading = 'lazy';
  button.appendChild(cover);
  if (p.detalle) {
    const detail = document.createElement('img');
    detail.className = 'alternate detalle'; detail.src = p.detalle; detail.alt = ''; detail.draggable = false; detail.loading = 'lazy';
    detail.setAttribute('aria-hidden', 'true');
    button.appendChild(detail);
  }
  article.appendChild(button); galleryEl.appendChild(article);
});

const gallery = document.querySelector('#gallery');
const projects = [...document.querySelectorAll('.project')];
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let visible = projects;
let selected = 0;
let dragged = false;
let drag = null;
let targetScroll = 0;
let animation = 0;
let paintFrame = 0;
const photoLayers = projects.map(p => ({card:p, image:p.querySelector('.mockup')})).filter(p => p.image);
function updatePhotos() {
  paintFrame = 0;
  const bounds = gallery.getBoundingClientRect();
  photoLayers.forEach(({card,image}) => {
    if (card.hidden) return;
    const rect = card.getBoundingClientRect();
    if (rect.right < bounds.left || rect.left > bounds.right) return;
    const offset = Math.max(-1, Math.min(1, (rect.left + rect.width / 2 - bounds.left - bounds.width / 2) / bounds.width));
    image.style.transform = reducedMotion.matches ? 'none' : `translate3d(${offset * -9}px,0,0) scale(1.045)`;
  });
}
function schedulePhotos() { if (!paintFrame) paintFrame = requestAnimationFrame(updatePhotos); }
const projectDialog = document.querySelector('#project-dialog');

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
function step(direction, smooth) { move(direction * (visible[0].offsetWidth + parseFloat(getComputedStyle(gallery).gap)), smooth); }
gallery.addEventListener('scroll', () => { schedulePhotos(); }, {passive:true});
window.addEventListener('resize', () => { stopMotion(); schedulePhotos(); });
reducedMotion.addEventListener('change', () => { stopMotion(); photoLayers.forEach(({image}) => image.style.transform = 'none'); schedulePhotos(); });
document.querySelector('main').addEventListener('wheel', e => {
  if (document.querySelector('dialog[open]') || e.ctrlKey) return;
  e.preventDefault();
  const delta = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY;
  move(delta * (e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? gallery.clientWidth : 1));
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
document.querySelector('.brand').addEventListener('click',e => { e.preventDefault(); stopMotion(); move(-gallery.scrollLeft, e.detail !== 0); });
function showDialog(dialog) {
  stopMotion();
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

schedulePhotos();
