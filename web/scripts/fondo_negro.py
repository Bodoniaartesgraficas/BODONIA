import sys,numpy as np
from PIL import Image,ImageFilter
from scipy import ndimage as nd
def neg(src,dst,lummax=236,satmax=16):
    im=Image.open(src).convert('RGB');a=np.array(im).astype(float)
    sat=a.max(2)-a.min(2);lum=a.mean(2)
    cand=(sat<satmax)&(lum<lummax)&(lum>120)
    cand=nd.binary_opening(cand,iterations=2)
    lab,n=nd.label(cand)
    edge=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    m=np.isin(lab,list(edge))
    m=nd.binary_closing(m,iterations=2)
    m=nd.binary_erosion(m,iterations=1) if False else m
    mf=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2))).astype(float)/255
    out=a*(1-mf[...,None])
    Image.fromarray(out.astype('uint8')).save(dst,quality=88)
if __name__=='__main__':
    neg(sys.argv[1],sys.argv[2],*map(float,sys.argv[3:]))
