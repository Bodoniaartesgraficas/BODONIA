import re,json
P='bodonia/project/'
m=open('live/project/Main.dc.html').read()
figs=re.findall(r'<figure class="work[^"]*".*?</figure>',m,flags=re.S)
cat=[f for f in figs if re.search(r'class="work c\d',f)];tra=[f for f in figs if re.search(r'class="work t\d',f)]
print(len(cat),len(tra))
legal=m[m.index('<section id="legal"'):];legal=legal[:legal.index('</section>')+10]
script=m[m.index('<script type="text/x-dc"'):m.index('</script>',m.index('<script type="text/x-dc"'))+9]
def clean(f):
    f=re.sub(r'class="work [ct]\d"','class="work"',f);return re.sub(r' style="margin: 0"','',f,1)
big=clean(cat[0]);rest=''.join(clean(f) for f in cat[1:]);tr=''.join(clean(f) for f in tra)
legal=re.sub(r'<section id="legal"[^>]*>','<section id="legal">',legal)
LOGO='/_blob/0b2d9e7a5215291be84e7cc8fb5d8b90'
css='''
body{margin:0}html{scroll-behavior:smooth}
.pg{font-family:'Bodoni Moda','Bodoni MT',Didot,serif;font-optical-sizing:auto;background:#0D0D0D;color:#F6F1E3;line-height:1.5;overflow-x:hidden}
.pg a{color:inherit}
.w{max-width:1240px;margin:0 auto;padding:0 40px}
.meta{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:24px;font-size:13px;line-height:1.35;letter-spacing:.02em}
.meta p{margin:0}
.nav{display:flex;justify-content:space-between;align-items:center;padding:26px 0;font-size:15px}
.nav span{display:flex;gap:34px}
.nav a{text-decoration:none;padding:10px 0}
.hero{padding:0 0 70px}
.hero h1{margin:90px 0 110px;font-weight:400;font-style:italic;font-size:clamp(44px,9.4vw,132px);line-height:.95;letter-spacing:-.02em;text-align:center}
.oliva{background:#8E8250;color:#F6F1E3}
.crema{background:#F6F1E3;color:#0D0D0D}
.marron{background:#5C4A3E;color:#F6F1E3}
.txt{padding:96px 0;text-align:center}
.txt p{margin:0 auto 22px;max-width:760px;font-size:19px}
.txt .gr{font-size:34px;line-height:1.2;font-style:italic;max-width:880px;margin-bottom:34px}
.dos{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}
.dos>div{min-height:620px;padding:48px;display:flex;flex-direction:column;justify-content:space-between;box-sizing:border-box}
.ancho{font-style:italic;font-size:30px;text-transform:uppercase;word-spacing:.9em;letter-spacing:.02em;text-align:center;line-height:1.15;margin:0}
.tit{font-style:italic;font-weight:400;font-size:clamp(40px,6vw,84px);line-height:1;margin:0 0 48px;letter-spacing:-.01em}
.sec{padding:96px 0}
.work{margin:0;display:flex;flex-direction:column;gap:12px}
.shot{width:100%;aspect-ratio:5/3;object-fit:cover;display:block;background:#1c1c1c}
.cap{display:flex;justify-content:space-between;gap:16px;font-size:14px;flex-direction:row-reverse}
.cap span{color:#B3A66C;font-style:italic;flex-shrink:0}
.marron .cap span{color:#D9CB95}
.g2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:40px 24px}
.g3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:36px 20px}
.g2 .work:nth-child(odd){transform:translateY(34px)}
.g3 .work:last-child:nth-child(3n+1){grid-column:2}
.lista{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 64px;max-width:980px;margin:0 auto}
.lista p{margin:0;padding:20px 0;border-top:1px solid rgba(13,13,13,.25);font-size:22px;line-height:1.3}
.lista em{display:block;font-size:17px;opacity:.75}
.cont{padding:96px 0 40px;text-align:center}
.cont .big{display:block;font-style:italic;font-size:clamp(34px,6vw,84px);line-height:1.1;text-decoration:none}
.cont form{margin:56px auto 0;max-width:620px;background:#0D0D0D;color:#F6F1E3;padding:40px;display:flex;flex-direction:column;gap:16px;text-align:left;box-sizing:border-box}
.field{display:flex;flex-direction:column;gap:6px;font-size:14px}
.field input,.field textarea{font:inherit;font-size:16px;padding:13px 14px;border:1px solid #F6F1E3;background:transparent;color:#F6F1E3;border-radius:0;resize:vertical;transition:border-color .15s ease-out}
.field input:focus,.field textarea:focus{outline:2px solid #B3A66C;outline-offset:1px}
.field input[type=file]{border:0;padding:8px 0}
.cont button{align-self:center;background:#F6F1E3;color:#0D0D0D;border:0;padding:14px 34px;font:inherit;font-size:17px;font-style:italic;cursor:pointer;min-height:48px;transition:transform .16s cubic-bezier(.23,1,.32,1)}
.cont button:active{transform:scale(.97)}
#legal{padding:64px 40px 40px;max-width:1240px;margin:0 auto}
.label{font-style:italic;font-size:20px;margin:0 0 18px;color:#B3A66C}
.legal{border-top:1px solid rgba(246,241,227,.25)}
.legal summary{cursor:pointer;font-size:20px;padding:18px 0;min-height:44px;box-sizing:border-box}
.legal-b{display:flex;flex-direction:column;gap:12px;font-size:15px;max-width:820px;padding:0 0 28px;opacity:.85}
.pie{padding:28px 40px 40px;max-width:1240px;margin:0 auto;font-size:13px;display:flex;flex-wrap:wrap;gap:8px 24px;justify-content:space-between;opacity:.8}
a,button,summary{-webkit-tap-highlight-color:transparent}
@media(max-width:800px){.w{padding:0 20px}.meta{grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.nav{flex-direction:column;align-items:flex-start;gap:0;padding:14px 0}.nav span{gap:8px 18px;flex-wrap:wrap}.hero h1{margin:56px 0 64px}.txt,.sec{padding:60px 0}.txt .gr{font-size:25px}.txt p{font-size:17px}.dos,.g2,.lista{grid-template-columns:1fr}.dos>div{min-height:380px;padding:28px}.g3{grid-template-columns:repeat(2,minmax(0,1fr));gap:24px 12px}.g3 .cap{flex-direction:column;gap:2px;font-size:13px}.g2 .work:nth-child(odd){transform:none}.g3 .work:last-child:nth-child(3n+1){grid-column:auto}.ancho{font-size:22px}.cont{padding-top:60px}.cont form{padding:24px 20px}.cont button{align-self:stretch}#legal{padding:48px 20px 24px}.pie{padding:20px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition-duration:.01ms!important}}
'''
meta='<div class="meta"><p>Diseño, maquetación<br>e impresión</p><p>Offset<br>y digital</p><p>Más de 35 años<br>de experiencia</p><p>La Zubia<br>Granada</p></div>'
body=f'''<div class="pg">
<section id="inicio" class="hero"><div class="w">
<nav class="nav" aria-label="Principal"><a href="#inicio">Bodonia Artes Gráficas S.L.</a><span><a href="#catalogos">Catálogos</a><a href="#trabajos">Trabajos</a><a href="#taller">El taller</a><a href="#contacto">Contacto</a></span></nav>
<h1>Bodonia Artes Gráficas</h1>
{meta}
</div></section>
<section id="taller" class="oliva txt"><div class="w">
<p class="gr">Tú traes la idea. Nosotros, más de 35 años de imprenta.</p>
<p>Bodonia Artes Gráficas es un taller de La Zubia al que se puede venir con un archivo terminado o con solo una intención. Te ayudamos a elegir formato, papel y acabado, lo diseñamos y maquetamos, y lo imprimimos en offset o en digital según lo que pida el trabajo.</p>
<p style="font-style: italic; margin-bottom: 0">Lo que entregamos es lo que nos gustaría recibir.</p>
</div></section>
<section class="dos">
<div class="crema">{meta}<div style="display: flex; flex-direction: column; align-items: center; gap: 36px"><p class="ancho">Diseño maquetación<br>impresión</p><img src="{LOGO}" alt="Logo de Bodonia Artes Gráficas" style="width: min(420px, 80%); height: auto; display: block"></div><p style="margin: 0; font-size: 13px; text-align: center">Offset y digital, en tiradas cortas o largas</p></div>
<div class="marron" style="justify-content: center">{big}</div>
</section>
<section id="catalogos" class="sec"><div class="w"><h2 class="tit">Catálogos y libros</h2><div class="g2">{rest}</div></div></section>
<section class="crema sec"><div class="w"><h2 class="tit" style="text-align: center">Qué hacemos</h2><div class="lista">
<p>Damos forma<em>Diseño gráfico, diseño editorial y maquetación.</em></p>
<p>Hacemos libros<em>Catálogos de arte, revistas y facsímiles.</em></p>
<p>Llenamos paredes y manos<em>Carteles, mupis, folletos, dípticos y desplegables.</em></p>
<p>Y lo de cada día<em>Tarjetas, sobres, postales y papelería.</em></p>
</div></div></section>
<section id="trabajos" class="marron sec"><div class="w"><h2 class="tit">Trabajos</h2><div class="g3">{tr}</div></div></section>
<footer id="contacto" class="oliva cont"><div class="w">
<a class="big" href="mailto:info@bodonia.es">info@bodonia.es</a>
<a class="big" href="tel:648823250">648 82 32 50</a>
<p style="margin: 34px 0 0; font-size: 18px">C/ Gredos nº 27, 18140 La Zubia, Granada, España<br><a href="https://www.google.com/maps/search/?api=1&amp;query=37.10948,-3.591575">Ver en el mapa</a></p>
<p style="margin: 18px 0 0; font-size: 18px">Lunes a viernes, 9:00 – 20:00. Sábado y domingo, cerrado</p>
<form onSubmit="{{{{ send }}}}">
<p style="margin: 0; font-size: 28px; font-style: italic; text-align: center">Pide información</p>
<label class="field">Nombre<input type="text" name="nombre" required=""></label>
<label class="field">Correo electrónico<input type="email" name="correo" required=""></label>
<label class="field">Mensaje<textarea name="mensaje" rows="5" required=""></textarea></label>
<label class="field">Adjuntar archivos<input type="file" name="archivos" multiple=""></label>
<button type="submit">Enviar correo</button>
<sc-if value="{{{{ sent }}}}" hint-placeholder-val="{{{{ false }}}}"><p style="margin: 0; font-size: 14px; text-align: center">Se ha abierto su programa de correo con el mensaje preparado. Si ha elegido archivos, adjúntelos allí antes de pulsar «Enviar».</p></sc-if>
</form>
</div></footer>
{legal}
<div class="pie"><span>Bodonia Artes Gráficas S.L.</span><span>Diseño, maquetación e impresión offset y digital</span></div>
</div>'''
def page(width):
    sc=re.sub(r'"width":\d+','"width":%d'%width,script)
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Bodonia Artes Gráficas — Copia</title>
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
open(P+'Copia.dc.html','w').write(page(1360));open(P+'CopiaMovil.dc.html','w').write(page(390))
open('mob/Copia.html','w').write('<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><style>'+css+'</style>'+body)
c=json.load(open('live/project/canvas.json'))
c['boards']['Copia.dc.html']={"x":0,"y":8200,"w":1360,"h":7200,"title":"Copia","is_interactive":True,"expand":"fill"}
c['boards']['CopiaMovil.dc.html']={"x":1440,"y":8200,"w":390,"h":7800,"title":"Copia — móvil","is_interactive":True}
c['order']+=['Copia.dc.html','CopiaMovil.dc.html']
json.dump(c,open(P+'canvas.json','w'),ensure_ascii=False,indent=2)
print('data-props' in script, script[:120])
