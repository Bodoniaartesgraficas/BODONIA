"""Territorios de la mirada: monta los interiores sobre los tres fondos del cliente.

Foto 1: portadilla, tríptico y cuatríptico juntos; foto 2: La Revolución Mexicana suelta. Formato 3:4. Los originales sobre negro están en
web/referencias-mockups/territorios-dobles/1..4.jpg.

Uso: python3 web/scripts/territorios_fondos.py <fondo1> <fondo2>
Escribe fotos/proyectos/02-territorios-de-la-mirada-interior-1..2.jpg.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import santa_fe_fondos as sf

ORIGEN = Path(__file__).resolve().parents[1] / "referencias-mockups" / "territorios-dobles"

def doble(n):
    im = Image.open(ORIGEN / f"{n}.jpg").convert("RGB")
    ys, xs = np.where(np.asarray(im).max(axis=2) > 20)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

def alto(sp):
    return round(sp.height * sf.W * sf.ANCHO / sp.width)

def main(fondos):
    b = [sf.fondo(f) for f in fondos[:2]]
    piezas = [doble(1), doble(3), doble(4)]  # portadilla, tríptico y cuatríptico en la misma foto
    hs = [alto(p) for p in piezas]
    sep = 90
    y = sf.H / 2 - (sum(hs) + sep * 2) / 2
    for p, h in zip(piezas, hs):
        sf.pon(b[0], p, y + h / 2)
        y += h + sep
    sf.pon(b[1], doble(2), sf.H * .5)
    for i, im in enumerate(b, 1):
        im.save(sf.SITIO / f"02-territorios-de-la-mirada-interior-{i}.jpg", quality=86, optimize=True, progressive=True)

if __name__ == "__main__":
    main(sys.argv[1:4])
