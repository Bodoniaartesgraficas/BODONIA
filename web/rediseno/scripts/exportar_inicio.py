"""Exporta el tablero Inicio (Main.dc.html) a una web estática para Netlify en web/sitio-inicio/ (alternativa; la web elegida es daigual).

Uso: python3 web/rediseno/scripts/exportar_inicio.py <raíz del repo> <vídeo de Territorios de la mirada>
El vídeo es el asset 053a625835bd636e747914353249fd24 del artifact del rediseño (1,8 MB)."""
import re, shutil, sys
from pathlib import Path
from PIL import Image
from fontTools.ttLib import TTFont

REPO = Path(sys.argv[1])
VIDEO_TERRITORIOS = Path(sys.argv[2])
SRC = REPO / "web/rediseno/web-canvas/project/Main.dc.html"
OUT = REPO / "web/sitio-inicio"  # la web publicada es daigual (web/sitio/)
A = REPO / "web/rediseno/assets"
FONTS = REPO / "redes-sociales/instagram/POST BANQUILLO/Fuente_Bodoni_Moda"

# blob del tablero -> archivo del repositorio (mismo sha256)
BLOBS = {
    "0b2d9e7a5215291be84e7cc8fb5d8b90": (A / "logo-bodonia-transparente.png", "img/logo-bodonia-artes-graficas.png"),
    "7980c1d359736909d39bd790a3e03542": (A / "cat-la-tortajada.jpg", "img/la-tortajada.jpg"),
    "74027d664552864d1ad8fb3d429d92f8": (A / "cat-santa-maria-coin.jpg", "img/santa-maria-de-coin.jpg"),
    "de82459fa029a805a13e2551bc980577": (A / "cat-territorios-mirada.jpg", "img/territorios-de-la-mirada.jpg"),
    "812eacbe68f1f60863baf6dcf88e89bf": (A / "cat-arte-africano.jpg", "img/primitivismo-y-modernidad.jpg"),
    "cbb76f15537c2d3ea7c6f03edfb4fa9c": (A / "mauthausen-nuevo.jpg", "img/santa-fe-mauthausen.jpg"),
    "f2bedf7d636a74e98e6965840a866ee9": (A / "cat-pedro-zamora-en-noir.jpg", "img/pedro-zamora-en-noir.jpg"),
    "fcbc30758957f5d55498d7b0ab53fbee": (A / "cat-yauco-5x3.jpg", "img/yauco.jpg"),
    "0f95cbc661a90ad79ecc9f4f119739e3": (REPO / "web/mockups-finalizados/mockup_pedro_zamora_en_noir.mp4", "video/pedro-zamora-en-noir.mp4"),
    "053a625835bd636e747914353249fd24": (VIDEO_TERRITORIOS, "video/territorios-de-la-mirada.mp4"),
    "87c6c761f0f882f194cec5160a4518b6": (A / "otros-revista-rdg.jpg", "img/revista-rdg.jpg"),
    "deb397ed1eff495d7d5ba4548b4ad86a": (A / "otros-revista-pequeno-oso.jpg", "img/pequeno-oso.jpg"),
    "27a7f2ba1c78da000d01343396c4ee65": (A / "otros-diptico-en-torno-santa-fe.jpg", "img/diptico-en-torno-a-santa-fe.jpg"),
    "f4a4a5ee3b19a1ba434575dc5a163839": (A / "otros-diptico-pedro-zamora.jpg", "img/diptico-pedro-zamora.jpg"),
    "0c66cc5d7fbbc84f9b2f9e816670aeb5": (A / "otros-cartel-capitulaciones.jpg", "img/cartel-capitulaciones-santa-fe.jpg"),
    "99ce3c0d8e2037c351b3327cda59e5a8": (A / "otros-cartel-festival-literatura.jpg", "img/cartel-festival-literatura-historica.jpg"),
    "2c8c1de360492203dec13225c595e87b": (A / "otros-haiku.jpg", "img/haiku-pliegos-del-azul.jpg"),
    "c6612999e242f4bda8c144224c56f977": (A / "calendario-bodonia-v3.jpg", "img/calendario-bodonia.jpg"),
    "4eb05b26b9d57c238c57a302781f7dbd": (A / "otros-tarjetas-besa.jpg", "img/tarjetas-besa.jpg"),
    "8a51ca2a34f6c0a3d4b415c9b6b9bc5b": (A / "sobre-nuevo.jpg", "img/sobre-bodonia.jpg"),
}

src = SRC.read_text(encoding="utf-8")
css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
body = re.search(r"</helmet>\n(.*?)\n</x-dc>", src, re.S).group(1)

# --- archivos ---
if OUT.exists():
    shutil.rmtree(OUT)
for sub in ("img", "video", "fonts"):
    (OUT / sub).mkdir(parents=True)
