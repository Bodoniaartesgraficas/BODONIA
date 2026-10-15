"""Vídeo final de cada catálogo a partir de un render del cliente: libro sólido sobre negro liso, 3:4 (1080x1440).

El libro se recorta fotograma a fotograma con U2-Net (paquete rembg) y se rellenan sus huecos, para que el
negro nunca entre dentro del libro. Encuadre:
  - vídeo vertical: ancho completo y se recorta arriba y abajo a 3:4, centrado en el libro;
  - vídeo apaisado: el menor 3:4 que contiene el libro en todo el vídeo (lo que sobra es negro).
Requiere: python3 -m pip install "rembg[cpu]"
Uso: python3 web/scripts/video_sin_fondo.py <vídeo.mp4> <salida.mp4 en fotos/proyectos>
"""
import sys, subprocess
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
from rembg import remove, new_session
import santa_fe_fondos as sf

W, H = 1080, 1440
MW = 640  # ancho de trabajo para las máscaras

def info(v):
    w, h = map(int, subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                             "-of", "csv=p=0:s=x", v], text=True).strip().split("x"))
    fps = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                                   "-of", "csv=p=0", v], text=True).strip()
    return w, h, fps

def lee(v, w, h):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", v, "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = w * h * 3
    while (b := p.stdout.read(n)) and len(b) == n:
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)

def mascara(f, sesion):
    m = np.asarray(remove(Image.fromarray(f), session=sesion, only_mask=True), np.float32) / 255
    solido = ndimage.binary_fill_holes(ndimage.binary_closing(m > .5, iterations=3))  # sin huecos dentro del libro
    return np.maximum(np.clip((m - .25) / .5, 0, 1), solido).astype(np.float32)

def main(video, salida):
    vw, vh, fps = info(video)
    mh = round(vh * MW / vw)
    sesion = new_session("u2net")
    mascaras = [(mascara(f, sesion) * 255).astype(np.uint8) for f in lee(video, MW, mh)]
    # caja del libro: percentiles de las cajas de cada fotograma (un primer plano suelto no encoge todo)
    cajas = []
    for m in mascaras:
        ys, xs = np.where(m > 128)
        if len(xs): cajas.append((xs.min(), ys.min(), xs.max(), ys.max()))
    c = np.array(cajas); k = vw / MW
    x0, y0 = np.percentile(c[:, 0], 5) * k, np.percentile(c[:, 1], 5) * k
    x1, y1 = np.percentile(c[:, 2], 95) * k, np.percentile(c[:, 3], 95) * k
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if vh * 3 > vw * 4:  # vertical: ancho completo, recorte arriba y abajo
        ww = vw; hh = ww * 4 / 3; cx = vw / 2
        cy = min(max(cy, hh / 2), vh - hh / 2)
    else:  # apaisado: el menor 3:4 que contiene el libro, con margen
        bw, bh = (x1 - x0) * 1.12, (y1 - y0) * 1.12
        ww = max(bw, bh * 3 / 4); hh = ww * 4 / 3
    s = W / ww  # escala vídeo -> salida
    ow, oh = round(vw * s), round(vh * s)
    ox, oy = round(W / 2 - cx * s), round(H / 2 - cy * s)  # posición del vídeo escalado dentro de la salida
    out = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", fps, "-i", "-",
                            "-an", "-c:v", "libx264", "-crf", "24", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                            str(sf.SITIO / salida)], stdin=subprocess.PIPE)
    # zona visible del vídeo escalado
    ax0, ay0 = max(0, -ox), max(0, -oy); ax1, ay1 = min(ow, W - ox), min(oh, H - oy)
    for f, m in zip(lee(video, ow, oh), mascaras):
        a = np.asarray(Image.fromarray(m).resize((ow, oh), Image.BILINEAR), np.float32)[ay0:ay1, ax0:ax1, None] / 255
        lienzo = np.zeros((H, W, 3), np.float32)
        lienzo[ay0 + oy:ay1 + oy, ax0 + ox:ax1 + ox] = f[ay0:ay1, ax0:ax1] * a
        out.stdin.write(lienzo.astype(np.uint8).tobytes())
    out.stdin.close(); out.wait()

if __name__ == "__main__":
    main(*sys.argv[1:3])
