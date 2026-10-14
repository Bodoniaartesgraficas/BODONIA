"""Exporta el prototipo daigual (futuros-proyectos/daigual/) a una web estática para Netlify en web/sitio/.

Uso: python3 web/scripts/exportar_daigual.py <raíz del repo> <carpeta de @fontsource-variable/dm-sans/files>

Diseño sin cambios. Lo que añade: fuentes alojadas en la propia web, mockups en JPEG (los PNG pesaban 2-3 MB),
formulario con Netlify Forms, ventana de información legal (textos de la versión Inicio, ya corregidos),
título y datos para Google y redes, favicon, gracias.html, 404.html, robots.txt, sitemap.xml y netlify.toml.
"""
import re, shutil, sys
from pathlib import Path
from PIL import Image
from fontTools.ttLib import TTFont

REPO = Path(sys.argv[1])
DMSANS = Path(sys.argv[2])
SRC = REPO / "futuros-proyectos/daigual"
OUT = REPO / "web/sitio"
BODONI = REPO / "redes-sociales/instagram/POST BANQUILLO/Fuente_Bodoni_Moda"
LEGAL_SRC = REPO / "web/rediseno/web-canvas/project/Main.dc.html"

html = (SRC / "index.html").read_text(encoding="utf-8")
css = (SRC / "styles.css").read_text(encoding="utf-8")
js = (SRC / "script.js").read_text(encoding="utf-8")

if OUT.exists():
    shutil.rmtree(OUT)
for sub in ("assets", "fonts"):
    (OUT / sub).mkdir(parents=True)

# --- imágenes: solo las que usa la página; mockups PNG (sin transparencia) -> JPEG ---
used = sorted(set(re.findall(r'src="(assets/[^"]+)"', html)))
for rel in used:
    src = SRC / rel
    if src.suffix == ".png" and rel.startswith("assets/mockup-"):
        new = rel[:-4] + ".jpg"
        Image.open(src).convert("RGB").save(OUT / new, quality=88, optimize=True, progressive=True)
        html = html.replace(f'"{rel}"', f'"{new}"')
    else:
        shutil.copyfile(src, OUT / rel)

# --- fuentes alojadas en la web (sin Google Fonts) ---
for name, out in (("BodoniModa[opsz,wght].ttf", "bodoni-moda.woff2"),):
    f = TTFont(BODONI / name)
    f.flavor = "woff2"
    f.save(OUT / "fonts" / out)
shutil.copyfile(BODONI / "OFL.txt", OUT / "fonts/OFL-bodoni-moda.txt")
shutil.copyfile(DMSANS / "dm-sans-latin-opsz-normal.woff2", OUT / "fonts/dm-sans.woff2")
shutil.copyfile(DMSANS.parent / "LICENSE", OUT / "fonts/OFL-dm-sans.txt")

html = re.sub(r'<link rel="preconnect"[^>]*>', "", html)
html = re.sub(r'<link href="https://fonts\.googleapis\.com[^>]*>', "", html)
assert "googleapis" not in html and "gstatic" not in html

FONTS_CSS = """@font-face{font-family:'Bodoni Moda';src:url(fonts/bodoni-moda.woff2) format('woff2');font-weight:400 900;font-style:normal;font-display:swap}
@font-face{font-family:'DM Sans';src:url(fonts/dm-sans.woff2) format('woff2');font-weight:100 1000;font-style:normal;font-display:swap}
"""
LEGAL_CSS = """
/* Información legal y formulario (añadido para publicar) */
.legal-links{display:flex;flex-wrap:wrap;gap:4px 16px;margin-top:20px;font-size:12px;color:var(--muted)}
.legal-links button{color:inherit;text-decoration:underline;text-underline-offset:3px;padding:6px 0}
form small button{color:inherit;text-decoration:underline;text-underline-offset:3px;font-size:inherit}
.form-status{color:var(--red);font-size:13px;line-height:1.6;margin:0}.form-status:empty{display:none}
.legal{border-top:1px solid var(--line)}.legal:last-child{border-bottom:1px solid var(--line)}
.legal summary{cursor:pointer;font:400 23px/1.3 var(--serif);padding:18px 0;list-style-position:inside}
.legal-b{display:flex;flex-direction:column;gap:12px;font-size:14px;line-height:1.7;color:var(--muted);max-width:70ch;padding:0 0 28px}
.legal-b p{margin:0}.legal-b .legal-h{color:var(--ink);font-weight:500}
@media(hover:hover) and (pointer:fine){.legal-links button:hover,form small button:hover{color:var(--red)}}
"""
(OUT / "styles.css").write_text(FONTS_CSS + css.rstrip() + "\n" + LEGAL_CSS, encoding="utf-8")

