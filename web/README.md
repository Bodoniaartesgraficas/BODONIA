# Web

## Objetivo

Renovar la presencia online de Bodonia: una página web que presente la imprenta, sus servicios (diseño, maquetación e impresión) y sus 35 años de oficio, y una landing para captar encargos.

Contexto completo y pendientes: [`docs/resumenes/2026-10-14-web-rediseno-y-publicacion.md`](../docs/resumenes/2026-10-14-web-rediseno-y-publicacion.md).

## Contenido

| Carpeta | Qué hay | Origen |
| --- | --- | --- |
| [`sitio/`](sitio/) | **Web lista para Netlify: versión daigual** (galería horizontal de proyectos). `index.html`, `styles.css`, `script.js`, fotos, fuentes Bodoni Moda y DM Sans, formulario, información legal, `gracias.html`, `404.html` y `netlify.toml`. Se arrastra esta carpeta a Netlify | Exportada de `../futuros-proyectos/daigual/` con [`scripts/exportar_daigual.py`](scripts/exportar_daigual.py) |
| [`rediseno/web-canvas/project/`](rediseno/web-canvas/project/) | Tableros del rediseño: Inicio, Variante loca, Copia y Retro, cada uno en escritorio y móvil, más pruebas del logo | `bodonia-artifacts.zip` |
| [`rediseno/web-canvas/project/PLAN-PUBLICACION.md`](rediseno/web-canvas/project/PLAN-PUBLICACION.md) | Plan de publicación en 6 fases (Netlify + dominio bodonia.es de OVH) | `bodonia-artifacts.zip` |
| [`rediseno/assets/`](rediseno/assets/) | Logos sin fondo, fotos de trabajos, calendario, sobre y fuente Bodoni Moda | `bodonia-artifacts.zip` |
| [`rediseno/fb/`](rediseno/fb/) | Portada de Facebook y pruebas | `bodonia-artifacts.zip` |
| [`rediseno/scripts/`](rediseno/scripts/) | Generadores de Copia y Retro y reglas móviles | `bodonia-artifacts.zip` |
| [`mockups-finalizados/`](mockups-finalizados/) | Mockups finales de los trabajos (libros, catálogos, carteles, dípticos, revistas, calendarios) y el vídeo de En Noir | `z WEB.zip` |

Los `.dc.html` son tableros del editor de diseño: para publicar hay que exportarlos a HTML normal (Fase 2 del plan).

No subido por tamaño: `mockup finalizados/territorios_v2_ligero.mp4` (9,8 MB), sigue dentro de `z WEB.zip`.

## Entregables

| Entregable | Descripción | Archivo / enlace | Estado |
| --- | --- | --- | --- |
| Rediseño web | Cuatro versiones (Inicio, Variante loca, Copia, Retro) en escritorio y móvil | [`rediseno/web-canvas/project/`](rediseno/web-canvas/project/) · [artifact](https://claude.ai/artifact/5gNNFqz4XXHA9tKQtcwrim) | Descartado para publicar: se elige daigual (14/10/2026) |
| Web para publicar (daigual) | HTML estático, formulario con Netlify Forms, información legal con bodonia.es y sin cookies | [`sitio/`](sitio/) | Lista, pendiente de confirmar y subir a Netlify |
| Plan de publicación | Netlify + bodonia.es | [`PLAN-PUBLICACION.md`](rediseno/web-canvas/project/PLAN-PUBLICACION.md) | Fases 1 y 2 hechas (falta confirmar versión); siguiente: Fase 3 |
| Mockups de trabajos | Imágenes para la galería | [`mockups-finalizados/`](mockups-finalizados/) | Hecho |
| Portada de Facebook | 3280×1440 | [`rediseno/fb/`](rediseno/fb/) | Hecho |

## Notas de la exportación (versión daigual)

- Versión elegida para publicar: **daigual** (14/10/2026). Diseño sin cambios respecto al prototipo.
- Tipografías Bodoni Moda y DM Sans alojadas en la propia web (`sitio/fonts/`, licencia OFL), sin Google Fonts.
- Los cinco mockups PNG (2-3 MB cada uno) pasan a JPEG de alta calidad (≈ 0,2-0,4 MB) con el mismo aspecto.
- Formulario «Hablemos»: se envía con Netlify Forms (antes abría el programa de correo) y el botón pasa de «Preparar correo» a «Enviar». En Netlify hay que activar la detección de formularios y el aviso por correo a info@bodonia.es.
- Información legal: el prototipo no tenía. Se añade una ventana con Aviso legal, Condiciones de uso, Política de cookies y Política de privacidad (los textos de la web actual, con bodonia.es, sin cookies y con el formulario y Netlify). Se abre desde la ventana de contacto y desde la nota del formulario.
- Añadidos: título y datos para Google y redes, favicon, imagen para compartir, `robots.txt` y `sitemap.xml`.
- La exportación de la versión Inicio sigue disponible con `rediseno/scripts/exportar_inicio.py` (sale en `sitio-inicio/`).
