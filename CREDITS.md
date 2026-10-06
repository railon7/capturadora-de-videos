# Créditos y licencias

Este repositorio no incluye código copiado de terceros: los scripts están
escritos desde cero. Pero varias mejoras están **inspiradas** en cómo otros
proyectos open source resuelven el mismo problema, encontrados en una
revisión de GitHub en español, inglés y japonés (septiembre 2026). Se
documentan aquí por transparencia y para dejar claro qué se podría adaptar
directamente en el futuro (licencias permisivas) y qué es solo una idea sin
línea de código de por medio (GPL o sin licencia).

## Adaptable con atribución (MIT / BSD / Apache / Unlicense)

| Proyecto | Licencia | Qué inspiró aquí |
|---|---|---|
| [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) | BSD-3-Clause | El modo `-DeteccionEscena` de `extraer-capturas.ps1`: la idea de complementar el muestreo a intervalo fijo con detección real de cambios de plano, en vez de fiarlo todo al intervalo |
| [vcsi](https://github.com/amietn/vcsi) | MIT | `-SaltarInicioPct`/`-SaltarFinalPct` (saltar intro/outro) y `-SoloKeyframes` (evitar frames borrosos, con su mismo trade-off documentado en HEVC) en `extraer-capturas.ps1`; el flag `-Preciso` de `extraer-captura-puntual.ps1` viene de su `--accurate` |
| [yahoo/hecate](https://github.com/yahoo/hecate) | Apache-2.0 | La idea de descartar fotogramas cercanos a una transición en vez de aceptar cualquiera que caiga en el segundo exacto (aplicada al filtrar duplicados entre intervalo fijo y detección de escena) |
| [Mimik](https://github.com/westpoint-io/mimik) | MIT | El principio de auditoría de privacidad antes de exportar (su "blur PII" por regex), y la idea de que el manual final es un formato de salida separado de la fuente editable |
| [shot-annotate](https://github.com/commte/shot-annotate) | MIT | Confirma que la numeración con círculos ①②③ no está resuelta en ninguna herramienta existente — validó mantenerla como convención propia en `plantillas/plantilla-protocolo.md`, en vez de descartarla por "ya debe existir algo así" |
| [auto-editor](https://github.com/WyattBlue/auto-editor) | Unlicense | Referencia para el manejo de ffmpeg como dependencia opcional con instalación automática (ya presente en `extraer-capturas.ps1` antes de esta revisión, reforzado por su enfoque) |

## Solo idea, sin copiar código (GPL / licencia no confirmada)

| Proyecto | Licencia | Qué NO se copió, solo se observó |
|---|---|---|
| [ShareX](https://github.com/ShareX/ShareX) | GPL-3.0 | Su función de numeración incremental de anotaciones — inspiración de diseño únicamente, ninguna línea de su código |
| [movie-thumbnailer](https://github.com/indiscipline/movie-thumbnailer) | GPL-3.0 | Sirvió como ejemplo de qué **no** hacer (coeficientes de margen fijos sin configurar, sin limpieza de temporales) |
| `demo-engine` (repo pequeño, licencia no confirmada) | — | La idea de una auditoría de privacidad por OCR con validadores de checksum (aplicada de forma independiente en `auditar-privacidad.py`, con DNI/NIE y Luhn en vez de RUT) |
| `meeting-minutes` (IwataRisa1996) | Sin licencia (todos los derechos reservados) | El patrón de pipeline por etapas con carpeta por sesión — solo como referencia de estructura |
| `transcribe-with-whisper` | Sin licencia confirmada | La idea de enlazar transcripción y vídeo por marca de tiempo — implementada de forma independiente en `transcribir.py` (TSV/Markdown, sin visor HTML) |

## Herramientas mencionadas como referencia de dominio, sin relación de código

- **Whisper / faster-whisper** (MIT) — es una dependencia real de `transcribir.py`, no solo inspiración; se instala con `pip install faster-whisper`.
- **Tesseract OCR** (Apache-2.0) — dependencia real y opcional de `auditar-privacidad.py --ocr`.
- **Tango, Scribe, Guidde, Teachme Biz, ZASSHA** — productos comerciales sin código disponible. Se citan en la investigación como validación de que el pipeline "grabación → pasos → plantilla anotada → manual" es el mismo que usan las herramientas líderes del sector, no como fuente de ningún código o texto.

## Metodología

Nada del contenido de `metodologia/` ni `plantillas/` está copiado de estos
proyectos: son la generalización del proceso ya desarrollado internamente
para la demo de Distrito K (Novatecnic), ajustado con las ideas de arriba.

## Técnicas genéricas usadas en las herramientas añadidas después (sin repo de origen)

`scripts/detectar-redundantes.py` implementa dos técnicas de dominio
público, de las que no se copió código de ningún proyecto concreto:

- **aHash** (average hash): reducir la imagen a 8×8 en escala de grises y
  comparar cada píxel con la media, para obtener una huella de 64 bits
  comparable por distancia de Hamming. Es una técnica estándar de hashing
  perceptivo, descrita en múltiples fuentes públicas desde hace más de una
  década (p. ej. los artículos de Neal Krawetz sobre pHash/aHash).
- **Nitidez por dispersión de bordes**: aproximación de la varianza del
  laplaciano (la métrica de nitidez más común en visión por computador) sin
  depender de OpenCV/numpy, usando el filtro `FIND_EDGES` de Pillow y la
  desviación típica del resultado.

`scripts/anotar-captura.py` (círculo + número dibujados, en vez de confiar
en el glyph unicode ①-⑳) y `scripts/consolidar-patrones.py` (comparación de
similitud con `difflib.SequenceMatcher`, de la librería estándar de Python)
son implementaciones propias sin relación con ningún repositorio de la
revisión de septiembre de 2026.

`scripts/redactar-captura.py` y las funciones de validación de
`auditar-privacidad.py` implementan los algoritmos de dígito de control del
DNI/NIE y del CIF español — son estándares administrativos públicos (BOE),
no código de ningún proyecto de terceros. La localización de texto sobre la
imagen usa `pytesseract.image_to_data` (Apache-2.0, ya era dependencia del
repo) para obtener la caja de cada palabra detectada.

## Ideas de documentación para la biblioteca de conocimiento (sin copiar texto ni código)

La organización de la biblioteca (`metodologia/biblioteca-de-conocimiento.md`, `plantillas/biblioteca/`) se apoya en estas
fuentes. Se tomaron ideas de estructura, no texto ni código. La investigación completa está en
`conocimiento/organizacion-documental/`.

| Fuente | Licencia | Qué inspiró aquí |
|---|---|---|
| [Diátaxis](https://diataxis.fr/) (Daniele Procida) | CC BY-SA 4.0 | Los cuatro tipos (tutorial, cómo hacer, referencia, explicación) y la brújula para elegir el de cada documento. No se copió texto: de hacerlo, la parte copiada heredaría CC BY-SA |
| [The Good Docs Project](https://www.thegooddocsproject.dev/template) | Zero-Clause BSD (según su `LICENSE.txt`) | Qué tipos de plantilla existen (how-to, tutorial, reference, troubleshooting, release notes, glossary, quickstart). Las plantillas de este repo son propias |
| [DITA, OASIS](https://docs.oasis-open.org/dita/v1.2/os/spec/archSpec/dita_technicalContent_InformationTypes.html) | Especificación abierta | Concepto, tarea y referencia como temas reutilizables: "escribir una vez, enlazar muchas" |
| ISO 9001 y guías de control documental | Norma de pago, no consultada en su texto | Solo las prácticas que describen las guías públicas: identificador, versión mayor.menor, estados, revisión anual, archivo |
| Guías de propiedades y alias de Obsidian | Documentación pública | Alias para el título en el otro idioma, etiquetas anidadas, convenciones de nombres de propiedades |

