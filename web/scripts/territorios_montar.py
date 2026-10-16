import subprocess, sys
SRC="/mnt/project-files/IMG_3251.MOV"
# (inicio, duracion_salida, velocidad, (cx,cy,w) inicio, (cx,cy,w) fin)
PLANOS=[
 (0.3, 2.0,1.0,(.55,.46,.92),(.55,.46,.84)),   # portada
 (10.5,1.4,1.0,(.55,.42,.80),(.55,.42,.76)),   # lomo
 (16.4,1.4,1.0,(.56,.45,.94),(.56,.45,.90)),   # texto y retratos
 (19.2,1.3,1.0,(.58,.48,.90),(.60,.48,.86)),   # doble de retratos
 (21.8,1.3,1.0,(.56,.46,.90),(.56,.46,.86)),   # guarda roja
 (26.4,1.8,1.0,(.50,.50,1.0),(.50,.50,.96)),   # cuadríptico
 (34.0,1.8,1.0,(.50,.48,1.0),(.52,.48,.94)),   # tríptico color
 (38.6,1.2,1.0,(.58,.47,.88),(.58,.47,.84)),   # ventanas de noche
 (45.0,2.4,1.0,(.50,.47,1.0),(.54,.46,.92)),   # desplegable de paisajes
 (54.3,2.0,1.25,(.56,.48,.92),(.56,.48,.88)),  # pase de páginas
 (60.2,1.2,1.0,(.56,.52,.90),(.56,.52,.86)),   # paisajes
 (64.9,2.4,1.0,(.55,.42,.80),(.55,.42,.88)),   # portada final
]
FPS=30
def tramo(i,p):
    t0,d,v,a,b=p; n=round(d*FPS)
    s=f"(max(0,on-4)/{n-1})"; s=f"({s}*{s}*(3-2*{s}))"
    L=lambda k:f"({a[k]}+({b[k]}-{a[k]})*{s})"
    z=f"(1/{L(2)})"
    x=f"max(0,min(iw-iw/zoom,{L(0)}*iw-iw/zoom/2))"
    y=f"max(0,min(ih-ih/zoom,{L(1)}*ih-ih/zoom/2))"
    vf=(f"transpose=2,setpts=(PTS-STARTPTS)/{v},fps={FPS},"
        f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s=1920x1080:fps={FPS},"
        "curves=all='0/0 0.12/0.06 0.3/0.27 1/1',trim=start_frame=4,setpts=PTS-STARTPTS,format=yuv420p")
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(t0),"-t",str(d*v+0.4),"-i",SRC,"-an",
        "-vf",vf,"-frames:v",str(n),"-c:v","libx264","-crf","16","-preset","fast",f"t{i:02d}.mp4"],check=True)
sel=[int(a) for a in sys.argv[1:]] or range(len(PLANOS))
for i in sel: tramo(i,PLANOS[i]); print(i,flush=True)
