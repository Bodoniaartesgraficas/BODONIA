"""Monta dobles de páginas sacados del PDF de interior sobre fondos 3:4, dos dobles por foto.

Uso: python3 web/scripts/dobles_pdf.py <interior.pdf> <salida.jpg> <fondo> <pág izq 1> <pág izq 2>
Cada doble es la página indicada (izquierda) y la siguiente. Se recorta al TrimBox (23,5 pt de sangre).
"""
import sys, subprocess, tempfile
from pathlib import Path
import numpy as np
from PIL import Image
import santa_fe_fondos as sf

DPI = 150
SANGRE = 23.5

def pagina(pdf, n, tmp):
    base = Path(tmp) / f"p{n}"
    subprocess.run(["pdftoppm", "-r", str(DPI), "-f", str(n), "-l", str(n), "-jpeg", "-jpegopt", "quality=92", "-singlefile", pdf, str(base)], check=True)
    im = Image.open(str(base) + ".jpg").convert("RGB")
    s = round(SANGRE * DPI / 72)
    return im.crop((s, s, im.width - s, im.height - s))

def doble(pdf, n, tmp):
    a, b = pagina(pdf, n, tmp), pagina(pdf, n + 1, tmp)
    im = Image.new("RGB", (a.width + b.width, a.height)); im.paste(a, (0, 0)); im.paste(b, (a.width, 0))
    # sombra suave del lomo
    x = np.arange(im.width) - a.width
    g = 1 - .16 * np.exp(-(x / (im.width * .035)) ** 2)
    arr = (np.asarray(im).astype(float) * g[None, :, None]).clip(0, 255).astype("uint8")
    return Image.fromarray(arr)

def main(pdf, salida, fondo, n1, n2):
    with tempfile.TemporaryDirectory() as tmp:
        piezas = [doble(pdf, int(n1), tmp), doble(pdf, int(n2), tmp)]
    b = sf.fondo(fondo)
    hs = [round(p.height * sf.W * sf.ANCHO / p.width) for p in piezas]
    sep = 110
    y = sf.H / 2 - (sum(hs) + sep) / 2
    for p, h in zip(piezas, hs):
        sf.pon(b, p, y + h / 2); y += h + sep
    b.save(sf.SITIO / salida, quality=86, optimize=True, progressive=True)

if __name__ == "__main__":
    main(*sys.argv[1:6])
