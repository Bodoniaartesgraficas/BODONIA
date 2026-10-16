import subprocess
from PIL import Image
# ancho de recorte (sobre 1920x1080) por plano; 1080 = cuadrado real
CW=[1080,1080,1700,1600,1500,1920,1920,1500,1920,1500,1600,1080]
FONDO=(7,6,5); L=1080; F=70
for i,cw in enumerate(CW):
    h=round(L*1080/cw/2)*2; top=(L-h)//2
    m=Image.new("RGBA",(L,L),FONDO+(0,))
    if h<L:
        px=m.load()
        for y in range(L):
            d=min(y-top,top+h-1-y)
            a=255 if d<0 else max(0,255-int(255*d/F)) if d<F else 0
            for x in range(L): px[x,y]=FONDO+(a,)
    m.save(f"m{i:02d}.png")
    vf=(f"[0:v]crop={cw}:1080:(1920-{cw})/2:0,scale={L}:{h},pad={L}:{L}:0:{top}:color=0x070605[v];"
        f"[v][1:v]overlay=0:0,format=yuv420p")
    subprocess.run(["ffmpeg","-v","error","-y","-i",f"t{i:02d}.mp4","-i",f"m{i:02d}.png","-filter_complex",vf,
        "-c:v","libx264","-crf","14","-preset","fast",f"q{i:02d}.mp4"],check=True)
