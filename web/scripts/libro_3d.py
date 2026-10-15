"""Vídeo 3:4 (1080x1440) de un libro real en 3D: se abre por la mitad y pasa dos páginas.

Se modela el libro con sus medidas reales (tapas de cartulina, bloque de hojas con su grosor, páginas que se
curvan hacia el lomo) y se renderiza con Blender/Cycles (trazado de rayos): luz de estudio suave, sombras de
contacto, papel con textura y cámara que gira alrededor del libro con el encuadre siempre ajustado.

Requiere: python3 -m pip install bpy   (Blender como módulo de Python)
Uso:
  python3 web/scripts/libro_3d.py --pdf interior.pdf --dobles 53 57 63 --portada portada.png \
      --paginas 96 --mm 165 235 --salida ../sitio/fotos/proyectos/03-santa-fe-mauthausen-video.mp4
  --dobles: página izquierda de cada doble (se usa esa y la siguiente).
  --imagenes a.png b.png c.png: en vez de --pdf y --dobles, tres dobles en imagen plana.
  --prueba 0,40,90: solo renderiza esos fotogramas (PNG en --carpeta), para revisar.
"""
import argparse, math, os, shutil, subprocess, sys, tempfile, time
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dobles_pdf import sangre  # noqa: E402

import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

VW, VH, FPS = 1080, 1440, 24
TOTAL = 11.6
ABRE = (1.2, 3.5)                    # se abre por la mitad
PASES = [(4.9, 6.7), (8.3, 10.1)]    # dos pasos de página
NU, NV, NS, NY = 64, 7, 72, 14       # resolución de las mallas
ESCALA = 75                          # % de 1080x1440 al que se renderiza; el vídeo final se escala a 1080x1440

def suave(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)

def tramo(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))

# ---------------------------------------------------------------- texturas

def pagina_pdf(pdf, n, carpeta, dpi=200):
    base = os.path.join(carpeta, f"p{n}")
    subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(n), "-l", str(n), "-png", "-singlefile", pdf, base],
                   check=True, stderr=subprocess.DEVNULL)
    im = Image.open(base + ".png").convert("RGB")
    s = round(sangre(pdf) * dpi / 72)
    im.crop((s, s, im.width - s, im.height - s)).save(base + ".png")
    return base + ".png"

def aplana_lomo(im):
    """Quita la sombra del lomo que traen algunos dobles planos. Se mide en el margen de arriba, que es papel liso;
    si el margen no es liso (una foto a sangre, un titulillo), se deja el doble tal cual."""
    a = np.asarray(im).astype(float)
    H, W = a.shape[:2]
    banda = a[int(H * .01):int(H * .045)].mean(2)
    perfil = np.median(banda, axis=0)
    fuera = np.r_[perfil[int(W * .05):int(W * .35)], perfil[int(W * .65):int(W * .95)]]
    if fuera.std() > 3 or banda.std(axis=0)[int(W * .05):int(W * .95)].mean() > 4:
        return im
    r = np.clip(np.convolve(perfil, np.ones(9) / 9, mode="same") / np.median(fuera), .4, 1)
    r[:5] = r[-5:] = 1
    if r.min() > .97:
        return im
    return Image.fromarray(np.clip(a / r[None, :, None], 0, 255).astype(np.uint8))

def dobles_imagen(ruta, carpeta, i):
    """Doble de páginas desde una imagen plana: se recorta lo transparente, se parte por el centro (o por el hueco
    entre las dos páginas, si lo hay) y se quita la sombra del lomo si viene pintada."""
    im = Image.open(ruta).convert("RGBA")
    al = np.asarray(im)[..., 3] > 200
    ys, xs = np.where(al)
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    al = np.asarray(im)[..., 3] > 200
    W = im.width
    centro = al[int(im.height * .2):int(im.height * .8), int(W * .45):int(W * .55)].mean(axis=0) < .5
    if centro.any():
        hueco = np.where(centro)[0] + int(W * .45)
        a0, b0 = hueco.min(), hueco.max() + 1
    else:
        a0 = b0 = W // 2
    fondo = Image.new("RGB", im.size, (255, 255, 255)); fondo.paste(im, (0, 0), im)
    fondo = aplana_lomo(fondo)
    out = []
    for k, caja_ in enumerate([(0, 0, a0, im.height), (b0, 0, W, im.height)]):
        f = os.path.join(carpeta, f"d{i}{'ab'[k]}.png"); fondo.crop(caja_).save(f); out.append(f)
    return tuple(out)

