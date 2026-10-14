# Cómo editar la web

La web está en [`sitio/`](sitio/). Es una sola página basada en la idea de daigual: galería horizontal de trabajos y tres ventanas (El taller, Qué hacemos, Hablemos).

## Qué se cambia y dónde

| Quiero cambiar… | Archivo | Qué tocar |
| --- | --- | --- |
| Cualquier texto de la página (titular, presentación, El taller, Qué hacemos, contacto, botones, formulario) | [`sitio/contenido.js`](sitio/contenido.js) | El texto entre comillas de cada apartado |
| Los trabajos de las dos filas (catálogos; otros trabajos): añadir, quitar, reordenar, renombrar | [`sitio/contenido.js`](sitio/contenido.js), apartado `filas` (incluye `velocidad` de deslizamiento de cada fila) | Cada fila tiene `titulo` y sus `proyectos`; un bloque `{ ... }` por trabajo, en el orden en que salen |
| Las fotos | [`sitio/fotos/proyectos/`](sitio/fotos/proyectos/) | Sube la foto y escribe su nombre en `contenido.js` |
| El logo | [`sitio/fotos/logo-bodonia.png`](sitio/fotos/logo-bodonia.png) | Sustituye el archivo con el mismo nombre |
| Aviso legal, condiciones, cookies y privacidad | [`sitio/legal.html`](sitio/legal.html) | El texto de cada párrafo `<p>` |
| Colores, tipografías y tamaños (diseño) | [`sitio/styles.css`](sitio/styles.css) | Al principio: `--red` es el rojo, `--ink` el texto, `--muted` el gris |
| Página de «gracias» tras enviar el formulario | [`sitio/gracias.html`](sitio/gracias.html) | El titular y el párrafo |

`index.html` (estructura) y `script.js` (funcionamiento) no hace falta tocarlos para cambiar contenidos.

## Fotos de cada trabajo

Cada trabajo usa hasta tres fotos, con nombres `NN-nombre-portada.jpg`, `-detalle.jpg` y `-completa.jpg`:

- **portada**: la que se ve en la galería, vertical (proporción 4:5, por ejemplo 1000 × 1250 px).
- **detalle** (opcional): la que aparece al pasar el ratón por encima.
- **completa** (opcional): la que se abre al pulsar el trabajo.

Con una sola foto basta: si faltan detalle o completa, la web usa la portada. Si la portada no es 4:5, `encuadre` decide qué parte se ve.

## Ver los cambios antes de publicar

Vista previa en Claude: https://claude.ai/artifact/KwJk3khBZxwvkKWtCEdYAs (se actualiza con `python3 web/scripts/vista_previa.py <carpeta>` y se vuelve a publicar en el mismo enlace). En la vista previa el formulario no envía mensajes.


Abre la carpeta `sitio` con cualquier servidor local o súbela a Netlify como borrador. Abrir `index.html` con doble clic también funciona, pero el formulario solo envía una vez publicado en Netlify.

## Origen

- Idea y diseño: prototipo [`../futuros-proyectos/daigual/`](../futuros-proyectos/daigual/).
- Las portadas y detalles de los trabajos que no son fotos de libro se recortaron tal como se veían en el prototipo.
- Textos legales: los de la web actual, con bodonia.es en lugar de WordPress, sin cookies y con el formulario y Netlify.
