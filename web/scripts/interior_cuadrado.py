"""Cada doble página del interior, entera, centrada sobre un cuadrado negro.

Uso: python3 web/scripts/interior_cuadrado.py CARPETA_ORIGINALES CARPETA_SALIDA PREFIJO
Los originales se leen en orden de nombre y salen como PREFIJO-1.jpg, PREFIJO-2.jpg...
"""
import sys, glob, os
from PIL import Image

LADO, MARGEN = 2000, 70
src, dst, prefijo = sys.argv[1:4]
archivos = sorted(glob.glob(src + '/*INTERIOR*.png'), key=lambda f: os.path.basename(f).split('-', 1)[-1])
for n, f in enumerate(archivos, 1):
    im = Image.open(f).convert('RGB')
    esc = min((LADO - 2 * MARGEN) / im.width, (LADO - 2 * MARGEN) / im.height)
    im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
    lienzo = Image.new('RGB', (LADO, LADO), (0, 0, 0))
    lienzo.paste(im, ((LADO - im.width) // 2, (LADO - im.height) // 2))
    lienzo.save(f'{dst}/{prefijo}-{n}.jpg', quality=90)
    print(n, os.path.basename(f))
