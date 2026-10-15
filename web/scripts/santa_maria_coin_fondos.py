"""Iglesia y Convento de Santa María de Coín: monta los interiores sobre los tres fondos del cliente.

Fondo 1 y 2 con un doble suelto cada uno; fondo 3 con dos dobles apilados. Formato 3:4. Los originales sobre negro están en
web/referencias-mockups/santa-maria-coin-dobles/1..4.jpg.

Uso: python3 web/scripts/territorios_fondos.py <fondo1> <fondo2> <fondo3>
Escribe fotos/proyectos/06-santa-maria-de-coin-interior-1..3.jpg.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import santa_fe_fondos as sf

ORIGEN = Path(__file__).resolve().parents[1] / "referencias-mockups" / "santa-maria-coin-dobles"

def doble(n):
    im = Image.open(ORIGEN / f"{n}.jpg").convert("RGB")
    ys, xs = np.where(np.asarray(im).max(axis=2) > 20)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

def alto(sp):
    return round(sp.height * sf.W * sf.ANCHO / sp.width)

def main(fondos):
    b = [sf.fondo(f) for f in fondos]
    sf.pon(b[0], doble(1), sf.H * .5)
    sf.pon(b[1], doble(2), sf.H * .5)
    x, y = doble(3), doble(4)
    sep = 110
    total = alto(x) + sep + alto(y)
    sf.pon(b[2], x, sf.H / 2 - total / 2 + alto(x) / 2)
    sf.pon(b[2], y, sf.H / 2 + total / 2 - alto(y) / 2)
    for i, im in enumerate(b, 1):
        im.save(sf.SITIO / f"06-santa-maria-de-coin-interior-{i}.jpg", quality=86, optimize=True, progressive=True)

if __name__ == "__main__":
    main(sys.argv[1:4])
