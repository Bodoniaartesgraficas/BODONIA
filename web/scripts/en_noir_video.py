"""Pone un vídeo de mockup (apaisado o vertical) sobre el fondo que sobra, en formato 3:4.

Uso: python3 web/scripts/en_noir_video.py <vídeo.mp4> <fondo> <salida.mp4> [escala, p. ej. 0.8]
En noir: salida 05-pedro-zamora-en-noir-interior-5.mp4; Territorios: 02-territorios-de-la-mirada-interior-3.mp4.
Sale 1080x1440, sin audio, en fotos/proyectos/.
"""
import sys, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageFilter
import santa_fe_fondos as sf

W, H = 1080, 1440
ANCHO = .88

def main(video, fondo, salida, escala=1):
    bg = sf.fondo(fondo).resize((W, H), Image.LANCZOS)
    vw, vh = map(int, subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                                "-of", "csv=p=0:s=x", video], text=True).strip().split("x"))
    w = round(W * ANCHO); h = round(w * vh / vw)
    if h > H * ANCHO:  # vídeos verticales: limita por el alto
        h = round(H * ANCHO); w = round(h * vw / vh)
    w = round(w * float(escala)); h = round(h * float(escala))
    w -= w % 2; h -= h % 2; x, y = (W - w) // 2, (H - h) // 2
    sombra = Image.new("L", (W, H), 0)
    sombra.paste(Image.new("L", (w, h), 255), (x + 4, y + 18))
    sombra = sombra.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * .5))
    bg.paste(Image.new("RGB", (W, H), (20, 14, 8)), (0, 0), sombra)
    tmp = Path(tempfile.mkdtemp()) / "fondo.png"; bg.save(tmp)
    out = sf.SITIO / salida
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(tmp), "-i", video,
        "-filter_complex", f"[1:v]scale={w}:{h}[v];[0:v][v]overlay={x}:{y}:shortest=1,format=yuv420p",
        "-an", "-c:v", "libx264", "-crf", "30", "-preset", "slow", "-movflags", "+faststart", str(out)], check=True)

if __name__ == "__main__":
    main(*sys.argv[1:5])
