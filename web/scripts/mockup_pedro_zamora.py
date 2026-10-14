"""Mockups de "Pedro Zamora. En noir": libro cerrado y cuatro dobles páginas abiertas, sobre una mesa de madera.

Uso: python3 web/scripts/mockup_pedro_zamora.py CARPETA_ORIGINALES CARPETA_SALIDA
CARPETA_ORIGINALES lleva la cubierta completa (PORTADA_EN_NOIR.png) y los interiores
(Pedro_Zamora_PAR_S_INTERIOR*.png), tal como los pasó el cliente.
"""
import sys, glob, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SS = 2  # supersampling


def coeffs(dst, src):
    A = []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
    sol = np.linalg.solve(np.array(A, float), np.array(src, float).reshape(8))
    return sol.tolist()


def place(canvas, tex, quad, shade=None):
    """Pega `tex` en el cuadrilátero `quad` (tl, tr, br, bl) con perspectiva y antialias."""
    W, H = canvas.size
    w, h = tex.size
    c = coeffs(quad, [(0, 0), (w, 0), (w, h), (0, h)])
    tex = tex.convert('RGBA')
    out = tex.transform((W, H), Image.PERSPECTIVE, c, Image.BICUBIC)
    mask = Image.new('L', (w, h), 255).transform((W, H), Image.PERSPECTIVE, c, Image.BILINEAR)
    out.putalpha(mask)
    if shade is not None:
        out = shade(out)
    canvas.alpha_composite(out)


def mesa(W, H, seed=3):
    rng = np.random.default_rng(seed)
    base = np.array([196, 160, 120], float)
    yy = np.linspace(0, 1, H)[:, None]
    xx = np.linspace(0, 1, W)[None, :]
    # tablones horizontales con veta larga
    n = np.zeros((H, W))
    for fh, fw, amp in ((H, W // 500, .14), (H // 2, W // 400, .5), (H // 4, W // 200, .3), (H // 8, W // 90, .12)):
        r = rng.random((max(fh, 4), max(fw, 4)))
        n += amp * np.array(Image.fromarray((r * 255).astype('uint8')).resize((W, H), Image.BICUBIC)) / 255
    n = (n - n.mean()) / n.std()
    rings = np.sin((yy * 38 + n * 1.4) * math.pi)  # vetas
    plank = np.floor(yy * 3.0)  # 3 tablones
    tone = (plank * 0.07 - 0.07)
    img = base[None, None, :] * (1 + 0.045 * n[:, :, None] + 0.03 * rings[:, :, None] + tone[:, :, None])
    # juntas entre tablones
    for k in (1, 2):
        y = int(H * k / 3)
        img[y - 2:y + 2] *= .55
    # luz suave desde arriba a la izquierda y viñeta
    luz = 1.08 - 0.26 * (xx * .55 + yy * .75) ** 1.3
    vig = 1 - 0.30 * (((xx - .5) * 1.6) ** 2 + ((yy - .5) * 1.6) ** 2)
    img *= (luz * vig)[:, :, None]
    return Image.fromarray(np.clip(img, 0, 255).astype('uint8')).convert('RGBA')


def sombra(canvas, polys, blur, opacity, off=(0, 0)):
    W, H = canvas.size
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    for p in polys:
        d.polygon([(x + off[0], y + off[1]) for x, y in p], fill=int(255 * opacity))
    m = m.filter(ImageFilter.GaussianBlur(blur))
    s = Image.new('RGBA', (W, H), (25, 15, 8, 255))
    s.putalpha(m)
    canvas.alpha_composite(s)


def rot(pts, ang, cx, cy):
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    return [((x - cx) * ca - (y - cy) * sa + cx, (x - cx) * sa + (y - cy) * ca + cy) for x, y in pts]


def cantos(canvas, edge, color_a, color_b, lines=70, seed=1):
    """Dibuja un canto de páginas (franja) como un polígono relleno con finas líneas."""
    rng = np.random.default_rng(seed)
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = edge  # tl tr br bl de la franja
    d = ImageDraw.Draw(canvas)
    d.polygon(edge, fill=color_a)
    for i in range(lines):
        t = (i + rng.random()) / lines
        a = (x0 + (x3 - x0) * t, y0 + (y3 - y0) * t)
        b = (x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)
        v = rng.integers(-14, 10)
        col = tuple(int(c + v) for c in color_b) + (255,)
        d.line([a, b], fill=col, width=max(1, SS))
    # sombra interior arriba y abajo
    return canvas


def cierre_luz(img, strength=.10):
    arr = np.array(img).astype(float)
    h, w = arr.shape[:2]
    g = 1 + strength * (np.linspace(.5, -.5, h)[:, None] * .7 + np.linspace(.5, -.5, w)[None, :] * .5)
    arr[:, :, :3] *= g[:, :, None]
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), 'RGBA')


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def franja(cv, a, b, v, t0, t1, color):
    """Rectángulo entre a-b desplazado por v*t0 .. v*t1 (para los cantos)."""
    p = [(a[0] + v[0] * t0, a[1] + v[1] * t0), (b[0] + v[0] * t0, b[1] + v[1] * t0),
         (b[0] + v[0] * t1, b[1] + v[1] * t1), (a[0] + v[0] * t1, a[1] + v[1] * t1)]
    ImageDraw.Draw(cv).polygon(p, fill=color)
    return p


