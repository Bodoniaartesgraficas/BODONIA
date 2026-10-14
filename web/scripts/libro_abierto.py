import sys,glob
from PIL import Image,ImageFilter,ImageDraw
import numpy as np
f=sorted(glob.glob(sys.argv[1]));a,b=Image.open(f[0]).convert('RGB'),Image.open(f[1]).convert('RGB')
W=1000;pw=int(W*0.46)
def fit(im):return im.resize((pw,int(im.height*pw/im.width)),Image.LANCZOS)
a,b=fit(a),fit(b);ph=a.height
CW,CH=1000,1250
bg=Image.new('RGB',(CW,CH),(232,231,227))
# vertical soft gradient
arr=np.array(bg).astype(float);arr*= (1-0.06*np.linspace(0,1,CH))[:,None,None];bg=Image.fromarray(arr.astype('uint8'))
x0=(CW-2*pw)//2;y0=(CH-ph)//2
# drop shadow
sh=Image.new('L',(CW,CH),0);ImageDraw.Draw(sh).rectangle([x0+6,y0+22,x0+2*pw-6,y0+ph+26],fill=150)
sh=sh.filter(ImageFilter.GaussianBlur(22));bg.paste((60,55,50),(0,0),sh)
spread=Image.new('RGB',(2*pw,ph));spread.paste(a,(0,0));spread.paste(b,(pw,0))
# gutter shading
s=np.array(spread).astype(float);xs=np.arange(2*pw)-pw
g=1-0.38*np.exp(-(xs/ (pw*0.06))**2)- 0.10*np.exp(-(xs/(pw*0.3))**2)
s*=g[None,:,None];spread=Image.fromarray(np.clip(s,0,255).astype('uint8'))
bg.paste(spread,(x0,y0));bg.save(sys.argv[2],quality=85)
