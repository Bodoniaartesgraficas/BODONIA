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
  image.src = project.querySelector('img').src;
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
  button.disabled = true; status.textContent = 'Enviando…';
  fetch('/', {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body:new URLSearchParams(new FormData(form)).toString()})
    .then(r => { if(!r.ok) throw new Error(r.status); form.reset(); status.textContent = 'Gracias. Hemos recibido tu mensaje y te responderemos lo antes posible.'; })
    .catch(() => { status.textContent = 'No se ha podido enviar. Escríbenos a info@bodonia.es o llámanos al 648 82 32 50.'; })
    .finally(() => { button.disabled = false; });
});
document.querySelectorAll('[data-legal]').forEach(button=>button.addEventListener('click',()=>{
  const section = document.getElementById(button.dataset.legal);
  document.querySelectorAll('#legal-dialog details').forEach(d=>d.open = d === section);
  section.scrollIntoView({block:'start'});
}));

schedulePhotos();
