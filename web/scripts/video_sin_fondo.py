"""Quita el fondo gris de estudio de un vídeo de mockup y lo pone sobre el fondo del catálogo (3:4).

modo "negro": el recuadro del vídeo queda con fondo negro (como los vídeos de libro generados).
modo "fondo": sin recuadro; el libro va directamente sobre la imagen de fondo, con su sombra.
El libro se recorta fotograma a fotograma con U2-Net (paquete rembg), que lo deja sólido aunque tenga
zonas del mismo gris que el estudio. Requiere: python3 -m pip install "rembg[cpu]".

Uso: python3 web/scripts/video_sin_fondo.py <vídeo.mp4> <fondo.jpg> <salida.mp4> <negro|fondo> [escala]
"""
import sys, subprocess
import numpy as np
from rembg import remove, new_session
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
    bg = np.asarray(sf.fondo(fondo).resize((W, H), Image.LANCZOS)).astype(np.float32)
    if modo == "negro":  # recuadro negro con su sombra sobre el fondo
        sh = Image.new("L", (W, H), 0); sh.paste(255, (x0 + 4, y0 + 18, x0 + w + 4, y0 + h + 18))
        sh = np.asarray(sh.filter(ImageFilter.GaussianBlur(22)), np.float32)[..., None] / 255 * .5
        bg = bg * (1 - sh)
    out = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", fps, "-i", "-",
                            "-an", "-c:v", "libx264", "-crf", "26", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                            str(sf.SITIO / salida)], stdin=subprocess.PIPE)
    yy, xx = np.mgrid[0:h, 0:w]
    borde = np.clip(np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]) / 50, 0, 1)[..., None]
    sesion = new_session("u2net")
    prev = None
    for f in lee(video, filtro, w, h):
        # máscara del libro con U2-Net (rembg): el libro queda sólido, sin mezclarse con el fondo
        m = np.asarray(remove(Image.fromarray(f.astype(np.uint8)), session=sesion, only_mask=True), np.float32) / 255
        m = np.clip((m - .1) / .8, 0, 1)
        if prev is not None: m = .7 * m + .3 * prev  # suaviza el parpadeo entre fotogramas
        prev = m
        a = m[..., None]
        if modo == "fondo":
            a = a * borde  # el libro se funde al salir del encuadre del vídeo
            som = np.asarray(Image.fromarray((a[..., 0] * 255).astype(np.uint8)).transform((w, h), Image.AFFINE, (1, 0, -8, 0, 1, -22))
                             .filter(ImageFilter.GaussianBlur(18)), np.float32)[..., None] / 255 * .55
        lienzo = bg.copy()
        zona = lienzo[y0:y0 + h, x0:x0 + w]
        if modo == "negro":
            zona[:] = f * a
        else:
            zona[:] = zona * (1 - som) * (1 - a) + f * a
        out.stdin.write(np.clip(lienzo, 0, 255).astype(np.uint8).tobytes())
    out.stdin.close(); out.wait()

if __name__ == "__main__":
    main(*sys.argv[1:6])
