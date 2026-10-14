import re,json
P='bodonia/project/'
m=open('live/project/Main.dc.html').read()
figs=re.findall(r'<figure class="work[^"]*".*?</figure>',m,flags=re.S)
cat=[f for f in figs if re.search(r'class="work c\d',f)];tra=[f for f in figs if re.search(r'class="work t\d',f)]
legal=m[m.index('<section id="legal"'):];legal=legal[:legal.index('</section>')+10]
legal=re.sub(r'<section id="legal"[^>]*>','<section id="legal">',legal)
script=m[m.index('<script type="text/x-dc"'):m.index('</script>',m.index('<script type="text/x-dc"'))+9]
def clean(f):
    f=re.sub(r'class="work [ct]\d"','class="work"',f);return re.sub(r' style="margin: 0"','',f,count=1)
cats=''.join(clean(f) for f in cat);tr=''.join(clean(f) for f in tra)
LOGO='/_blob/0b2d9e7a5215291be84e7cc8fb5d8b90'
css='''
body{margin:0}html{scroll-behavior:smooth}
.pg{--n:#161616;--c:#ECE6D2;--r:#9A0015;font-family:'Bodoni Moda','Bodoni MT',Didot,serif;font-optical-sizing:auto;background:var(--n);color:var(--c);line-height:1.5;overflow-x:hidden}
.pg a{color:inherit}
.w{max-width:1280px;margin:0 auto;padding:0 32px}
.disp{font-weight:900;text-transform:uppercase;letter-spacing:-.01em;line-height:.9;margin:0}
.pill{display:inline-flex;align-items:center;border:1.5px solid currentColor;border-radius:999px;padding:3px 16px;font-style:italic;font-size:17px;line-height:1.3;white-space:nowrap}
.pill.s{background:var(--c);color:var(--n);border-color:var(--c)}
.dot{display:inline-block;width:18px;height:18px;border-radius:50%;border:1.5px solid currentColor;flex-shrink:0}
.dot.f{background:var(--c)}
.glass{position:absolute;border-radius:999px;border:1px solid rgba(236,230,210,.14);background:radial-gradient(rgba(236,230,210,.10) 1px,transparent 1.5px) 0 0/4px 4px,rgba(22,22,22,.25);-webkit-backdrop-filter:blur(7px);backdrop-filter:blur(7px);box-shadow:0 10px 30px rgba(0,0,0,.35);pointer-events:none}
.nav{display:flex;justify-content:space-between;align-items:center;padding:22px 0;font-size:15px;font-style:italic}
.nav span{display:flex;gap:10px;flex-wrap:wrap}
.nav span a{text-decoration:none;border:1px solid rgba(236,230,210,.4);border-radius:999px;padding:6px 14px}
.nav span a:hover{background:var(--c);color:var(--n)}
.hero{position:relative;padding:90px 0 120px}
.hero .t{position:relative;width:max-content;max-width:100%;margin:0 auto}
.hero h1{font-size:clamp(40px,9.4vw,136px);text-align:center;white-space:nowrap}
.hero h1 span{display:block}
.hero .top{display:flex;gap:8px;align-items:center;margin:0 0 14px 4px}
.hero .bot{display:flex;gap:10px;align-items:center;justify-content:flex-end;margin-top:16px}
.cards{display:grid;grid-template-columns:1.05fr 1fr 1fr;gap:12px;padding:12px;background:var(--c);border-radius:22px;color:var(--n)}
.card{background:#E2DBC4;border-radius:16px;padding:26px;display:flex;flex-direction:column;gap:14px}
.card h3{font-weight:900;text-transform:uppercase;font-size:26px;line-height:1;margin:0}
.card p{margin:0;font-size:16px}
.card .pill{font-size:15px;border-width:1px;padding:2px 12px}
.tags{display:flex;flex-wrap:wrap;gap:8px}
.card.n{background:var(--n);color:var(--c);justify-content:center;align-items:center}
.ct{display:flex;flex-direction:column;gap:8px;font-size:16px}
.ct a{text-decoration:none}
.big{position:relative;border-top:1px solid rgba(236,230,210,.35);border-bottom:1px solid rgba(236,230,210,.35);margin:110px 0 0;padding:34px 0 28px;text-align:center}
.big h2{font-size:clamp(56px,12vw,176px)}
.big .pill{margin-top:14px;font-size:15px}
.big .star{position:absolute;top:10px;font-size:22px;line-height:1}
.bar{display:flex;align-items:center;gap:18px;padding:16px 0;margin:24px 0 26px;border-bottom:1px solid rgba(236,230,210,.35)}
.bar h3{font-weight:900;text-transform:uppercase;font-size:28px;margin:0;line-height:1;white-space:nowrap}
.bar i{flex:1;height:1px;background:rgba(236,230,210,.45);min-width:30px}
.gal{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:30px 16px}
.gal3{grid-template-columns:repeat(3,minmax(0,1fr));gap:26px 12px}
.gal3 .work:last-child:nth-child(3n+1){grid-column:2}
.gal:not(.gal3) .work:last-child:nth-child(odd){grid-column:1 / -1;width:calc(50% - 8px);justify-self:center}
.work{margin:0;display:flex;flex-direction:column;gap:10px}
.shot{width:100%;aspect-ratio:5/3;object-fit:cover;display:block;border-radius:14px;background:#222}
.cap{display:flex;flex-direction:row-reverse;justify-content:center;gap:10px;align-items:center;font-size:15px;text-align:center;flex-wrap:wrap}
.cap span{font-style:italic;border:1px solid rgba(236,230,210,.55);border-radius:999px;padding:0 10px;font-size:14px}
.form{margin:0 auto;max-width:680px;background:var(--c);color:var(--n);border-radius:22px;padding:36px;display:flex;flex-direction:column;gap:14px;box-sizing:border-box}
.field{display:flex;flex-direction:column;gap:6px;font-size:14px;font-style:italic}
.field input,.field textarea{font:inherit;font-style:normal;font-size:16px;padding:12px 16px;border:1.5px solid var(--n);background:transparent;color:var(--n);border-radius:14px;resize:vertical}
.field input[type=file]{border:0;padding:6px 0}
.field input:focus,.field textarea:focus{outline:2px solid var(--r);outline-offset:1px}
.form button{align-self:center;background:var(--n);color:var(--c);border:0;border-radius:999px;padding:13px 34px;font:inherit;font-style:italic;font-size:18px;cursor:pointer;min-height:48px;transition:transform .16s cubic-bezier(.23,1,.32,1)}
.form button:active{transform:scale(.97)}
.fin{position:relative;text-align:center;padding:120px 0 70px}
.fin h2{font-size:clamp(46px,9vw,132px)}
.fin .sub{display:flex;justify-content:center;align-items:center;gap:10px;margin-top:18px}
.flechas{display:flex;align-items:center;justify-content:space-between;gap:16px;border-top:1px solid rgba(236,230,210,.35);border-bottom:1px solid rgba(236,230,210,.35);padding:14px 0;flex-wrap:wrap}
.flechas b{font-size:22px;letter-spacing:-.1em;font-weight:400}
.flechas div{display:flex;gap:14px;flex-wrap:wrap;justify-content:center}
.flechas a{text-decoration:none}
#legal{padding:56px 32px 40px;max-width:1280px;margin:0 auto}
.label{font-weight:900;text-transform:uppercase;font-size:24px;margin:0 0 14px}
.legal{border-top:1px solid rgba(236,230,210,.3)}
.legal summary{cursor:pointer;font-size:19px;font-style:italic;padding:16px 0;min-height:44px;box-sizing:border-box}
.legal-b{display:flex;flex-direction:column;gap:12px;font-size:15px;max-width:820px;padding:0 0 26px;opacity:.85}
.pie{max-width:1280px;margin:0 auto;padding:0 32px 34px;font-size:13px;font-style:italic;opacity:.75}
a,button,summary{-webkit-tap-highlight-color:transparent}
@media(max-width:860px){.w{padding:0 18px}.nav{flex-direction:column;align-items:flex-start;gap:10px}.hero{padding:50px 0 70px}.cards{grid-template-columns:1fr;border-radius:18px}.big{margin-top:70px}.bar{flex-wrap:wrap;gap:10px}.bar h3{font-size:22px}.bar i{display:none}.gal{grid-template-columns:1fr}.gal:not(.gal3) .work:last-child:nth-child(odd){width:100%}.hero h1{white-space:normal}.gal3{grid-template-columns:repeat(2,minmax(0,1fr))}.gal3 .work:last-child:nth-child(3n+1){grid-column:auto}.gal3 .cap{flex-direction:column;gap:4px;font-size:13px}.form{padding:24px 18px}.form button{align-self:stretch}.fin{padding:80px 0 50px}.fin .sub .pill{white-space:normal}.flechas b{display:none}.glass{display:none}#legal{padding:44px 18px 28px}.pie{padding:0 18px 28px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition-duration:.01ms!important}}
'''
def big(t,sub):
    return f'<div class="big"><span class="star" style="left: 6px">✳</span><span class="star" style="right: 6px">✳</span><h2 class="disp">{t}</h2><span class="pill">{sub}</span></div>'