for blob, (path, dest) in BLOBS.items():
    shutil.copyfile(path, OUT / dest)
    body = body.replace(f"/_blob/{blob}", dest)
assert "/_blob/" not in body, "quedan blobs sin resolver"

for name, out in (("BodoniModa[opsz,wght].ttf", "bodoni-moda.woff2"), ("BodoniModa-Italic[opsz,wght].ttf", "bodoni-moda-italic.woff2")):
    f = TTFont(FONTS / name)
    f.flavor = "woff2"
    f.save(OUT / "fonts" / out)
shutil.copyfile(FONTS / "OFL.txt", OUT / "fonts/OFL.txt")

# favicon e imagen para compartir
perfil = Image.open(REPO / "redes-sociales/instagram/LOGOS/bodonia_perfil_rojo.png").convert("RGB")
perfil.resize((180, 180), Image.LANCZOS).save(OUT / "apple-touch-icon.png")
perfil.resize((32, 32), Image.LANCZOS).save(OUT / "favicon.png")
perfil.save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
portada = Image.open(REPO / "web/rediseno/fb/portada-facebook-bodonia-artes-graficas.jpg").convert("RGB")
w, h = portada.size  # 3280x1440 -> recorte centrado 1.905:1
cw = int(h * 1200 / 630)
x0 = (w - cw) // 2
portada.crop((x0, 0, x0 + cw, h)).resize((1200, 630), Image.LANCZOS).save(OUT / "img/compartir.jpg", quality=86)

# --- cuerpo ---
# alturas y anchos fijos del lienzo del editor: en una web real cortarían o dejarían huecos
for prop in (" height: 3364px", " height: 2621px", " height: 785px", " height: 86px", " height: 663px"):
    body = body.replace(";" + prop, "")
body = body.replace("; width: 1252px; height: 97px", "")

# imágenes y vídeos fuera de la primera pantalla: carga diferida
body = body.replace('<img class="shot"', '<img class="shot" loading="lazy" decoding="async"')
body = body.replace('<video class="shot"', '<video class="shot" preload="metadata"')

# formulario: Netlify Forms en lugar de mailto
old_form_open = re.search(r'<form class="rojo" onSubmit="\{\{ send \}\}"', body).group(0)
body = body.replace(old_form_open,
    '<form class="rojo" id="pide-informacion" name="pide-informacion" method="POST" action="/gracias.html" '
    'enctype="multipart/form-data" data-netlify="true" netlify-honeypot="bot-field"')
body = body.replace(
    '<p style="margin: 0; font-size: 26px; font-weight: 500; letter-spacing: -.01em; text-align: center">Pide información</p>',
    '<p style="margin: 0; font-size: 26px; font-weight: 500; letter-spacing: -.01em; text-align: center">Pide información</p>\n'
    '<input type="hidden" name="form-name" value="pide-informacion">\n'
    '<p hidden><label>No rellenar: <input name="bot-field"></label></p>')
body = body.replace(">Enviar correo</button>", ">Enviar</button>")
body, n = re.subn(r'<sc-if value="\{\{ sent \}\}"[^>]*><p style="([^"]*)">.*?</p></sc-if>',
                  r'<p style="\1" id="aviso-formulario" role="status" aria-live="polite"></p>', body)
assert n == 1

# --- textos legales ---
body = body.replace("La Entidad titular del website http://www.bodoniaartesgraficas.wordpress.com es",
                    "La Entidad titular del sitio web https://bodonia.es es")
body = body.replace("Ser usuario de la web bodoniaartesgraficas.wordpress.com,", "Ser usuario de la web bodonia.es,")
body = body.replace("PROTECCIÓN DE LA INFORMACIÓN Y CONTENIDOS DE bodoniaartesgraficas.wordpress.com.",
                    "PROTECCIÓN DE LA INFORMACIÓN Y CONTENIDOS DE bodonia.es.")
assert "wordpress" not in body.lower()

body = re.sub(r"<p style=\"margin: 0\">A\.- BODONIA ARTES GRAFICAS, S\.L\. utiliza cookies.*?</p>",
    '<p style="margin: 0">A.- Este sitio web no utiliza cookies propias ni de terceros. Cuando el usuario visita la web, '
    "el servidor donde está alojada recibe automáticamente la dirección IP de su ordenador, el día y la hora de la visita y "
    "las páginas consultadas. Es necesario que el servidor conozca estos datos para poder comunicarse y mostrar en el "
    "navegador la página solicitada. No se elaboran perfiles en ningún caso.</p>", body, flags=re.S)

