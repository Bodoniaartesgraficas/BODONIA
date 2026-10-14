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
    const galleryEl = document.createElement('div');
  galleryEl.className = 'gallery'; galleryEl.tabIndex = 0;
  galleryEl.setAttribute('aria-label', fila.titulo + '. Galería horizontal: usa las flechas para recorrer los trabajos.');
  fila.proyectos.forEach(p => {
    const article = document.createElement('article');
    article.className = 'project'; article.dataset.title = p.titulo; article.dataset.type = p.tipo;
    article.dataset.full = p.completa || p.portada;
    article.dataset.escenas = JSON.stringify([p.portada].concat(p.escenas || [p.detalle, p.completa]).filter(Boolean));
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
  const flecha = (clase, texto) => { const b = document.createElement('button'); b.className = 'fila-flecha ' + clase; b.setAttribute('aria-label', texto); b.innerHTML = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'; return b; };
  section.append(galleryEl, flecha('atras', 'Trabajos anteriores'), flecha('adelante', 'Trabajos siguientes')); filasEl.appendChild(section);
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
  // Flechas a los lados de la fila: avanzan o retroceden tres trabajos.
  const section = gallery.parentElement;
  section.querySelector('.fila-flecha.atras').addEventListener('click', () => { hold = 2.5; dir = -1; step(-3); });
  section.querySelector('.fila-flecha.adelante').addEventListener('click', () => { hold = 2.5; dir = 1; step(3); });
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
// Al pasar el ratón: el trabajo se ensancha, los de al lado se oscurecen y dentro pasan sus escenas en una ventanita.
const puedeHover = window.matchMedia('(hover:hover) and (pointer:fine)');
projects.forEach(project => {
  const escenas = JSON.parse(project.dataset.escenas).slice(1);
  if (!escenas.length) return;
  const caja = document.createElement('span'); caja.className = 'carrusel'; caja.setAttribute('aria-hidden', 'true');
  const img = document.createElement('img'); img.alt = ''; img.draggable = false; caja.appendChild(img);
  project.querySelector('.project-image').appendChild(caja);
  let timer = 0, k = 0;
  project.addEventListener('pointerenter', e => {
    if (e.pointerType !== 'mouse' || !puedeHover.matches || document.querySelector('.gallery.dragging')) return;
    project.classList.add('activo'); project.parentElement.classList.add('con-activo');
    k = 0; img.src = escenas[0];
    clearInterval(timer);
    if (escenas.length > 1 && !reducedMotion.matches) timer = setInterval(() => { k = (k + 1) % escenas.length; img.src = escenas[k]; }, 420);
  });
  project.addEventListener('pointerleave', () => {
    clearInterval(timer); project.classList.remove('activo'); project.parentElement.classList.remove('con-activo');
  });
});

// Puntero con la B de Bodonia sobre las fotos: sigue al ratón con un poco de retraso y se inclina al moverse.
(function () {
  const b = document.querySelector('#cursor-b');
  if (!b || !puedeHover.matches) return;
  let x = -200, y = -200, cx = x, cy = y, dentro = false, frame = 0;
  function pinta() {
    const dx = x - cx; cx += dx * .22; cy += (y - cy) * .22;
    const giro = Math.max(-25, Math.min(25, dx * .6));
    b.style.transform = `translate3d(${cx}px,${cy}px,0) translate(-50%,-50%) rotate(${giro}deg) scale(${dentro ? 1 : .2})`;
    frame = (Math.abs(dx) > .3 || Math.abs(y - cy) > .3 || dentro) ? requestAnimationFrame(pinta) : 0;
  }
  document.addEventListener('pointermove', e => {
    if (e.pointerType !== 'mouse') return;
    x = e.clientX; y = e.clientY;
    const sobre = !!e.target.closest('.gallery .project-image') && !document.querySelector('dialog[open]');
    if (sobre !== dentro) { dentro = sobre; b.classList.toggle('visible', sobre); if (sobre && cx < -100) { cx = x; cy = y; } }
    if (!frame) frame = requestAnimationFrame(pinta);
  }, {passive: true});
  document.addEventListener('pointerleave', () => { dentro = false; b.classList.remove('visible'); });
})();

// Vista de un trabajo: la foto pulsada crece hasta llenar la pantalla y después aparecen sus escenas en fila.
const track = document.querySelector('#project-track');
let origen = null;
function renderProject(index) {
  selected = (index + visible.length) % visible.length;
  const project = visible[selected];
  document.querySelector('#project-title').textContent = project.dataset.title;
  document.querySelector('#project-type').textContent = project.dataset.type;
  track.textContent = '';
  JSON.parse(project.dataset.escenas).forEach((src, i) => {
    const fig = document.createElement('figure'); fig.className = 'escena';
    const img = document.createElement('img'); img.src = src; img.draggable = false;
    img.alt = i ? `${project.dataset.title}: escena ${i + 1}` : project.dataset.title;
    fig.appendChild(img); track.appendChild(fig);
  });
  track.scrollLeft = 0;
}
function rectDe(el) { const r = el.getBoundingClientRect(); return {left:r.left+'px', top:r.top+'px', width:r.width+'px', height:r.height+'px'}; }
function abrirProyecto(project) {
  controls.forEach(c => c.stop());
  document.querySelectorAll('dialog[open]').forEach(d => d.close());
  renderProject(visible.indexOf(project));
  origen = project.querySelector('.cover');
  projectDialog.showModal();
  if (reducedMotion.matches) return;
  const destino = track.querySelector('.escena');
  const clon = document.createElement('img'); clon.className = 'vuelo'; clon.src = origen.src; clon.alt = '';
  projectDialog.appendChild(clon);
  projectDialog.classList.add('volando');
  const desde = rectDe(origen), hasta = rectDe(destino);
  const vuelo = clon.animate([desde, hasta], {duration: 900, easing: 'cubic-bezier(.76,0,.24,1)', fill: 'forwards'});
  vuelo.finished.then(() => { projectDialog.classList.remove('volando'); clon.remove(); });
}
function cerrarProyecto() {
  if (reducedMotion.matches || !origen || !projectDialog.open) return projectDialog.close();
  const primera = track.querySelector('.escena');
  const r = origen.getBoundingClientRect();
  if (track.scrollLeft > 10 || r.bottom < 0 || r.top > innerHeight) return projectDialog.close();
  const clon = document.createElement('img'); clon.className = 'vuelo'; clon.src = primera.querySelector('img').src; clon.alt = '';
  projectDialog.appendChild(clon); projectDialog.classList.add('volando', 'cerrando');
  clon.animate([rectDe(primera), rectDe(origen)], {duration: 700, easing: 'cubic-bezier(.76,0,.24,1)', fill: 'forwards'})
    .finished.then(() => { projectDialog.close(); projectDialog.classList.remove('volando', 'cerrando'); clon.remove(); });
}
projectDialog.querySelector('.close').addEventListener('click', e => { e.stopImmediatePropagation(); cerrarProyecto(); }, true);
projectDialog.addEventListener('cancel', e => { e.preventDefault(); cerrarProyecto(); });
projects.forEach(project=>project.querySelector('button').addEventListener('click',e=>{
  if(dragged && e.detail) { dragged = false; return; }
  abrirProyecto(project);
}));
document.querySelector('#project-prev').addEventListener('click',()=>renderProject(selected-1));
document.querySelector('#project-next').addEventListener('click',()=>renderProject(selected+1));
projectDialog.addEventListener('keydown',e=>{ if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();track.scrollBy({left:(e.key==='ArrowRight'?1:-1)*track.clientWidth*.6,behavior:'smooth'});} });
// Arrastrar las escenas con el ratón
(function(){ let d=null; track.addEventListener('pointerdown',e=>{ if(e.pointerType!=='mouse')return; d={x:e.clientX,s:track.scrollLeft}; track.setPointerCapture(e.pointerId); });
  track.addEventListener('pointermove',e=>{ if(d) track.scrollLeft=d.s-(e.clientX-d.x); });
  track.addEventListener('pointerup',()=>{ d=null; }); track.addEventListener('pointercancel',()=>{ d=null; }); })();

// Tamaño de las fotos: la primera fila llena la pantalla y deja asomar la segunda.
function medir() {
  const g = galleries[0]; if (!g) return;
  const top = g.getBoundingClientRect().top + scrollY;
  const asoma = innerWidth <= 600 ? 0 : Math.max(70, innerHeight * .1);
  document.documentElement.style.setProperty('--alto', Math.max(260, innerHeight - top - asoma - 8) + 'px');
}
medir(); addEventListener('resize', medir);
document.querySelector('#contact-form').addEventListener('submit',e=>{
  e.preventDefault();
  const form = e.currentTarget, status = document.querySelector('#form-status'), button = form.querySelector('button[type=submit]');
  button.disabled = true; status.textContent = C.formulario.enviando;
  fetch('/', {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body:new URLSearchParams(new FormData(form)).toString()})
    .then(r => { if(!r.ok) throw new Error(r.status); form.reset(); status.textContent = C.formulario.enviado; })
    .catch(() => { status.textContent = C.formulario.error; })
    .finally(() => { button.disabled = false; });
});

// Pantalla de carga: el logo, un contador de 000 a 100 y, al terminar, una cortina que sube y descubre las fotos.
(function () {
  const loader = document.querySelector('#loader');
  if (!loader) return;
  const cuenta = loader.querySelector('.loader-cuenta'), barra = loader.querySelector('.loader-barra');
  const imgs = [...document.querySelectorAll('#proyectos img.cover')].slice(0, 3);
  let cargadas = 0;
  imgs.forEach(i => { if (i.complete) cargadas++; else { const ok = () => cargadas++; i.addEventListener('load', ok, {once:true}); i.addEventListener('error', ok, {once:true}); } });
  const inicio = performance.now(), minimo = reducedMotion.matches ? 300 : 2000, maximo = 6000;
  let mostrado = 0;
  document.documentElement.classList.add('cargando');
  function paso(now) {
    const t = now - inicio;
    const real = imgs.length ? cargadas / imgs.length : 1;
    const objetivo = Math.min(t / minimo, t > maximo ? 1 : real, 1);
    mostrado += (objetivo - mostrado) * .2;
    if (objetivo === 1 && 1 - mostrado < .004) mostrado = 1;
    cuenta.textContent = String(Math.round(mostrado * 100)).padStart(3, '0');
    barra.style.transform = `scaleX(${mostrado})`;
    if (mostrado < 1) return requestAnimationFrame(paso);
    setTimeout(() => {
      loader.classList.add('hecho');
      document.documentElement.classList.remove('cargando');
      document.documentElement.classList.add('entra');
      setTimeout(() => { loader.remove(); document.documentElement.classList.remove('entra'); }, 1800);
    }, 120);
  }
  requestAnimationFrame(paso);
})();
