"""Ensancha el libro de la portada de Territorios de la mirada (el real es más ancho que alto)
sin tocar el fondo, y vuelve a montar la cubierta real del PDF encima.
Uso: python3 territorios_ancho.py FOTO PORTADA_PDF_PNG SALIDA"""
import sys, numpy as np
from PIL import Image, ImageFilter, ImageDraw
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import mockup_fotos as mf

foto, pdfpng, out = sys.argv[1:4]
im = Image.open(foto).convert('RGB'); W, H = im.size
src = np.array(im).astype(float)
TL, TR, BR, BL = map(np.array, [(128, 545), (626, 371), (1051, 825), (533, 1085)])
K, S0, GROSOR = 1.3, -0.16, np.array([0, 42])


def homografia(src, dst):
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y, -u], [0, 0, 0, x, y, 1, -v * x, -v * y, -v]]
    return np.linalg.svd(np.array(A, float))[2][-1].reshape(3, 3)


Hq = homografia([(0, 0), (1, 0), (1, 1), (0, 1)], [TL, TR, BR, BL])  # (s,t) -> imagen
Hi = np.linalg.inv(Hq)


def aplica(H, x, y):
    w = H[2, 0] * x + H[2, 1] * y + H[2, 2]
    return (H[0, 0] * x + H[0, 1] * y + H[0, 2]) / w, (H[1, 0] * x + H[1, 1] * y + H[1, 2]) / w

# máscara del libro original (cubierta + lomo + bloque de páginas)
m = Image.new('L', (W, H)); d = ImageDraw.Draw(m)
pts = [TL, TR, BR, BL]; d.polygon([tuple(p) for p in pts] + [], fill=255)
for p, q in zip(pts, pts[1:] + pts[:1]):
    d.polygon([tuple(p), tuple(q), tuple(q + GROSOR), tuple(p + GROSOR)], fill=255)
d.polygon([tuple(TL), tuple(TL + np.array([-8, 10])), tuple(BL + np.array([-8, 10]) + GROSOR), tuple(BL)], fill=255)
mask = np.array(m) > 127

ys, xs = np.mgrid[0:H, 0:W]
sn, t = aplica(Hi, xs.astype(float), ys.astype(float))
s = np.where(sn < S0, sn - S0, np.where(sn > S0 + K, 1 + sn - S0 - K, (sn - S0) / K))
sx, sy = aplica(Hq, s, t)
xi, yi = np.clip(np.round(sx).astype(int), 0, W - 1), np.clip(np.round(sy).astype(int), 0, H - 1)
dentro = mask[yi, xi] & (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H)

# sombra suave del libro nuevo sobre la mesa
sm = Image.fromarray((dentro * 255).astype('uint8')).transform((W, H), Image.AFFINE, (1, 0, -28, 0, 1, -30)).filter(ImageFilter.GaussianBlur(22))
sombra = 1 - .5 * np.array(sm).astype(float)[..., None] / 255
res = src * sombra
res[dentro] = src[yi[dentro], xi[dentro]]
Image.fromarray(res.clip(0, 255).astype('uint8')).save(out + '.base.png')

# cubierta real del PDF sobre la cubierta nueva
pdf = Image.open(pdfpng).convert('RGB'); pw, ph = pdf.size
fr = pdf.crop((round(pw * 1105 / 2087), round(ph * 78 / 977), round(pw * 2012 / 2087), round(ph * 897 / 977)))
q = [np.array(aplica(Hq, u, v)) for u, v in [(S0, 0), (S0 + K, 0), (S0 + K, 1), (S0, 1)]]
mf.ESCALA = 1
mf.montar(out + '.base.png', [(fr, [tuple(p) for p in q], 'cubierta')], out)
print('ok', [tuple(np.round(p)) for p in q])