def libro_cerrado(cubierta, out):
    W, H = 1600 * SS, 2000 * SS
    cv = mesa(W, H, seed=5)
    full = Image.open(cubierta).convert('RGB')
    fh = full.size[1]
    front = full.crop((4137, 0, 6050, fh))
    spine = full.crop((3890, 0, 4137, fh))
    fw_, fh_ = front.size
    ang = -7
    cw = int(W * .52)
    ch = int(cw * fh_ / fw_)
    cx, cy = W * .52, H * .47
    x0, y0 = cx - cw / 2, cy - ch / 2
    k = cw * .010
    top = [(x0 + k, y0), (x0 + cw - k, y0), (x0 + cw, y0 + ch), (x0, y0 + ch)]
    quad = rot(top, ang, cx, cy)
    T = cw * .085  # grosor del libro
    v = (-T * .55, T * .42)  # dirección en la que se ve el grosor (desde abajo a la izquierda)
    sp = [quad[0], quad[3], (quad[3][0] + v[0], quad[3][1] + v[1]), (quad[0][0] + v[0], quad[0][1] + v[1])]
    pg = [quad[3], quad[2], (quad[2][0] + v[0], quad[2][1] + v[1]), (quad[3][0] + v[0], quad[3][1] + v[1])]
    sombra(cv, [quad, sp, pg], blur=70 * SS, opacity=.55, off=(30 * SS, 64 * SS))
    sombra(cv, [quad, sp, pg], blur=9 * SS, opacity=.5, off=(4 * SS, 9 * SS))
    # lomo (a la izquierda): textura del lomo, el texto lee de abajo arriba
    place(cv, spine, [sp[3], sp[0], sp[1], sp[2]],
          shade=lambda im: cierre_luz(im, -.10))
    # canto inferior: cartón (tapa), páginas y cartón (contratapa)
    a, b = pg[0], pg[1]
    franja(cv, a, b, (1, 0), 0, 0, (0, 0, 0, 0))
    vv = (pg[3][0] - pg[0][0], pg[3][1] - pg[0][1])
    tablero = (44, 40, 38, 255)
    franja(cv, a, b, vv, 0, .10, tablero)
    p_ = franja(cv, lerp(a, b, .012), lerp(a, b, .992), vv, .10, .90, (238, 231, 214, 255))
    rng = np.random.default_rng(2)
    d = ImageDraw.Draw(cv)
    for i in range(80):
        t = .10 + .80 * (i + rng.random()) / 80
        pa = (a[0] + vv[0] * t + (b[0] - a[0]) * .012, a[1] + vv[1] * t + (b[1] - a[1]) * .012)
        pb = (a[0] + vv[0] * t + (b[0] - a[0]) * .992, a[1] + vv[1] * t + (b[1] - a[1]) * .992)
        c = int(226 + rng.integers(-12, 8))
        d.line([pa, pb], fill=(c, c - 6, c - 22, 255), width=SS)
    franja(cv, a, b, vv, .90, 1.0, tablero)
    place(cv, front, quad, shade=lambda im: cierre_luz(im, .16))
    d.line([quad[0], quad[1], quad[2]], fill=(98, 88, 80, 255), width=2 * SS)
    cv = cv.resize((W // SS, H // SS), Image.LANCZOS).convert('RGB')
    cv.save(out, quality=90)


def libro_abierto(inter, out, tam, ang, cx, cy, ancho, seed, mesa_seed):
    W, H = tam[0] * SS, tam[1] * SS
    cv = mesa(W, H, seed=mesa_seed)
    spread = Image.open(inter).convert('RGB')
    sw, sh = spread.size
    w = int(W * ancho)
    h = int(w * sh / sw)
    s = np.array(spread.resize((w, h), Image.LANCZOS)).astype(float)
    xs = np.linspace(-1, 1, w)
    g = 1 - .24 * np.exp(-(xs / .028) ** 2) - .10 * np.exp(-(xs / .22) ** 2) + .02 * np.abs(xs) ** 2
    s *= g[None, :, None]
    spread = Image.fromarray(np.clip(s, 0, 255).astype('uint8'))
    x0, y0 = cx - w / 2, cy - h / 2
    k = w * .006
    top = [(x0 + k, y0), (x0 + w - k, y0), (x0 + w, y0 + h), (x0, y0 + h)]
    quad = rot(top, ang, cx, cy)
    t = h * .045
    m = w * .007  # el cartón de las tapas sobresale un poco de las páginas
    v = (0, t)
    tablero = [(quad[0][0] - m, quad[0][1] - m), (quad[1][0] + m, quad[1][1] - m),
               (quad[2][0] + m, quad[2][1] + m * 1.4 + t * .35), (quad[3][0] - m, quad[3][1] + m * 1.4 + t * .35)]
    sombra(cv, [tablero], blur=80 * SS, opacity=.6, off=(14 * SS, 56 * SS))
    sombra(cv, [tablero], blur=9 * SS, opacity=.5, off=(3 * SS, 9 * SS))
    d = ImageDraw.Draw(cv)
    d.polygon(tablero, fill=(40, 36, 34, 255))
    d.line([tablero[0], tablero[1]], fill=(88, 80, 74, 255), width=2 * SS)
    # canto de páginas apilado bajo la doble página
    a, b = quad[3], quad[2]
    pg = [a, b, (b[0] + v[0], b[1] + v[1]), (a[0] + v[0], a[1] + v[1])]
    d.polygon(pg, fill=(238, 231, 214, 255))
    rng = np.random.default_rng(seed)
    for i in range(60):
        tt = (i + rng.random()) / 60
        c = int(228 + rng.integers(-12, 8))
        d.line([(a[0], a[1] + v[1] * tt), (b[0], b[1] + v[1] * tt)], fill=(c, c - 6, c - 22, 255), width=SS)
    place(cv, spread, quad, shade=lambda im: cierre_luz(im, .08))
    cv = cv.resize((W // SS, H // SS), Image.LANCZOS).convert('RGB')
    cv.save(out, quality=90)


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    cub = glob.glob(src + '/*PORTADA_EN_NOIR.png')[0]
    libro_cerrado(cub, dst + '/05-pedro-zamora-en-noir-portada.jpg')
    esc = [
        ('*INTERIOR.png', (-2.0, .50, .47, .74, 11, 11)),
        ('*INTERIOR3.png', (1.6, .50, .47, .74, 12, 12)),
        ('*INTERIOR4.png', (-1.2, .50, .47, .74, 13, 13)),
        ('*INTERIOR6.png', (2.2, .50, .47, .74, 14, 14)),
    ]
    for n, (pat, (ang, fx, fy, ancho, seed, ms)) in enumerate(esc, 1):
        f = glob.glob(src + '/' + pat)[0]
        libro_abierto(f, dst + f'/05-pedro-zamora-en-noir-abierto-{n}.jpg', (2600, 1650), ang,
                      2600 * SS * fx, 1650 * SS * fy, ancho, seed, ms)
    print('ok')
