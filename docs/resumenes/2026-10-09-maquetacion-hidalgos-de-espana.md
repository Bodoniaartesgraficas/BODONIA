# Resumen del chat: maquetación de "Hidalgos de España 2024 TOMO 1" para InDesign

Fecha de la sesión: 9 de octubre de 2026.
Proyecto: Bodonia. Este documento resume lo hecho, las decisiones tomadas y lo pendiente, para retomarlo desde Claude Code.

## 1. Objetivo

Maquetar el libro *Hidalgos de España 2024, Tomo 1* (fichas de pleitos de hidalguía del Archivo de la Real Chancillería de Granada, reinado de Felipe III, letras A–L) usando como referencia un IDML de muestra, y entregar un único archivo IDML listo para abrir en InDesign.

## 2. Entradas

| Archivo | Contenido |
|---|---|
| `FICHAS_EDICIÓN.docx` | Texto completo: 1.342 fichas en total. Las principales van de la 1 a la 1.287 (A–Z) y, después, un apéndice con numeración propia de 1 a 55. Cada ficha tiene etiquetas (Vecindad, Fecha de Inicio, Fecha Final, Prueba de Nobleza, Casado, Hijos, Padre, Abuelo, Signatura, Notas, Documentación relacionada, etc.). |
| `prueba_Hidalgos_de_España_2024_TOMO1.idml` | Muestra de maquetación. Tiene 26 páginas: portadas, créditos, prólogo, introducción, una página de letra "A" (página 15) y spreads de fichas. Fuente: PF Agora Sans Pro. Maestra con marcos de cabecera y pie. |

## 3. Qué se entregó

**Archivo final:** `Hidalgos_de_España_2024_TOMO1_maquetado.idml` (aprox. 2,3 MB).

- Páginas 1–15 se conservan tal cual de la muestra (portadas, créditos, prólogo, introducción y la "A" de la p. 15).
- Páginas 16–1265: 625 spreads con un flujo único de texto enlazado (cadena de marcos de 1.251 frames, verificada).
- Estilos creados en `Styles.xml`:
  - Párrafo: `FICHA Texto` (base, 10/11,3 pt, sangría francesa 14,17 pt, tabuladores 14,17 / 28,35 / 428), `FICHA Texto separado` (+11,3 pt antes), `FICHA Título`, `FICHA Título 3 cifras`, `FICHA Título 4 cifras`, `FICHA Letra` (48 pt, página nueva).
  - Carácter: `ETIQUETA` (versalitas, para "Vecindad:", "Prueba de Nobleza:", etc.).
  - Se reutilizan los carácteres ya existentes en la muestra: `NUMERO` y `NOMBRE`, y `LETRA` para las letras.
- Preferencias: `LimitToMasterTextFrames=false`, `DeleteEmptyPages=true`, reflujo automático activado.
- Verificación técnica: XML bien formado en los 667 archivos, sin IDs duplicados, sin referencias rotas en `designmap.xml`, texto idéntico al Word (2.319.258 caracteres comparados tras normalizar espacios y comillas).

## 4. Decisiones de maquetación tomadas (revisar con la editorial)

1. **Letras de apertura** (B, C, D…) van dentro del flujo como `FICHA Letra`, en página nueva. Solo la "A" de la p. 15 se mantiene como marco de la muestra.
2. **Números de tres y cuatro cifras** (a partir de la ficha 100) usan un tabulador más ancho, porque con el de la muestra el nombre saltaba al margen derecho.
3. **Comillas** rectas del Word pasan a tipográficas “ ” y ‘ ’.
4. **Etiquetas con dos puntos**, como en el Word ("Fecha Final:"). La muestra los omitía en algún caso.
5. **"INFORMACIÓN HERÁLDICA"** se unifica como "Información Heráldica".
6. **"APÉNDICE"** se compone como letra de apertura.
7. **Justificación**: el texto va justificado a la izquierda (`LeftJustified`), igual que la muestra. La última página de cada letra puede estirarse verticalmente; ajustar a "Arriba" si molesta.

