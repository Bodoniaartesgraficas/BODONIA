# Web

## Objetivo

Renovar la presencia online de Bodonia: una página web que presente la imprenta, sus servicios (diseño, maquetación e impresión) y sus 35 años de oficio, y una landing para captar encargos.

Contexto completo y pendientes: [`docs/resumenes/2026-10-14-web-rediseno-y-publicacion.md`](../docs/resumenes/2026-10-14-web-rediseno-y-publicacion.md).

## Contenido

| Carpeta | Qué hay | Origen |
| --- | --- | --- |
| [`sitio/`](sitio/) | **Web lista para Netlify** (versión Inicio, escritorio y móvil): `index.html`, fotos, vídeos, fuente Bodoni Moda, formulario, `gracias.html`, `404.html` y `netlify.toml`. Se arrastra esta carpeta a Netlify | Exportada de `Main.dc.html` con `rediseno/scripts/exportar_inicio.py` |
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
| Rediseño web | Cuatro versiones (Inicio, Variante loca, Copia, Retro) en escritorio y móvil | [`rediseno/web-canvas/project/`](rediseno/web-canvas/project/) · [artifact](https://claude.ai/artifact/5gNNFqz4XXHA9tKQtcwrim) | Inicio preparada; falta confirmarla |
| Web para publicar (Inicio) | HTML estático, formulario con Netlify Forms, textos legales con bodonia.es y sin cookies | [`sitio/`](sitio/) | Lista, pendiente de confirmar y subir a Netlify |
| Plan de publicación | Netlify + bodonia.es | [`PLAN-PUBLICACION.md`](rediseno/web-canvas/project/PLAN-PUBLICACION.md) | Fases 1 y 2 hechas (falta confirmar versión); siguiente: Fase 3 |
| Mockups de trabajos | Imágenes para la galería | [`mockups-finalizados/`](mockups-finalizados/) | Hecho |
| Portada de Facebook | 3280×1440 | [`rediseno/fb/`](rediseno/fb/) | Hecho |

## Notas de la exportación (versión Inicio)

- Diseño sin cambios. Solo se quitaron las alturas y anchos fijos del lienzo del editor (cortaban o dejaban huecos fuera de 1360 px) y el título se escala entre 700 y 1100 px para que no se salga de la pantalla.
- Formulario «Pide información»: se envía con Netlify Forms (adjuntos incluidos) y el botón pasa de «Enviar correo» a «Enviar». En Netlify hay que activar la detección de formularios y añadir el aviso por correo a info@bodonia.es.
- Textos legales: bodonia.es en lugar de la dirección de WordPress; la política de cookies dice que la web no usa cookies; la privacidad incluye el formulario y a Netlify como encargado del tratamiento.
- Fuente Bodoni Moda alojada en la propia web (`sitio/fonts/`, licencia OFL), sin Google Fonts.
- Añadidos: título y descripción para Google, favicon, imagen para compartir (recorte de la portada de Facebook), ficha de empresa local, `robots.txt` y `sitemap.xml`.
