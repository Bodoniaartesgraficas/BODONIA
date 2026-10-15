"""Santa Fe—Mauthausen—Santa Fe: monta los dobles de páginas sobre los tres fondos del cliente.

Uso: python3 web/scripts/santa_fe_fondos.py <fondo1> <fondo2> <fondo3>
Lee los dobles (los originales sobre negro
están en web/referencias-mockups/santa-fe-dobles/1..4.jpg) y escribe interior-1..3.jpg.
"""
import sys, shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageChops

SITIO = Path(__file__).resolve().parents[1] / "sitio" / "fotos" / "proyectos"
ORIGEN = Path(__file__).resolve().parents[1] / "referencias-mockups" / "santa-fe-dobles"
W, H = 1600, 2844
ANCHO = .88


def doble(n):
    im = Image.open(ORIGEN / f"{n}.jpg").convert("RGB")
    a = np.asarray(im).max(axis=2) > 28
    ys, xs = np.where(a)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

def fondo(ruta, quita_abajo=0):
    im = Image.open(ruta).convert("RGB")
    if quita_abajo:  # el tercer fondo trae una marca de agua abajo a la derecha
        im = im.crop((0, 0, im.width, round(im.height * (1 - quita_abajo))))
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((x, y, x + W, y + H))
    r = np.random.default_rng(3)
    g = r.normal(0, 2.2, (H, W, 1))
    return Image.fromarray(np.clip(np.asarray(im) + g, 0, 255).astype("uint8"))

def pon(lienzo, spread, cy):
    w = round(W * ANCHO); h = round(spread.height * w / spread.width)
    sp = spread.resize((w, h), Image.LANCZOS)
    x, y = (W - w) // 2, round(cy - h / 2)
    sombra = Image.new("L", (W, H), 0)
    sombra.paste(Image.new("L", (w, h), 255), (x + 6, y + 26))
    sombra = sombra.filter(ImageFilter.GaussianBlur(30)).point(lambda v: int(v * .42))
    lienzo.paste(Image.new("RGB", (W, H), (30, 22, 12)), (0, 0), sombra)
    lienzo.paste(sp, (x, y))
    return h

def main(fondos):
    b = [fondo(f, .07 if i == 2 else 0) for i, f in enumerate(fondos)]
    pon(b[0], doble(1), H * .5)
    pon(b[1], doble(2), H * .5)
    d3, d4 = doble(3), doble(4)
    h = round(d3.height * W * ANCHO / d3.width)
    sep = 110
    pon(b[2], d3, H / 2 - (h + sep) / 2)
    pon(b[2], d4, H / 2 + (h + sep) / 2)
    for i, im in enumerate(b, 1):
        im.save(SITIO / f"03-santa-fe-mauthausen-interior-{i}.jpg", quality=86, optimize=True, progressive=True)

if __name__ == "__main__":
    main(sys.argv[1:4])
