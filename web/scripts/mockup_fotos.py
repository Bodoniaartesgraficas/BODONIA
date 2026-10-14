"""Monta la cubierta y las páginas de un libro sobre fotos de mockup reales.

Cada escena es una foto de referencia con las esquinas de la cubierta o de cada página medidas a mano.
La luz y las sombras de la foto se conservan: se calcula la iluminación del papel original
(quitando lo que estaba impreso) y se aplica sobre la página nueva.

Uso: python3 web/scripts/mockup_fotos.py CARPETA_FOTOS CARPETA_ORIGINALES CARPETA_SALIDA
"""
import sys, glob
import numpy as np
from PIL import Image, ImageFilter

ESCALA = 3  # las fotos de referencia son pequeñas; se trabaja ampliado


def coeffs(dst, src):
    A = []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
    return np.linalg.solve(np.array(A, float), np.array(src, float).reshape(8)).tolist()


def blur(a, r):
    """Desenfoque gaussiano aproximado con tres pasadas de caja (en float, sin perder precisión)."""
    k = max(1, int(r))

    def caja(x, eje):
        pad = [(0, 0)] * x.ndim
        pad[eje] = (k + 1, k)
        c = np.cumsum(np.pad(x, pad, mode='edge'), axis=eje)
        n = x.shape[eje]
        return (np.take(c, range(2 * k + 1, 2 * k + 1 + n), axis=eje) - np.take(c, range(0, n), axis=eje)) / (2 * k + 1)

    out = a.astype(float)
    for _ in range(3):
        out = caja(caja(out, 0), 1)
    return out


def luz_del_papel(foto, mascara, radio=None):
    """Color e iluminación del papel original: un polinomio suave ajustado solo sobre el papel en blanco,
    para que no se transparente nada de lo que estaba impreso."""
    f = foto.astype(float)
    H, W = mascara.shape
    ys, xs = np.nonzero(mascara > .5)
    px = f[ys, xs]
    sat = px.max(1) - px.min(1)
    lum = px.mean(1)
    ok = (sat < 30) & (lum > 60)
    x = xs / W - .5
    y = ys / H - .5
    def base(x, y):
        return np.stack([np.ones_like(x), x, y, x * x, x * y, y * y, x ** 3, x * x * y, x * y * y, y ** 3], 1)
    A = base(x, y)
    out = np.zeros_like(f)
    for c in range(3):
        sel = ok.copy()
        for _ in range(3):
            coef = np.linalg.lstsq(A[sel], px[sel, c], rcond=None)[0]
            r = px[:, c] - A @ coef
            s_ = r[sel].std()
            sel = ok & (np.abs(r) < 2 * s_ + 4)
        out[ys, xs, c] = A @ coef
    return out


