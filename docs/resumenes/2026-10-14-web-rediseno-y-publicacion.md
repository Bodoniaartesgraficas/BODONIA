# Bodonia Artes Gráficas — resumen del trabajo (rediseño web y publicación)

Fecha de este resumen: 14/10/2026

## Datos del negocio

- Nombre: BODONIA ARTES GRÁFICAS, S.L. (siempre el nombre completo, nunca "Bodonia" solo)
- Dirección: C/ Gredos nº 27, 18140 La Zubia (Granada)
- Teléfono: 648 82 32 50
- Correo: info@bodonia.es
- Horario: L-V 9:00–20:00
- Web actual: https://bodoniaartesgraficas.wordpress.com/ (WordPress)
- Dominio que se quiere usar: bodonia.es (registrado en OVH)

## Qué hay en esta carpeta

- `web-canvas/project/` — tableros del rediseño (Design canvas) tal como están publicados en
  https://claude.ai/artifact/5gNNFqz4XXHA9tKQtcwrim (versión 1791907493-1a62, leída en este momento):
  - `Main.dc.html` — Inicio (versión principal de escritorio)
  - `MainMovil.dc.html` — Inicio, versión móvil (390 px)
  - `Loca.dc.html` — Variante loca (escritorio)
  - `LocaMovil.dc.html` — Variante loca, móvil
  - `Copia.dc.html` / `CopiaMovil.dc.html` — Copia, paleta blanco, negro, rojo #9A0015 y gris
  - `Retro.dc.html` / `RetroMovil.dc.html` — Retro, fondo blanco, rojo y negro
  - `LogoVariantes.dc.html` y `LogoInteractivo.dc.html` — pruebas del título/logo
  - `canvas.json` — índice de los tableros (posición de cada uno en el lienzo)
  - `PLAN-PUBLICACION.md` — plan de publicación en 6 fases
- `web-canvas/index.html` — página contenedora del artifact (no hace falta para la web final)
- `assets/` — logos (PNG sin fondo, versión negra y versión con texto blanco), fotos de trabajos,
  calendario (v2 y v3), sobre, Mauthausen, y la fuente Bodoni Moda (BodoniModa.ttf)
- `fb/` — portada de Facebook (3280×1440) y otras pruebas
- `scripts/` — generadores usados para crear Copia y Retro a partir de Main, y las reglas móviles

Nota: los archivos `.dc.html` son tableros del editor de diseño. Para publicar la web real hay que
exportarlos a HTML normal (ver Fase 2 del plan).

## Otros artifacts de la cuenta (no incluidos en el zip)

- Bodonia Artes Gráficas — rediseño web: https://claude.ai/artifact/5gNNFqz4XXHA9tKQtcwrim (incluido)
- Bodonia en redes: https://claude.ai/artifact/Bw8pahrAHywDaH7wsmnb1N
- Plantilla mockup catálogo: https://claude.ai/artifact/RH5XhLqL89ifK2gBCTEkzW
- Mascota maceta guasona: https://claude.ai/artifact/FWSjsHC4p1T9EE2qXDr9qb

## Historia del trabajo

1. Revisión de la web de WordPress y primera propuesta de mejora estética, menos orientada a vender productos
   y más a mostrar trabajos.
2. Mockups de piezas: libros, calendario, sobre, tarjetas, haiku, carteles, díptico y revista.
   Las imágenes de los trabajos pasaron a la web: catálogos arriba y el resto debajo.
3. Formulario "Pide información" (en la versión de escritorio y en la móvil; ahora se envía con mailto a
   info@bodonia.es; pendiente de cambiar a Netlify Forms cuando se publique).
4. Logo: PNG sin fondo para que se vea bien sobre cualquier color. Fuente Bodoni para todo el texto.
5. Variante loca: misma estructura con tipografía y piezas más juguetonas.
6. Banner de Facebook (portada) con toda la información.
7. Cambios de imagen en Inicio y Variante loca: sobre nuevo, Mauthausen nuevo, calendario Bodonia
   (v3 sin dirección de WordPress) y teléfono 648 82 32 50.
8. Pies de foto centrados en Inicio, con el tipo en rojo y el título en negro.
9. Copia: nueva versión a partir de una referencia de Behance (grabada en vídeo, porque Behance bloquea el acceso),
   recoloreada a blanco, negro, rojo y gris.
10. Retro: nueva versión a partir del vídeo de referencia, con fondo blanco y colores rojo y negro.
11. Versiones móviles de Inicio, Variante loca, Copia y Retro.

## Decisiones y pendientes

- PENDIENTE: el cliente debe elegir la versión definitiva (Inicio, Variante loca, Copia o Retro).
- PENDIENTE: textos legales — quitar la referencia a WordPress, poner bodonia.es y aclarar que la web no usa cookies.
- PENDIENTE: revisar paleta de Copia y Retro con el cliente.
- PENDIENTE: publicación. Plan completo en `web-canvas/project/PLAN-PUBLICACION.md`:
  Netlify (gratis) con dominio bodonia.es de OVH, sin tocar los registros MX del correo;
  formulario con Netlify Forms; comprobar que info@bodonia.es sigue recibiendo correo.
- Nota técnica: los archivos locales pueden quedar desfasados si el cliente edita en el editor de diseño.
  Antes de exportar, releer siempre la versión publicada.

## Avisos útiles

- La fuente usada en la portada de Facebook es Latin Modern (no Bodoni Moda), por falta de acceso a la fuente
  en ese momento. Para la web sí está Bodoni Moda (incluida en assets/).
- Los permisos de compartir el artifact dependen del plan de Claude y de la versión de la app.
