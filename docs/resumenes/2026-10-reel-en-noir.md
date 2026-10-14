# Bodonia Artes Gráficas: resumen del proyecto

Resumen del chat de trabajo para continuar el proyecto en Claude Code.

## 1. Contexto

- **Cliente:** Bodonia Artes Gráficas S.L. (info@bodonia.es), taller de diseño, maquetación e impresión de libros de arte.
- **Idioma de trabajo:** español. Zona horaria Europa/Madrid.
- **Trabajo principal:** mockups y vídeos promocionales de catálogos de arte que Bodonia diseña e imprime.

## 2. Catálogo actual: "Pedro Zamora. En Noir"

- Exposición en Galerie Tourrette, París, marzo–abril de 2026.
- Textos: Gabriel Insausti. Fotografía: Pablo Asenjo.
- Crédito de impresión: "Conception et impression: Bodonia Artes Gráficas S.L."
- Portada: negro sobre mármol negro, marco en relieve y detalle dorado.

## 3. Evolución de la tarea: de mockups a reels

1. **Mockups de catálogos abiertos** (plantilla con libros abiertos y portada de pie), pensados para que el grosor de los libros abiertos sea coherente con el catálogo.
2. **Mockup 3D animado** con páginas que se pasan (primer intento). Se hizo con un renderizador propio (`render2`, `render3`, `render4`). **Al usuario no le gustó el libro 3D animado.**
3. **Reels para Instagram** (1080×1920) del proceso de producción, a partir de vídeos del propio taller.

## 4. Preferencias del cliente (importantes)

- Seguir el **orden cronológico** de la producción (de la pantalla a la impresión, pasando por el libro terminado).
- **Pocos textos.** Solo una firma pequeña al final.
- **No agresivo:** nada de destellos, paneos bruscos ni cortes violentos.
- **Sin el libro 3D animado.** Sí se aprobó el **mockup estático** como final.
- Los planos con las manos y el libro deben verse **con su color natural**. No quieren que las manos parezcan sucias.
- **Sin filtro al vídeo:** la última versión aprobada mantiene los colores originales (sin blanco y negro parcial, sin viñeta, sin grano).
- **Planos de pantalla (diseño en el ordenador):** van al principio. Deben ser cortos, con transiciones rápidas y sin espacios en blanco de la interfaz. Tienen que verse profesionales.
- **Planos con zoom a pie de foto:** la última versión los alarga para que se lea el texto.
- **Título final "PEDRO ZAMORA · EN NOIR"** grande, y debajo "DISEÑA, MAQUETA E IMPRIME" y "BODONIA ARTES GRÁFICAS" en negrita.
- **Música:** no quieren audio en la última versión. Si se añade, debe ser una pieza tranquila sin derechos de autor (el usuario la puede cambiar en Instagram).

## 5. Estado del último reel

- **Archivo entregado:** `reel_p2.mp4`
- **Duración:** 59,0 s exactos (límite pedido: 1 minuto).
- **Formato:** 1080×1920, 30 fps, H.264, sin audio, unos 28 MB.
- **Estructura:**
  1. Arranque de diseño en pantalla, unos 12 s, con planos de zoom y transiciones rápidas. Cortes a 0,2 s.
  2. Producción (impresora, guillotina, manos, tóner, pliegos), con los planos de personas más largos (unos 31,6 s en total).
  3. Libro terminado: portada, papel cristal, obras, detalle de página, canto del libro.
  4. Mockup final estático (unos 5 s) con el título y la firma de Bodonia.
- **Pendiente:** el usuario ha pedido texto para el reel y hashtags (ya entregados).

## 6. Textos ya entregados para el reel

**Versión formal:**
> Así nace un catálogo de arte 🖤
> *Pedro Zamora. En Noir* (Galerie Tourrette, París, marzo–abril de 2026): del diseño en pantalla al libro ya en las manos. Cada pliego, cada negro y cada detalle, cuidados hasta el último paso.
> Diseñamos, maquetamos e imprimimos en Bodonia Artes Gráficas.
> Texto: Gabriel Insausti · Fotografía: Pablo Asenjo

Hashtags: #BodoniaArtesGraficas #LibroDeArte #PedroZamora #CatalogoDeArte #ImpresionDeCalidad

**Versión informal:** titular "Esto es lo que pasa detrás de un libro de arte 🖤". Hashtags: #BodoniaArtesGraficas #LibroDeArte #PedroZamora #CatalogoDeArte #DetrasDeLasCamaras

Pendiente de confirmar: si Bodonia imprime siempre internamente (en la versión informal aparece "Todo en casa").

## 7. Pipeline técnico (scratchpad del proyecto)

Ruta base: `/tmp/claude-0/-home-claude/b21dfd75-fb6f-5da3-ae94-06a08b8bb6bb/scratchpad/reel/`

| Archivo | Función |
|---|---|
| `compose.py` | Utilidades: capas de texto (Pillow), fundidos, lectura de clips con ffmpeg |
| `compose3.py` … `compose14.py` | Versiones del montador del reel (la última: `compose14.py`) |
| `audio3.py`, `audio4.py` | Generación de música procedural (numpy) |
| `src/prod.mov` | Vídeo largo de producción (40,5 s de referencia) |
| `src2/a.mov`, `src2/b.mov` | Vídeos nuevos del libro terminado (4K, HEVC, rotación −90°) |
| `src2/s1.mov`, `src2/s2.mov` | Grabaciones de pantalla del diseño (606×944, 60 fps) |
| `real_cover.jpg`, `real_spread.jpg` | Fotos del catálogo impreso (portada y doble página) |
| `mock.png` | Mockup estático aprobado (2576×1546) |

**Notas técnicas:**
- Los renders largos hay que lanzarlos con `setsid nohup ... &` y consultar el log. Las llamadas en primer plano se cortan a los 10 min.
- Coordenadas del mockup: multiplicar por 1,288 sobre la imagen de 2000 px.
- Límite de envío: 30 MiB. Para cumplirlo, usar `-crf 17` a `-crf 18` con `-maxrate` de unos 4 MB/s para 60 s.
- La fuente `GFSBaskerville.otf` no renderiza en Pillow. Usar Inter o Lora.
- Los vídeos 4K del libro terminado tardan unos 2 min en pasarse a 1080×1920 con ffmpeg.

## 8. Errores ya resueltos (para no repetirlos)

- Franjas en el libro 3D (z-fighting del pintor): solucionado con búfer de profundidad por píxel.
- Pliegos mal modelados (cuadríptico): se abre a los dos lados.
- Título invisible por fuente rota: cambiado a Lora.
- Vídeo corrupto por proceso matado: relanzar a un archivo nuevo.
- Archivo de 34 MB sobre el límite de 30 MiB: re-codificar con menor bitrate.

## 9. Próximos pasos sugeridos

- Probar en el teléfono el reel `reel_p2.mp4` y revisar la nitidez de los zooms sobre las grabaciones de pantalla (son de baja resolución; con una exportación más grande desde el programa de diseño quedarían más nítidos).
- Confirmar el texto final y los hashtags del post.
- Si se quiere música, generar una pista tranquila sin derechos (o el usuario la añade en Instagram).
- Crear un segundo reel para otro catálogo reutilizando el pipeline (compose + audio) cambiando los planos y el título.
