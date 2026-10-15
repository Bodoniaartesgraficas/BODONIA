"""Genera un vídeo vertical (720x1280) de un libro que se abre en perspectiva y pasa páginas.

Es una versión sencilla del mockup 3D: portada que se abre y dos pasos de página sobre un fondo gris de estudio.
Uso: python3 web/scripts/libro_video.py <portada.png (solo la cara frontal, o desplegada con 2 caras)> <doble1.jpg> <doble2.jpg> <doble3.jpg> <salida.mp4>
Después se coloca sobre el fondo con en_noir_video.py.
"""
import sys, math, subprocess
import numpy as np
from PIL import Image, ImageFilter

VW, VH, FPS = 720, 1280, 24
PW, PH = 1.0, 1.43          # página: ancho y alto en unidades del libro
PHI = math.radians(52)      # elevación de la cámara
DIST = 6.0

def recorta_claro(im, umbral=20):
    a = np.asarray(im.convert("RGB")).max(axis=2) > umbral
    ys, xs = np.where(a)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

def mitades(im):
    im = im.convert("RGB"); w = im.width // 2
    t = (360, 515)
    return im.crop((0, 0, w, im.height)).resize(t, Image.LANCZOS), im.crop((w, 0, im.width, im.height)).resize(t, Image.LANCZOS)

def portada(ruta):
    im = Image.open(ruta).convert("RGB")
    # el PDF trae marcas de corte: nos quedamos con el rectángulo del color de fondo
    a = np.asarray(im).astype(int); c = a[a.shape[0] // 2, 5]
    m = (abs(a - c).sum(axis=2) < 40)
    ys, xs = np.where(m); 
    cols = np.where(m.mean(axis=0) > .5)[0]; rows = np.where(m.mean(axis=1) > .5)[0]
    return im.crop((cols.min(), rows.min(), cols.max() + 1, rows.max() + 1))

def proyecta(p, cx, zoom):
    x, y, z = p
    up = np.array([0, math.sin(PHI), math.cos(PHI)]); d = np.array([0, math.cos(PHI), -math.sin(PHI)])
    tgt = np.array([cx, PH / 2, 0]); cam = tgt - DIST * d
    v = np.array([x, y, z]) - cam
    depth = v @ d
    f = 317 * DIST * zoom
    return (VW / 2 + f * v[0] / depth, VH / 2 - f * (v @ up) / depth + 40)

def coef(dst, src):
    A = []; B = []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))

def pinta(lienzo, mascara, tex, quad3, cx, zoom, sombra=1.0):
    """Dibuja la textura (rectángulo) sobre el cuadrilátero 3D (4 esquinas: sup-izq, sup-der, inf-der, inf-izq)."""
    q = [proyecta(p, cx, zoom) for p in quad3]
    w, h = tex.size
    try:
        k = coef(q, [(0, 0), (w, 0), (w, h), (0, h)])
    except np.linalg.LinAlgError:  # hoja de canto: no se ve
        return
    t = tex if sombra == 1 else Image.eval(tex, lambda v: int(v * sombra))
    t = t.convert("RGBA")
    out = t.transform((VW, VH), Image.PERSPECTIVE, tuple(k), Image.BILINEAR)
    lienzo.alpha_composite(out)
    m = out.getchannel("A"); mascara.paste(255, (0, 0), m)

def hoja(lienzo, mascara, frente, dorso, ang, cx, zoom):
    """Hoja con bisagra en x=0 girada ang grados (0 = sobre la derecha, 180 = sobre la izquierda), con algo de curvatura."""
    N = 10; bend = .32 * math.sin(math.radians(ang)); th0 = math.radians(ang)
    pts = [(0.0, 0.0)]  # (x, z)
    for j in range(N):
        a = th0 - bend * (j / N)
        pts.append((pts[-1][0] + PW / N * math.cos(a), pts[-1][1] + PW / N * math.sin(a)))
    cara_frente = ang < 90
    tex = frente if cara_frente else dorso
    for j in range(N):
        (x0, z0), (x1, z1) = pts[j], pts[j + 1]
        if cara_frente:
            a, b = j / N, (j + 1) / N
        else:
            a, b = 1 - (j + 1) / N, 1 - j / N   # dorso: se ve invertido en horizontal
        W, H = tex.size
        sub = tex.crop((round(a * W), 0, round(b * W), H))
        if not cara_frente:
            sub = sub.transpose(Image.FLIP_LEFT_RIGHT)
        sh = .78 + .22 * abs(math.cos(math.radians(ang))) if True else 1
        pinta(lienzo, mascara, sub, [(x0, PH, z0 + .02), (x1, PH, z1 + .02), (x1, 0, z1 + .02), (x0, 0, z0 + .02)], cx, zoom, sh)

