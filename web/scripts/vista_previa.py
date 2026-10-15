"""Genera una vista previa de web/sitio/ para publicarla como artifact de Claude (no es la web final).

Uso: python3 web/scripts/vista_previa.py <carpeta de salida>
Diferencias con la web real: CSS, JS y tipografías van dentro del HTML (el visor no carga otros archivos de estilo
o código) y el formulario no envía nada; solo avisa de que funcionará al publicar en Netlify.
"""
import base64, re, shutil, sys
from pathlib import Path

SITIO = Path(__file__).resolve().parents[1] / "sitio"
OUT = Path(sys.argv[1])
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)
shutil.copytree(SITIO / "fotos", OUT / "fotos")

css = (SITIO / "styles.css").read_text(encoding="utf-8")
for name in ("bodoni-moda.woff2", "bodoni-moda-italic.woff2", "dm-sans.woff2"):
    data = base64.b64encode((SITIO / "fonts" / name).read_bytes()).decode()
    css = css.replace(f"url(fonts/{name})", f"url(data:font/woff2;base64,{data})")

AVISO_FORM = """document.querySelector('#contact-form').addEventListener('submit',e=>{
  e.preventDefault();
  document.querySelector('#form-status').textContent = 'Vista previa: el formulario enviará los mensajes cuando la web esté publicada en Netlify.';
});
"""
js = (SITIO / "script.js").read_text(encoding="utf-8")
i = js.index("document.querySelector('#contact-form').addEventListener('submit'")
j = js.index("\n});\n", i) + 5
js = js[:i] + AVISO_FORM + js[j:]
contenido = (SITIO / "contenido.js").read_text(encoding="utf-8")

html = (SITIO / "index.html").read_text(encoding="utf-8")
body = re.search(r"<body>(.*)</body>", html, re.S).group(1)
body = re.sub(r'<script src="[^"]+"></script>\n?', "", body)
index = ("<title>Web de Bodonia</title>\n<style>\n" + css + "\n</style>\n" + body
         + "<script>\n" + contenido + "\n</script>\n<script>\n" + js + "\n</script>\n")
(OUT / "index.html").write_text(index, encoding="utf-8")

legal = (SITIO / "legal.html").read_text(encoding="utf-8")
legal = legal.replace('<link rel="stylesheet" href="styles.css">', "<style>\n" + css + "\n</style>")
legal = legal.replace('href="/"', 'href="index.html"')
legal = re.sub(r'<link rel="(icon|apple-touch-icon)"[^>]*>', "", legal)
(OUT / "legal.html").write_text(legal, encoding="utf-8")
print("ok", len(index) // 1024, "KB")

# --- Versión de un solo archivo (fotos incrustadas), para el visor de artifacts ---
import io
from PIL import Image

def data_uri(rel, width):
    im = Image.open(SITIO / rel)
    buf = io.BytesIO()
    if rel.endswith(".png"):
        im.thumbnail((width, width * 4)); im.save(buf, "PNG", optimize=True); mime = "image/png"
    else:
        im = im.convert("RGB"); im.thumbnail((width, width * 4)); im.save(buf, "JPEG", quality=80, optimize=True, progressive=True); mime = "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(buf.getvalue()).decode()

unico = index
import base64 as _b
unico = unico.replace('"fotos/instagram.svg"', '"data:image/svg+xml;base64,' + _b.b64encode(open(SITIO / 'fotos/instagram.svg','rb').read()).decode() + '"')
for rel in sorted(set(re.findall(r'(fotos/[\w./-]+\.(?:jpg|png))', unico))):
    width = 1800 if rel.endswith("-completa.jpg") else (400 if "logo" in rel else 900)
    unico = unico.replace(f'"{rel}"', f'"{data_uri(rel, width)}"')
legal_body = re.search(r"<main>(.*)</main>", legal, re.S).group(1)
CLOSE = '<button class="close" aria-label="Cerrar"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m6 6 12 12M6 18 18 6"/></svg></button>'
legal_dialog = (f'<dialog id="legal-dialog" class="text-dialog" aria-labelledby="legal-t">{CLOSE}<div class="dialog-content">'
                + legal_body.replace('<section class="intro"><h1>Información legal.</h1></section>', '<h2 id="legal-t">Información legal.</h2>')
                + "</div></dialog>\n")
unico = unico.replace('<dialog class="project-dialog"', legal_dialog + '<dialog class="project-dialog"', 1)
unico = re.sub(r'<a href="legal\.html#([\w-]+)"', r'<a href="#\1" data-legal="\1"', unico)
unico = unico.replace("</script>\n", "</script>\n", 1)
unico += """<script>
document.querySelectorAll('[data-legal]').forEach(a => a.addEventListener('click', e => {
  e.preventDefault();
  document.querySelectorAll('dialog[open]').forEach(d => d.close());
  const dlg = document.querySelector('#legal-dialog'); dlg.showModal();
  dlg.querySelectorAll('details').forEach(d => d.open = d.id === a.dataset.legal);
  document.getElementById(a.dataset.legal).scrollIntoView();
}));
document.querySelector('#legal-dialog .close').addEventListener('click', () => document.querySelector('#legal-dialog').close());
</script>
"""
assert not re.search(r"(src|href)=.fotos/", unico)
(OUT / "web-bodonia.html").write_text(unico, encoding="utf-8")
print("un solo archivo:", len(unico) // 1024, "KB")
