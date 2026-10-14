# Web

## Objetivo

Renovar la presencia online de Bodonia: una página web que presente la imprenta, sus servicios (diseño, maquetación e impresión) y sus 35 años de oficio, y una landing para captar encargos.

Contexto completo y pendientes: [`docs/resumenes/2026-10-14-web-rediseno-y-publicacion.md`](../docs/resumenes/2026-10-14-web-rediseno-y-publicacion.md).

## Contenido

| Carpeta | Qué hay | Origen |
| --- | --- | --- |
| [`sitio/`](sitio/) | **Web en edición** basada en la idea de daigual: una página con dos filas de trabajos (catálogos y otros trabajos) y ventanas de El taller, Qué hacemos y Hablemos. Textos en `contenido.js`, fotos en `fotos/`, información legal en `legal.html`. Cómo editarla: [`EDITAR.md`](EDITAR.md) | Montada a partir de `../futuros-proyectos/daigual/` |
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
| Web (basada en daigual) | Página editable: textos en `contenido.js`, fotos en `fotos/`, formulario con Netlify Forms, información legal | [`sitio/`](sitio/) · [`EDITAR.md`](EDITAR.md) | En edición; no publicar todavía |
| Plan de publicación | Netlify + bodonia.es | [`PLAN-PUBLICACION.md`](rediseno/web-canvas/project/PLAN-PUBLICACION.md) | Fases 1 y 2 hechas (falta confirmar versión); siguiente: Fase 3 |
| Mockups de trabajos | Imágenes para la galería | [`mockups-finalizados/`](mockups-finalizados/) | Hecho |
| Portada de Facebook | 3280×1440 | [`rediseno/fb/`](rediseno/fb/) | Hecho |

## Estado (14/10/2026)

- daigual es la idea de partida, no la versión final: la web se seguirá editando antes de publicar.
- `sitio/` es la versión editable. Guía en [`EDITAR.md`](EDITAR.md).
- Ya resuelto para cuando se publique: tipografías alojadas en la web (sin Google Fonts), formulario con Netlify Forms, información legal con bodonia.es y sin cookies, favicon, imagen para compartir, `robots.txt`, `sitemap.xml` y `netlify.toml`.
- La exportación de la versión Inicio sigue disponible con `rediseno/scripts/exportar_inicio.py` (sale en `sitio-inicio/`).
