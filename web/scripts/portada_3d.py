"""Portadas de la galería (4:5) con el libro real en 3D: su cubierta impresa, el lomo y el grosor de verdad,
sobre una escena con luz de ventana (mesa de madera, mármol, terciopelo...). Todo sale del render de Blender/Cycles,
sin fotos pegadas, así que se puede sacar a la resolución que haga falta.

Uso:  python3 web/scripts/portada_3d.py <libro> <salida.jpg> [--escala 25] [--muestras 16]
      libro: tortajada | territorios | santa-fe | primitivismo | en-noir | coin
La cubierta sale del PDF de cubierta del cliente (trasera, lomo y portada, sin solapas).
"""
import argparse, math, os, re, subprocess, sys, tempfile
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import libro_3d as L3  # noqa: E402  (materiales y utilidades de Blender)
from libro_3d import nodo, entrada, salida, material, imagen  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

ANCHO, ALTO = 1600, 2000
UP = "/mnt/project-files/uploads/hearth/"

# Cubiertas: PDF, medidas del libro (mm), lomo (mm) y dónde empieza la trasera dentro de la caja de corte (mm).
LIBROS = {
    "tortajada": dict(pdf=UP + "199014d9-abc6-475c-8455-fbb4a4f9282d", W=165, H=240, lomo=26, x_trasera=148.7, paginas=320),
    # las líneas de plegado del PDF marcan un lomo de 29,2 mm centrado en la caja de corte (491,3 mm)
    "territorios": dict(pdf=UP + "a217327d-7950-4580-8ae6-4e8ebd1873ae", W=231.05, H=208.2, lomo=29.2, x_trasera=0, paginas=144),
    "santa-fe": dict(pdf=UP + "2ca113e9-5af3-420e-bb31-f545f81ea725", W=165, H=235, lomo=6, x_trasera=146, paginas=96),
    # tapa dura: W y H son los del cartón con su cajo (171 x 247 para un bloque de 165 x 240); el PDF trae las pestañas
    "primitivismo": dict(pdf=UP + "a77ffdd4-1a92-4357-bb69-8f8d19d8e985", W=170.95, H=247, lomo=23.1, x_trasera=19.86,
                         y_arriba=19.86, paginas=224, tapa_dura=True, bloque=(165, 240)),
    "en-noir": dict(pdf=UP + "a9317eac-86aa-44cf-aba8-140d6824e898", W=211, H=255, lomo=12.2, x_trasera=0, paginas=100),
    "coin": dict(pdf=UP + "51bdafd9-a3ad-4d6a-9248-a43a50880425", W=166, H=240, lomo=14, x_trasera=150.1, paginas=168),
}

# ---------------------------------------------------------------- cubierta desde el PDF

def cajas(pdf):
    t = subprocess.run(["pdfinfo", "-box", pdf], capture_output=True, text=True).stdout
    def caja(n):
        m = re.search(n + r"Box:\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", t)
        return [float(v) * 25.4 / 72 for v in m.groups()]
    return caja("Media"), caja("Trim")

def cubierta(cfg, carpeta, dpi=300):
    """[trasera | lomo | portada] del PDF de cubierta, recortada a sangre cero y sin solapas."""
    media, trim = cajas(cfg["pdf"])
    if cfg.get("sin_trim"): trim = media   # caja de corte mal puesta en el PDF: se usa la página entera
    base = os.path.join(carpeta, "cub")
    subprocess.run(["pdftoppm", "-r", str(dpi), "-singlefile", "-png", cfg["pdf"], base], check=True)
    im = Image.open(base + ".png").convert("RGB")
    k = dpi / 25.4
    x0 = trim[0] + cfg["x_trasera"]; y0 = media[3] - trim[3] + cfg.get("y_arriba", 0)
    ancho = 2 * cfg["W"] + cfg["lomo"]
    out = im.crop((round(x0 * k), round(y0 * k), round((x0 + ancho) * k), round((y0 + cfg["H"]) * k)))
    ruta = os.path.join(carpeta, "cubierta.png"); out.save(ruta)
    return ruta

# ---------------------------------------------------------------- libro cerrado

def mat_cubierta(ruta):
    m, nt, bsdf = material("cubierta")
    tx = nodo(nt, "ShaderNodeTexImage"); tx.image = imagen(ruta); tx.interpolation = "Cubic"; tx.extension = "EXTEND"
    tc = nodo(nt, "ShaderNodeTexCoord"); nt.links.new(salida(tc, "UV"), entrada(tx, "Vector"))
    nt.links.new(salida(tx, "Color"), entrada(bsdf, "Base Color"))
    entrada(bsdf, "Roughness").default_value = .62
    entrada(bsdf, "Specular IOR Level").default_value = .28
    # grano de la cartulina
    nz = nodo(nt, "ShaderNodeTexNoise"); entrada(nz, "Scale").default_value = 1800; entrada(nz, "Detail").default_value = 2
    nt.links.new(salida(tc, "Object"), entrada(nz, "Vector"))
    bp = nodo(nt, "ShaderNodeBump"); entrada(bp, "Strength").default_value = .06; entrada(bp, "Distance").default_value = .0002
    nt.links.new(salida(nz, "Factor"), entrada(bp, "Height")); nt.links.new(salida(bp, "Normal"), entrada(bsdf, "Normal"))
    return m