def fondo_gris():
    yy, xx = np.mgrid[0:VH, 0:VW]
    r = np.sqrt(((xx - VW * .45) / VW) ** 2 + ((yy - VH * .42) / VH) ** 2)
    g = np.clip(222 - 70 * r, 0, 255)
    img = np.stack([g, g * .975, g * .955], axis=2).astype("uint8")
    return Image.fromarray(img).convert("RGBA")

def ease(t): return t * t * (3 - 2 * t)
def tramo(t, a, b): return min(1, max(0, (t - a) / (b - a)))

def main(portada_png, d1, d2, d3, salida):
    cov = Image.open(portada_png).convert("RGB")
    if cov.width > cov.height:  # portada desplegada (contraportada + portada): nos quedamos con la mitad derecha
        cov = portada(portada_png); cw = cov.width // 2
        cov = cov.crop((cw, 0, cov.width, cov.height))
    frente_cub = cov.resize((360, 515), Image.LANCZOS)
    S = [mitades(recorta_claro(Image.open(p))) for p in (d1, d2, d3)]
    papel = Image.new("RGB", (360, 515), (232, 226, 217))
    bg = fondo_gris()
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}", "-r", str(FPS), "-i", "-",
                           "-an", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", salida], stdin=subprocess.PIPE)
    total = 11.5
    for n in range(int(total * FPS)):
        t = n / FPS
        a0 = ease(tramo(t, 1.2, 3.2)) * 180
        a1 = ease(tramo(t, 5.0, 6.6)) * 180
        a2 = ease(tramo(t, 8.2, 9.8)) * 180
        cx = .5 * (1 - ease(tramo(t, 1.2, 3.0)))
        zoom = 1.0 + .55 * (1 - ease(tramo(t, 1.2, 3.4))) - .03 * tramo(t, 0, 1.2)
        lienzo = bg.copy(); capa = Image.new("RGBA", (VW, VH), (0, 0, 0, 0)); masc = Image.new("L", (VW, VH), 0)
        # pilas de hojas (grosor)
        for i in range(6, 0, -1):
            g = 215 - 4 * i
            for side in ((0, 1),) + (((-1, 0),) if a0 > 20 else ()):
                x0, x1 = side
                pinta(capa, masc, Image.new("RGB", (8, 8), (g, g - 4, g - 10)), [(x0 * PW + .01, PH, -.014 * i), (x1 * PW + .01 if x1 else 0, PH, -.014 * i), (x1 * PW if x1 else 0, 0, -.014 * i), (x0 * PW, 0, -.014 * i)], cx, zoom)
        # hojas por debajo
        if a1 > 0 or a2 > 0 or a0 >= 180:
            pass
        estado = 0 if a1 == 0 else (1 if a2 == 0 else 2)
        # página derecha de debajo y izquierda
        def pag(tex, x0, x1):
            pinta(capa, masc, tex, [(x0, PH, 0), (x1, PH, 0), (x1, 0, 0), (x0, 0, 0)], cx, zoom)
        if a0 < 180:
            pag(S[0][1], 0, PW)                      # derecha del primer doble (bajo la portada)
        else:
            if estado == 0:
                pag(S[0][0], -PW, 0); pag(S[0][1], 0, PW)
                if a1 > 0: pass
            elif estado == 1:
                pag(S[1][0], -PW, 0); pag(S[1][1], 0, PW)
            else:
                pag(S[2][0], -PW, 0); pag(S[2][1], 0, PW)
        if 0 < a1 < 180 or (a1 == 180 and a2 == 0):
            pass
        # la izquierda bajo una hoja en giro
        if a0 >= 180 and 0 < a1 < 180: pag(S[0][0], -PW, 0); pag(S[1][1], 0, PW)
        if a1 >= 180 and 0 < a2 < 180: pag(S[1][0], -PW, 0); pag(S[2][1], 0, PW)
        # hojas en giro / aterrizadas
        if a0 < 180: hoja(capa, masc, frente_cub, S[0][0], a0, cx, zoom)
        if 0 < a1 < 180: hoja(capa, masc, S[0][1], S[1][0], a1, cx, zoom)
        if 0 < a2 < 180: hoja(capa, masc, S[1][1], S[2][0], a2, cx, zoom)
        # sombra proyectada
        sh = Image.new("L", (VW, VH), 0); sh.paste(masc.transform((VW, VH), Image.AFFINE, (1, 0, -10, 0, 1, -26)), (0, 0))
        sh = sh.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * .45))
        lienzo.paste(Image.new("RGBA", (VW, VH), (30, 24, 18, 255)), (0, 0), sh)
        lienzo.alpha_composite(capa)
        ff.stdin.write(lienzo.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()

if __name__ == "__main__":
    main(*sys.argv[1:6])
