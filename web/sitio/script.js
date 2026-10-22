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
const piePalabras = document.querySelector('#pie-palabras');
if (piePalabras && C.pie) C.pie.palabras.forEach(t => { const li = document.createElement('li'); li.textContent = t; piePalabras.appendChild(li); });
const filasEl = document.querySelector('#filas');
const galleries = [];
const projects = [];
const clones = [];
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
    if (p.bloques) article.dataset.bloques = JSON.stringify(p.bloques);
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
  // Copias de la fila al final: al llegar a Convento sigue Tortajada (bucle infinito).
  const copias = [...galleryEl.children].map(a => {
    const c = a.cloneNode(true); c.dataset.clon = '1'; c.setAttribute('aria-hidden', 'true');
    c.querySelectorAll('button,img').forEach(x => { x.tabIndex = -1; x.removeAttribute('loading'); });
    galleryEl.appendChild(c); clones.push({copia: c, original: a}); return c;
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
  const cards = [...gallery.querySelectorAll('.project:not([data-clon])')];
  const primeraCopia = () => gallery.querySelector('.project[data-clon]');
  const largo = () => { const c = primeraCopia(); return c ? c.offsetLeft - cards[0].offsetLeft : 0; };
  let pos = 0;
  function vuelta() { const L = largo(); if (L > 0 && gallery.scrollLeft >= L) { gallery.scrollLeft -= L; targetScroll -= L; pos -= L; if (drag) drag.scroll -= L; } }
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
  gallery.addEventListener('scroll', () => { vuelta(); schedulePhotos(); }, {passive:true});
  window.addEventListener('resize', () => { stopMotion(); schedulePhotos(); });
  reducedMotion.addEventListener('change', () => { stopMotion(); photoLayers.forEach(({image}) => image.style.transform = 'none'); schedulePhotos(); });
  // La rueda del ratón baja la página; con Mayús recorre la fila.
  gallery.addEventListener('wheel', e => {
    if (!e.shiftKey || e.ctrlKey || document.querySelector('dialog[open]')) return;
    e.preventDefault();
    move(1.2 * (e.deltaX || e.deltaY) * (e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? gallery.clientWidth : 1));
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
  let dir = 1, last = 0, hold = 0, hovering = false, focused = false;
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
      pos += (largo() > 0 ? 1 : dir) * speed * dt;
      const L = largo();
      if (L > 0) { if (pos >= L) pos -= L; } else if (pos >= max) { pos = max; dir = -1; hold = 1.5; } else if (pos <= 0) { pos = 0; dir = 1; hold = 1.5; }
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
  const abre = document.activeElement;
  dialog.showModal();
  if (abre && abre !== document.body) dialog.addEventListener('close', () => { if (abre.isConnected) abre.focus({preventScroll: true}); }, {once: true});
}
document.querySelectorAll('[data-dialog]').forEach(button=>button.addEventListener('click',()=>showDialog(document.getElementById(button.dataset.dialog))));
document.querySelectorAll('dialog').forEach(dialog=>{
  dialog.querySelector('.close').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',e=>{
    const rect = dialog.getBoundingClientRect();
    if(e.target === dialog && (e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom)) dialog.close();
  });
});
// Al pasar el ratón: el trabajo se ensancha, los de al lado se oscurecen 
const puedeHover = window.matchMedia('(hover:hover) and (pointer:fine)');
projects.forEach(project => {
  const escenas = JSON.parse(project.dataset.escenas).slice(1);
  if (!escenas.length) return;
  project.addEventListener('pointerenter', e => {
    if (e.pointerType !== 'mouse' || !puedeHover.matches || document.querySelector('.gallery.dragging')) return;
    project.classList.add('activo'); project.parentElement.classList.add('con-activo');
  });
  project.addEventListener('pointerleave', () => {
    project.classList.remove('activo'); project.parentElement.classList.remove('con-activo');
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
    b.style.transform = `translate3d(${cx}px,${cy}px,0) translate(-50%,-50%) rotate(${giro}deg) scale(${dentro ? (b.dataset.boton ? 1.25 : 1) : .2})`;
    frame = (Math.abs(dx) > .3 || Math.abs(y - cy) > .3 || dentro) ? requestAnimationFrame(pinta) : 0;
  }
  document.addEventListener('pointermove', e => {
    if (e.pointerType !== 'mouse') return;
    x = e.clientX; y = e.clientY;
    const abierto = document.querySelector('dialog[open]');
    const anfitrion = abierto || document.body;  // dentro de un diálogo la B vive en él, o quedaría tapada
    if (b.parentElement !== anfitrion) anfitrion.appendChild(b);
    const sobre = !e.target.closest('input,textarea,select');  // en los campos de texto vuelve el cursor normal
    const boton = !!e.target.closest('button,a,summary,[role=button]');
    b.dataset.boton = boton ? '1' : '';
    if (sobre !== dentro) { dentro = sobre; b.classList.toggle('visible', sobre); if (sobre && cx < -100) { cx = x; cy = y; } }
    if (!frame) frame = requestAnimationFrame(pinta);
  }, {passive: true});
  document.addEventListener('pointerleave', () => { dentro = false; b.classList.remove('visible'); });
})();

// Vista de un trabajo: la foto pulsada crece hasta llenar la pantalla y después aparecen sus escenas en fila.
const track = document.querySelector('#project-track');
let origen = null;
const movil = matchMedia('(max-width: 600px)');
movil.addEventListener('change', () => { if (projectDialog.open) renderProject(selected); });
function renderProject(index) {
  selected = (index + visible.length) % visible.length;
  const project = visible[selected];
  document.querySelector('#project-title').textContent = project.dataset.title;
  document.querySelector('#project-type').textContent = project.dataset.type;
  track.textContent = '';
  const vertical = movil.matches;  // ordenador: de izquierda a derecha; móvil: hacia abajo
  track.classList.add('mosaico'); track.classList.toggle('vertical', vertical);
  const titulo = project.dataset.title;
  const todas = JSON.parse(project.dataset.escenas);
  const esVideo = src => /\.mp4$/.test(src);
  const fotos = todas.filter(src => !esVideo(src)), videos = todas.filter(esVideo);
  const figura = (src, i) => {
    const fig = document.createElement('figure'); fig.className = 'escena';
    if (esVideo(src)) {  // vídeo: se reproduce solo, mudo y en bucle
      const v = document.createElement('video'); v.src = src;
      v.autoplay = v.loop = v.muted = v.playsInline = true; v.setAttribute('aria-label', `${titulo}: vídeo`);
      fig.appendChild(v); return fig;
    }
    const img = document.createElement('img'); img.src = src; img.draggable = false;
    img.alt = i ? `${titulo}: escena ${i + 1}` : titulo;
    fig.appendChild(img); return fig;
  };
  // Al pasar el ratón el bloque se ensancha un 30% y empuja a los vecinos, como en la portada.
  function crecer(b, track) {
    if (!matchMedia('(hover:hover) and (pointer:fine) and (min-width:601px)').matches) return;
    b.addEventListener('mouseenter', () => {
      const w = b.getBoundingClientRect().width;
      b.style.width = w + 'px'; b.style.setProperty('--w', w + 'px'); b.classList.add('crece'); track.classList.add('con-activo');
      requestAnimationFrame(() => { b.style.width = (w * 1.15) + 'px'; });
      b.dataset.w = w;
    });
    // Dentro de la columna, la imagen bajo el ratón gana alto y las otras se encogen (el bloque siempre cabe en pantalla).
    const celdas = [...b.children];
    if (celdas.length > 1) celdas.forEach((c, k) => c.addEventListener('mouseenter', () => {
      b.style.gridTemplateRows = celdas.map((_, j) => j === k ? '1.5fr' : '1fr').join(' ');
    }));
    b.addEventListener('mouseleave', () => {
      b.style.width = b.dataset.w + 'px'; b.style.gridTemplateRows = ''; track.classList.remove('con-activo');
      setTimeout(() => { if (!b.matches(':hover')) { b.classList.remove('crece'); b.style.width = ''; } }, 460);
    });
  }
  // Mosaico cerrado: cada bloque es un rectángulo completo (1, 2 o 3 fotos), sin huecos ni celdas vacías.
  // El último bloque se ajusta a las fotos que quedan.
  const CICLO = vertical ? [3, 2, 3, 1] : [1, 2, 1, 3];
  const TRES = ['fa', 'fc', 'fd'];
  // Cada libro puede fijar sus columnas (índices de foto); si no, se usa el ciclo.
  const fijos = project.dataset.bloques ? JSON.parse(project.dataset.bloques) : null;
  const orden = fijos ? fijos.flat() : fotos.map((_, k) => k);
  let i = 0, vez = 0, tres = 0;
  while (i < orden.length) {
    const n = fijos ? fijos[vez++].length : Math.min(CICLO[vez++ % CICLO.length], orden.length - i);
    const clase = vertical ? (n === 1 ? 'v1' : n === 2 ? 'v2' : TRES[tres++ % 3]) : 'b' + n;
    const bloque = document.createElement('div'); bloque.className = 'bloque ' + clase;
    for (let k = 0; k < n; k++, i++) bloque.appendChild(figura(fotos[orden[i]], orden[i]));
    track.appendChild(bloque);
    crecer(bloque, track);
  }
  videos.forEach(src => {  // el vídeo va aparte, al final
    const bloque = document.createElement('div'); bloque.className = 'bloque ' + (vertical ? 'fv' : 'b1');
    bloque.appendChild(figura(src, 0)); track.appendChild(bloque);
  });

  track.scrollLeft = 0; track.scrollTop = 0;
  // Escritorio: la primera imagen es, como mínimo, tan ancha como el título (+1 cm) para que el nombre nunca se salga de la portada.
  if (!vertical) {
    const ajusta = () => {
      const primero = track.firstElementChild, tit = document.querySelector('#project-title');
      if (!primero || !tit) return;
      const hace = tit.getBoundingClientRect().width + 28 + 38;
      primero.style.removeProperty('width'); primero.classList.remove('portada-ancha');
      if (primero.getBoundingClientRect().width < hace) { primero.style.width = hace + 'px'; primero.classList.add('portada-ancha'); }
    };
    requestAnimationFrame(ajusta);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(ajusta);
  }
}
function rectDe(el) { const r = el.getBoundingClientRect(); return {left:r.left+'px', top:r.top+'px', width:r.width+'px', height:r.height+'px'}; }
function abrirProyecto(project, copiaOrigen) {
  controls.forEach(c => c.stop());
  document.querySelectorAll('dialog[open]').forEach(d => d.close());
  renderProject(visible.indexOf(project));
  origen = (copiaOrigen || project).querySelector('.cover');
  projectDialog.showModal();
  if (reducedMotion.matches) return;
  const destino = track.querySelector('.escena img');
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
  if (track.scrollLeft > 10 || track.scrollTop > 10 || r.bottom < 0 || r.top > innerHeight) return projectDialog.close();
  const clon = document.createElement('img'); clon.className = 'vuelo'; clon.src = primera.querySelector('img').src; clon.alt = '';
  projectDialog.appendChild(clon); projectDialog.classList.add('volando', 'cerrando');
  clon.animate([rectDe(primera.querySelector('img')), rectDe(origen)], {duration: 700, easing: 'cubic-bezier(.76,0,.24,1)', fill: 'forwards'})
    .finished.then(() => { projectDialog.close(); projectDialog.classList.remove('volando', 'cerrando'); clon.remove(); });
}
clones.forEach(({copia, original}) => {
  const escenas = JSON.parse(original.dataset.escenas).slice(1);
  if (escenas.length) {
    copia.addEventListener('pointerenter', e => { if (e.pointerType !== 'mouse' || !puedeHover.matches || document.querySelector('.gallery.dragging')) return; copia.classList.add('activo'); copia.parentElement.classList.add('con-activo'); });
    copia.addEventListener('pointerleave', () => { copia.classList.remove('activo'); copia.parentElement.classList.remove('con-activo'); });
  }
  copia.querySelector('button').addEventListener('click', e => { if (dragged && e.detail) { dragged = false; return; } abrirProyecto(original, copia); });
});
projectDialog.querySelector('.close').addEventListener('click', e => { e.stopImmediatePropagation(); cerrarProyecto(); }, true);
projectDialog.addEventListener('cancel', e => { e.preventDefault(); cerrarProyecto(); });
projects.forEach(project=>project.querySelector('button').addEventListener('click',e=>{
  if(dragged && e.detail) { dragged = false; return; }
  abrirProyecto(project);
}));
document.querySelector('#project-prev').addEventListener('click',()=>renderProject(selected-1));
document.querySelector('#project-next').addEventListener('click',()=>renderProject(selected+1));
projectDialog.addEventListener('keydown',e=>{ if(e.key==='ArrowRight'||e.key==='ArrowLeft'||e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();const d=(e.key==='ArrowRight'||e.key==='ArrowDown'?1:-1);movil.matches?track.scrollBy({top:d*track.clientHeight*.6,behavior:'smooth'}):track.scrollBy({left:d*track.clientWidth*.6,behavior:'smooth'});} });
// Arrastrar las escenas con el ratón
(function(){ let d=null; track.addEventListener('pointerdown',e=>{ if(e.pointerType!=='mouse')return; d={x:e.clientX,s:track.scrollLeft}; track.setPointerCapture(e.pointerId); });
  track.addEventListener('pointermove',e=>{ if(d) track.scrollLeft=d.s-(e.clientX-d.x); });
  track.addEventListener('pointerup',()=>{ d=null; }); track.addEventListener('pointercancel',()=>{ d=null; }); })();

// Tamaño de las fotos: la fila llena la pantalla.
function medir() {
  const g = galleries[0]; if (!g) return;
  const top = g.getBoundingClientRect().top + scrollY;
  const asoma = 0;
  document.documentElement.style.setProperty('--alto', Math.max(260, innerHeight - top - asoma) + 'px');
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

// Pantalla de carga: las piezas del logo caen una a una (3 s) y, al terminar, una cortina que sube y descubre las fotos.
(function () {
  const loader = document.querySelector('#loader');
  if (!loader) return;
  const imgs = [...document.querySelectorAll('#proyectos img.cover')].slice(0, 3);
  let cargadas = 0;
  imgs.forEach(i => { if (i.complete) cargadas++; else { const ok = () => cargadas++; i.addEventListener('load', ok, {once:true}); i.addEventListener('error', ok, {once:true}); } });
  // La A termina de girar a los 3 s; la pantalla se quita una décima después.
  const inicio = performance.now(), maximo = 6500; let minimo = reducedMotion.matches ? 300 : 2800;
  loader.style.cursor = 'pointer'; loader.addEventListener('click', () => { minimo = Math.min(minimo, Math.max(performance.now() - inicio, 300)); }, {once: true});
  let mostrado = 0;
  document.documentElement.classList.add('cargando');
  function paso(now) {
    const t = now - inicio;
    const real = imgs.length ? cargadas / imgs.length : 1;
    const objetivo = Math.min(t / minimo, t > maximo ? 1 : real, 1);
    mostrado += (objetivo - mostrado) * .2;
    if (objetivo === 1 && 1 - mostrado < .004) mostrado = 1;
    if (mostrado < 1) return requestAnimationFrame(paso);
    setTimeout(() => {
      loader.classList.add('hecho');
      document.documentElement.classList.remove('cargando');
      document.documentElement.classList.add('entra');
      setTimeout(() => { loader.remove(); document.documentElement.classList.remove('entra'); document.dispatchEvent(new Event('portada-lista')); }, 1800);
    }, 120);
  }
  requestAnimationFrame(paso);
})();


// Móvil: la portada avanza sola hacia la izquierda, una foto cada pocos segundos, hasta que la persona la toca.
(function () {
  const movilFront = matchMedia('(max-width: 600px)');
  let activo = false;
  function arranca() {
    const galeria = document.querySelector('.gallery');
    if (activo || !galeria || !movilFront.matches || reducedMotion.matches) return;
    activo = true;
    let tiempo;
    const para = () => { clearInterval(tiempo); ['pointerdown', 'touchstart', 'wheel', 'keydown'].forEach(e => galeria.removeEventListener(e, para)); };
    ['pointerdown', 'touchstart', 'wheel', 'keydown'].forEach(e => galeria.addEventListener(e, para, { passive: true }));
    tiempo = setInterval(() => {
      if (document.hidden || document.querySelector('dialog[open]')) return;
      const fichas = [...galeria.querySelectorAll('.project:not([hidden])')];
      const actual = fichas.findIndex(f => f.offsetLeft >= galeria.scrollLeft - 4);
      const siguiente = fichas[actual + 1];
      const desde = galeria.scrollLeft, hasta = siguiente ? siguiente.offsetLeft : 0, dur = 800, ini = performance.now();
      galeria.style.scrollSnapType = 'none';
      const frame = ahora => {
        const k = Math.min(1, (ahora - ini) / dur), e = 1 - Math.pow(1 - k, 3);  // ease-out suave
        galeria.scrollLeft = desde + (hasta - desde) * e;
        if (k < 1) requestAnimationFrame(frame); else galeria.style.scrollSnapType = '';
      };
      requestAnimationFrame(frame);
    }, 3200);
  }
  document.addEventListener('portada-lista', arranca);
})();

// Versión oscura: el botón de la luna cambia el fondo blanco por negro y lo recuerda.
(function () {
  const b = document.querySelector('.modo-oscuro');
  if (!b) return;
  const pon = on => { document.documentElement.classList.toggle('oscuro', on); b.setAttribute('aria-pressed', on); b.setAttribute('aria-label', on ? 'Versión clara' : 'Versión oscura'); };
  let guardado = null;
  try { guardado = localStorage.getItem('bodonia-oscuro'); } catch (e) {}
  // En el móvil el modo oscuro es el de partida; si la persona lo cambia, se respeta su elección.
  pon(guardado === null ? matchMedia('(max-width: 600px)').matches : guardado === '1');
  b.addEventListener('click', () => { const on = !document.documentElement.classList.contains('oscuro'); pon(on); try { localStorage.setItem('bodonia-oscuro', on ? '1' : '0'); } catch (e) {} });
})();

// Propuesta móvil «ondas» (ahora un mosaico de rectángulos): el logo en el centro y las portadas alrededor.
// Solo se ve en móvil cuando <html> lleva la clase «ondas». Al tocar una onda se abre ese trabajo.
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const caja = document.createElement('div'); caja.id = 'ondas';
  const svg = document.createElementNS(NS, 'svg'); svg.setAttribute('aria-hidden', 'true');
  const logo = document.createElement('div'); logo.className = 'ondas-logo';
  const h1 = document.querySelector('.intro .logo');
  if (h1) { const c = h1.cloneNode(true); c.removeAttribute('id'); logo.appendChild(c); }
  const menu = document.createElement('nav'); menu.className = 'ondas-menu';
  [['Nosotros', 'about-dialog'], ['De la idea al papel', 'services-dialog'], ['Contacto', 'contact-dialog']].forEach(([t, id]) => {
    const b = document.createElement('button'); b.type = 'button'; b.textContent = t;
    b.addEventListener('click', () => document.querySelector('.site-header [data-dialog="' + id + '"]').click());
    menu.appendChild(b);
  });
  const ig = document.createElement('a'); ig.href = 'https://www.instagram.com/bodonia.artesgraficas/'; ig.target = '_blank'; ig.rel = 'noopener'; ig.className = 'ondas-ig'; ig.setAttribute('aria-label', 'Instagram de Bodonia'); ig.innerHTML = '<img src="' + (document.querySelector('.instagram-flotante img')?.getAttribute('src') || 'fotos/instagram.svg') + '" alt="">';
  menu.appendChild(ig);
  caja.append(svg, logo, menu); document.body.appendChild(caja);

  // Mosaico de seis rectángulos que llenan la pantalla (x0, y0, x1, y1 en tanto por uno) y el trabajo que va en cada uno.
  // Hay horizontales y verticales de tamaños parecidos; el logo queda en el cruce del centro.
  const MOSAICO = [
    [[0, 0, 1, .25], 1],       // Territorios, horizontal arriba
    [[0, .25, .52, .5], 0],    // Tortajada
    [[.52, .25, 1, .5], 5],    // Coín
    [[0, .5, .56, .75], 2],    // Santa Fe, horizontal
    [[0, .75, .56, 1], 4],     // Noir, horizontal
    [[.56, .5, 1, 1], 3],      // Primitivismo, vertical alto
  ];
  // Dónde está el libro dentro de cada foto de portada (x0, y0, x1, y1 en tanto por uno), en el orden de contenido.js.
  const LIBRO = [[.17, .22, .87, .82], [.10, .30, .87, .80], [.24, .37, .62, .68], [.20, .23, .83, .93], [.13, .25, .85, .75], [.18, .18, .98, .92]];
  const tamano = {};
  projects.forEach((art, k) => { const im = new Image(); im.onload = () => { tamano[k] = [im.naturalWidth, im.naturalHeight]; dibuja(); }; im.src = art.querySelector('img.cover').getAttribute('src'); });
  const dibuja = () => {
    const W = caja.clientWidth, H = caja.clientHeight;
    if (!W || !H) return;
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.innerHTML = '';
    const defs = document.createElementNS(NS, 'defs'); svg.appendChild(defs);
    const abajo = H - (menu.offsetHeight || 0), G = 1.5; // medio grosor de la línea blanca entre fotos
    MOSAICO.forEach(([[u0, v0, u1, v1], k]) => {
      const art = projects[k]; if (!art) return;
      const x0 = u0 * W + (u0 > 0 ? G : 0), y0 = v0 * H + (v0 > 0 ? G : 0), x1 = u1 * W - (u1 < 1 ? G : 0), y1 = v1 * H - (v1 < 1 ? G : 0);
      const cp = document.createElementNS(NS, 'clipPath'); cp.id = 'tesela-' + k;
      const r = document.createElementNS(NS, 'rect'); r.setAttribute('x', x0); r.setAttribute('y', y0); r.setAttribute('width', x1 - x0); r.setAttribute('height', y1 - y0);
      cp.appendChild(r); defs.appendChild(cp);
      // El libro va centrado en la parte que se ve (sin la franja de los botones) y la foto cubre todo el rectángulo.
      const vy1 = Math.min(y1, abajo), mx = (x0 + x1) / 2, my = (y0 + vy1) / 2, tw = x1 - x0, th = vy1 - y0;
      const [iw, ih] = tamano[k] || [1200, 1500], [bx0, by0, bx1, by1] = LIBRO[k] || [.2, .2, .8, .8];
      const bw = (bx1 - bx0) * iw, bh = (by1 - by0) * ih, ncx = (bx0 + bx1) / 2, ncy = (by0 + by1) / 2;
      // desplazamiento posible del libro en un eje para la escala t (hasta un 10 % de su tamaño), o null si no cubre
      const holgura = (m, a0, a1, n, tam, lado, t) => {
        const lo = a1 - m - (1 - n) * tam * t, hi = n * tam * t - (m - a0), lim = .1 * lado * t;
        const d0 = Math.max(lo, -lim), d1 = Math.min(hi, lim);
        return d0 <= d1 ? (d0 <= 0 && d1 >= 0 ? 0 : (Math.abs(d0) < Math.abs(d1) ? d0 : d1)) : null;
      };
      let sc = Math.min(tw * .9 / bw, th * .9 / bh), dx = null, dy = null;
      for (let it = 0; it < 80; it++) {
        dx = holgura(mx, x0, x1, ncx, iw, bw, sc); dy = holgura(my, y0, y1, ncy, ih, bh, sc);
        if (dx !== null && dy !== null) break;
        sc *= 1.03;
      }
      const g = document.createElementNS(NS, 'g'); g.setAttribute('class', 'onda'); g.setAttribute('clip-path', `url(#tesela-${k})`);
      const img = document.createElementNS(NS, 'image');
      img.setAttribute('href', art.querySelector('img.cover').getAttribute('src'));
      img.setAttribute('preserveAspectRatio', 'none');
      img.setAttribute('x', (mx + (dx || 0) - ncx * iw * sc).toFixed(1)); img.setAttribute('y', (my + (dy || 0) - ncy * ih * sc).toFixed(1));
      img.setAttribute('width', (iw * sc).toFixed(1)); img.setAttribute('height', (ih * sc).toFixed(1));
      g.append(img); svg.appendChild(g);
      g.addEventListener('click', () => art.querySelector('button').click());
    });
    logo.style.top = H / 2 + 'px';
  };
  new ResizeObserver(dibuja).observe(caja); dibuja();
})();

// Flechas dentro del trabajo (ordenador): pasan a la imagen anterior o siguiente sin tener que hacer scroll.
(function () {
  const svg = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
  const haz = (clase, texto, dir) => {
    const b = document.createElement('button'); b.type = 'button'; b.className = 'escena-flecha ' + clase; b.setAttribute('aria-label', texto); b.innerHTML = svg;
    b.addEventListener('click', () => {
      const bloques = [...track.children], x = track.scrollLeft, tope = track.scrollWidth - track.clientWidth;
      const izq = el => el.offsetLeft - bloques[0].offsetLeft;
      let destino = dir > 0 ? bloques.map(izq).find(l => l > x + 4) : bloques.map(izq).reverse().find(l => l < x - 4);
      if (destino === undefined) destino = dir > 0 ? tope : 0;
      track.scrollTo({left: Math.min(destino, tope), behavior: reducedMotion.matches ? 'auto' : 'smooth'});
    });
    projectDialog.appendChild(b); return b;
  };
  const atras = haz('atras', 'Imagen anterior', -1), adelante = haz('adelante', 'Imagen siguiente', 1);
  const estado = () => { const tope = track.scrollWidth - track.clientWidth; atras.disabled = track.scrollLeft < 4; adelante.disabled = track.scrollLeft > tope - 4; };
  let quieto;
  const mueve = () => { projectDialog.classList.add('moviendo'); clearTimeout(quieto); quieto = setTimeout(() => projectDialog.classList.remove('moviendo'), 1800); };
  projectDialog.addEventListener('pointermove', mueve); track.addEventListener('wheel', mueve, {passive: true});
  track.addEventListener('scroll', estado, {passive: true});
  new MutationObserver(() => requestAnimationFrame(estado)).observe(track, {childList: true});
})();

// Ordenador: dentro de un trabajo, al acercar el ratón a un borde las imágenes se deslizan solas hacia ese lado.
(function () {
  if (!matchMedia('(hover:hover) and (pointer:fine)').matches) return;
  const ZONA = 160, MAX = 300;  // px desde el borde; velocidad máxima en px/s
  let v = 0, last = 0, frame = 0, pos = 0;
  function mueve(now) {
    const dt = Math.min(now - (last || now), 50) / 1000; last = now;
    if (!v || !projectDialog.open || movil.matches) { frame = 0; last = 0; track.style.removeProperty('scroll-snap-type'); track.style.removeProperty('scroll-behavior'); return; }
    if (!last || dt === 0) { track.style.scrollSnapType = 'none'; track.style.scrollBehavior = 'auto'; pos = track.scrollLeft; }  // el ajuste a imágenes frenaría el deslizamiento
    pos = Math.max(0, Math.min(track.scrollWidth - track.clientWidth, pos + v * dt)); track.scrollLeft = pos;
    frame = requestAnimationFrame(mueve);
  }
  projectDialog.addEventListener('pointermove', e => {
    if (e.pointerType !== 'mouse' || reducedMotion.matches) return;
    const r = track.getBoundingClientRect();
    const izq = e.clientX - r.left, der = r.right - e.clientX;
    v = izq < ZONA ? -MAX * (1 - izq / ZONA) ** 2 : der < ZONA ? MAX * (1 - der / ZONA) ** 2 : 0;
    if (v && !frame) frame = requestAnimationFrame(mueve);
  });
  projectDialog.addEventListener('pointerleave', () => { v = 0; });
  projectDialog.addEventListener('close', () => { v = 0; });
})();
