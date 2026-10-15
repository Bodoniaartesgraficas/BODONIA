"""Quita el fondo gris de estudio de un vídeo de mockup y lo pone sobre el fondo del catálogo (3:4).

modo "negro": el recuadro del vídeo queda con fondo negro (como los vídeos de libro generados).
modo "fondo": sin recuadro; el libro va directamente sobre la imagen de fondo, con su sombra.
El fondo gris se modela como una superficie suave (polinomio) ajustada a la mediana de los fotogramas,
descartando el libro de forma iterativa; lo que se aparta de ese modelo es libro (o sombra).

Uso: python3 web/scripts/video_sin_fondo.py <vídeo.mp4> <fondo.jpg> <salida.mp4> <negro|fondo> [escala]
"""
import sys, subprocess
import numpy as np
from scipy import ndimage
from PIL import Image, ImageFilter
import santa_fe_fondos as sf

W, H = 1080, 1440
ANCHO = .88

def info(v):
    w, h = map(int, subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                             "-of", "csv=p=0:s=x", v], text=True).strip().split("x"))
    fps = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                                   "-of", "csv=p=0", v], text=True).strip()
    return w, h, fps

def lee(v, filtro, w, h):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", v, "-vf", filtro, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = w * h * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3).astype(np.float32)

def base(w, h, grado=3):
    y, x = np.mgrid[0:h, 0:w]; x = x / w - .5; y = y / h - .5
    return np.stack([x ** i * y ** j for i in range(grado + 1) for j in range(grado + 1 - i)], axis=-1).reshape(-1, (grado + 1) * (grado + 2) // 2)

def modelo_fondo(v, filtro, w, h):
    fr = np.array(list(lee(v, filtro.replace("scale=", "fps=4,scale="), w, h)))
    med = np.median(fr, axis=0).reshape(-1, 3)
    A = base(w, h)
    ok = np.ones(len(med), bool)
    for _ in range(6):
        c, *_ = np.linalg.lstsq(A[ok], med[ok], rcond=None)
        res = np.abs(med - A @ c).max(axis=1)
        ok = res < max(6, np.percentile(res[ok], 70) * 1.5)
    return (A @ c).reshape(h, w, 3)

def main(video, fondo, salida, modo, escala=1):
    vw, vh, fps = info(video)
    recorte = ""
    if vh * 3 > vw * 4:  # vertical: se recorta arriba y abajo a 3:4, centrado
        ch = vw * 4 // 3; ch -= ch % 2; recorte = f"crop={vw}:{ch}:0:{(vh - ch) // 2},"; vh = ch
    w = round(W * ANCHO * float(escala)); h = round(w * vh / vw)
    if h > H * ANCHO * float(escala):
        h = round(H * ANCHO * float(escala)); w = round(h * vw / vh)
    w -= w % 2; h -= h % 2; x0, y0 = (W - w) // 2, (H - h) // 2
    filtro = f"{recorte}scale={w}:{h}"
    B = modelo_fondo(video, filtro, w, h)
    bg = np.asarray(sf.fondo(fondo).resize((W, H), Image.LANCZOS)).astype(np.float32)
    if modo == "negro":  # recuadro negro con su sombra sobre el fondo
        sh = Image.new("L", (W, H), 0); sh.paste(255, (x0 + 4, y0 + 18, x0 + w + 4, y0 + h + 18))
        sh = np.asarray(sh.filter(ImageFilter.GaussianBlur(22)), np.float32)[..., None] / 255 * .5
        bg = bg * (1 - sh)
    out = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", fps, "-i", "-",
                            "-an", "-c:v", "libx264", "-crf", "26", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                            str(sf.SITIO / salida)], stdin=subprocess.PIPE)
    lum = B.mean(axis=2)
    yy, xx = np.mgrid[0:h, 0:w]
    borde = np.clip(np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]) / 50, 0, 1)[..., None]
    for f in lee(video, filtro, w, h):
        d = f - B
        m = d.mean(axis=2); croma = np.abs(d - m[..., None]).max(axis=2)
        ratio = f.mean(axis=2) / np.maximum(lum, 1)
        # libro: más claro que el estudio, con color propio, o muy oscuro (cubiertas negras); la sombra gris no cuenta
        a = np.maximum.reduce([np.clip((m - 8) / 14, 0, 1), np.clip((croma - 9) / 12, 0, 1), np.clip((.5 - ratio) / .15, 0, 1)])
        # rellena los huecos del libro (zonas de la cubierta parecidas al gris del estudio)
        lleno = ndimage.binary_fill_holes(ndimage.binary_closing(a > .5, iterations=6))
        a = np.maximum(a, lleno)
        a = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2)), np.float32)[..., None] / 255
        if modo == "fondo":
            a = a * borde  # el libro se funde al salir del encuadre del vídeo
        # sombra: donde el fotograma es más oscuro que el estudio
        osc = np.clip((lum - f.mean(axis=2)) / np.maximum(lum, 1), 0, 1)[..., None] * (1 - a)
        lienzo = bg.copy()
        zona = lienzo[y0:y0 + h, x0:x0 + w]
        if modo == "negro":
            zona[:] = f * a
        else:
            zona[:] = zona * (1 - np.clip(osc * 1.6, 0, .75)) * (1 - a) + f * a
        out.stdin.write(np.clip(lienzo, 0, 255).astype(np.uint8).tobytes())
    out.stdin.close(); out.wait()

if __name__ == "__main__":
    main(*sys.argv[1:6])
