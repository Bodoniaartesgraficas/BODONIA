"""Pedro Zamora. En noir: monta los seis dobles de páginas sobre los tres fondos negros del cliente (dos por fondo).

Uso: python3 web/scripts/en_noir_fondos.py <fondo1> <fondo2> <fondo3>
Los dobles originales sobre negro están en web/referencias-mockups/en-noir-dobles/1..6.jpg.
Escribe fotos/proyectos/05-pedro-zamora-en-noir-interior-1..3.jpg.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import santa_fe_fondos as sf

ORIGEN = Path(__file__).resolve().parents[1] / "referencias-mockups" / "en-noir-dobles"
SITIO = sf.SITIO

def doble(n):
    im = Image.open(ORIGEN / f"{n}.jpg").convert("RGB")
    ys, xs = np.where(np.asarray(im).max(axis=2) > 20)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

def pon(lienzo, spread, cy):
    h = sf.pon(lienzo, spread, cy)
    w = round(sf.W * sf.ANCHO); x, y = (sf.W - w) // 2, round(cy - h / 2)
    ImageDraw.Draw(lienzo).rectangle((x, y, x + w - 1, y + h - 1), outline=(88, 88, 88), width=2)
    return h

def main(fondos):
    for i, f in enumerate(fondos, 1):
        b = sf.fondo(f)
        a, c = doble(2 * i - 1), doble(2 * i)
        h = round(a.height * sf.W * sf.ANCHO / a.width); sep = 110
        pon(b, a, sf.H / 2 - (h + sep) / 2)
        pon(b, c, sf.H / 2 + (h + sep) / 2)
        b.save(SITIO / f"05-pedro-zamora-en-noir-interior-{i}.jpg", quality=88, optimize=True, progressive=True)

if __name__ == "__main__":
    main(sys.argv[1:4])
