"""Pedro Zamora. En noir: monta los seis dobles de páginas sobre los cinco fondos negros del cliente,
mezclando sueltos y un doble (ver REPARTO).

Uso: python3 web/scripts/en_noir_fondos.py <fondo1> ... <fondo5>
Los dobles originales sobre negro están en web/referencias-mockups/en-noir-dobles/1..6.jpg.
Escribe fotos/proyectos/05-pedro-zamora-en-noir-interior-1..5.jpg.
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

REPARTO = [[1], [3, 4], [2], [5, 6]]  # dobles de páginas que lleva cada fondo (el quinto fondo es para el vídeo)

def main(fondos):
    for i, (f, grupo) in enumerate(zip(fondos, REPARTO), 1):
        b = sf.fondo(f)
        piezas = [doble(n) for n in grupo]
        hs = [round(p.height * sf.W * sf.ANCHO / p.width) for p in piezas]
        sep = 110
        y = sf.H / 2 - (sum(hs) + sep * (len(hs) - 1)) / 2
        for p, h in zip(piezas, hs):
            pon(b, p, y + h / 2)
            y += h + sep
        b.save(SITIO / f"05-pedro-zamora-en-noir-interior-{i}.jpg", quality=88, optimize=True, progressive=True)

if __name__ == "__main__":
    main(sys.argv[1:5])
