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
for name in ("bodoni-moda.woff2", "dm-sans.woff2"):
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
