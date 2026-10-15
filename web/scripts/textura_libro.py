"""Da textura de libro a la cubierta de una foto de mockup: grano de papel y,
según el acabado, brillo de plastificado o relieve de la tinta.
Uso desde Python: textura(foto, salida, cubiertas, acabado) con cubiertas = [[TL,TR,BR,BL], ...]
(la primera es la de delante; las siguientes se tapan con las anteriores)."""
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter


def blur(a, r):
    return gaussian_filter(a.astype('float32'), r)


def textura(foto, salida, cubiertas, acabado, semilla=3):
    im = Image.open(foto).convert('RGB'); W, H = im.size
    a = np.array(im).astype(float)
    rng = np.random.default_rng(semilla)
    ocupado = np.zeros((H, W), bool)
    for quad in cubiertas:
        m = Image.new('L', (W, H)); ImageDraw.Draw(m).polygon([tuple(p) for p in quad], fill=255)
        m = np.array(m) > 127
        m &= ~ocupado; ocupado |= m
        mf = blur(m.astype(float) * 255, 1.2) / 255
        lum = a.mean(2)
        # grano de papel: ruido fino con algo de fibra
        g = rng.normal(0, 1, (H, W))
        grano = blur(g, .7) * 1.0 + blur(g, 2.2) * 1.6
        grano /= grano.std()
        efecto = np.zeros((H, W))
        if acabado == 'brillo':
            efecto += grano * 2.2
            # reflejo del plastificado: banda diagonal suave, más fuerte donde ya hay luz
            q = np.array(quad, float)
            c = q.mean(0); d = (q[1] - q[3]); d /= np.linalg.norm(d)
            ys, xs = np.mgrid[0:H, 0:W]
            u = ((xs - c[0]) * d[0] + (ys - c[1]) * d[1]) / np.linalg.norm(q[1] - q[3])
            banda = np.exp(-((u + .12) / .18) ** 2) * 38 + np.exp(-((u - .28) / .05) ** 2) * 16
            efecto += banda * (0.55 + 0.45 * blur(lum, 25) / 255)
            # brillos puntuales muy finos de la película
            efecto += np.clip(blur(rng.normal(0, 1, (H, W)), 1.5) * 8 - 6, 0, None) * 2
        else:  # relieve: la tinta y el dibujo se levantan del papel
            efecto += grano * 3.2
            l = blur(lum, 1.1)
            emb = (np.roll(l, (1, 1), (0, 1)) - np.roll(l, (-1, -1), (0, 1)))
            efecto += np.clip(emb, -40, 40) * .45
            # bisel: el borde de la cubierta coge luz arriba-izquierda y sombra abajo-derecha
            borde = blur(m.astype(float), 3) - blur(m.astype(float), 9)
            efecto += borde * 18
        a = a + (efecto * mf)[..., None]
    Image.fromarray(np.clip(a, 0, 255).astype('uint8')).save(salida, quality=90)