# --- <head> ---
HEAD_EXTRA = """<link rel="canonical" href="https://bodonia.es/">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" href="/favicon.png" type="image/png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website"><meta property="og:locale" content="es_ES"><meta property="og:site_name" content="Bodonia Artes Gráficas">
<meta property="og:title" content="Bodonia Artes Gráficas · Diseño, maquetación e impresión"><meta property="og:description" content="Más de 35 años dando forma a tus ideas. Diseño, maquetación e impresión offset y digital en La Zubia, Granada.">
<meta property="og:url" content="https://bodonia.es/"><meta property="og:image" content="https://bodonia.es/assets/compartir.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="/fonts/bodoni-moda.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="/fonts/dm-sans.woff2" as="font" type="font/woff2" crossorigin>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"LocalBusiness","name":"Bodonia Artes Gráficas S.L.","url":"https://bodonia.es/","image":"https://bodonia.es/assets/compartir.jpg","logo":"https://bodonia.es/assets/bodonia-logo.png","telephone":"+34648823250","email":"info@bodonia.es","address":{"@type":"PostalAddress","streetAddress":"C/ Gredos nº 27","postalCode":"18140","addressLocality":"La Zubia","addressRegion":"Granada","addressCountry":"ES"},"geo":{"@type":"GeoCoordinates","latitude":37.10948,"longitude":-3.591575},"openingHours":"Mo-Fr 09:00-20:00"}</script>
"""
html = html.replace('<link rel="stylesheet" href="styles.css">', HEAD_EXTRA + '<link rel="stylesheet" href="styles.css">')
html = html.replace("<title>Bodonia — Artes Gráficas</title>", "<title>Bodonia Artes Gráficas · Imprenta en La Zubia, Granada</title>")

# --- formulario: Netlify Forms en lugar de mailto ---
old = '<form id="contact-form">'
assert old in html
html = html.replace(old,
    '<form id="contact-form" name="contacto" method="POST" action="/gracias.html" data-netlify="true" netlify-honeypot="bot-field">'
    '<input type="hidden" name="form-name" value="contacto"><p hidden><label>No rellenar: <input name="bot-field"></label></p>')
old = '<button class="text-link" type="submit">Preparar correo</button><small>Se abrirá tu aplicación de correo con el mensaje preparado.</small></form>'
assert old in html
html = html.replace(old,
    '<button class="text-link" type="submit">Enviar</button>'
    '<p class="form-status" id="form-status" role="status" aria-live="polite"></p>'
    '<small>Usaremos tus datos solo para responderte. Más información en la '
    '<button type="button" data-dialog="legal-dialog" data-legal="politica-de-privacidad">política de privacidad</button>.</small></form>')

# enlaces legales al pie de los datos de contacto
old = 'rel="noreferrer">Ver en el mapa</a></div>'
assert old in html
html = html.replace(old, 'rel="noreferrer">Ver en el mapa</a>'
    '<nav class="legal-links" aria-label="Información legal">'
    '<button type="button" data-dialog="legal-dialog" data-legal="aviso-legal">Aviso legal</button>'
    '<button type="button" data-dialog="legal-dialog" data-legal="politica-de-privacidad">Privacidad</button>'
    '<button type="button" data-dialog="legal-dialog" data-legal="politica-de-cookies">Cookies</button>'
    '</nav></div>')

# --- textos legales: los de la web anterior, corregidos (bodonia.es, sin cookies, formulario y Netlify) ---
legal = LEGAL_SRC.read_text(encoding="utf-8")
blocks = re.findall(r'<details id="[^"]+" class="legal">.*?</details>', legal, re.S)
assert len(blocks) == 4
legal = "\n".join(blocks)
legal = legal.replace("La Entidad titular del website http://www.bodoniaartesgraficas.wordpress.com es",
                      "La Entidad titular del sitio web https://bodonia.es es")