def libro_cerrado(nombre, W, H, T, ruta_cub, n_hojas, c=.0004):
    """Rústica cerrada: la cubierta envuelve el bloque (trasera, lomo redondeado y portada) y el bloque enseña el
    corte de las hojas. El libro ocupa x 0..W (lomo en x=0), y 0..H (pie en y=0), z 0..T."""
    r = min(.0018, T * .3)
    # perfil exterior de la cubierta, de la trasera (abajo) a la portada (arriba) pasando por el lomo
    pts = []
    for x in np.linspace(W, r, 40): pts.append((x, 0.0))
    for a in np.linspace(-math.pi / 2, -math.pi, 7)[1:]: pts.append((r + r * math.cos(a), r + r * math.sin(a)))
    for z in np.linspace(r, T - r, 8)[1:]: pts.append((0.0, z))
    for a in np.linspace(math.pi, math.pi / 2, 7)[1:]: pts.append((r + r * math.cos(a), T - r + r * math.sin(a)))
    for x in np.linspace(r, W, 40)[1:]: pts.append((x, T))
    pts = np.array(pts)
    s = np.r_[0, np.cumsum(np.hypot(*np.diff(pts, axis=0).T))]; u = s / s[-1]
    ys = np.linspace(0, H, 3)
    n1, n2 = len(pts), len(ys)
    verts = [(x, y, z) for (x, z) in pts for y in ys]
    caras = [(i * n2 + j, (i + 1) * n2 + j, (i + 1) * n2 + j + 1, i * n2 + j + 1) for i in range(n1 - 1) for j in range(n2 - 1)]
    me = bpy.data.meshes.new(nombre + "_cub"); me.from_pydata(verts, [], caras)
    uvl = me.uv_layers.new(name="UV")
    for p in me.polygons:
        for li in p.loop_indices:
            vi = me.loops[li].vertex_index
            uvl.data[li].uv = (u[vi // n2], ys[vi % n2] / H)
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    for mt in (mat_cubierta(ruta_cub), L3.mat_liso("interior", (.86, .85, .82), .7), L3.mat_liso("canto_cub", (.82, .81, .78), .8)):
        me.materials.append(mt)
    cub = bpy.data.objects.new(nombre + "_cub", me); bpy.context.scene.collection.objects.link(cub)
    sol = cub.modifiers.new("grosor", "SOLIDIFY"); sol.thickness = c; sol.offset = -1
    sol.material_offset = 1; sol.material_offset_rim = 2; sol.use_even_offset = True
    # bloque de hojas
    blo = bloque(nombre, c * .6, W - .00015, .0001, H - .0001, c, T - c, n_hojas)
    raiz = bpy.data.objects.new(nombre, None); bpy.context.scene.collection.objects.link(raiz)
    cub.parent = raiz; blo.parent = raiz
    return raiz, cub

def libro_tapa_dura(nombre, cfg, ruta_cub):
    """Tapa dura cerrada (el mismo modelo que el vídeo): cartones con su ceja, lomo redondeado con los cajos y el
    bloque de hojas metido entre los cartones."""
    Wb, Hb = cfg["bloque"][0] / 1000, cfg["bloque"][1] / 1000
    lomo, carton = cfg["lomo"] / 1000, .0025
    L = L3.Libro(Wb, Hb, cfg["paginas"], (lomo / 2 - carton) / (cfg["paginas"] / 4), cubierta=carton)
    T = L3.TapaDura(L, ruta_cub, lomo); L.tapa = T
    a2 = 2 * L.a
    cub = mat_cubierta(ruta_cub); canto = L3.mat_liso("canto_tapa", T.color, .7, .3)
    x0, x1, y0, y1 = T.cajo, Wb + T.ceja, -T.ceja, Hb + T.ceja
    tr = L3.caja(nombre + "_trasera", x0, x1, y0, y1, 0, carton, [cub, canto, canto], lambda x, y: (T.u_trasera(x), T.v(y)))
    de = L3.caja(nombre + "_portada", x0, x1, y0, y1, a2 - carton, a2, [canto, cub, canto], lambda x, y: (T.u_portada(-x), T.v(y)))
    for ob in (tr, de): ob.modifiers["bisel"].width = .0004; ob.modifiers["bisel"].segments = 3
    lomo_ob = L3.Rejilla(nombre + "_lomo", T.uv(), cub)
    lomo_ob.me.materials.append(L3.mat_liso("carton_gris", (.40, .38, .35), .9, .2)); lomo_ob.me.materials.append(canto)
    lomo_ob.pon(T.rejilla(L.a, -math.pi))
    so = lomo_ob.ob.modifiers.new("grosor", "SOLIDIFY"); so.thickness = .0009; so.offset = -1
    so.material_offset = 1; so.material_offset_rim = 2
    blo = bloque(nombre, 0, Wb - .0002, .0001, Hb - .0001, carton + .0002, a2 - carton - .0002, max(30, cfg["paginas"] // 2))
    raiz = bpy.data.objects.new(nombre, None); bpy.context.scene.collection.objects.link(raiz)
    for ob in (tr, de, lomo_ob.ob, blo): ob.parent = raiz
    return raiz, (T.pliegue, x1, y0, y1, a2)

def bloque(nombre, x0, x1, y0, y1, z0, z1, n_hojas):
    """Bloque de hojas: caja con el canto de las hojas en las cuatro caras de los lados."""
    v = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    caras = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (1, 3, 7, 5), (3, 2, 6, 7), (2, 0, 4, 6)]
    mb = bpy.data.meshes.new(nombre + "_bloque"); mb.from_pydata(v, [], caras)
    uvb = mb.uv_layers.new(name="UV")
    for p in mb.polygons:
        for li in p.loop_indices:
            x, y, z = v[mb.loops[li].vertex_index]
            uvb.data[li].uv = ((y - y0) / (y1 - y0) if abs(p.normal.x) > .5 else (x - x0) / (x1 - x0), (z - z0) / (z1 - z0))
    mb.materials.append(L3.mat_canto(n_hojas))
    blo = bpy.data.objects.new(nombre + "_bloque", mb); bpy.context.scene.collection.objects.link(blo)
    bv = blo.modifiers.new("bisel", "BEVEL"); bv.width = .0003; bv.segments = 2
    return blo

def libro(nombre, cfg, ruta_cub):
    """El libro cerrado que toque (rústica o tapa dura). Devuelve la raíz y su caja: x0, x1, y0, y1 (lomo en x0) y alto."""
    if cfg.get("tapa_dura"):
        return libro_tapa_dura(nombre, cfg, ruta_cub)
    W, H, T = cfg["W"] / 1000, cfg["H"] / 1000, cfg["lomo"] / 1000
    raiz, _ = libro_cerrado(nombre, W, H, T, ruta_cub, max(30, cfg["paginas"] // 2))
    return raiz, (0, W, 0, H, T)

def coloca(raiz, caja, giro, centro, z=0.0, inclina=None):
    """Gira el libro sobre la mesa (grados) y lo deja con el centro de su caja en `centro` (x, y) a la altura z.
    inclina: (grados, eje) para apoyarlo de pie o ladeado, girando antes alrededor del eje x o y del libro."""
    from mathutils import Matrix
    x0, x1, y0, y1, a = caja
    M = Matrix.Translation((-(x0 + x1) / 2, -(y0 + y1) / 2, 0))
    if inclina:
        ang, eje = inclina
        M = Matrix.Rotation(math.radians(ang), 4, eje) @ M
    M = Matrix.Translation((centro[0], centro[1], z)) @ Matrix.Rotation(math.radians(giro), 4, "Z") @ M
    raiz.matrix_world = M
    return M

# ---------------------------------------------------------------- materiales de la escena

def mat_madera(nombre, oscuro, claro, tabla=.11, anillos=140, barniz=.55):
    """Tablero de madera maciza en tablas a lo largo de x. Cada tabla es un corte de tronco con su eje desplazado al
    azar, así que los anillos salen como vetas largas con catedrales, distintas en cada tabla; encima, fibra y poro."""
    m, nt, bsdf = material(nombre)
    def mate(op, a, b=None, c=None):
        n = nodo(nt, "ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a, b, c)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: nt.links.new(v, n.inputs[i])
        return n.outputs[0]
    def ruido(vec, escala, detalle=3, rug=.55, dims="3D"):
        n = nodo(nt, "ShaderNodeTexNoise"); n.noise_dimensions = dims
        entrada(n, "Scale").default_value = escala; entrada(n, "Detail").default_value = detalle; entrada(n, "Roughness").default_value = rug
        nt.links.new(vec, entrada(n, "Vector")); return salida(n, "Factor")
    def estira(vec, sx, sy, sz):
        mp = nodo(nt, "ShaderNodeMapping"); entrada(mp, "Scale").default_value = (sx, sy, sz)
        nt.links.new(vec, entrada(mp, "Vector")); return salida(mp, "Vector")
    tc = nodo(nt, "ShaderNodeTexCoord"); P = salida(tc, "Object")
    sep = nodo(nt, "ShaderNodeSeparateXYZ"); nt.links.new(P, sep.inputs[0])
    x, y, z = sep.outputs[0], sep.outputs[1], sep.outputs[2]
    k = mate("FLOOR", mate("DIVIDE", y, tabla))
    def azar(sem):
        wn = nodo(nt, "ShaderNodeTexWhiteNoise"); wn.noise_dimensions = "1D"
        nt.links.new(mate("ADD", k, sem), entrada(wn, "W")); return salida(wn, "Value")
    r1, r2, r3, r4 = azar(.37), azar(17.1), azar(41.9), azar(63.3)
    y0 = mate("ADD", mate("MULTIPLY", mate("ADD", k, .5), tabla), mate("MULTIPLY", mate("SUBTRACT", r1, .5), .3))
    z0 = mate("SUBTRACT", -.04, mate("MULTIPLY", r2, .3))
    ondula = mate("MULTIPLY", mate("SUBTRACT", ruido(estira(P, .7, 2, 2), 1, 2), .5), .035)
    dy = mate("ADD", mate("SUBTRACT", y, y0), ondula)
    # el tablón no va paralelo al eje del tronco: los anillos cortan la cara en arcos (catedrales)
    inclina = mate("MULTIPLY", x, mate("ADD", .02, mate("MULTIPLY", r4, .05)))
    dz = mate("ADD", mate("SUBTRACT", z, z0), inclina)
    radio = mate("SQRT", mate("ADD", mate("MULTIPLY", dy, dy), mate("MULTIPLY", dz, dz)))
    irreg = mate("MULTIPLY", ruido(estira(P, 1.5, 12, 12), 1, 3), .5)
    nr = nodo(nt, "ShaderNodeTexNoise"); nr.noise_dimensions = "1D"; entrada(nr, "Scale").default_value = 1
    entrada(nr, "Detail").default_value = 2; nt.links.new(mate("MULTIPLY", radio, 45), entrada(nr, "W"))
    crece = mate("MULTIPLY", salida(nr, "Factor"), 2.5)   # anillos de anchura irregular
    fase = mate("FRACT", mate("ADD", mate("ADD", mate("MULTIPLY", radio, anillos), irreg), crece))
    r_an = nodo(nt, "ShaderNodeValToRGB"); e = r_an.color_ramp.elements
    e[0].position = .0; e[0].color = (*claro, 1); e[1].position = .55; e[1].color = (*claro, 1)
    e3 = r_an.color_ramp.elements.new(.86); e3.color = (*oscuro, 1)
    e4 = r_an.color_ramp.elements.new(.97); e4.color = (*[(a + b) / 2 for a, b in zip(oscuro, claro)], 1)
    nt.links.new(fase, entrada(r_an, "Factor"))
    # fibra fina a lo largo de la veta y tono de cada tabla
    fibra = ruido(estira(P, 5, 420, 420), 1, 8, .62)
    r_f = nodo(nt, "ShaderNodeValToRGB")
    r_f.color_ramp.elements[0].position = .3; r_f.color_ramp.elements[0].color = (.8, .78, .76, 1)
    r_f.color_ramp.elements[1].position = .7; r_f.color_ramp.elements[1].color = (1.07, 1.06, 1.05, 1)
    nt.links.new(fibra, entrada(r_f, "Factor"))
    tono = mate("ADD", .9, mate("MULTIPLY", r3, .2))
    # vetas anchas de color a lo largo de la tabla
    tono = mate("MULTIPLY", tono, mate("ADD", .84, mate("MULTIPLY", ruido(estira(P, 1.2, 26, 26), 1, 3), .32)))
    poro = mate("SUBTRACT", 1, mate("MULTIPLY", .22, mate("GREATER_THAN", ruido(estira(P, 14, 1500, 1500), 1, 2), .66)))
    tono = mate("MULTIPLY", tono, poro)
    junta = mate("SUBTRACT", 1, mate("MULTIPLY", .25, mate("LESS_THAN", mate("PINGPONG", mate("DIVIDE", y, tabla), .5), .006)))
    def mult(a, b, valor=False):
        mx = nodo(nt, "ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"
        entrada(mx, "Factor", "VALUE").default_value = 1
        nt.links.new(a, entrada(mx, "A", "RGBA"))
        if valor:
            cv = nodo(nt, "ShaderNodeCombineXYZ")
            for i in range(3): nt.links.new(b, cv.inputs[i])
            nt.links.new(cv.outputs[0], entrada(mx, "B", "RGBA"))
        else:
            nt.links.new(b, entrada(mx, "B", "RGBA"))
        return salida(mx, "Result", "RGBA")
    col = mult(mult(mult(salida(r_an, "Color"), salida(r_f, "Color")), tono, True), junta, True)
    nt.links.new(col, entrada(bsdf, "Base Color"))
    nt.links.new(mate("ADD", .38, mate("MULTIPLY", fibra, .18)), entrada(bsdf, "Roughness"))
    entrada(bsdf, "Coat Weight").default_value = barniz; entrada(bsdf, "Coat Roughness").default_value = .2
    bp = nodo(nt, "ShaderNodeBump"); entrada(bp, "Strength").default_value = .05; entrada(bp, "Distance").default_value = .0003
    nt.links.new(fibra, entrada(bp, "Height")); nt.links.new(salida(bp, "Normal"), entrada(bsdf, "Normal"))
    return m

def mat_yeso(nombre, color, rug=.9):
    m, nt, bsdf = material(nombre)
    tc = nodo(nt, "ShaderNodeTexCoord")
    nz = nodo(nt, "ShaderNodeTexNoise"); entrada(nz, "Scale").default_value = 35; entrada(nz, "Detail").default_value = 8
    nt.links.new(salida(tc, "Object"), entrada(nz, "Vector"))
    cr = nodo(nt, "ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (*[v * .9 for v in color], 1); cr.color_ramp.elements[1].color = (*[v * 1.06 for v in color], 1)
    nt.links.new(salida(nz, "Factor"), entrada(cr, "Factor")); nt.links.new(salida(cr, "Color"), entrada(bsdf, "Base Color"))
    entrada(bsdf, "Roughness").default_value = rug; entrada(bsdf, "Specular IOR Level").default_value = .2
    bp = nodo(nt, "ShaderNodeBump"); entrada(bp, "Strength").default_value = .25; entrada(bp, "Distance").default_value = .001
    nt.links.new(salida(nz, "Factor"), entrada(bp, "Height")); nt.links.new(salida(bp, "Normal"), entrada(bsdf, "Normal"))
    return m

def _ruido(nt, vec, escala, detalle=3, rug=.55, dist=0.0, dims="3D"):
    n = nodo(nt, "ShaderNodeTexNoise"); n.noise_dimensions = dims
    entrada(n, "Scale").default_value = escala; entrada(n, "Detail").default_value = detalle
    entrada(n, "Roughness").default_value = rug; entrada(n, "Distortion").default_value = dist
    nt.links.new(vec, entrada(n, "Vector")); return n

def _rampa(nt, fac, puntos):
    r = nodo(nt, "ShaderNodeValToRGB"); e = r.color_ramp.elements
    e[0].position, e[0].color = puntos[0][0], (*puntos[0][1], 1)
    e[1].position, e[1].color = puntos[-1][0], (*puntos[-1][1], 1)
    for pos, col in puntos[1:-1]:
        x = e.new(pos); x.color = (*col, 1)
    nt.links.new(fac, entrada(r, "Factor")); return r

def mat_terciopelo(nombre, color, brillo):
    """Terciopelo: base oscura y mucho brillo rasante (sheen) del pelo, con zonas aplastadas que brillan distinto."""
    m, nt, bsdf = material(nombre)
    tc = nodo(nt, "ShaderNodeTexCoord"); P = salida(tc, "Object")
    aplastado = _ruido(nt, P, 9, 4, .6, 1.5)
    col = _rampa(nt, salida(aplastado, "Factor"), [(.3, [v * .8 for v in color]), (.7, [v * 1.12 for v in color])])
    nt.links.new(salida(col, "Color"), entrada(bsdf, "Base Color"))
    entrada(bsdf, "Roughness").default_value = .95; entrada(bsdf, "Specular IOR Level").default_value = .15
    entrada(bsdf, "Sheen Weight").default_value = 1.0; entrada(bsdf, "Sheen Roughness").default_value = .32
    entrada(bsdf, "Sheen Tint").default_value = (*brillo, 1)
    pelo = _ruido(nt, P, 2600, 2, .5)
    bp = nodo(nt, "ShaderNodeBump"); entrada(bp, "Strength").default_value = .12; entrada(bp, "Distance").default_value = .0002
    nt.links.new(salida(pelo, "Factor"), entrada(bp, "Height")); nt.links.new(salida(bp, "Normal"), entrada(bsdf, "Normal"))
    return m

def mat_hormigon(nombre, color):
    """Hormigón pulido: manchas grandes, árido fino y poros."""
    m, nt, bsdf = material(nombre)
    tc = nodo(nt, "ShaderNodeTexCoord"); P = salida(tc, "Object")
    manchas = _ruido(nt, P, 2.5, 5, .65, .4)
    grano = _ruido(nt, P, 160, 4, .7)
    c1 = _rampa(nt, salida(manchas, "Factor"), [(.3, [v * .78 for v in color]), (.5, color), (.72, [v * 1.15 for v in color])])
    mx = nodo(nt, "ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "OVERLAY"
    entrada(mx, "Factor", "VALUE").default_value = .35
    nt.links.new(salida(c1, "Color"), entrada(mx, "A", "RGBA")); nt.links.new(salida(grano, "Color"), entrada(mx, "B", "RGBA"))
    vo = nodo(nt, "ShaderNodeTexVoronoi"); entrada(vo, "Scale").default_value = 420
    nt.links.new(P, entrada(vo, "Vector"))
    poro = nodo(nt, "ShaderNodeMath"); poro.operation = "LESS_THAN"; poro.inputs[1].default_value = .07
    nt.links.new(salida(vo, "Distance"), poro.inputs[0])
    os_ = nodo(nt, "ShaderNodeMix"); os_.data_type = "RGBA"; os_.blend_type = "MULTIPLY"
    nt.links.new(poro.outputs[0], entrada(os_, "Factor", "VALUE"))
    nt.links.new(salida(mx, "Result", "RGBA"), entrada(os_, "A", "RGBA")); entrada(os_, "B", "RGBA").default_value = (.55, .55, .55, 1)
    nt.links.new(salida(os_, "Result", "RGBA"), entrada(bsdf, "Base Color"))
    rg = nodo(nt, "ShaderNodeMapRange"); entrada(rg, "To Min").default_value = .45; entrada(rg, "To Max").default_value = .75
    nt.links.new(salida(manchas, "Factor"), entrada(rg, "Value")); nt.links.new(salida(rg, "Result"), entrada(bsdf, "Roughness"))
    entrada(bsdf, "Specular IOR Level").default_value = .35
    bp = nodo(nt, "ShaderNodeBump"); entrada(bp, "Strength").default_value = .2; entrada(bp, "Distance").default_value = .0005
    hb = nodo(nt, "ShaderNodeMath"); hb.operation = "SUBTRACT"
    nt.links.new(salida(grano, "Factor"), hb.inputs[0]); nt.links.new(poro.outputs[0], hb.inputs[1])
    nt.links.new(hb.outputs[0], entrada(bp, "Height")); nt.links.new(salida(bp, "Normal"), entrada(bsdf, "Normal"))
    return m

def mat_marmol(nombre, base, oscuro, vena):
    """Mármol pulido (tipo emperador): nubes de color, vetas finas que se ramifican y brillo de pulido."""
    m, nt, bsdf = material(nombre)
    tc = nodo(nt, "ShaderNodeTexCoord"); P = salida(tc, "Object")
    nubes = _ruido(nt, P, 3.5, 6, .62, 1.2)
    c = _rampa(nt, salida(nubes, "Factor"), [(.32, oscuro), (.55, base), (.75, [min(1, v * 1.2) for v in base])])
    venas = []
    # vetas finas y sin mucho contraste; una máscara de ruido hace que aparezcan y se pierdan como en la piedra
    for esc, dist, grosor, peso in ((3.2, 7, .022, .75), (9, 10, .013, .45)):
        wv = nodo(nt, "ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "DIAGONAL"; wv.wave_profile = "SIN"
        entrada(wv, "Scale").default_value = esc; entrada(wv, "Distortion").default_value = dist
        entrada(wv, "Detail").default_value = 8; entrada(wv, "Detail Roughness").default_value = .62
        nt.links.new(P, entrada(wv, "Vector"))
        r = nodo(nt, "ShaderNodeMapRange"); entrada(r, "From Min").default_value = 1 - grosor; entrada(r, "From Max").default_value = 1
        entrada(r, "To Max").default_value = peso
        nt.links.new(salida(wv, "Factor"), entrada(r, "Value")); venas.append(salida(r, "Result"))
    vmax = nodo(nt, "ShaderNodeMath"); vmax.operation = "MAXIMUM"
    nt.links.new(venas[0], vmax.inputs[0]); nt.links.new(venas[1], vmax.inputs[1])
    mascara = _ruido(nt, P, 2.2, 3, .5)
    mr = nodo(nt, "ShaderNodeMapRange"); entrada(mr, "From Min").default_value = .38; entrada(mr, "From Max").default_value = .62
    entrada(mr, "To Min").default_value = .2
    nt.links.new(salida(mascara, "Factor"), entrada(mr, "Value"))
    vm = nodo(nt, "ShaderNodeMath"); vm.operation = "MULTIPLY"
    nt.links.new(vmax.outputs[0], vm.inputs[0]); nt.links.new(salida(mr, "Result"), vm.inputs[1]); vmax = vm
    mx = nodo(nt, "ShaderNodeMix"); mx.data_type = "RGBA"
    nt.links.new(vmax.outputs[0], entrada(mx, "Factor", "VALUE"))
    nt.links.new(salida(c, "Color"), entrada(mx, "A", "RGBA")); entrada(mx, "B", "RGBA").default_value = (*vena, 1)
    nt.links.new(salida(mx, "Result", "RGBA"), entrada(bsdf, "Base Color"))
    entrada(bsdf, "Roughness").default_value = .3; entrada(bsdf, "Specular IOR Level").default_value = .5
    entrada(bsdf, "Coat Weight").default_value = .8; entrada(bsdf, "Coat Roughness").default_value = .12
    return m

def mat_tela_libro(nombre, color):
    """Tela de encuadernar (para el libro de atrezo): color liso con trama fina."""
    m, nt, bsdf = material(nombre)
    tc = nodo(nt, "ShaderNodeTexCoord"); P = salida(tc, "Object")
    tr = _ruido(nt, P, 1400, 2, .5)
    c = _rampa(nt, salida(tr, "Factor"), [(.35, [v * .88 for v in color]), (.65, [v * 1.08 for v in color])])
    nt.links.new(salida(c, "Color"), entrada(bsdf, "Base Color"))
    entrada(bsdf, "Roughness").default_value = .8; entrada(bsdf, "Specular IOR Level").default_value = .2
    entrada(bsdf, "Sheen Weight").default_value = .3; entrada(bsdf, "Sheen Roughness").default_value = .5
    bp = nodo(nt, "ShaderNodeBump"); entrada(bp, "Strength").default_value = .15; entrada(bp, "Distance").default_value = .0002
    nt.links.new(salida(tr, "Factor"), entrada(bp, "Height")); nt.links.new(salida(bp, "Normal"), entrada(bsdf, "Normal"))
    return m

# ---------------------------------------------------------------- luz de ventana

def gobo(sol, luz, barras=(), distancia=1.7, tam=4.0, n=2048, carpeta=".", sombras=(), nombre="ventana"):
    """Plano entre el sol y la escena que solo deja pasar la luz por la ventana; no se ve en cámara.
    luz: polígono (x, y) sobre el plano z=0 que queda al sol; barras: segmentos (x0, y0, x1, y1, grosor) de la
    carpintería, también sobre z=0. Se proyectan a lo largo del sol hasta el plano de la ventana."""
    from PIL import ImageDraw
    s = Vector(sol).normalized(); q = s.to_track_quat("Z", "Y")
    ua, va = q @ Vector((1, 0, 0)), q @ Vector((0, 1, 0)); C = s * distancia
    def px(x, y):
        P = Vector((x, y, 0)); Q = P + s * (C - P).dot(s)
        return ((Q - C).dot(ua) / tam + .5) * n, (.5 - (Q - C).dot(va) / tam) * n
    im = Image.new("L", (n, n), 0); d = ImageDraw.Draw(im)
    d.polygon([px(x, y) for x, y in luz], fill=255)
    for x0, y0, x1, y1, g in barras:
        a, b = Vector((x1 - x0, y1 - y0, 0)).normalized(), None
        b = Vector((-a.y, a.x, 0)) * g / 2
        d.polygon([px(x0 + b.x, y0 + b.y), px(x1 + b.x, y1 + b.y), px(x1 - b.x, y1 - b.y), px(x0 - b.x, y0 - b.y)], fill=0)
    for pol in sombras:
        d.polygon([px(x, y) for x, y in pol], fill=0)
    ruta = os.path.join(carpeta, nombre + ".png"); im.save(ruta)
    bpy.ops.mesh.primitive_plane_add(size=tam)
    p = bpy.context.active_object; p.name = "gobo"
    p.location = C; p.rotation_euler = q.to_euler()
    m, nt, bsdf = material("gobo")
    tx = nodo(nt, "ShaderNodeTexImage"); tx.image = bpy.data.images.load(ruta); tx.image.colorspace_settings.name = "Non-Color"
    tr = nodo(nt, "ShaderNodeBsdfTransparent"); df = nodo(nt, "ShaderNodeBsdfDiffuse")
    entrada(df, "Color").default_value = (0, 0, 0, 1)
    ms = nodo(nt, "ShaderNodeMixShader")
    nt.links.new(salida(tx, "Color"), entrada(ms, "Factor"))
    nt.links.new(salida(df, "BSDF"), ms.inputs[1]); nt.links.new(salida(tr, "BSDF"), ms.inputs[2])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"); nt.links.new(salida(ms, "Shader"), entrada(out, "Surface"))
    p.data.materials.append(m)
    p.visible_camera = False; p.visible_diffuse = False; p.visible_glossy = False; p.visible_transmission = False
    return p

def sol(direccion, fuerza, color, angulo=1.2):
    d = bpy.data.lights.new("sol", "SUN"); d.energy = fuerza; d.color = color; d.angle = math.radians(angulo)
    o = bpy.data.objects.new("sol", d); bpy.context.scene.collection.objects.link(o)
    o.rotation_euler = Vector(direccion).normalized().to_track_quat("Z", "Y").to_euler()
    return o

def camara(objetivo, dist, az, el, lente, f_num):
    cd = bpy.data.cameras.new("cam"); cd.lens = lente; cd.sensor_width = 36; cd.sensor_fit = "AUTO"
    cd.dof.use_dof = True; cd.dof.aperture_fstop = f_num; cd.dof.focus_distance = dist
    c = bpy.data.objects.new("cam", cd); bpy.context.scene.collection.objects.link(c)
    az, el = math.radians(az), math.radians(el)
    pos = Vector(objetivo) + dist * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    c.location = pos; c.rotation_euler = (Vector(objetivo) - pos).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = c
    return c

# ---------------------------------------------------------------- escenas

def ajustes(muestras):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = muestras
    sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = .02
    sc.cycles.use_denoising = True
    try: sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception: pass
    sc.cycles.max_bounces = 6; sc.cycles.diffuse_bounces = 3; sc.cycles.glossy_bounces = 2
    sc.cycles.transparent_max_bounces = 4; sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
    sc.render.resolution_x, sc.render.resolution_y = ANCHO, ALTO
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
    w = bpy.data.worlds.new("mundo"); sc.world = w
    try: w.use_nodes = True
    except Exception: pass
    return w

def mundo(w, color, fuerza):
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    entrada(bg, "Color").default_value = (*color, 1); entrada(bg, "Strength").default_value = fuerza

def caja_redonda(nombre, tam, centro, radio, mat, segmentos=6, giro=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=centro, rotation=[math.radians(g) for g in giro])
    ob = bpy.context.active_object; ob.name = nombre; ob.scale = tam
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    b = ob.modifiers.new("bisel", "BEVEL"); b.width = radio; b.segments = segmentos; b.limit_method = "NONE"
    ob.data.materials.append(mat); bpy.ops.object.shade_smooth()
    return ob

def plano(nombre, tam, centro, mat, giro=(0, 0, 0), sombra=True):
    bpy.ops.mesh.primitive_plane_add(size=tam, location=centro, rotation=[math.radians(g) for g in giro])
    ob = bpy.context.active_object; ob.name = nombre; ob.data.materials.append(mat); ob.visible_shadow = sombra
    return ob

def direccion(az, el):
    """Hacia dónde está el sol: azimut desde +x en sentido antihorario y elevación, en grados."""
    az, el = math.radians(az), math.radians(el)
    return (math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el))

def hojas(n, caja, tam=(.05, .11), semilla=3):
    """Siluetas de hojas (para la sombra de una planta junto a la ventana), sobre el plano z=0."""
    rng = np.random.default_rng(semilla); x0, x1, y0, y1 = caja; out = []
    for _ in range(n):
        cx, cy = rng.uniform(x0, x1), rng.uniform(y0, y1); a = rng.uniform(0, math.pi)
        l = rng.uniform(*tam); w = l * rng.uniform(.28, .4)
        t = np.linspace(0, math.pi, 14)
        pts = [(math.cos(a) * (l * (u / math.pi - .5)) - math.sin(a) * (w * math.sin(u) * (1 - .25 * u / math.pi) * (1 if k == 0 else -1)),
                math.sin(a) * (l * (u / math.pi - .5)) + math.cos(a) * (w * math.sin(u) * (1 - .25 * u / math.pi) * (1 if k == 0 else -1)))
               for k, tt in enumerate((t, t[::-1])) for u in tt]
        out.append([(cx + x, cy + y) for x, y in pts])
        # tallo hasta la rama
        ex, ey = cx - math.cos(a) * l * .5, cy - math.sin(a) * l * .5
        out.append([(ex, ey), (ex - math.cos(a) * l * .4 + .003, ey - math.sin(a) * l * .4), (ex - math.cos(a) * l * .4, ey - math.sin(a) * l * .4 + .003)])
    return out

def tapa_lisa(carpeta, nombre, color, bloque, lomo, ceja=3.0, pliegue=-3.0):
    """Cubierta lisa (tela de un color) para un libro de atrezo de tapa dura."""
    panel = bloque[0] + ceja - pliegue; total = 2 * panel + lomo; alto = bloque[1] + 2 * ceja
    k = 4
    a = np.random.default_rng(7).normal(0, 3, (round(alto * k), round(total * k), 1)) + np.array(color) * 255
    ruta = os.path.join(carpeta, nombre + ".png")
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(ruta)
    return ruta

def escena_santa_fe(cfg, ruta_cub, carpeta):
    w = ajustes(cfg["muestras"]); mundo(w, (.55, .52, .5), .17)
    # mesa redonda de madera de cerezo, pared de yeso detrás y suelo oscuro
    bpy.ops.mesh.primitive_cylinder_add(vertices=160, radius=.36, depth=.03, location=(0, 0, -.015))
    mesa = bpy.context.active_object; mesa.data.materials.append(mat_madera("cerezo", (.17, .065, .028), (.30, .13, .055)))
    b = mesa.modifiers.new("bisel", "BEVEL"); b.width = .004; b.segments = 3
    bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=.045, depth=.7, location=(0, 0, -.38))
    bpy.context.active_object.data.materials.append(mat_madera("pie", (.16, .07, .03), (.36, .18, .08)))
    plano("suelo", 6, (0, 0, -.73), L3.mat_liso("suelo", (.08, .07, .06), .7))
    plano("pared", 6, (0, .62, 2.27), mat_yeso("pared", (.36, .35, .33)), (90, 0, 0), sombra=False)
    raiz, caja = libro("libro", cfg, ruta_cub)
    coloca(raiz, caja, 58, (0, 0))
    # sol bajo de ventana desde atrás a la derecha, con la carpintería recortando el haz
    d = direccion(40, 30)
    sol(d, 4.2, (1.0, .87, .72), 1.0)
    gobo(d, [(-.02, -.6), (.9, -.6), (.9, .7), (-.30, .7)], [(.30, -.6, .02, .7, .03)], carpeta=carpeta)
    camara((0, 0, caja[4] / 2), .70, -26, 36, 58, 8)

def escena_primitivismo(cfg, ruta_cub, carpeta):
    w = ajustes(cfg["muestras"]); mundo(w, (.6, .52, .44), .12)
    # cubo de roble claro, pared oscura y cálida detrás
    caja_redonda("cubo", (.46, .46, .5), (0, .04, -.25), .004, mat_madera("roble", (.26, .12, .04), (.52, .29, .11), tabla=.15), 3)
    plano("suelo", 6, (0, 0, -.5), L3.mat_liso("suelo", (.06, .045, .035), .6))
    plano("pared", 6, (0, .5, 2.4), mat_yeso("pared", (.13, .095, .07)), (90, 0, 0), sombra=False)
    # libro de atrezo debajo (tela verde oliva) y encima el catálogo
    cfg2 = dict(bloque=(205, 270), lomo=30, paginas=300, tapa_dura=True)
    r2, c2 = libro("atrezo", cfg2, tapa_lisa(carpeta, "oliva", (.42, .44, .22), cfg2["bloque"], cfg2["lomo"]))
    coloca(r2, c2, 76, (.03, .07))
    raiz, caja = libro("libro", cfg, ruta_cub)
    coloca(raiz, caja, 62, (-.01, .02), z=c2[4])
    d = direccion(15, 32)
    sol(d, 4.0, (1.0, .84, .66), 1.1)
    gobo(d, [(-.13, -.7), (.9, -.7), (.9, .7), (-.30, .7)], carpeta=carpeta)
    camara((-.01, .03, c2[4] + caja[4] / 2), .70, -30, 36, 60, 8)

def escena_coin(cfg, ruta_cub, carpeta):
    w = ajustes(cfg["muestras"]); mundo(w, (.5, .47, .44), .1)
    bpy.ops.mesh.primitive_cylinder_add(vertices=180, radius=.34, depth=.025, location=(0, 0, -.0125))
    mesa = bpy.context.active_object
    mesa.data.materials.append(mat_marmol("marmol", (.19, .105, .06), (.07, .038, .02), (.62, .5, .37)))
    b = mesa.modifiers.new("bisel", "BEVEL"); b.width = .005; b.segments = 4
    bpy.ops.object.shade_smooth()
    plano("suelo", 6, (0, 0, -.72), L3.mat_liso("suelo", (.05, .04, .035), .5))
    plano("pared", 6, (0, .7, 2.3), mat_yeso("pared", (.1, .085, .07)), (90, 0, 0), sombra=False)
    r1, c1 = libro("libro1", cfg, ruta_cub)
    coloca(r1, c1, 70, (-.045, -.035))
    r2, c2 = libro("libro2", cfg, ruta_cub)
    coloca(r2, c2, 81, (-.022, -.012), z=c1[4])   # encima del primero, apoyado del todo
    d = direccion(125, 34)
    sol(d, 3.8, (1.0, .88, .74), 1.0)
    gobo(d, [(-.9, -.6), (.25, -.6), (.35, .8), (-.9, .8)], [(-.12, -.6, -.08, .8, .03)], carpeta=carpeta)
    camara((-.03, -.02, c1[4]), .80, 14, 40, 56, 8)

def escena_en_noir(cfg, ruta_cub, carpeta):
    w = ajustes(cfg["muestras"]); mundo(w, (.55, .55, .55), .22)
    alto = .46
    plano("suelo", 8, (0, 0, -alto), mat_hormigon("hormigon", (.30, .295, .28)))
    # taburete de madera oscura: asiento redondo, cuatro patas abiertas y aro
    madera = mat_madera("wengue", (.03, .018, .011), (.075, .045, .026), tabla=.09, barniz=.35)
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=.17, depth=.032, location=(0, 0, -.016))
    asiento = bpy.context.active_object; asiento.data.materials.append(madera)
    b = asiento.modifiers.new("bisel", "BEVEL"); b.width = .008; b.segments = 5
    bpy.ops.object.shade_smooth()
    for k in range(4):
        a = math.radians(45 + 90 * k)
        top = Vector((.11 * math.cos(a), .11 * math.sin(a), -.03)); pie = Vector((.17 * math.cos(a), .17 * math.sin(a), -alto))
        mid = (top + pie) / 2; dv = top - pie
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=.0135, depth=dv.length, location=mid)
        pata = bpy.context.active_object; pata.rotation_euler = dv.to_track_quat("Z", "Y").to_euler()
        pata.data.materials.append(madera); bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_torus_add(major_radius=.15, minor_radius=.008, location=(0, 0, -.30), major_segments=96, minor_segments=12)
    aro = bpy.context.active_object; aro.data.materials.append(madera); bpy.ops.object.shade_smooth()
    raiz, caja = libro("libro", cfg, ruta_cub)
    coloca(raiz, caja, 104, (0, 0))
    d = direccion(160, 40)
    sol(d, 3.6, (1.0, .9, .78), 1.6)
    gobo(d, [(-.9, -.8), (.14, -.8), (.24, .8), (-.9, .8)], [(-.25, -.8, -.2, .8, .025)], carpeta=carpeta)
    camara((0, -.005, caja[4] / 2 - .06), 1.02, 6, 58, 50, 8)

def escena_tortajada(cfg, ruta_cub, carpeta):
    w = ajustes(cfg["muestras"]); mundo(w, (.6, .5, .38), .14)
    terciopelo = mat_terciopelo("terciopelo", (.33, .19, .035), (1.0, .82, .45))
    # sillón: cojín del asiento, respaldo inclinado y brazos
    caja_redonda("asiento", (.66, .6, .16), (0, 0, -.08), .05, terciopelo, 8)
    caja_redonda("respaldo", (.66, .2, .62), (0, .34, .22), .07, terciopelo, 8, (-12, 0, 0))
    for sx in (-1, 1):
        caja_redonda("brazo", (.16, .78, .5), (sx * .41, .06, .02), .06, terciopelo, 8)
    caja_redonda("base", (.98, .84, .26), (0, .06, -.29), .03, terciopelo, 6)
    plano("suelo", 8, (0, 0, -.42), mat_madera("tarima", (.10, .05, .025), (.2, .11, .055), tabla=.12, barniz=.4))
    plano("pared", 8, (0, .9, 2.0), mat_yeso("pared", (.30, .24, .17)), (90, 0, 0), sombra=False)
    # el libro de pie sobre el cojín, girado para que se vea el lomo y apoyado en el respaldo
    raiz, caja = libro("libro", cfg, ruta_cub)
    x0, x1, y0, y1, T = caja
    M = coloca(raiz, caja, 24, (0, 0), inclina=(78, "X"))
    esquinas = [M @ Vector((x, y, z)) for x in (x0, x1) for y in (y0, y1) for z in (0, T)]
    pend = math.tan(math.radians(12))             # cara del respaldo: y = .197 + pend * z
    dy = .197 - max(p.y - pend * p.z for p in esquinas)
    dz = -.006 - min(p.z for p in esquinas)       # se hunde un poco en el cojín
    from mathutils import Matrix
    raiz.matrix_world = Matrix.Translation((0, dy, dz)) @ M
    centro = sum(esquinas, Vector()) / len(esquinas) + Vector((0, dy, dz))
    # sol de delante a la izquierda, por encima del brazo, para que entre de lleno en la cubierta
    d = direccion(205, 38)
    sol(d, 4.2, (1.0, .84, .64), 1.2)
    gobo(d, [(-.9, -.9), (.55, -.9), (.7, .9), (-.9, .9)], [(-.34, -.9, -.26, .9, .035)], carpeta=carpeta)
    camara(centro, 1.0, -24, 14, 62, 6.3)

def escena_territorios(cfg, ruta_cub, carpeta):
    w = ajustes(cfg["muestras"]); mundo(w, (.5, .52, .5), .14)
    caja_redonda("mesa", (.5, .5, .03), (0, 0, -.015), .003, mat_madera("nogal", (.07, .035, .018), (.17, .085, .04), tabla=.1), 3)
    caja_redonda("pata", (.04, .04, .5), (.2, .2, -.28), .002, mat_madera("nogal_p", (.07, .035, .018), (.17, .085, .04)), 2)
    plano("suelo", 8, (0, 0, -.53), L3.mat_liso("suelo", (.06, .05, .04), .6))
    # sofá de terciopelo verde detrás, desenfocado
    verde = mat_terciopelo("terciopelo_verde", (.02, .07, .055), (.5, .8, .7))
    caja_redonda("sofa_asiento", (1.6, .7, .2), (-.3, .62, -.12), .06, verde, 8)
    caja_redonda("sofa_respaldo", (1.6, .22, .55), (-.3, .95, .1), .08, verde, 8, (-8, 0, 0))
    plano("pared", 8, (0, 1.2, 2.0), mat_yeso("pared", (.24, .22, .19)), (90, 0, 0), sombra=False)
    raiz, caja = libro("libro", cfg, ruta_cub)
    coloca(raiz, caja, 18, (0, -.01))
    d = direccion(130, 33)
    sol(d, 4.4, (1.0, .86, .68), .7)
    gobo(d, [(-.9, -.9), (.9, -.9), (.9, .9), (-.9, .9)], carpeta=carpeta,
         sombras=hojas(46, (-.5, .25, -.05, .5), semilla=11) + hojas(12, (-.45, -.05, -.4, .1), semilla=5))
    camara((0, .0, caja[4] / 2), .84, -22, 38, 58, 8)

ESCENAS = {"santa-fe": escena_santa_fe, "primitivismo": escena_primitivismo, "coin": escena_coin,
           "en-noir": escena_en_noir, "tortajada": escena_tortajada, "territorios": escena_territorios}

# ---------------------------------------------------------------- principal

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("libro", choices=sorted(LIBROS)); ap.add_argument("salida")
    ap.add_argument("--escala", type=int, default=100); ap.add_argument("--muestras", type=int, default=160)
    a = ap.parse_args()
    cfg = dict(LIBROS[a.libro]); cfg["muestras"] = a.muestras
    carpeta = tempfile.mkdtemp(prefix="portada3d_")
    ruta_cub = cubierta(cfg, carpeta)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ESCENAS[a.libro](cfg, ruta_cub, carpeta)
    sc = bpy.context.scene; sc.render.resolution_percentage = a.escala
    png = os.path.join(carpeta, "render.png"); sc.render.filepath = png; sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    im = Image.open(png).convert("RGB")
    # grano fino de foto
    g = np.random.default_rng(1).normal(0, 2.2, (im.height, im.width, 1))
    im = Image.fromarray(np.clip(np.asarray(im).astype(float) + g, 0, 255).astype(np.uint8))
    im.save(a.salida, quality=92, optimize=True, progressive=True)

if __name__ == "__main__":
    main()
