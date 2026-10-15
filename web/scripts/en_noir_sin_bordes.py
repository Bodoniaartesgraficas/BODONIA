import numpy as np, sys
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, gaussian_filter
src,dst=sys.argv[1:3]
im=Image.open(src).convert('RGB');W,H=im.size;a=np.array(im).astype(float)
q=[(544,510),(1116,750),(744,1424),(120,1196)]
m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(q,fill=255);m=np.array(m)>127
band=binary_dilation(m,iterations=40)
lum=a.mean(2);sat=a.max(2)-a.min(2)
claro=band&(lum>165)&(sat<40)
# franja del canto: lado derecho e inferior del libro (las páginas blancas)
f=Image.new('L',(W,H));d=ImageDraw.Draw(f)
TR,BR,BL=np.array(q[1]),np.array(q[2]),np.array(q[3])
for p0,p1 in [(TR,BR),(BR,BL)]:
    n=np.array([p1[1]-p0[1],-(p1[0]-p0[0])],float);n/=np.linalg.norm(n)
    d.polygon([tuple(p0-n*2),tuple(p1-n*2),tuple(p1+n*16),tuple(p0+n*16)],fill=255)
canto=np.array(f)>127
claro=(claro|(canto&(lum>70)&(sat<50)))
claro=binary_dilation(claro,iterations=1)&band&(lum>70)
w=gaussian_filter(claro.astype(float),1.2)
oscuro=np.clip(a*.22,0,255)
a=a*(1-w[...,None])+oscuro*w[...,None]
Image.fromarray(a.astype('uint8')).save(dst,quality=92)
print(claro.sum())