legal = legal.replace("Ser usuario de la web bodoniaartesgraficas.wordpress.com,", "Ser usuario de la web bodonia.es,")
legal = legal.replace("PROTECCIÓN DE LA INFORMACIÓN Y CONTENIDOS DE bodoniaartesgraficas.wordpress.com.",
                      "PROTECCIÓN DE LA INFORMACIÓN Y CONTENIDOS DE bodonia.es.")
legal = re.sub(r'<p style="margin: 0">A\.- BODONIA ARTES GRAFICAS, S\.L\. utiliza cookies.*?</p>',
    '<p style="margin: 0">A.- Este sitio web no utiliza cookies propias ni de terceros. Cuando el usuario visita la web, '
    "el servidor donde está alojada recibe automáticamente la dirección IP de su ordenador, el día y la hora de la visita y "
    "las páginas consultadas. Es necesario que el servidor conozca estos datos para poder comunicarse y mostrar en el "
    "navegador la página solicitada. No se elaboran perfiles en ningún caso.</p>", legal, flags=re.S)
FORM_PRIV = (
    '<p class="legal-h">Formulario de contacto:</p>\n'
    "<p>Los datos que nos envía a través del formulario (nombre, correo electrónico y mensaje) se usan únicamente para "
    "responder a su consulta y, en su caso, preparar el presupuesto o el trabajo solicitado. La base legal es su "
    "consentimiento al enviar el formulario. Se conservan mientras sea necesario para atender la consulta y durante los "
    "plazos que exija la ley.</p>\n"
    "<p>La web está alojada en Netlify, Inc., que actúa como encargado del tratamiento y recibe los datos del formulario para "
    "hacérnoslos llegar. Netlify tiene su sede en Estados Unidos y está adherida al Marco de Privacidad de Datos UE-EE. UU., "
    "que garantiza un nivel de protección adecuado para esta transferencia internacional.</p>\n")
NO_TRANSFER = "y no están previstas las transferencias internacionales de datos.</p>"
assert legal.count(NO_TRANSFER) == 2
legal = legal.replace(NO_TRANSFER, "salvo la indicada más abajo para el formulario de contacto.</p>")
DPD = '<p style="margin: 0; font-weight: 600; color: #000000">Delegado de Protección de Datos:</p>\n<p style="margin: 0">Datasur'
parts = legal.split(DPD)
assert len(parts) == 4
legal = parts[0] + DPD + parts[1] + FORM_PRIV + DPD + parts[2] + FORM_PRIV + DPD + parts[3]
COOKIES = (
    '<details id="politica-de-cookies" class="legal"><summary>Política de cookies</summary><div class="legal-b">'
    '<p class="legal-h">COOKIES</p>\n'
    "<p>Se denomina cookie a un pequeño archivo que una web guarda en el navegador del usuario para recordar información "
    "sobre su visita.</p>\n"
    "<p>El sitio web bodonia.es no utiliza cookies: ni propias ni de terceros, ni técnicas, de análisis, de personalización "
    "o publicitarias. Tampoco usa herramientas de estadística ni de seguimiento, y las tipografías y las imágenes se sirven "
    "desde el propio sitio, sin conectar con servicios externos.</p>\n"
    "<p>Por eso no le pedimos consentimiento para instalar cookies. Si en el futuro incorporáramos alguna, actualizaríamos "
    "esta política y le pediríamos su consentimiento antes de instalarla, cuando la ley lo exija.</p>\n"
    "<p>Puede configurar su navegador para bloquear o borrar cookies en cualquier momento desde sus opciones de "
    "privacidad.</p></div></details>")
legal = re.sub(r'<details id="politica-de-cookies".*?</details>', lambda m: COOKIES, legal, flags=re.S)
legal = legal.replace('<p style="margin: 0; font-weight: 600; color: #000000">', '<p class="legal-h">')
legal = legal.replace('<p style="margin: 0">', "<p>")
legal = re.sub(r"<p>\s+", "<p>", legal)
assert "style=" not in legal and "wordpress" not in legal.lower() and "GED_PLAYLIST" not in legal

