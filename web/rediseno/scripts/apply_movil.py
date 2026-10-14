import re,shutil
P='bodonia/project/'
COMMON='h1,h2,section,footer,form,div[style*="height:"]{height:auto!important}h1,h2,.wrap,div[style*="width:"]{width:auto!important;max-width:100%}form{width:100%!important}'
MAIN='@media(max-width:700px){'+COMMON+'''
.nav{flex-direction:column!important;align-items:flex-start!important;gap:0!important}
.nav img{height:50px!important}
.nav a{padding:8px 0}
.links{display:flex!important;gap:8px 18px!important;width:100%;justify-content:space-between;flex-wrap:wrap}
.hero-t{font-size:7vw!important}
#inicio .label{font-size:12px!important;letter-spacing:.08em!important}
#trabajos{padding-bottom:48px!important}
#trabajos>.wrap{padding-bottom:44px}
#taller+*{margin-top:44px}
.gal{gap:26px 12px}
.gal12{gap:22px 12px}
.t4,.t3{grid-column:span 6!important}
.gal12 .cap,.gal12 .t3 .cap{flex-direction:column;text-align:left;gap:2px;font-size:13px;white-space:normal}
.cap{font-size:14px;gap:10px}
#taller{padding:52px 0!important}
#taller .wrap{gap:36px!important}
#taller p[style*="font-size: 26px"],#taller div[style*="font-size: 26px"]{font-size:19px!important}
#taller p[style*="font-size: 19px"]{font-size:17px!important}
#taller .split{gap:14px;padding-top:28px}
#otros{padding-bottom:52px!important}
#contacto{padding-top:52px!important}
#contacto div[style*="align-items: baseline"]{flex-direction:column}
#contacto div[style*="text-align: right"]{text-align:left!important}
#contacto .two{gap:22px!important}
#contacto form{padding:24px 20px!important}
#contacto form button{align-self:stretch!important;min-height:52px}
.legal summary{font-size:17px}
}
'''
LOCA='@media(max-width:700px){'+COMMON+'''
#inicio>.wrap:first-child{flex-direction:column;align-items:flex-start!important;gap:4px!important;padding-top:12px!important}
#inicio>.wrap:first-child img{height:52px!important}
#inicio nav{font-size:16px!important;gap:0 18px!important}
#inicio nav a{padding:10px 0!important}
#inicio>.wrap+.wrap{padding-top:22px!important;padding-bottom:40px!important}
#inicio h1{gap:26px!important}
#catalogos>h2{margin-bottom:20px!important}
.marq{font-size:17px!important;padding:10px 0!important}
#catalogos{padding:44px 0 32px!important}
#catalogos>h2,#trabajos>h2{padding:0 18px}
.pila{gap:26px 0}
.videos{gap:22px!important}
.tit{font-size:17px}
#trabajos{padding:44px 0 20px!important}
#trabajos .wrap{padding-bottom:20px!important}
.pista{gap:16px}
.pista figcaption{font-size:14px;flex-direction:column;gap:2px}
#taller{padding:20px 0 60px!important}
#taller div[aria-hidden]{font-size:150px!important}
#taller .wrap+.wrap{padding-top:44px!important}
#contacto{padding:56px 0 24px!important}
#contacto .wrap{gap:32px!important}
#contacto [style*="font-size: 34px"]{font-size:22px!important}
#contacto .dos{font-size:17px!important}
#contacto form{padding:22px 18px!important;box-shadow:8px 8px 0 #141414!important;box-sizing:border-box}
.legal summary{font-size:19px}
}
'''
for f,css in(('Main',MAIN),('Loca',LOCA)):
    s=open(P+f+'.dc.html').read()
    s=re.sub(r'/\*MOVIL\*/.*?/\*FIN\*/\n','',s,flags=re.S)
    assert s.count('</style>')==1
    s=s.replace('</style>','/*MOVIL*/'+css+'/*FIN*/\n</style>')
    open(P+f+'.dc.html','w').write(s)
    t=s.replace('"width":1360','"width":390')
    open(P+f+'Movil.dc.html','w').write(t)
    # plain test html
    h=s[s.index('<helmet>')+8:s.index('</helmet>')];b=s[s.index('</helmet>')+9:s.index('</x-dc>')]
    open(f'mob/{f}.html','w').write('<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">'+h+b)