def bar(t,note): return f'<div class="bar"><h3>✳ {t}</h3><i></i><span class="pill">{note}</span></div>'
body=f'''<div class="pg">
<div class="w">
<nav class="nav" aria-label="Principal"><a href="#inicio" style="text-decoration: none">Bodonia Artes Gráficas S.L.</a><span><a href="#catalogos">Catálogos</a><a href="#trabajos">Trabajos</a><a href="#taller">El taller</a><a href="#contacto">Contacto</a></span></nav>
<section id="inicio" class="hero"><div class="t">
<div class="top"><span class="dot"></span><span class="pill">Desde hace más de 35 años</span></div>
<h1 class="disp"><span>Bodonia</span><span>Artes Gráficas</span></h1>
<div class="glass" style="left: 46%; top: 21%; width: 40%; height: 24%"></div>
<div class="glass" style="left: -6%; top: 58%; width: 44%; height: 22%"></div>
<div class="bot"><span class="dot f"></span><span class="pill s">S.L. · La Zubia, Granada</span></div>
</div></section>
<section id="taller" class="cards">
<div class="card n"><img src="{LOGO}" alt="Logo de Bodonia Artes Gráficas" style="width: 92%; max-width: 380px; height: auto; display: block; background: #ECE6D2; border-radius: 12px; padding: 18px 14px; box-sizing: border-box"></div>
<div class="card"><h3>El taller</h3><div class="tags"><span class="pill">Offset</span><span class="pill">Digital</span><span class="pill">+35 años</span></div><p style="font-size: 20px; line-height: 1.25; font-style: italic">Tú traes la idea. Nosotros, más de 35 años de imprenta.</p><p>Bodonia Artes Gráficas es un taller de La Zubia al que se puede venir con un archivo terminado o con solo una intención. Te ayudamos a elegir formato, papel y acabado, lo diseñamos y maquetamos, y lo imprimimos en offset o en digital según lo que pida el trabajo.</p><p style="font-style: italic">Lo que entregamos es lo que nos gustaría recibir.</p></div>
<div style="display: flex; flex-direction: column; gap: 12px">
<div class="card"><h3>Qué hacemos</h3><div class="tags"><span class="pill">Diseño gráfico</span><span class="pill">Diseño editorial</span><span class="pill">Maquetación</span><span class="pill">Catálogos de arte</span><span class="pill">Libros</span><span class="pill">Revistas</span><span class="pill">Facsímiles</span><span class="pill">Carteles</span><span class="pill">Mupis</span><span class="pill">Folletos</span><span class="pill">Dípticos</span><span class="pill">Desplegables</span><span class="pill">Tarjetas</span><span class="pill">Sobres</span><span class="pill">Postales</span><span class="pill">Papelería</span></div></div>
<div class="card"><h3>Contacto</h3><div class="ct"><a href="tel:648823250">☎ 648 82 32 50</a><a href="mailto:info@bodonia.es">✉ info@bodonia.es</a><span>C/ Gredos nº 27, 18140 La Zubia, Granada</span><span>Lunes a viernes, 9:00 – 20:00</span></div></div>
</div>
</section>
<section id="catalogos">{big('Catálogos','y libros')}{bar('Catálogos y libros','Arte, historia y patrimonio')}<div class="gal">{cats}</div></section>
<section id="trabajos">{big('Trabajos','Carteles, revistas y papelería')}{bar('Impresos','Para la calle y para el día a día')}<div class="gal gal3">{tr}</div></section>
<section id="contacto" style="padding-top: 110px">
<form class="form" onSubmit="{{{{ send }}}}">
<h3 class="disp" style="font-size: 34px; text-align: center">Pide información</h3>
<label class="field">Nombre<input type="text" name="nombre" required=""></label>
<label class="field">Correo electrónico<input type="email" name="correo" required=""></label>
<label class="field">Mensaje<textarea name="mensaje" rows="5" required=""></textarea></label>
<label class="field">Adjuntar archivos<input type="file" name="archivos" multiple=""></label>
<button type="submit">Enviar correo</button>
<sc-if value="{{{{ sent }}}}" hint-placeholder-val="{{{{ false }}}}"><p style="margin: 0; font-size: 14px; text-align: center">Se ha abierto su programa de correo con el mensaje preparado. Si ha elegido archivos, adjúntelos allí antes de pulsar «Enviar».</p></sc-if>
</form>
</section>
<section class="fin"><h2 class="disp">Gracias por<br>la visita !!</h2>
<div class="glass" style="left: 30%; top: 22%; width: 42%; height: 20%"></div>
<div class="sub"><span class="dot"></span><span class="pill">Escríbenos cuando quieras, aquí estamos</span><span class="dot"></span></div></section>
<div class="flechas"><b>▶▶▷▶</b><div><a class="pill s" href="tel:648823250">648 82 32 50</a><a class="pill s" href="mailto:info@bodonia.es">info@bodonia.es</a></div><b>◀▷◀◀</b></div>
</div>
{legal}
<p class="pie">Bodonia Artes Gráficas S.L. · Diseño, maquetación e impresión offset y digital</p>
</div>'''
def page(width):
    sc=re.sub(r'"width":\d+','"width":%d'%width,script)
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Bodonia Artes Gráficas — Retro</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..900;1,6..96,400..900&display=swap">
<style>{css}</style>
</helmet>
{body}
</x-dc>
{sc}
</body>
</html>
'''
open(P+'Retro.dc.html','w').write(page(1360));open(P+'RetroMovil.dc.html','w').write(page(390))
import json
c=json.load(open('live/project/canvas.json'))
c['boards']['Retro.dc.html']={'x':2400,'y':8200,'w':1360,'h':7400,'title':'Retro','is_interactive':True,'expand':'fill'}
c['boards']['RetroMovil.dc.html']={'x':3840,'y':8200,'w':390,'h':7600,'title':'Retro — móvil','is_interactive':True}
for k in ['Retro.dc.html','RetroMovil.dc.html']:
    c['order']=[o for o in c['order'] if o!=k]+[k]
json.dump(c,open(P+'canvas.json','w'),ensure_ascii=False,indent=2)
open('mob/Retro.html','w').write('<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><style>'+css+'</style>'+body)