CLOSE = '<button class="close" aria-label="Cerrar"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m6 6 12 12M6 18 18 6"/></svg></button>'
LEGAL_DIALOG = (f'<dialog id="legal-dialog" class="text-dialog" aria-labelledby="legal-dialog-title">{CLOSE}'
                '<div class="dialog-content"><h2 id="legal-dialog-title">Información legal.</h2>'
                f'<section aria-label="Textos legales">{legal}</section></div></dialog>')
html = html.replace('<dialog class="project-dialog"', LEGAL_DIALOG + '<dialog class="project-dialog"', 1)

# --- script: envío del formulario y apertura de la sección legal pedida ---
old_submit = re.search(r"document\.querySelector\('#contact-form'\)\.addEventListener\('submit'.*?\n\}\);\n", js, re.S).group(0)
js = js.replace(old_submit, """document.querySelector('#contact-form').addEventListener('submit',e=>{
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
""")
assert "mailto:info@bodonia.es?subject" not in js
(OUT / "script.js").write_text(js, encoding="utf-8")
(OUT / "index.html").write_text(html, encoding="utf-8")

# --- favicon e imagen para compartir ---
perfil = Image.open(REPO / "redes-sociales/instagram/LOGOS/bodonia_perfil_rojo.png").convert("RGB")
perfil.resize((180, 180), Image.LANCZOS).save(OUT / "apple-touch-icon.png")
perfil.resize((32, 32), Image.LANCZOS).save(OUT / "favicon.png")
perfil.save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
portada = Image.open(REPO / "web/rediseno/fb/portada-facebook-bodonia-artes-graficas.jpg").convert("RGB")
w, h = portada.size
cw = int(h * 1200 / 630); x0 = (w - cw) // 2
portada.crop((x0, 0, x0 + cw, h)).resize((1200, 630), Image.LANCZOS).save(OUT / "assets/compartir.jpg", quality=86)

# --- páginas de gracias y 404, con la misma cabecera e introducción ---
head = html.split("<body>")[0].replace('<link rel="canonical" href="https://bodonia.es/">', '<meta name="robots" content="noindex">')
HEADER = ('<header class="site-header"><a class="brand" href="/" aria-label="Bodonia, inicio">'
          '<img src="assets/bodonia-logo.png" alt="Bodonia Artes Gráficas" width="148" height="52"></a>'
          '<nav aria-label="Principal"><button class="contact-chip" onclick="location.href=\'/\'">Volver al inicio</button></nav></header>')
def simple(title, h1, p):
    return (head.replace(re.search(r"<title>.*?</title>", head).group(0), f"<title>{title}</title>")
            + f'<body>{HEADER}<main><section class="intro"><h1>{h1}</h1><p>{p}</p></section></main></body></html>\n')
(OUT / "gracias.html").write_text(simple("Gracias · Bodonia Artes Gráficas", "Gracias. Hemos recibido tu mensaje.",
    'Te responderemos lo antes posible. Si es urgente, llámanos al <a href="tel:+34648823250">648 82 32 50</a> '
    'o escríbenos a <a href="mailto:info@bodonia.es">info@bodonia.es</a>.'), encoding="utf-8")
(OUT / "404.html").write_text(simple("Página no encontrada · Bodonia Artes Gráficas", "Esta página no existe.",
    'Puede que el enlace haya cambiado. Vuelve al <a href="/">inicio</a> o escríbenos a '
    '<a href="mailto:info@bodonia.es">info@bodonia.es</a>.'), encoding="utf-8")

(OUT / "robots.txt").write_text("User-agent: *\nAllow: /\n\nSitemap: https://bodonia.es/sitemap.xml\n")
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>https://bodonia.es/</loc></url>\n</urlset>\n')
(OUT / "netlify.toml").write_text("""[build]
  publish = "."

# www.bodonia.es redirige a https://bodonia.es
[[redirects]]
  from = "https://www.bodonia.es/*"
  to = "https://bodonia.es/:splat"
  status = 301
  force = true

[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    X-Frame-Options = "SAMEORIGIN"

[[headers]]
  for = "/fonts/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=604800"
""")
print("ok", sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file()) // 1024, "KB")
