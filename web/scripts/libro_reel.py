"""Reel vertical 9:16 (1080x1920) de un libro de tapa dura en 3D, para Instagram.

El libro cerrado descansa sobre una mesa gris oscura con luz lateral de ventana. La cámara se acerca despacio a la
portada, la tapa se abre girando sobre el cajo y enseña las guardas, y luego pasan las hojas en el orden del libro:
una hoja suelta, o un mazo de hojas cuando se salta a un doble más adelante (nunca hacia atrás). Plano final fijo.

Modelo: libro abierto por el principio. El bloque de hojas sigue entero sobre la tapa trasera; la tapa delantera
cuelga del cajo (arriba del lomo) y queda apoyada en la mesa un poco inclinada; las hojas que pasan se apilan encima.
El lomo de la cubierta es redondeado, con los surcos de los cajos, y se dobla en el cajo delantero al abrir.

Requiere: python3 -m pip install bpy   (Blender como módulo de Python)
Uso:
  python3 web/scripts/libro_reel.py --cubierta cubierta.png --lomo 26 --mm 165 240 --paginas 320 \
      --pagina 1=titulo.png --doble 10=dobles_10_11.png --doble 22=... --pasos 0 1-5 6-11 12-24 --salida reel.mp4
  --pdf interior.pdf: las páginas que falten salen del PDF (página n del PDF = página n del libro).
  --pasos: hojas que pasa cada paso (la hoja 0 es la guarda; la hoja k lleva las páginas 2k-1 y 2k).
  --prueba 0,90,200: solo esos fotogramas (PNG en --carpeta/f), para revisar.
  --cortes 0,4,6.1: dibuja el perfil del libro (corte por el pie) en esos segundos, sin renderizar.
"""
import argparse, math, os, shutil, subprocess, sys, tempfile, time
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libro_3d import (suave, tramo, pagina_pdf, dobles_imagen, Rejilla, caja, matriz_giro, nodo, entrada,  # noqa: E402
                      salida, material, imagen, mat_imagen, mat_canto, mat_liso)

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

VW, VH, FPS = 1080, 1920, 24
TOTAL = 15.0
ACERCA = (0.0, 3.0)        # la cámara se acerca a la portada
TAPA = (3.0, 5.0)          # se abre la tapa
PASAN = (5.3, 13.5)        # pasan las hojas; luego plano fijo hasta el final
DURA = 1.45                # lo que tarda cada paso de hoja
QUIETO = 14.3              # desde aquí la cámara ya no se mueve
NS, NY, NV = 90, 16, 6     # resolución: a lo ancho de la hoja, a lo alto, en el grueso

# ---------------------------------------------------------------- utilidades 2D

def bezier(P, n=80):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3]

def por_arco(c, s):
    """Puntos de la polilínea c (n, 2) a las longitudes de arco s, contadas desde su primer punto."""
    arco = np.r_[0, np.cumsum(np.hypot(*np.diff(c, axis=0).T))]
    return np.stack([np.interp(s, arco, c[:, 0]), np.interp(s, arco, c[:, 1])], -1)

def angulos(p):
    return np.arctan2(np.diff(p[:, 1]), np.diff(p[:, 0]))

# ---------------------------------------------------------------- el libro