def montar(foto_path, piezas, out, recorte=None, ref_blanco=None):
    foto = Image.open(foto_path).convert('RGB')
    if recorte:
        foto = foto.crop(recorte)
        dx, dy = recorte[0], recorte[1]
    else:
        dx = dy = 0
    W, H = foto.size[0] * ESCALA, foto.size[1] * ESCALA
    foto = foto.resize((W, H), Image.LANCZOS)
    base = np.array(foto).astype(float)
    res = base.copy()
    for pieza in piezas:
        tex, quad, tipo = pieza[:3]
        curva = pieza[3] if len(pieza) > 3 else (None, None)
        S_ = lambda pt: ((pt[0] - dx) * ESCALA, (pt[1] - dy) * ESCALA)
        q = [S_(p) for p in quad]
        tw, th = tex.size
        texrgb = tex.convert('RGB')
        warp = np.zeros((H, W, 3))
        m = np.zeros((H, W))

        def bez(p0, p2, mid, t):
            if mid is None:
                return (p0[0] + (p2[0] - p0[0]) * t, p0[1] + (p2[1] - p0[1]) * t)
            c = (2 * mid[0] - (p0[0] + p2[0]) / 2, 2 * mid[1] - (p0[1] + p2[1]) / 2)
            return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p2[0],
                    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p2[1])

        top_mid = S_(curva[0]) if curva[0] else None
        bot_mid = S_(curva[1]) if curva[1] else None
        N = 24 if (top_mid or bot_mid) else 1
        for i in range(N):
            t0, t1 = i / N, (i + 1) / N
            a0, a1 = bez(q[0], q[1], top_mid, t0), bez(q[0], q[1], top_mid, t1)
            b0, b1 = bez(q[3], q[2], bot_mid, t0), bez(q[3], q[2], bot_mid, t1)
            x0, x1 = int(round(tw * t0)), min(tw, int(round(tw * t1)) + 2)
            strip = texrgb.crop((x0, 0, x1, th))
            sw = x1 - x0
            e = (x1 - x0 - (tw * (t1 - t0))) / sw  # pequeño solape
            c = coeffs([a0, (a1[0] + (a1[0] - a0[0]) * e, a1[1] + (a1[1] - a0[1]) * e),
                        (b1[0] + (b1[0] - b0[0]) * e, b1[1] + (b1[1] - b0[1]) * e), b0],
                       [(0, 0), (sw, 0), (sw, th), (0, th)])
            w_ = np.array(strip.transform((W, H), Image.PERSPECTIVE, c, Image.BICUBIC)).astype(float)
            mm = np.array(Image.new('L', (sw, th), 255).transform((W, H), Image.PERSPECTIVE, c, Image.BILINEAR)).astype(float) / 255
            nuevo_m = np.maximum(m, mm)
            peso = np.where(nuevo_m > 0, (mm - np.minimum(m, mm) * 0) , 0)
            warp = np.where(mm[:, :, None] > m[:, :, None], w_, warp)
            m = nuevo_m
        # bordes un poco hacia dentro para no dejar ver el papel original
        m = np.array(Image.fromarray((m * 255).astype('uint8')).filter(ImageFilter.MinFilter(3))).astype(float) / 255
        if tipo == 'papel':
            luz = luz_del_papel(base, (m > .5).astype(float))
            dentro = luz[m > .5]
            blanco = ref_blanco or np.percentile(dentro.mean(1), 97)
            factor = luz / blanco
            nuevo = warp * np.clip(factor, 0, 1.15)
        else:  # cubierta: se conserva la luz general de la foto, sin el dibujo de la cubierta original
            lum = base.mean(2, keepdims=True)
            luz = blur(lum, 18 * ESCALA)
            dentro = luz[m > .5]
            factor = luz / np.percentile(dentro, 90)
            nuevo = warp * np.clip(factor, 0, 1.2)
        res = res * (1 - m[:, :, None]) + nuevo * m[:, :, None]
    img = Image.fromarray(np.clip(res, 0, 255).astype('uint8'))
    img = img.filter(ImageFilter.UnsharpMask(2, 40, 2))
    img.save(out, quality=90)


def mitades(spread):
    w, h = spread.size
    return spread.crop((0, 0, w // 2, h)), spread.crop((w // 2, 0, w, h))


if __name__ == '__main__':
    fotos, orig, dst = sys.argv[1:4]
    F = lambda p: glob.glob(fotos + '/' + p + '*')[0]
    O = lambda p: glob.glob(orig + '/' + p)[0]

    cub = Image.open(O('*PORTADA_EN_NOIR.png')).convert('RGB')
    frente = cub.crop((4137, 0, 6050, cub.size[1]))
    montar(F('b475993c'), [(frente, [(350, 210), (636, 288), (490, 632), (180, 548)], 'cubierta')],
           dst + '/05-pedro-zamora-en-noir-portada.jpg', recorte=(0, 0, 736, 770))

    escenas = [
        ('47ffaca8', '*INTERIOR3.png', [(100, 318), (378, 288), (408, 622), (118, 652)],
         [(382, 287), (655, 265), (700, 600), (410, 622)], (0, 120, 736, 800)),
        ('4247760a', '*INTERIOR.png', [(58, 300), (366, 160), (555, 551), (215, 698)],
         [(370, 158), (672, 35), (859, 425), (557, 550)], None, ((205, 192), None), ((521, 90), None)),
        ('c4df1cff', '*INTERIOR6.png', [(300, 230), (540, 378), (300, 692), (40, 520)],
         [(545, 378), (845, 525), (600, 888), (300, 695)], None),
    ]
    for n, esc in enumerate(escenas, 1):
        foto, pag, izq, der, rec = esc[:5]
        ci, cd = esc[5:7] if len(esc) > 5 else ((None, None), (None, None))
        a, b = mitades(Image.open(O(pag)).convert('RGB'))
        montar(F(foto), [(a, izq, 'papel', ci), (b, der, 'papel', cd)],
               dst + f'/05-pedro-zamora-en-noir-abierto-{n}.jpg', recorte=rec)
    print('ok')