def portada_frontal(ruta, carpeta):
    """Cara frontal de la cubierta. Si es la cubierta desplegada (apaisada), se queda con la mitad derecha."""
    im = Image.open(ruta).convert("RGB")
    if im.width > im.height:
        a = np.asarray(im).astype(int); c = a[a.shape[0] // 2, 5]
        m = (abs(a - c).sum(axis=2) < 40)
        cols = np.where(m.mean(axis=0) > .5)[0]; rows = np.where(m.mean(axis=1) > .5)[0]
        im = im.crop((cols.min(), rows.min(), cols.max() + 1, rows.max() + 1))
        im = im.crop((im.width // 2, 0, im.width, im.height))
    out = os.path.join(carpeta, "portada.png"); im.save(out)
    lomo = np.asarray(im)[:, : max(2, im.width // 60)].reshape(-1, 3)
    return out, tuple(np.median(lomo, axis=0) / 255)

# ---------------------------------------------------------------- geometría del libro

class Libro:
    def __init__(s, W, H, paginas, hoja=.000105, cubierta=.00045):
        s.W, s.H = W, H
        s.c = cubierta                       # rústica: cartulina plastificada; tapa dura: el cartón
        s.h = paginas / 4 * hoja             # media tripa (hoja: grosor de cada hoja, en metros)
        s.a = s.c + s.h
        s.tapa = None                        # TapaDura, si el libro es de tapa dura
        s.g0 = .2                            # fondo del lomo, en fracción de la media tripa
        s.lam = .3 * s.h + .0045             # cuánto tarda la página en subir desde el lomo
        s.lomo_sube = .12 * s.h + .0009      # abombado de la página abierta
        s.us = np.linspace(0, 1, NU) ** 1.6  # más puntos cerca del lomo
        s.vs = np.linspace(0, 1, NV)
        s.ys = np.linspace(0, H, 2)
        ss = np.linspace(0, 1, NS + 1)
        X, Z = s.perfil(1.0, ss)
        s.hoja_s = ss * W
        s.hoja_phi = np.arctan2(np.diff(Z), np.diff(X))   # ángulo de reposo de cada tramo de la hoja
        s.bisagra = (0.0, s.z_abierto(np.array([0.0]))[0])

    def z_abierto(s, x):
        x = np.asarray(x, float)
        sube = 1 - np.exp(-(x / s.lam) ** .85)
        return s.c + s.h * (s.g0 + (1 - s.g0) * sube) + s.lomo_sube * np.sin(np.pi * np.clip(x / s.W, 0, 1)) ** 1.3 * sube

    def perfil(s, k, us):
        """Cara de arriba de media tripa (lado derecho) con apertura k, parametrizada por longitud de arco."""
        xs = np.linspace(0, s.W * 1.05, 3000)
        z = s.a + k * (s.z_abierto(xs) - s.a)
        arco = np.concatenate([[0], np.cumsum(np.hypot(np.diff(xs), np.diff(z)))])
        return np.interp(us * s.W, arco, xs), np.interp(us * s.W, arco, z)

    def bloque(s, k):
        """Rejillas (n1, n2, 3) de la media tripa derecha; la normal sale por d1 x d2."""
        Xt, Zt = s.perfil(k, s.us)
        Xb, Zb = s.us * s.W, np.full(NU, s.c)
        P = np.empty((NU, NV, 2))
        P[..., 0] = Xb[:, None] * (1 - s.vs) + Xt[:, None] * s.vs
        P[..., 1] = Zb[:, None] * (1 - s.vs) + Zt[:, None] * s.vs
        y0, y1 = 0.0, s.H
        def g(x, y, z): return np.stack(np.broadcast_arrays(x, y, z), -1)
        r = {}
        r["arriba"] = g(Xt[:, None], s.ys[None, :], Zt[:, None])                       # u, y
        r["abajo"] = g(Xb[None, :], s.ys[:, None], Zb[None, :])                        # y, u
        r["pie"] = g(P[..., 0], y0, P[..., 1])                                          # u, v
        r["cabeza"] = g(P[..., 0].T, y1, P[..., 1].T)                                   # v, u
        r["corte"] = g(P[-1, :, 0][None, :], s.ys[:, None], P[-1, :, 1][None, :])      # y, v
        r["lomo"] = g(P[0, :, 0][:, None], s.ys[None, :], P[0, :, 1][:, None])         # v, y
        return r

    def uvs(s):
        U, V, Y = s.us, s.vs, s.ys / s.H
        def g(a, b): return np.stack(np.broadcast_arrays(a, b), -1)
        return {"arriba": g(U[:, None], Y[None, :]), "abajo": g(U[None, :], Y[:, None]),
                "pie": g(U[:, None], V[None, :]), "cabeza": g(U[None, :], V[:, None]),
                "corte": g(Y[:, None], V[None, :]), "lomo": g(V[:, None], Y[None, :])}

    def hoja(s, u, pliegue=1.0):
        """Hoja que pasa de derecha (u=0) a izquierda (u=1): gira desde el lomo, primero se levanta la esquina
        de abajo y la punta va por delante; al caer, la punta va por detrás."""
        ys = np.linspace(0, s.H, NY)
        d = .16
        phi = s.hoja_phi; sm = (s.hoja_s[:-1] + s.hoja_s[1:]) / 2 / s.W
        pts = np.empty((NS + 1, NY, 3))
        for j, y in enumerate(ys):
            ue = min(1.0, max(0.0, (u - d * (y / s.H)) / (1 - d)))
            A = suave(ue)
            curva = (.75 * math.sin(2 * math.pi * ue) - .3 * math.sin(math.pi * ue)) * pliegue
            th = (1 - A) * phi + A * (np.pi - phi) + curva * sm ** 1.5
            th = np.minimum(np.maximum(th, phi), np.pi - phi)
            dx = np.diff(s.hoja_s) * np.cos(th); dz = np.diff(s.hoja_s) * np.sin(th)
            x = s.bisagra[0] + np.concatenate([[0], np.cumsum(dx)])
            z = s.bisagra[1] + np.concatenate([[0], np.cumsum(dz)]) + .00012
            pts[:, j] = np.stack([x, np.full_like(x, y), z], -1)
        return pts

class TapaDura:
    """Tapa dura (cartoné): dos cartones que sobresalen del bloque (la ceja) y el lomo de la cubierta, que los une por
    los cajos y va por fuera del lomo del bloque. La cubierta impresa [trasera | lomo | portada] lo forra todo y se
    dobla hacia dentro por los cantos de los cartones."""
    def __init__(s, L, ruta, lomo, ceja=.003, cajo=.004):
        s.L, s.ruta, s.ceja, s.cajo = L, ruta, ceja, cajo
        im = Image.open(ruta).convert("RGB")
        s.alto = L.H + 2 * ceja
        s.total = s.alto * im.width / im.height       # ancho de la cubierta desplegada
        s.panel = (s.total - lomo) / 2
        s.pliegue = L.W + ceja - s.panel               # x del lomo de la cubierta con el libro cerrado (por fuera del bloque)
        s.kappa = (cajo - s.pliegue) / (.75 * 2 * L.a)  # con el libro cerrado, la curva del lomo llega justo a x = pliegue
        a = np.asarray(im).astype(float) / 255
        n = max(2, a.shape[0] // 80)
        borde = np.concatenate([a[:n].reshape(-1, 3), a[-n:].reshape(-1, 3)])
        s.color = tuple(np.median(borde, axis=0) ** 2.2)   # el papel que se dobla por los cantos (en lineal)

    def u_trasera(s, x): return (s.L.W + s.ceja - x) / s.total
    def u_portada(s, x): return 1 - (s.L.W + s.ceja + x) / s.total   # x de la portada abierta (negativa)
    def v(s, y): return (y + s.ceja) / s.alto

    def perfil(s, eje, beta, n=72):
        """Perfil exterior del lomo, del cajo de la trasera al de la portada: Bézier tangente a los dos cartones,
        remuestreada por longitud de arco para que la cubierta no resbale de un fotograma a otro."""
        A = np.array([s.cajo, 0.0]); dA = np.array([-1.0, 0.0])
        B = gira(np.array([[-s.cajo, 0.0, 0.0]]), eje, beta)[0][[0, 2]]
        dB = np.array([-math.cos(beta), -math.sin(beta)])
        m = s.kappa * np.linalg.norm(B - A)
        P = [A, A + m * dA, B - m * dB, B]
        t = np.linspace(0, 1, 400)[:, None]
        c = (1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3]
        arco = np.r_[0, np.cumsum(np.hypot(*np.diff(c, axis=0).T))]
        q = np.linspace(0, arco[-1], n)
        p = np.stack([np.interp(q, arco, c[:, 0]), np.interp(q, arco, c[:, 1])], -1)
        # el cajo: un surco junto a cada cartón, donde la cubierta se mete entre el cartón y el lomo
        d = np.gradient(p, axis=0); d /= np.linalg.norm(d, axis=1)[:, None]
        hacia_dentro = np.stack([d[:, 1], -d[:, 0]], -1)
        surco = sum(np.exp(-((q - s0) / .0011) ** 2) for s0 in (.0028, arco[-1] - .0028))
        return p + hacia_dentro * (.0007 * surco)[:, None]

    def rejilla(s, eje, beta):
        p = s.perfil(eje, beta)
        ys = np.array([-s.ceja, s.L.H + s.ceja])
        return np.stack(np.broadcast_arrays(p[:, None, 0], ys[None, :], p[:, None, 1]), -1)

    def uv(s, n=72):
        u = np.linspace(s.u_trasera(s.cajo), s.u_portada(-s.cajo), n)
        return np.stack(np.broadcast_arrays(u[:, None], np.array([0.0, 1.0])[None, :]), -1)

def espejo(g):
    """Simetría x -> -x; se transpone la rejilla para que las normales sigan saliendo hacia fuera."""
    g = g.copy(); g[..., 0] *= -1
    return np.swapaxes(g, 0, 1)

def gira(g, eje_z, beta):
    """Giro en el plano xz, antihorario visto desde delante, alrededor del eje (x=0, z=eje_z)."""
    x, z = g[..., 0], g[..., 2] - eje_z
    cb, sb = math.cos(beta), math.sin(beta)
    out = g.copy(); out[..., 0] = x * cb - z * sb; out[..., 2] = x * sb + z * cb + eje_z
    return out

def matriz_giro(eje_z, beta):
    # el giro antihorario visto desde delante es un giro de -beta alrededor de +Y
    R = Matrix.Rotation(-beta, 4, "Y")
    return Matrix.Translation((0, 0, eje_z)) @ R @ Matrix.Translation((0, 0, -eje_z))

# ---------------------------------------------------------------- Blender: materiales

def nodo(nt, tipo, **kw):
    n = nt.nodes.new(tipo)
    for k, v in kw.items(): setattr(n, k, v)
    return n

def entrada(n, nombre, tipo=None):
    for i in n.inputs:
        if i.name == nombre and (tipo is None or i.type == tipo) and i.enabled: return i
    for i in n.inputs:
        if i.name == nombre and (tipo is None or i.type == tipo): return i
    raise KeyError(nombre)

def salida(n, nombre, tipo=None):
    for o in n.outputs:
        if o.name == nombre and (tipo is None or o.type == tipo): return o
    raise KeyError(nombre)

def material(nombre):
    m = bpy.data.materials.new(nombre)
    try: m.use_nodes = True
    except Exception: pass
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    return m, nt, bsdf

def imagen(ruta):
    im = bpy.data.images.load(ruta, check_existing=True)
    im.colorspace_settings.name = "sRGB"
    return im

def mat_imagen(nombre, ruta, rug=.5, espec=.4, espejo_u=False):
    m, nt, bsdf = material(nombre)
    tc = nodo(nt, "ShaderNodeTexCoord")
    tx = nodo(nt, "ShaderNodeTexImage"); tx.image = imagen(ruta); tx.interpolation = "Linear"; tx.extension = "EXTEND"
    uv = salida(tc, "UV")
    if espejo_u:
        mp = nodo(nt, "ShaderNodeMapping")
        entrada(mp, "Scale").default_value = (-1, 1, 1); entrada(mp, "Location").default_value = (1, 0, 0)
        nt.links.new(uv, entrada(mp, "Vector")); uv = salida(mp, "Vector")
    nt.links.new(uv, entrada(tx, "Vector"))
    nt.links.new(salida(tx, "Color"), entrada(bsdf, "Base Color"))
    entrada(bsdf, "Roughness").default_value = rug
    entrada(bsdf, "Specular IOR Level").default_value = espec
    return m, tx

def mat_hoja(nombre, frente, dorso):
    """Hoja de dos caras: frente en la cara de arriba (cuando está a la derecha) y dorso detrás."""
    m, nt, bsdf = material(nombre)
    tc = nodo(nt, "ShaderNodeTexCoord"); geo = nodo(nt, "ShaderNodeNewGeometry")
    tf = nodo(nt, "ShaderNodeTexImage"); tf.image = imagen(frente); tf.interpolation = "Linear"; tf.extension = "EXTEND"
    tb = nodo(nt, "ShaderNodeTexImage"); tb.image = imagen(dorso); tb.interpolation = "Linear"; tb.extension = "EXTEND"
    mp = nodo(nt, "ShaderNodeMapping")
    entrada(mp, "Scale").default_value = (-1, 1, 1); entrada(mp, "Location").default_value = (1, 0, 0)
    nt.links.new(salida(tc, "UV"), entrada(tf, "Vector"))
    nt.links.new(salida(tc, "UV"), entrada(mp, "Vector")); nt.links.new(salida(mp, "Vector"), entrada(tb, "Vector"))
    mx = nodo(nt, "ShaderNodeMix"); mx.data_type = "RGBA"
    nt.links.new(salida(geo, "Backfacing"), entrada(mx, "Factor", "VALUE"))
    nt.links.new(salida(tf, "Color"), entrada(mx, "A", "RGBA")); nt.links.new(salida(tb, "Color"), entrada(mx, "B", "RGBA"))
    col = salida(mx, "Result", "RGBA")
    nt.links.new(col, entrada(bsdf, "Base Color"))
    entrada(bsdf, "Roughness").default_value = .5
    entrada(bsdf, "Specular IOR Level").default_value = .4
    # algo de luz a través del papel
    tr = nodo(nt, "ShaderNodeBsdfTranslucent"); nt.links.new(col, entrada(tr, "Color"))
    ms = nodo(nt, "ShaderNodeMixShader"); entrada(ms, "Factor").default_value = .07
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(salida(bsdf, "BSDF"), ms.inputs[1]); nt.links.new(salida(tr, "BSDF"), ms.inputs[2])
    nt.links.new(salida(ms, "Shader"), entrada(out, "Surface"))
    return m, tf, tb

def mat_canto(n_hojas):
    """Canto del bloque: muchas hojas finas (bandas a lo largo del grosor) con algo de irregularidad."""
    m, nt, bsdf = material("canto")
    tc = nodo(nt, "ShaderNodeTexCoord")
    wv = nodo(nt, "ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "Y"
    entrada(wv, "Scale").default_value = n_hojas; entrada(wv, "Distortion").default_value = 1.2
    entrada(wv, "Detail").default_value = 2
    nt.links.new(salida(tc, "UV"), entrada(wv, "Vector"))
    cr = nodo(nt, "ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (.66, .645, .615, 1); cr.color_ramp.elements[1].color = (.84, .83, .80, 1)
    nt.links.new(salida(wv, "Factor"), entrada(cr, "Factor"))
    nt.links.new(salida(cr, "Color"), entrada(bsdf, "Base Color"))
    entrada(bsdf, "Roughness").default_value = .82
    entrada(bsdf, "Specular IOR Level").default_value = .2
    return m

def mat_liso(nombre, color, rug=.6, espec=.4):
    m, nt, bsdf = material(nombre)
    entrada(bsdf, "Base Color").default_value = (*color, 1)
    entrada(bsdf, "Roughness").default_value = rug
    entrada(bsdf, "Specular IOR Level").default_value = espec
    return m

def mat_suelo():
    m, nt, bsdf = material("suelo")
    tc = nodo(nt, "ShaderNodeTexCoord")
    nz = nodo(nt, "ShaderNodeTexNoise"); entrada(nz, "Scale").default_value = 6; entrada(nz, "Detail").default_value = 1
    nt.links.new(salida(tc, "Object"), entrada(nz, "Vector"))
    cr = nodo(nt, "ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (.53, .525, .515, 1); cr.color_ramp.elements[1].color = (.57, .565, .555, 1)
    nt.links.new(salida(nz, "Factor"), entrada(cr, "Factor")); nt.links.new(salida(cr, "Color"), entrada(bsdf, "Base Color"))
    entrada(bsdf, "Roughness").default_value = .92
    entrada(bsdf, "Specular IOR Level").default_value = .25
    return m

# ---------------------------------------------------------------- Blender: mallas

class Rejilla:
    """Superficie de cuadriláteros (n1 x n2) cuya forma se actualiza en cada fotograma."""
    def __init__(s, nombre, uv, mat, suave_=True):
        n1, n2 = uv.shape[:2]
        caras = [(i * n2 + j, (i + 1) * n2 + j, (i + 1) * n2 + j + 1, i * n2 + j + 1)
                 for i in range(n1 - 1) for j in range(n2 - 1)]
        me = bpy.data.meshes.new(nombre)
        me.from_pydata([(0, 0, 0)] * (n1 * n2), [], caras)
        capa = me.uv_layers.new(name="UV")
        vi = np.empty(len(me.loops), np.int32); me.loops.foreach_get("vertex_index", vi)
        capa.data.foreach_set("uv", uv.reshape(-1, 2)[vi].ravel().astype(np.float32))
        me.materials.append(mat)
        me.polygons.foreach_set("use_smooth", [suave_] * len(me.polygons))
        s.ob = bpy.data.objects.new(nombre, me)
        bpy.context.scene.collection.objects.link(s.ob)
        s.me = me

    def pon(s, g):
        s.me.vertices.foreach_set("co", np.ascontiguousarray(g, np.float32).ravel())
        s.me.update()

def caja(nombre, x0, x1, y0, y1, z0, z1, mats, uv_fuera):
    """Caja con materiales [fuera (cara z0), dentro (cara z1), cantos]; uv_fuera(x, y) -> (u, v)."""
    v = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    # índices: z0: 0..3 (x0y0, x1y0, x0y1, x1y1); z1: 4..7
    caras = [((0, 2, 3, 1), 0), ((4, 5, 7, 6), 1), ((0, 1, 5, 4), 2), ((1, 3, 7, 5), 2), ((3, 2, 6, 7), 2), ((2, 0, 4, 6), 2)]
    me = bpy.data.meshes.new(nombre)
    me.from_pydata(v, [], [c for c, _ in caras])
    for m in mats: me.materials.append(m)
    for p, (_, mi) in zip(me.polygons, caras): p.material_index = mi
    capa = me.uv_layers.new(name="UV")
    for p in me.polygons:
        for li in p.loop_indices:
            x, y, _ = v[me.loops[li].vertex_index]
            capa.data[li].uv = uv_fuera(x, y)
    ob = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(ob)
    b = ob.modifiers.new("bisel", "BEVEL"); b.width = .00025; b.segments = 2; b.limit_method = "NONE"
    return ob

# ---------------------------------------------------------------- escena

def escena(L, tex, color_lomo, muestras):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = muestras
    sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = .05
    sc.cycles.use_light_tree = False
    sc.cycles.use_denoising = True
    try: sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception: pass
    sc.cycles.max_bounces = 4; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 1
    sc.cycles.transmission_bounces = 1; sc.cycles.transparent_max_bounces = 2
    sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
    sc.render.use_persistent_data = True
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = VW, VH, ESCALA
    sc.render.image_settings.file_format = "PNG"
    sc.view_settings.view_transform = "Standard"   # colores de imprenta tal cual
    sc.view_settings.look = "None"

    w = bpy.data.worlds.new("mundo"); sc.world = w
    try: w.use_nodes = True
    except Exception: pass
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    entrada(bg, "Color").default_value = (.78, .79, .82, 1); entrada(bg, "Strength").default_value = .07

    def luz(nombre, pos, tam, energia, color=(1, 1, 1)):
        d = bpy.data.lights.new(nombre, "AREA"); d.shape = "DISK"; d.size = tam; d.energy = energia; d.color = color
        o = bpy.data.objects.new(nombre, d); sc.collection.objects.link(o)
        o.location = pos
        o.rotation_euler = (Vector((0, L.H / 2, 0)) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    luz("principal", (-.75, -.35, 1.25), 1.0, 19, (1, .97, .93))
    luz("relleno", (1.0, -.9, .7), 1.4, 5.5, (.93, .96, 1))
    luz("contra", (.5, 1.3, .9), 1.0, 7)

    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, L.H / 2, -.0001))
    bpy.context.active_object.data.materials.append(mat_suelo())

    O = {}
    O["canto"] = mat_canto(max(20, min(90, int(L.h / .00011))))
    O["blanco"] = mat_liso("papel", (.86, .85, .82), .7)
    # tapa dura: el lomo del bloque va tapado por la cubierta y solo asoma por los extremos (papel)
    O["lomo"] = mat_liso("lomo", (.74, .72, .68) if L.tapa else color_lomo, .45, .5)
    O["carton"] = mat_liso("carton", (.80, .79, .76), .75, .3)
    if not L.tapa:
        O["tapa"], _ = mat_imagen("tapa", tex["portada"], rug=.4, espec=.5)
    O["der"], O["tex_der"] = mat_imagen("pag_der", tex["S"][0][1])
    O["izq"], O["tex_izq"] = mat_imagen("pag_izq", tex["S"][0][0])
    uv = L.uvs()
    # media tripa derecha
    B = {k: Rejilla("der_" + k, uv[k], O["der"] if k == "arriba" else (O["lomo"] if k == "lomo" else
                    (O["blanco"] if k == "abajo" else O["canto"])), k == "arriba") for k in uv}
    # media tripa izquierda (la que gira con la tapa): espejo de la derecha
    uvi = {k: np.swapaxes(v, 0, 1).copy() for k, v in uv.items()}
    uvi["arriba"][..., 0] = 1 - uvi["arriba"][..., 0]   # página izquierda: el lomo queda a la derecha de la imagen
    I = {k: Rejilla("izq_" + k, uvi[k], O["izq"] if k == "arriba" else (O["lomo"] if k == "lomo" else
                    (O["blanco"] if k == "abajo" else O["canto"])), k == "arriba") for k in uv}
    # tapas
    W, H, c = L.W, L.H, L.c
    lomo_tapa = None
    if L.tapa:
        T = L.tapa
        O["cub"], _ = mat_imagen("cubierta", T.ruta, rug=.55, espec=.35)
        O["canto_tapa"] = mat_liso("canto_tapa", T.color, .7, .3)
        x0, x1, y0, y1 = T.cajo, W + T.ceja, -T.ceja, H + T.ceja
        mats = [O["cub"], O["canto_tapa"], O["canto_tapa"]]
        trasera = caja("trasera", x0, x1, y0, y1, 0, c, mats, lambda x, y: (T.u_trasera(x), T.v(y)))
        delantera = caja("delantera", -x1, -x0, y0, y1, 0, c, mats, lambda x, y: (T.u_portada(x), T.v(y)))
        for ob in (trasera, delantera): ob.modifiers["bisel"].width = .0004
        # lomo de la cubierta, con el grosor del cartón del lomo
        lomo_tapa = Rejilla("lomo_tapa", T.uv(), O["cub"])
        lomo_tapa.me.materials.append(mat_liso("carton_gris", (.40, .38, .35), .9, .2)); lomo_tapa.me.materials.append(O["canto_tapa"])
        so = lomo_tapa.ob.modifiers.new("grosor", "SOLIDIFY"); so.thickness = .0009; so.offset = -1
        so.material_offset = 1; so.material_offset_rim = 2
    else:
        trasera = caja("trasera", 0, W, 0, H, 0, c, [O["lomo"], O["blanco"], O["carton"]], lambda x, y: (x / W, y / H))
        delantera = caja("delantera", -W, 0, 0, H, 0, c, [O["tapa"], O["blanco"], O["carton"]], lambda x, y: (-x / W, y / H))
    # hojas que pasan
    uvh = np.stack(np.broadcast_arrays(np.linspace(0, 1, NS + 1)[:, None], np.linspace(0, 1, NY)[None, :]), -1)
    hojas = []
    for i in range(2):
        m, tf, tb = mat_hoja(f"hoja{i}", tex["S"][i][1], tex["S"][i + 1][0])
        hojas.append(Rejilla(f"hoja{i}", uvh, m))
    cam_d = bpy.data.cameras.new("camara"); cam_d.sensor_width = 36; cam_d.sensor_fit = "AUTO"
    cam_d.dof.use_dof = True; cam_d.dof.aperture_fstop = 14
    cam = bpy.data.objects.new("camara", cam_d); sc.collection.objects.link(cam); sc.camera = cam
    return dict(B=B, I=I, trasera=trasera, delantera=delantera, lomo_tapa=lomo_tapa, hojas=hojas, cam=cam, O=O)

# ---------------------------------------------------------------- animación

def estado(L, t):
    phi = math.pi * suave(tramo(t, *ABRE))
    k = suave(phi / math.pi) ** .8
    u = [tramo(t, a, b) for a, b in PASES]
    u = [suave(x) * .5 + x * .5 for x in u]   # arranque y llegada suaves, sin pararse en medio
    return phi, k, u

def geometria(L, t):
    phi, k, u = estado(L, t)
    der = L.bloque(k)
    eje = L.a + k * (L.bisagra[1] - L.a)
    beta = phi - math.pi
    izq = {n: gira(espejo(g), eje, beta) for n, g in der.items()}
    hojas = [L.hoja(x) if 0 < x < 1 else None for x in u]
    lomo = L.tapa.rejilla(eje, beta) if L.tapa else None
    return dict(der=der, izq=izq, eje=eje, beta=beta, hojas=hojas, lomo=lomo, phi=phi, k=k, u=u)

def camara_base(L, t, phi):
    ab = suave(phi / math.pi)
    az = math.radians(36 - 56 * suave(t / TOTAL) + 2.0 * math.sin(t * .6))
    el = math.radians(36 + 22 * suave(tramo(t, .5, 4.5)) + 6 * suave(tramo(t, 6, TOTAL)))
    obj = np.array([L.W / 2 * (1 - ab), L.H * .5, L.a])
    D = 1.0
    pos = obj + D * np.array([math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)])
    return pos, obj

def base_camara(pos, obj):
    f = obj - pos; f /= np.linalg.norm(f)
    r = np.cross(f, [0, 0, 1]); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return f, r, u

def proyecta(P, pos, obj, lente, sx=0.0, sy=0.0):
    f, r, u = base_camara(pos, obj)
    d = P - pos
    xc, yc, zc = d @ r, d @ u, d @ f
    esc = lente / 36 * max(VW, VH)
    return VW / 2 + xc / zc * esc - sx * max(VW, VH), VH / 2 - yc / zc * esc + sy * max(VW, VH)

def puntos(G, L):
    pts = [g.reshape(-1, 3) for g in G["der"].values()] + [g.reshape(-1, 3) for g in G["izq"].values()]
    pts += [h.reshape(-1, 3) for h in G["hojas"] if h is not None]
    # tapas: esquinas
    W, H, c = L.W, L.H, L.c
    x0, x1, y0, y1 = (L.tapa.cajo, W + L.tapa.ceja, -L.tapa.ceja, H + L.tapa.ceja) if L.tapa else (0, W, 0, H)
    tr = np.array([[x, y, z] for x in (x0, x1) for y in (y0, y1) for z in (0, c)])
    de = np.array([[x, y, z] for x in (-x1, -x0) for y in (y0, y1) for z in (0, c)])
    de = gira(de[None], G["eje"], G["beta"])[0]
    if G["lomo"] is not None: pts.append(G["lomo"].reshape(-1, 3))
    return np.concatenate(pts + [tr, de])

def encuadres(L, n, lente0=50.0):
    """Zoom (lente) y descentrado de la cámara para que el libro llene el cuadro, suavizados en el tiempo."""
    M, CX, CY = [], [], []
    for i in range(n):
        t = i / FPS
        G = geometria(L, t)
        pos, obj = camara_base(L, t, G["phi"])
        x, y = proyecta(puntos(G, L), pos, obj, lente0)
        w, h = x.max() - x.min(), y.max() - y.min()
        M.append(min(.88 * VW / w, .74 * VH / h)); CX.append((x.max() + x.min()) / 2); CY.append((y.max() + y.min()) / 2)
    def gauss(v, sig=FPS * .45):
        v = np.array(v); r = int(3 * sig); k = np.exp(-np.arange(-r, r + 1) ** 2 / (2 * sig * sig)); k /= k.sum()
        return np.convolve(np.pad(v, r, mode="edge"), k, mode="valid")
    M, CX, CY = gauss(M), gauss(CX), gauss(CY)
    lente = lente0 * M
    sx = M * (CX - VW / 2) / max(VW, VH)
    sy = (VH * .5 - VH / 2 - M * (CY - VH / 2)) / max(VW, VH)
    return lente, sx, sy

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf"); ap.add_argument("--dobles", type=int, nargs=3, help="con --pdf: página izquierda de cada doble")
    ap.add_argument("--imagenes", nargs=3, help="en vez de --pdf: tres dobles de páginas en imagen plana")
    ap.add_argument("--hoja", type=float, help="grosor de cada hoja de papel, en mm (rústica: .105; tapa dura: sale del lomo)")
    ap.add_argument("--portada", help="rústica: la portada (o la cubierta desplegada)")
    ap.add_argument("--tapa-dura", nargs=2, metavar=("CUBIERTA", "LOMO_MM"),
                    help="tapa dura: cubierta desplegada [trasera | lomo | portada] sin pestañas, y ancho del lomo en mm")
    ap.add_argument("--paginas", type=int, required=True)
    ap.add_argument("--mm", type=float, nargs=2, required=True); ap.add_argument("--salida", required=True)
    ap.add_argument("--muestras", type=int, default=40); ap.add_argument("--prueba", default="")
    ap.add_argument("--carpeta", default="")
    ap.add_argument("--escala", type=int, default=ESCALA, help="% de 1080x1440 para renderizar")
    ap.add_argument("--cada", type=int, default=1, help="renderizar uno de cada N fotogramas (para previsualizar)")
    a = ap.parse_args()
    tmp = a.carpeta or tempfile.mkdtemp(prefix="libro3d_")
    os.makedirs(tmp, exist_ok=True)
    if a.imagenes:
        S = [dobles_imagen(r, tmp, i) for i, r in enumerate(a.imagenes)]
    else:
        S = [(pagina_pdf(a.pdf, n, tmp), pagina_pdf(a.pdf, n + 1, tmp)) for n in a.dobles]
    if a.tapa_dura:
        # cartón de 2,5 mm; el bloque llena el lomo de la cubierta
        lomo = float(a.tapa_dura[1]) / 1000; carton = .0025
        hoja = a.hoja / 1000 if a.hoja else (lomo / 2 - carton) / (a.paginas / 4)
        L = Libro(a.mm[0] / 1000, a.mm[1] / 1000, a.paginas, hoja, cubierta=carton)
        L.tapa = TapaDura(L, a.tapa_dura[0], lomo)
        portada, color_lomo = None, None
    else:
        portada, color_lomo = portada_frontal(a.portada, tmp)
        L = Libro(a.mm[0] / 1000, a.mm[1] / 1000, a.paginas, (a.hoja or .105) / 1000)
    E = escena(L, {"S": S, "portada": portada}, color_lomo, a.muestras)
    sc = bpy.context.scene
    n = int(TOTAL * FPS)
    lente, sx, sy = encuadres(L, n)
    sc.render.resolution_percentage = a.escala
    cuadros = [int(x) for x in a.prueba.split(",")] if a.prueba else range(0, n, a.cada)
    for i in cuadros:
        t0 = time.time(); t = i / FPS
        G = geometria(L, t)
        for k, g in G["der"].items(): E["B"][k].pon(g)
        for k, g in G["izq"].items(): E["I"][k].pon(g)
        E["delantera"].matrix_world = matriz_giro(G["eje"], G["beta"])
        if E["lomo_tapa"]: E["lomo_tapa"].pon(G["lomo"])
        # texturas de cada lado según las páginas que ya han pasado
        u1, u2 = G["u"]
        der = 0 if u1 <= 0 else (1 if u2 <= 0 else 2)
        izq = 0 if u1 < 1 else (1 if u2 < 1 else 2)
        E["O"]["tex_der"].image = imagen(S[der][1]); E["O"]["tex_izq"].image = imagen(S[izq][0])
        for h, g in zip(E["hojas"], G["hojas"]):
            h.ob.hide_render = g is None
            if g is not None: h.pon(g)
        pos, obj = camara_base(L, t, G["phi"])
        cam = E["cam"]
        cam.location = Vector(pos)
        cam.rotation_euler = Vector(obj - pos).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = float(lente[i]); cam.data.shift_x = float(sx[i]); cam.data.shift_y = float(sy[i])
        cam.data.dof.focus_distance = float(np.linalg.norm(obj - pos))
        sc.render.filepath = os.path.join(tmp, "f", f"{i:04d}.png")
        bpy.ops.render.render(write_still=True)
        print(f"fotograma {i} {time.time() - t0:.1f}s", flush=True)
    if a.prueba or a.cada > 1:
        return
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(tmp, "f", "%04d.png"),
                    "-vf", f"scale={VW}:{VH}:flags=lanczos,noise=alls=3:allf=t,format=yuv420p", "-c:v", "libx264", "-crf", "22", "-preset", "slow",
                    "-movflags", "+faststart", a.salida], check=True)
    if not a.carpeta:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    main()