class Tomo:
    """Tapa dura abierta por el principio. Ejes: lomo en x=0, pie en y=0, mesa en z=0. Cerrado, el bloque ocupa
    x 0..W sobre la tapa trasera (z 0..c) y la tapa delantera va encima; abierto, la delantera queda a la izquierda."""
    def __init__(s, W, H, T, hojas, cubierta, lomo, c=.0025, ceja=.003, cajo=.004):
        s.W, s.H, s.T, s.c, s.ceja, s.cajo = W, H, T, c, ceja, cajo
        s.hojas, s.t = hojas, T / hojas
        s.zp = c + T + .0003                 # cara de dentro de la tapa delantera cerrada; el eje de giro (x=0)
        s.r0, s.lam, s.abombe = .0022, .007, .0012
        s.s = np.linspace(0, 1, NS + 1) ** 1.5 * W   # longitudes de arco a lo ancho de la hoja (más puntos en el lomo)
        D = W + ceja
        a = .1
        for _ in range(40): a = math.asin(min(1.0, (s.zp - c * math.cos(a)) / D))
        s.alfa = a                           # la tapa abierta toca la mesa por el canto
        s.beta_fin = math.pi + a
        # cubierta desplegada [trasera | lomo | portada], escalada al alto de los cartones
        im = Image.open(cubierta)
        s.alto = H + 2 * ceja
        s.total = s.alto * im.width / im.height
        pliegue = W + ceja - (s.total - lomo) / 2     # x del lomo de la cubierta con el libro cerrado
        s.mA = (cajo - pliegue) / .75
        a_ = np.asarray(im.convert("RGB")).astype(float) / 255
        k = max(2, a_.shape[0] // 80)
        def borde(x0, x1):
            p = a_[:, int(x0 * a_.shape[1]):int(x1 * a_.shape[1])]
            return tuple(np.median(np.concatenate([p[:k].reshape(-1, 3), p[-k:].reshape(-1, 3)]), axis=0) ** 2.2)
        s.color_portada, s.color_trasera = borde(.55, 1), borde(0, .45)

    # coordenadas de textura de la cubierta
    def u_trasera(s, x): return (s.W + s.ceja - x) / s.total
    def u_portada(s, x): return 1 - (s.W + s.ceja - x) / s.total     # x de la tapa delantera cerrada
    def v(s, y): return (y + s.ceja) / s.alto

    def gira(s, p, beta):
        """Tapa delantera: giro antihorario (visto desde el pie) de beta alrededor del eje (x=0, z=zp)."""
        x, z = p[..., 0], p[..., 1] - s.zp
        cb, sb = math.cos(beta), math.sin(beta)
        return np.stack([x * cb - z * sb, x * sb + z * cb + s.zp], -1)

    def derecha(s, hR, k=1.0):
        """Cara de arriba del bloque de la derecha (grueso hR), por longitud de arco desde el lomo."""
        xs = np.linspace(0, s.W * 1.2, 3000)
        S = 1 - np.exp(-(xs / s.lam) ** .85)
        z = s.c + hR - s.r0 * (1 - S) + k * s.abombe * np.sin(np.pi * np.clip(xs / s.W, 0, 1)) ** 1.3 * S
        return por_arco(np.stack([xs, z], -1), s.s)

    def izquierda(s, hL, beta):
        """Hoja de arriba de lo que hay a la izquierda (grueso hL sobre la tapa delantera; hL=0: la guarda pegada).
        Sale del lomo, pasa por el cajo y sigue la tapa."""
        G = np.array([0.0, s.c + s.T - hL - s.r0])
        cb, sb = math.cos(beta), math.sin(beta)
        nrm = np.array([sb, -cb])            # normal de la cara de dentro de la tapa, hacia las hojas
        dB = np.array([cb, sb])              # del cajo hacia el canto de la tapa
        Bi = np.array([0.0, s.zp]) + s.cajo * dB + (hL + .00015) * nrm
        L = np.linalg.norm(Bi - G)
        g = beta * .62
        tira = bezier([G, G + .45 * L * np.array([math.cos(g), math.sin(g)]), Bi - .45 * L * dB, Bi], 60)
        recta = Bi + np.linspace(0, s.W * 1.2, 800)[1:, None] * dB
        return por_arco(np.concatenate([tira, recta]), s.s)

    def hoja(s, u, R, Lz, pliegue=1.0):
        """Hoja (o mazo) que pasa de su sitio a la derecha (R) a su sitio a la izquierda (Lz), girando desde el lomo:
        primero se levanta la esquina del pie y la punta va por delante; al caer, la punta va por detrás."""
        thR = angulos(R)
        thL = angulos(Lz); thL = np.where(thL < 0, thL + 2 * np.pi, thL)
        ds = np.diff(s.s)
        sm = (s.s[:-1] + s.s[1:]) / 2 / s.W
        pts = np.empty((NS + 1, NY, 3))
        for j, y in enumerate(np.linspace(0, s.H, NY)):
            ue = min(1.0, max(0.0, (u - .16 * (y / s.H)) / .84))
            A = suave(ue)
            curva = (.75 * math.sin(2 * math.pi * ue) - .3 * math.sin(math.pi * ue)) * pliegue
            th = np.clip((1 - A) * thR + A * thL + curva * sm ** 1.5, np.minimum(thR, thL), np.maximum(thR, thL))
            x = R[0, 0] + np.r_[0, np.cumsum(ds * np.cos(th))]
            z = R[0, 1] + np.r_[0, np.cumsum(ds * np.sin(th))]
            pts[:, j] = np.stack([x, np.full_like(x, y), z], -1)
        return pts

    def lomo(s, beta, n=90):
        """Perfil de fuera del lomo de la cubierta, del cajo de la trasera al de la delantera; Bézier tangente a los
        cartones, que al abrir se cierra sobre el cajo delantero. Por longitud de arco, con el surco de cada cajo."""
        A = np.array([s.cajo, 0.0])
        B = s.gira(np.array([s.cajo, s.zp + s.c]), beta)
        dB = np.array([math.cos(beta), math.sin(beta)])
        abre = suave(tramo(beta, math.pi * .35, s.beta_fin))
        mB = s.mA * (1 - .78 * abre)
        c = bezier([A, A + s.mA * np.array([-1.0, 0]), B - mB * dB, B], 400)
        arco = np.r_[0, np.cumsum(np.hypot(*np.diff(c, axis=0).T))]
        q = np.linspace(0, arco[-1], n)
        p = por_arco(c, q)
        d = np.gradient(p, axis=0); d /= np.linalg.norm(d, axis=1)[:, None]
        dentro = np.stack([d[:, 1], -d[:, 0]], -1)
        surco = sum(np.exp(-((q - s0) / .0011) ** 2) for s0 in (.0028, arco[-1] - .0028))
        return p + dentro * (.0007 * surco)[:, None]

    def uv_lomo(s, n=90):
        u = np.linspace(s.u_trasera(s.cajo), s.u_portada(s.cajo), n)
        return np.stack(np.broadcast_arrays(u[:, None], np.array([0.0, 1.0])[None, :]), -1)

# ---------------------------------------------------------------- guion: qué hojas pasan y cuándo

class Guion:
    def __init__(s, pasos, hojas):
        s.hojas = hojas
        n = len(pasos)
        hueco = (PASAN[1] - PASAN[0] - n * DURA) / max(1, n - 1)
        s.pasos = [(PASAN[0] + i * (DURA + hueco), PASAN[0] + i * (DURA + hueco) + DURA, a, b)
                   for i, (a, b) in enumerate(pasos)]

    def en(s, t):
        """Hojas ya pasadas a la izquierda, mazo en el aire (primera, última, avance) o None."""
        izq, aire = 0, None
        for t0, t1, a, b in s.pasos:
            if t >= t1: izq = b + 1
            elif t > t0:
                x = (t - t0) / (t1 - t0)
                aire = (a, b, suave(x) * .5 + x * .5)
                izq = a
                break
            else:
                izq = a; break
        return izq, aire

# ---------------------------------------------------------------- texturas

def guarda(color, carpeta, w=1100, h=1600):
    """Papel de color para las guardas, con algo de fibra."""
    rng = np.random.default_rng(7)
    base = np.array(color, float)[None, None, :]
    ruido = sum(np.asarray(Image.fromarray((rng.random((h // f + 1, w // f + 1)) * 255).astype(np.uint8))
                           .resize((w, h), Image.BICUBIC)).astype(float) / 255 - .5 for f in (2, 9, 40)) / 3
    fibra = np.asarray(Image.fromarray((rng.random((h // 3, w)) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC))
    a = base * (1 + .05 * ruido[..., None] + .025 * (fibra[..., None] / 255 - .5))
    ruta = os.path.join(carpeta, "guarda.png")
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(ruta)
    return ruta

# ---------------------------------------------------------------- Blender

def bsdf_de(m):
    return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")

def grano(m, escala, fuerza, uv=True):
    """Relieve muy fino (papel o cartulina)."""
    nt = m.node_tree; b = bsdf_de(m)
    tc = nodo(nt, "ShaderNodeTexCoord")
    nz = nodo(nt, "ShaderNodeTexNoise"); entrada(nz, "Scale").default_value = escala; entrada(nz, "Detail").default_value = 3
    nt.links.new(salida(tc, "UV" if uv else "Object"), entrada(nz, "Vector"))
    bp = nodo(nt, "ShaderNodeBump"); entrada(bp, "Strength").default_value = fuerza
    entrada(bp, "Distance").default_value = .0001
    nt.links.new(salida(nz, "Factor"), entrada(bp, "Height")); nt.links.new(salida(bp, "Normal"), entrada(b, "Normal"))

def mat_pagina(nombre, ruta, espejo_u=False):
    m, tx = mat_imagen(nombre, ruta, rug=.62, espec=.3, espejo_u=espejo_u)
    tx.interpolation = "Cubic"
    grano(m, 260, .05)
    return m, tx

def mat_mesa():
    m, nt, b = material("mesa")
    tc = nodo(nt, "ShaderNodeTexCoord")
    nz = nodo(nt, "ShaderNodeTexNoise"); entrada(nz, "Scale").default_value = 9; entrada(nz, "Detail").default_value = 4
    nt.links.new(salida(tc, "Object"), entrada(nz, "Vector"))
    cr = nodo(nt, "ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (.034, .034, .035, 1); cr.color_ramp.elements[1].color = (.048, .047, .047, 1)
    nt.links.new(salida(nz, "Factor"), entrada(cr, "Factor")); nt.links.new(salida(cr, "Color"), entrada(b, "Base Color"))
    entrada(b, "Roughness").default_value = .88
    entrada(b, "Specular IOR Level").default_value = .3
    # textura fina, como un yeso mate
    nf = nodo(nt, "ShaderNodeTexNoise"); entrada(nf, "Scale").default_value = 900; entrada(nf, "Detail").default_value = 6
    nt.links.new(salida(tc, "Object"), entrada(nf, "Vector"))
    bp = nodo(nt, "ShaderNodeBump"); entrada(bp, "Strength").default_value = .12; entrada(bp, "Distance").default_value = .0004
    nt.links.new(salida(nf, "Factor"), entrada(bp, "Height")); nt.links.new(salida(bp, "Normal"), entrada(b, "Normal"))
    return m

def luz(sc, nombre, pos, tam, energia, color, mira):
    d = bpy.data.lights.new(nombre, "AREA"); d.shape = "RECTANGLE"; d.size, d.size_y = tam
    d.energy = energia; d.color = color
    o = bpy.data.objects.new(nombre, d); sc.collection.objects.link(o)
    o.location = pos
    o.rotation_euler = (Vector(mira) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    return o

def rejilla_y(p2, ys):
    """Perfil (n, 2) en xz estirado a lo largo de y: rejilla (n, len(ys), 3)."""
    return np.stack(np.broadcast_arrays(p2[:, None, 0], ys[None, :], p2[:, None, 1]), -1)

def uv_rect(n1, n2):
    return np.stack(np.broadcast_arrays(np.linspace(0, 1, n1)[:, None], np.linspace(0, 1, n2)[None, :]), -1)

def escena(L, tex, muestras):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"
    sc.cycles.samples = muestras
    sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = .03
    sc.cycles.use_denoising = True
    try: sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception: pass
    sc.cycles.max_bounces = 6; sc.cycles.diffuse_bounces = 3; sc.cycles.glossy_bounces = 2
    sc.cycles.transmission_bounces = 2; sc.cycles.transparent_max_bounces = 2
    sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
    sc.render.use_persistent_data = True
    sc.render.resolution_x, sc.render.resolution_y = VW, VH
    sc.render.image_settings.file_format = "PNG"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"

    w = bpy.data.worlds.new("mundo"); sc.world = w
    try: w.use_nodes = True
    except Exception: pass
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    entrada(bg, "Color").default_value = (.62, .64, .68, 1); entrada(bg, "Strength").default_value = .03

    centro = (0, L.H / 2, 0)
    luz(sc, "ventana", (-1.45, .5, 1.35), (1.0, 1.5), 52, (1, .975, .94), centro)
    luz(sc, "rebote", (1.4, -.6, 1.3), (1.6, 1.6), 10, (.93, .96, 1), centro)
    luz(sc, "frente", (-.2, -1.4, 1.0), (1.4, .7), 8, (1, .98, .96), centro)

    bpy.ops.mesh.primitive_plane_add(size=6, location=(0, L.H / 2, -.00005))
    bpy.context.active_object.data.materials.append(mat_mesa())

    O = {}
    O["canto"] = mat_canto(60)
    O["canto_izq"] = mat_canto(14)
    O["canto_mazo"] = mat_liso("canto_mazo", (.78, .76, .72), .85, .2)
    O["papel"] = mat_liso("papel", (.82, .80, .76), .8, .2)
    O["cub"], _ = mat_imagen("cubierta", tex["cubierta"], rug=.42, espec=.4)
    grano(O["cub"], 1500, .05, uv=False)
    O["dobla_p"] = mat_liso("dobla_portada", L.color_portada, .45, .4)
    O["dobla_t"] = mat_liso("dobla_trasera", L.color_trasera, .45, .4)
    O["carton"] = mat_liso("carton_gris", (.30, .28, .26), .9, .2)
    O["guarda"], _ = mat_pagina("guarda", tex["guarda"])
    O["der"], O["tx_der"] = mat_pagina("pag_der", tex["blanco"])
    O["izq"], O["tx_izq"] = mat_pagina("pag_izq", tex["blanco"], espejo_u=True)
    O["frente"], O["tx_frente"] = mat_pagina("mazo_frente", tex["blanco"])
    O["dorso"], O["tx_dorso"] = mat_pagina("mazo_dorso", tex["blanco"], espejo_u=True)

    W, H, c = L.W, L.H, L.c
    E = {}
    uvh = uv_rect(NS + 1, 2)
    # bloque de la derecha
    E["der"] = Rejilla("der_arriba", uvh, O["der"])
    E["der_pie"] = Rejilla("der_pie", uv_rect(NS + 1, NV), O["canto"])
    E["der_cab"] = Rejilla("der_cabeza", uv_rect(NS + 1, NV), O["canto"])
    E["der_corte"] = Rejilla("der_corte", uv_rect(2, NV), O["canto"])
    E["der_lomo"] = Rejilla("der_lomo", uv_rect(NV, 2), O["papel"])
    # a la izquierda: la guarda pegada a la tapa y, encima, las hojas que han pasado
    E["guarda"] = Rejilla("guarda_pegada", uvh, O["guarda"])
    E["izq"] = Rejilla("izq_arriba", uvh, O["izq"])
    E["izq_pie"] = Rejilla("izq_pie", uv_rect(NS + 1, NV), O["canto_izq"])
    E["izq_cab"] = Rejilla("izq_cabeza", uv_rect(NS + 1, NV), O["canto_izq"])
    E["izq_corte"] = Rejilla("izq_corte", uv_rect(2, NV), O["canto_izq"])
    # tapas
    x0, x1, y0, y1 = L.cajo, W + L.ceja, -L.ceja, H + L.ceja
    E["trasera"] = caja("trasera", x0, x1, y0, y1, 0, c, [O["cub"], O["dobla_t"], O["dobla_t"]],
                        lambda x, y: (L.u_trasera(x), L.v(y)))
    E["delantera"] = caja("delantera", x0, x1, y0, y1, L.zp, L.zp + c, [O["dobla_p"], O["cub"], O["dobla_p"]],
                          lambda x, y: (L.u_portada(x), L.v(y)))
    for ob in (E["trasera"], E["delantera"]): ob.modifiers["bisel"].width = .0005; ob.modifiers["bisel"].segments = 3
    E["lomo"] = Rejilla("lomo_tapa", L.uv_lomo(), O["cub"])
    E["lomo"].me.materials.append(O["carton"]); E["lomo"].me.materials.append(O["dobla_t"])
    so = E["lomo"].ob.modifiers.new("grosor", "SOLIDIFY"); so.thickness = .0009; so.offset = -1
    so.material_offset = 1; so.material_offset_rim = 2
    # el mazo (o la hoja) que pasa: cara de delante, cara de detrás y canto
    uvm = np.stack(np.broadcast_arrays((L.s / W)[:, None], np.linspace(0, 1, NY)[None, :]), -1)
    E["mazo"] = Rejilla("mazo", uvm, O["frente"])
    E["mazo"].me.materials.append(O["dorso"]); E["mazo"].me.materials.append(O["canto_mazo"])
    so = E["mazo"].ob.modifiers.new("grosor", "SOLIDIFY"); so.offset = -1
    so.material_offset = 1; so.material_offset_rim = 2
    E["mazo_grosor"] = so
    # las tapas de arriba de los bloques usan la misma u que el mazo (longitud de arco)
    for k in ("der", "izq", "guarda"):
        capa = E[k].me.uv_layers[0]
        vi = np.empty(len(E[k].me.loops), np.int32); E[k].me.loops.foreach_get("vertex_index", vi)
        uv = np.stack(np.broadcast_arrays((L.s / W)[:, None], np.array([0.0, 1.0])[None, :]), -1).reshape(-1, 2)
        capa.data.foreach_set("uv", uv[vi].ravel().astype(np.float32))

    cam_d = bpy.data.cameras.new("camara"); cam_d.sensor_width = 36; cam_d.sensor_fit = "AUTO"; cam_d.lens = 70
    cam = bpy.data.objects.new("camara", cam_d); sc.collection.objects.link(cam); sc.camera = cam
    E["cam"] = cam; E["O"] = O
    return E

# ---------------------------------------------------------------- estado en cada instante

def caras_bloque(top, bot, ys, nv=NV):
    """Caras de canto de un bloque de hojas entre el perfil de abajo y el de arriba (mismos puntos de arco)."""
    v = np.linspace(0, 1, nv)
    P = bot[:, None, :] * (1 - v)[None, :, None] + top[:, None, :] * v[None, :, None]   # (n, nv, 2)
    def g(x, y, z): return np.stack(np.broadcast_arrays(x, y, z), -1)
    return {"pie": g(P[..., 0], ys[0], P[..., 1]),
            "cab": g(P[..., 0], ys[1], P[..., 1]),
            "corte": g(P[-1, :, 0][None, :], np.array(ys)[:, None], P[-1, :, 1][None, :]),
            "lomo": g(P[0, :, 0][:, None], np.array(ys)[None, :], P[0, :, 1][:, None])}

def estado(L, guion, t):
    abre = suave(tramo(t, *TAPA))
    beta = L.beta_fin * abre
    izq, aire = guion.en(t)
    n_aire = 0 if aire is None else aire[1] - aire[0] + 1
    hL = izq * L.t
    hR = L.T - hL - n_aire * L.t
    G = {"beta": beta, "abre": abre, "izq_n": izq, "aire": aire, "hL": hL, "hR": hR}
    G["der"] = L.derecha(hR, abre)
    G["der_bajo"] = np.stack([L.s, np.full_like(L.s, L.c)], -1)
    G["guarda"] = L.izquierda(0, beta)
    G["izq"] = L.izquierda(hL, beta) if izq > 0 else None
    if aire:
        tb = n_aire * L.t
        R = L.derecha(hR + tb, abre)
        Lz = L.izquierda(hL, L.beta_fin)
        G["mazo"] = L.hoja(aire[2], R, Lz, pliegue=1.0 if n_aire == 1 else .55)
        G["mazo_t"] = tb
    else:
        G["mazo"] = None
    G["lomo"] = L.lomo(beta)
    return G

def puntos(L, G):
    ys = np.array([0.0, L.H])
    pts = [rejilla_y(G["der"], ys).reshape(-1, 3), rejilla_y(G["guarda"], ys).reshape(-1, 3),
           rejilla_y(G["lomo"], np.array([-L.ceja, L.H + L.ceja])).reshape(-1, 3)]
    if G["izq"] is not None: pts.append(rejilla_y(G["izq"], ys).reshape(-1, 3))
    if G["mazo"] is not None: pts.append(G["mazo"][::6, ::5].reshape(-1, 3))
    x0, x1, y0, y1 = L.cajo, L.W + L.ceja, -L.ceja, L.H + L.ceja
    tr = np.array([[x, y, z] for x in (x0, x1) for y in (y0, y1) for z in (0, L.c)])
    de = np.array([[x, y, z] for x in (x0, x1) for y in (y0, y1) for z in (L.zp, L.zp + L.c)])
    xz = L.gira(de[:, [0, 2]], G["beta"])
    de = np.stack([xz[:, 0], de[:, 1], xz[:, 1]], -1)
    return np.concatenate(pts + [tr, de])

# ---------------------------------------------------------------- cámara

def angulos_camara(t):
    t = min(t, QUIETO)
    el = math.radians(57 + 12 * suave(tramo(t, 1.5, PASAN[1])))
    az = math.radians(-18 + 18 * suave(tramo(t, 1.0, PASAN[1])))
    return el, az

def ancho_deseado(t, abre):
    cerrado = .63 + .06 * suave(tramo(t, *ACERCA))
    abierto = .86 + .025 * suave(tramo(t, 6, PASAN[1]))
    return cerrado + (abierto - cerrado) * abre

def base(dirc):
    f = -dirc / np.linalg.norm(dirc)
    r = np.cross(f, [0, 0, 1]); r /= np.linalg.norm(r)
    return f, r, np.cross(r, f)

def proyecta(P, pos, f, r, u, lente):
    d = P - pos
    esc = lente / 36 * max(VW, VH)
    zc = d @ f
    return d @ r / zc * esc, d @ u / zc * esc      # en píxeles desde el centro (x a la derecha, y arriba)

def suaviza(v, sig):
    v = np.array(v, float); r = int(3 * sig)
    k = np.exp(-np.arange(-r, r + 1) ** 2 / (2 * sig * sig)); k /= k.sum()
    pad = [(r, r)] + [(0, 0)] * (v.ndim - 1)
    return np.apply_along_axis(lambda c: np.convolve(c, k, mode="valid"), 0, np.pad(v, pad, mode="edge"))

def maximo(v, r):
    v = np.pad(np.asarray(v, float), r, mode="edge")
    return np.array([v[i:i + 2 * r + 1].max() for i in range(len(v) - 2 * r)])

def encuadres(L, guion, n, lente, margen=.035):
    """Para cada fotograma: punto al que mira la cámara, distancia y descentrado, suavizados en el tiempo y sin que
    el libro se salga nunca del cuadro (con un margen)."""
    sig = FPS * .7
    OB, DI, PS, DIR = [], [], [], []
    for i in range(n):
        t = i / FPS
        G = estado(L, guion, t)
        P = puntos(L, G)
        el, az = angulos_camara(t)
        dirc = np.array([math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)])
        ob = np.array([(P[:, 0].min() + P[:, 0].max()) / 2, (P[:, 1].min() + P[:, 1].max()) / 2, L.c + L.T / 2])
        f, r, u = base(dirc)
        D = .9
        for _ in range(6):
            x, y = proyecta(P, ob + D * dirc, f, r, u, lente)
            D *= ((x.max() - x.min()) / VW) / ancho_deseado(t, G["abre"])
        OB.append(ob); DI.append(D); PS.append(P); DIR.append(dirc)
    OB = suaviza(OB, sig)
    DI = suaviza(maximo(DI, int(sig)), sig)
    M = max(VW, VH)
    for _ in range(4):
        SX, SY, K = [], [], []
        for i in range(n):
            f, r, u = base(DIR[i])
            x, y = proyecta(PS[i], OB[i] + DI[i] * DIR[i], f, r, u, lente)
            SX.append((x.max() + x.min()) / 2 / M); SY.append((y.max() + y.min()) / 2 / M)
        SX, SY = suaviza(SX, sig * .6), suaviza(SY, sig * .6)
        for i in range(n):
            f, r, u = base(DIR[i])
            x, y = proyecta(PS[i], OB[i] + DI[i] * DIR[i], f, r, u, lente)
            x, y = x - SX[i] * M, y - SY[i] * M
            K.append(max(1.0, np.abs(x).max() / (VW * (.5 - margen)), np.abs(y).max() / (VH * (.5 - margen))))
        K = np.array(K)
        if K.max() <= 1.0005: break
        DI = DI * suaviza(maximo(K * 1.01, int(sig)), sig)
    q = int(QUIETO * FPS)
    for v in (OB, DI, SX, SY): v[q:] = v[q]
    return OB, DI, SX, SY

# ---------------------------------------------------------------- páginas

class Paginas:
    """Imagen de cada página del libro (1 = la primera). La hoja 0 es la guarda; la hoja k lleva 2k-1 y 2k."""
    def __init__(s, carpeta, pdf, sueltas, dobles, guarda_ruta, blanco, hojas):
        s.carpeta, s.pdf, s.p, s.guarda, s.blanco, s.hojas = carpeta, pdf, dict(sueltas), guarda_ruta, blanco, hojas
        for i, (n, ruta) in enumerate(dobles):
            a, b = dobles_imagen(ruta, carpeta, i)
            s.p.setdefault(n, a); s.p.setdefault(n + 1, b)

    def pagina(s, n):
        if n not in s.p:
            s.p[n] = pagina_pdf(s.pdf, n, s.carpeta) if s.pdf else s.blanco
        return s.p[n]

    def recto(s, k): return s.guarda if k <= 0 or k >= s.hojas - 1 else s.pagina(2 * k - 1)
    def verso(s, k): return s.guarda if k <= 0 or k >= s.hojas - 1 else s.pagina(2 * k)

# ---------------------------------------------------------------- principal

def cortes(L, guion, tiempos, ruta, esc=5.0):
    """Perfil del libro (corte por el pie) en esos segundos, en mm y a escala esc px/mm."""
    from PIL import ImageDraw
    w, h = int(380 * esc), int(60 * esc)
    hoja = Image.new("RGB", (w, h * len(tiempos)), "white")
    d = ImageDraw.Draw(hoja)
    for k, t in enumerate(tiempos):
        G = estado(L, guion, t)
        alto = 200 if 3.2 < t < 4.8 else 52
        e = esc * 52 / alto
        def xy(p): return [(w / 2 + x * 1000 * e, h * (k + 1) - 6 - z * 1000 * e) for x, z in np.asarray(p)]
        d.line([(0, h * (k + 1) - 6), (w, h * (k + 1) - 6)], fill=(0, 0, 0))
        x0, x1 = L.cajo, L.W + L.ceja
        d.polygon(xy([[x0, 0], [x1, 0], [x1, L.c], [x0, L.c]]), fill=(160, 160, 160))
        q = L.gira(np.array([[x0, L.zp], [x1, L.zp], [x1, L.zp + L.c], [x0, L.zp + L.c]]), G["beta"])
        d.polygon(xy(q), fill=(100, 100, 100))
        d.line(xy(G["der"]), fill=(0, 0, 255)); d.line(xy(G["guarda"]), fill=(200, 0, 160))
        if G["izq"] is not None: d.line(xy(G["izq"]), fill=(0, 160, 0))
        if G["mazo"] is not None:
            d.line(xy(G["mazo"][:, 0, [0, 2]]), fill=(255, 0, 0)); d.line(xy(G["mazo"][:, -1, [0, 2]]), fill=(255, 150, 0))
        d.line(xy(G["lomo"]), fill=(0, 0, 0), width=2)
        d.text((8, h * k + 6), f"t={t}s  escala {e:.1f} px/mm", fill=(0, 0, 0))
    hoja.save(ruta)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cubierta", required=True, help="cubierta desplegada [trasera | lomo | portada] sin solapas")
    ap.add_argument("--lomo", type=float, required=True, help="ancho del lomo en mm")
    ap.add_argument("--mm", type=float, nargs=2, required=True)
    ap.add_argument("--paginas", type=int, required=True)
    ap.add_argument("--pdf", help="interior; página n del PDF = página n del libro")
    ap.add_argument("--pagina", action="append", default=[], help="N=imagen de la página N")
    ap.add_argument("--doble", action="append", default=[], help="N=imagen del doble de páginas N y N+1")
    ap.add_argument("--pasos", nargs="+", required=True, help="hojas de cada paso: 0  1-5  6-11 ...")
    ap.add_argument("--color-guarda", default="7d1450")
    ap.add_argument("--salida", default=""); ap.add_argument("--carpeta", default="")
    ap.add_argument("--muestras", type=int, default=64); ap.add_argument("--escala", type=int, default=100)
    ap.add_argument("--prueba", default=""); ap.add_argument("--cada", type=int, default=1)
    ap.add_argument("--cortes", default="")
    a = ap.parse_args()
    tmp = a.carpeta or tempfile.mkdtemp(prefix="reel_")
    os.makedirs(os.path.join(tmp, "f"), exist_ok=True)

    hojas = a.paginas // 2 + 2                     # más las dos guardas sueltas
    lomo = a.lomo / 1000; carton = .0025
    L = Tomo(a.mm[0] / 1000, a.mm[1] / 1000, lomo - 2 * carton, hojas, a.cubierta, lomo, c=carton)
    pasos = []
    for p in a.pasos:
        i, _, j = p.partition("-"); pasos.append((int(i), int(j or i)))
    for (a0, b0), (a1, b1) in zip(pasos, pasos[1:]):
        assert a1 == b0 + 1, "los pasos tienen que ir seguidos: las hojas pasan en el orden del libro"
    assert pasos[0][0] == 0
    guion = Guion(pasos, hojas)
    if a.cortes:
        cortes(L, guion, [float(x) for x in a.cortes.split(",")], os.path.join(tmp, "cortes.png"))
        return

    col = tuple(int(a.color_guarda[i:i + 2], 16) for i in (0, 2, 4))
    blanco = os.path.join(tmp, "blanco.png"); Image.new("RGB", (64, 64), (238, 236, 230)).save(blanco)
    sueltas = [(int(x.split("=")[0]), x.split("=", 1)[1]) for x in a.pagina]
    dobles = [(int(x.split("=")[0]), x.split("=", 1)[1]) for x in a.doble]
    P = Paginas(tmp, a.pdf, sueltas, dobles, guarda(col, tmp), blanco, hojas)
    E = escena(L, {"cubierta": a.cubierta, "guarda": P.guarda, "blanco": blanco}, a.muestras)
    sc = bpy.context.scene
    sc.render.resolution_percentage = a.escala
    n = int(round(TOTAL * FPS))
    lente = 70.0
    OB, DI, SX, SY = encuadres(L, guion, n, lente)
    cuadros = [int(x) for x in a.prueba.split(",")] if a.prueba else range(0, n, a.cada)
    ys = np.array([0.0, L.H])
    fijo = int(max(QUIETO, PASAN[1]) * FPS) + 1     # desde aquí todos los fotogramas son iguales
    for i in cuadros:
        ruta = os.path.join(tmp, "f", f"{i:04d}.png")
        if not a.prueba and os.path.exists(ruta): continue
        if i > fijo and os.path.exists(os.path.join(tmp, "f", f"{fijo:04d}.png")):
            shutil.copy(os.path.join(tmp, "f", f"{fijo:04d}.png"), ruta); continue
        t0 = time.time(); t = i / FPS
        G = estado(L, guion, t)
        E["der"].pon(rejilla_y(G["der"], ys))
        for k, g in caras_bloque(G["der"], G["der_bajo"], ys).items(): E["der_" + k].pon(g)
        E["guarda"].pon(rejilla_y(G["guarda"], ys))
        hay = G["izq"] is not None
        for k in ("izq", "izq_pie", "izq_cab", "izq_corte"): E[k].ob.hide_render = not hay
        if hay:
            E["izq"].pon(rejilla_y(G["izq"], ys))
            for k, g in caras_bloque(G["izq"], G["guarda"], ys).items():
                if k != "lomo": E["izq_" + k].pon(g)
            E["O"]["tx_izq"].image = imagen(P.verso(G["izq_n"] - 1))
        E["delantera"].matrix_world = matriz_giro(L.zp, G["beta"])
        E["lomo"].pon(rejilla_y(G["lomo"], np.array([-L.ceja, L.H + L.ceja])))
        primera_der = G["izq_n"] + (0 if G["aire"] is None else G["aire"][1] - G["aire"][0] + 1)
        E["O"]["tx_der"].image = imagen(P.recto(primera_der))
        E["mazo"].ob.hide_render = G["mazo"] is None
        if G["mazo"] is not None:
            E["mazo"].pon(G["mazo"])
            E["mazo_grosor"].thickness = max(G["mazo_t"], .00012)
            E["O"]["tx_frente"].image = imagen(P.recto(G["aire"][0]))
            E["O"]["tx_dorso"].image = imagen(P.verso(G["aire"][1]))
        el, az = angulos_camara(t)
        dirc = np.array([math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)])
        pos = OB[i] + DI[i] * dirc
        cam = E["cam"]
        cam.location = Vector(pos)
        cam.rotation_euler = Vector(-dirc).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = lente; cam.data.shift_x = float(SX[i]); cam.data.shift_y = float(SY[i])
        sc.render.filepath = ruta
        bpy.ops.render.render(write_still=True)
        print(f"fotograma {i} {time.time() - t0:.1f}s", flush=True)
    if a.prueba or a.cada > 1 or not a.salida:
        return
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(tmp, "f", "%04d.png"),
                    "-vf", f"scale={VW}:{VH}:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-crf", "20",
                    "-preset", "slow", "-movflags", "+faststart", a.salida], check=True)

if __name__ == "__main__":
    main()