FORM_PRIV = (
    '<p style="margin: 0; font-weight: 600; color: #000000">Formulario «Pide información»:</p>\n'
    '<p style="margin: 0">Los datos que nos envía a través del formulario (nombre, correo electrónico, mensaje y archivos adjuntos) '
    "se usan únicamente para responder a su consulta y, en su caso, preparar el presupuesto o el trabajo solicitado. "
    "La base legal es su consentimiento al enviar el formulario. Se conservan mientras sea necesario para atender la consulta "
    "y durante los plazos que exija la ley.</p>\n"
    '<p style="margin: 0">La web está alojada en Netlify, Inc., que actúa como encargado del tratamiento y recibe los datos del '
    "formulario para hacérnoslos llegar. Netlify tiene su sede en Estados Unidos y está adherida al Marco de Privacidad de Datos "
    "UE-EE. UU., que garantiza un nivel de protección adecuado para esta transferencia internacional.</p>\n")
NO_TRANSFER = "y no están previstas las transferencias internacionales de datos.</p>"
assert body.count(NO_TRANSFER) == 2
body = body.replace(NO_TRANSFER, "salvo la indicada más abajo para el formulario de contacto.</p>")
# párrafo del formulario antes del Delegado de Protección de Datos en Condiciones (4.) y en Política de privacidad
DPD = '<p style="margin: 0; font-weight: 600; color: #000000">Delegado de Protección de Datos:</p>\n<p style="margin: 0">Datasur'
parts = body.split(DPD)
assert len(parts) == 4  # aviso legal, condiciones, privacidad
body = parts[0] + DPD + parts[1] + FORM_PRIV + DPD + parts[2] + FORM_PRIV + DPD + parts[3]

COOKIES = (
    '<details id="politica-de-cookies" class="legal"><summary>Política de cookies</summary><div class="legal-b">'
    '<p style="margin: 0; font-weight: 600; color: #000000">COOKIES</p>\n'
    '<p style="margin: 0">Se denomina cookie a un pequeño archivo que una web guarda en el navegador del usuario para recordar '
    "información sobre su visita.</p>\n"
    '<p style="margin: 0">El sitio web bodonia.es no utiliza cookies: ni propias ni de terceros, ni técnicas, de análisis, '
    "de personalización o publicitarias. Tampoco usa herramientas de estadística ni de seguimiento, y la tipografía y las "
    "imágenes se sirven desde el propio sitio, sin conectar con servicios externos.</p>\n"
    '<p style="margin: 0">Por eso no le pedimos consentimiento para instalar cookies. Si en el futuro incorporáramos alguna, '
    "actualizaríamos esta política y le pediríamos su consentimiento antes de instalarla, cuando la ley lo exija.</p>\n"
    '<p style="margin: 0">Puede configurar su navegador para bloquear o borrar cookies en cualquier momento desde sus opciones '
    "de privacidad.</p></div></details>")
body = re.sub(r'<details id="politica-de-cookies".*?</details>', lambda m: COOKIES, body, flags=re.S)
assert "GED_PLAYLIST" not in body and "Google Analytics" not in body

# --- CSS ---
css = css.strip()
# entre 700 y 1100 px el título de 84 px no cabía en una línea: se escala con la pantalla
css = css.replace("/*MOVIL*/", "@media(max-width:1100px){.hero-t{font-size:calc(8.4vw - 8px)!important}}\n/*MOVIL*/", 1)
assert "8.4vw" in css
FONT_FACE = """#aviso-formulario:empty{display:none}
@font-face{font-family:'Bodoni Moda';src:url(fonts/bodoni-moda.woff2) format('woff2');font-weight:400 900;font-style:normal;font-display:swap}
@font-face{font-family:'Bodoni Moda';src:url(fonts/bodoni-moda-italic.woff2) format('woff2');font-weight:400 900;font-style:italic;font-display:swap}
"""

JS = """<script>
(function(){
  var f=document.getElementById('pide-informacion'),aviso=document.getElementById('aviso-formulario');
  if(!f||!window.fetch||!window.FormData)return;
  f.addEventListener('submit',function(e){
    e.preventDefault();
    var b=f.querySelector('button[type=submit]');b.disabled=true;
    aviso.textContent='Enviando…';
    fetch('/',{method:'POST',body:new FormData(f)}).then(function(r){
      if(!r.ok)throw new Error(r.status);
      f.reset();aviso.textContent='Gracias. Hemos recibido tu mensaje y te responderemos lo antes posible.';
    }).catch(function(){
      aviso.textContent='No se ha podido enviar. Escríbenos a info@bodonia.es o llámanos al 648 82 32 50.';
    }).then(function(){b.disabled=false;});
  });
})();
</script>"""

