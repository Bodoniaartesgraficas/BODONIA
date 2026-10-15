"""Territorios de la mirada: monta los interiores sobre los tres fondos del cliente.

Cada doble va suelto, en horizontal, sobre un fondo en formato 3:4 (el cuarto reutiliza el primero, volteado). Los originales sobre negro están en
web/referencias-mockups/territorios-dobles/1..4.jpg.

Uso: python3 web/scripts/territorios_fondos.py <fondo1> <fondo2> <fondo3>
Escribe fotos/proyectos/02-territorios-de-la-mirada-interior-1..3.jpg.
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
    b = [sf.fondo(f) for f in fondos]
    b.append(b[0].transpose(Image.FLIP_LEFT_RIGHT))  # el cuarto reutiliza el primer fondo, volteado
    for i in range(4):
        sf.pon(b[i], doble(i + 1), sf.H * .5)
        b[i].save(sf.SITIO / f"02-territorios-de-la-mirada-interior-{i + 1}.jpg", quality=86, optimize=True, progressive=True)

if __name__ == "__main__":
    main(sys.argv[1:4])