## 5. Problemas conocidos y estimaciones

- **Número de páginas.** Estimado en 1.187–1.265 según escala tipográfica, sin usar las métricas reales de PF Agora. Se fijó 1.265, por lo que probablemente sobren páginas vacías al final. Hay que borrarlas en InDesign.
- **Anomalías del Word:** la numeración tiene saltos (p. ej. 45→47, 48→50, 135→137, 194→196…); algunos títulos tienen número sin nombre (186, 595) y otros aparecen en el orden de la transcripción. Se procesaron sin pérdida, pero conviene revisarlos.
- **Alcance del tomo.** La portada dice "Tomo I (A-L)", pero el Word contiene A–Z y apéndice. Si el tomo debe acabar en la L, hay que partir el libro antes de la ficha 717 (MACÍAS OCANO, primera de la M).
- **Comillas desbalanceadas:** 10 párrafos con comillas abiertas sin cerrar en el original (p. ej. "estaba”cayda"). No se corrigieron.
- **Fuente no instalada en el entorno:** PF Agora Sans Pro no está disponible aquí, así que las mediciones son aproximadas.

## 6. Pipeline (reproducible)

Carpeta de trabajo: `scratchpad/` (en la sesión de Claude). Scripts principales:

- `scripts/dx.py`: lee el Word (`word/document.xml`) con formato de runs.
- `scripts/model.py`: convierte el Word en bloques (título, letra, párrafo con etiqueta, apéndice), normaliza comillas y espacios, detecta anomalías.
- `scripts/est.py`: estimación de páginas con Liberation Sans como sustituto.
- `scripts/build.py <páginas>`: copia el IDML de muestra, crea estilos, escribe la historia `Story_u35a.xml`, genera los spreads y el `designmap.xml`, y empaqueta el IDML (mimetype sin comprimir, primero).
- `scripts/verify.py`: valida XML, IDs, cadena de marcos, número de páginas y texto contra el Word.

Ejecución: `python3 -I scripts/build.py 1265` y después `python3 -I scripts/verify.py`.

## 7. Qué no se ha hecho todavía

- [ ] Apertura en InDesign y revisión visual (no se ha podido comprobar).
- [ ] Métricas reales de PF Agora Sans Pro (el usuario puede subir .otf/.ttf, solo para medir; no se incrustan).
- [ ] Prueba corta de 20–30 fichas antes del libro completo (recomendado).
- [ ] Corrección ortotipográfica del Word con cambios controlados (acepta/rechaza). Se propuso, sin ejecutar. Lo que sí corregiría: espacios, comillas, etiquetas, numeración, erratas evidentes. Lo que no tocaría: grafía histórica (çiudad, avía, bino), fechas, signaturas, nombres y topónimos, que solo se señalan.
- [ ] Decidir el alcance del tomo (A–L o A–Z).
- [ ] Revisar la numeración anómala del Word.
- [ ] Crear una skill reutilizable (`maquetacion-indesign-idml`) con este procedimiento. Se propuso; no se ha guardado.
- [ ] Conector de Adobe para fusión de datos y plantillas .indd: disponible como skill, no usado.

## 8. Checklist para el próximo libro

1. Pedir IDML de muestra con todos los casos y estilos ya definidos.
2. Pedir el Word con estilos consistentes, sin formato manual ni saltos de página para las letras.
3. Pedir la fuente (licencia propia) para medir.
4. Prueba corta de 20–30 fichas, revisión en InDesign, luego el libro completo.
5. Entrega final con revisión de páginas sobrantes y justificación de las últimas páginas.

## 9. Notas sobre el propio chat

- El usuario trabaja en el plan de pago de Claude (Sonnet 5.5 en el chat; luego se cambió a Haiku 5.5 en Claude Code).
- Las respuestas se han redactado en castellano, con tono directo, sin jerga innecesaria.
- Archivo entregado desde el chat: el IDML maquetado (`Hidalgos_de_España_2024_TOMO1_maquetado.idml`).