HEAD = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="Imprenta en La Zubia (Granada) con más de 35 años de experiencia. Diseño, maquetación e impresión offset y digital: libros, catálogos, revistas, carteles, folletos y papelería.">
<link rel="canonical" href="https://bodonia.es/{path}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#9A0015">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_ES">
<meta property="og:site_name" content="Bodonia Artes Gráficas">
<meta property="og:title" content="{title}">
<meta property="og:description" content="Diseño, maquetación e impresión offset y digital en La Zubia (Granada). Más de 35 años de experiencia.">
<meta property="og:url" content="https://bodonia.es/{path}">
<meta property="og:image" content="https://bodonia.es/img/compartir.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="/fonts/bodoni-moda.woff2" as="font" type="font/woff2" crossorigin>
<style>
{font_face}{css}
</style>
</head>
<body>
"""

LD = """<script type="application/ld+json">
{"@context":"https://schema.org","@type":"LocalBusiness","name":"Bodonia Artes Gráficas S.L.","url":"https://bodonia.es/","image":"https://bodonia.es/img/compartir.jpg","logo":"https://bodonia.es/img/logo-bodonia-artes-graficas.png","telephone":"+34648823250","email":"info@bodonia.es","address":{"@type":"PostalAddress","streetAddress":"C/ Gredos nº 27","postalCode":"18140","addressLocality":"La Zubia","addressRegion":"Granada","addressCountry":"ES"},"geo":{"@type":"GeoCoordinates","latitude":37.10948,"longitude":-3.591575},"openingHours":"Mo-Fr 09:00-20:00"}
</script>
"""

index = (HEAD.format(title="Bodonia Artes Gráficas S.L. · Imprenta en La Zubia, Granada", path="", font_face=FONT_FACE, css=css)
         + body + "\n" + JS + "\n" + LD + "</body>\n</html>\n")
# las rutas relativas funcionan igual en la raíz del dominio
(OUT / "index.html").write_text(index, encoding="utf-8")

GRACIAS_BODY = """<div style="font-family: 'Bodoni Moda', 'Bodoni MT', Didot, serif; font-optical-sizing: auto; color: #000000; background: #FFFFFF; line-height: 1.5; min-height: 100vh">
<header><nav class="nav wrap" aria-label="Principal" style="display: flex; justify-content: space-between; align-items: center; gap: 24px">
<a href="/" style="display: flex; align-items: center; padding: 8px 0"><img src="img/logo-bodonia-artes-graficas.png" alt="Bodonia Artes Gráficas" style="height: 88px; width: auto; display: block"></a>
</nav></header>
<main class="wrap" style="padding-top: 48px; padding-bottom: 96px; display: flex; flex-direction: column; gap: 24px">
<p class="label">Pide información</p>
<h1 class="big" style="margin: 0; font-size: 44px; line-height: 1.18; font-weight: 400; letter-spacing: -.015em; border-top: 2px solid #9A0015; padding-top: 16px">Gracias. Hemos recibido tu mensaje.</h1>
<p style="margin: 0; font-size: 19px; max-width: 680px; color: #48484D">Te responderemos lo antes posible. Si es urgente, llámanos al <a href="tel:648823250" style="color: #9A0015">648 82 32 50</a> o escríbenos a <a href="mailto:info@bodonia.es" style="color: #9A0015">info@bodonia.es</a>.</p>
<p style="margin: 0"><a href="/" style="font-size: 17px">Volver al inicio</a></p>
</main>
</div>
"""
gracias = (HEAD.format(title="Gracias · Bodonia Artes Gráficas S.L.", path="gracias.html", font_face=FONT_FACE, css=css)
           .replace('<meta name="description"', '<meta name="robots" content="noindex">\n<meta name="description"')
           + GRACIAS_BODY + "</body>\n</html>\n")
(OUT / "gracias.html").write_text(gracias, encoding="utf-8")

(OUT / "404.html").write_text(
    HEAD.format(title="Página no encontrada · Bodonia Artes Gráficas S.L.", path="404.html", font_face=FONT_FACE, css=css)
    + GRACIAS_BODY.replace("Pide información", "Error 404")
      .replace("Gracias. Hemos recibido tu mensaje.", "Esta página no existe.")
      .replace("Te responderemos lo antes posible. Si es urgente, llámanos", "Puede que el enlace haya cambiado. Si buscas algo concreto, llámanos")
    + "</body>\n</html>\n", encoding="utf-8")

(OUT / "robots.txt").write_text("User-agent: *\nAllow: /\n\nSitemap: https://bodonia.es/sitemap.xml\n")
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>https://bodonia.es/</loc></url>\n</urlset>\n')
(OUT / "netlify.toml").write_text("""[build]
  publish = "."

# bodonia.netlify.app y www.bodonia.es redirigen a https://bodonia.es
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
  for = "/img/*"
  [headers.values]
    Cache-Control = "public, max-age=604800"

[[headers]]
  for = "/video/*"
  [headers.values]
    Cache-Control = "public, max-age=604800"
""")
print("ok", sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file()) // 1024, "KB")
