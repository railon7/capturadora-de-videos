# Capturadora de Vídeos

Herramienta genérica para sacarle partido a una grabación (una demo de
producto, una reunión, una formación): convertirla en fotogramas navegables,
en un guion con marcas de tiempo, en patrones reutilizables y, si hace falta,
en un manual paso a paso con capturas limpias.

Nació de procesar la grabación de la demo de Distrito K (proyecto
Novatecnic), pero no depende de ese cliente ni de ningún método de
implantación concreto: sirve para cualquier vídeo del que haga falta sacar
imágenes, texto o documentación.

## El pipeline

```
Vídeo
  │
  ├─► 1. CAPTURAS — scripts/extraer-capturas.ps1
  │     Un fotograma cada N segundos + hojas de contacto para
  │     navegar el vídeo de un vistazo, sin reproducirlo. Opcional:
  │     fotogramas extra en cada cambio de escena (-DeteccionEscena).
  │     scripts/detectar-redundantes.py avisa de los borrosos o casi
  │     duplicados antes de perder tiempo revisándolos a mano.
  │
  ├─► 1bis. CATÁLOGO — scripts/catalogar-capturas.py (obligatorio)
  │     Qué se ve en cada imagen capturada, en un Markdown — para
  │     entender el contenido sin abrir las imágenes una por una.
  │
  ├─► 2. GUION — metodologia/de-video-a-guion-y-patrones.md
  │     scripts/transcribir.py (Whisper) da la transcripción con
  │     marca de tiempo por segmento; scripts/generar-borrador-guion.py
  │     cruza esa transcripción con el catálogo y deja un primer
  │     borrador del mapa por bloques (plantillas/plantilla-mapa-de-video.md)
  │     con los tiempos y la pantalla sugerida ya puestos, a falta de
  │     agrupar en bloques/actos con criterio.
  │
  ├─► 3. PATRONES — (mismo documento, segunda mitad)
  │     Qué de lo visto es reutilizable más allá de este caso concreto,
  │     con plantillas/plantilla-patrones.md. scripts/consolidar-patrones.py
  │     los funde en conocimiento/patrones-acumulados.md: la segunda vez
  │     que aparece un patrón deja de ser una anécdota de un solo cliente.
  │
  └─► 4. MANUAL — metodologia/de-capturas-a-manual.md
        Capturas seleccionadas → DNI/CIF/tarjeta/nombres tapados con
        scripts/redactar-captura.py (obligatorio por protección de
        datos) → recortadas y anotadas con círculos numerados
        (scripts/anotar-captura.py) → protocolo, usando
        plantillas/plantilla-protocolo.md → entregable único con
        scripts/exportar-manual.py, con scripts/auditar-privacidad.py
        como segunda comprobación antes de entregar.
```

Los pasos 2-4 son independientes entre sí: si solo hacen falta las imágenes
(por ejemplo, para alimentar otra cosa que no es un manual), se para después
del catálogo. Si hace falta el guion de lo que se dijo sin escribir manual,
se para en el 2-3. **El catálogo (1bis) no se salta nunca**: sin él, nadie
sabe qué hay en las capturas sin abrirlas una por una — ni siquiera si el
destino final no es un manual.

## Protección de datos — DNI, CIF y nombres no pueden salir en una captura

Es un requisito legal, no una recomendación. `scripts/redactar-captura.py`
tapa lo que se puede detectar de forma fiable (DNI, NIE, CIF, tarjeta,
email, teléfono — todos con dígito de control verificable) directamente
sobre una copia de la imagen. `scripts/auditar-privacidad.py` hace la misma
detección pero solo avisa, sin tocar la imagen — útil como segunda
comprobación después de redactar.

**Los nombres propios y de empresa son distintos: no existe un patrón que
los detecte solos.** Los dos scripts aceptan `--nombres fichero.txt` (un
nombre por línea) para taparlos/avisar de ellos por coincidencia literal —
esa lista la tiene que rellenar quien conoce los nombres reales del vídeo
o del proyecto. **Ninguno de los dos scripts certifica el cumplimiento por
sí solo**: son una ayuda que ahorra hacerlo a mano pantalla por pantalla,
no un sustituto de la revisión humana antes de entregar.

## Quickstart

```powershell
# 1. Fotogramas cada 20s + hojas de contacto de un vídeo cualquiera.
#    Añade -DeteccionEscena si el vídeo tiene transiciones más rápidas
#    que el intervalo, o -SaltarInicioPct/-SaltarFinalPct si hay intro/outro.
.\scripts\extraer-capturas.ps1 -Video "C:\ruta\al\video.mp4" -Trabajo "C:\ruta\de\trabajo"

# 2. Cuando ya sabes el momento exacto (por el índice, las hojas de
#    contacto o la transcripción), saca esa pantalla en máxima calidad
.\scripts\extraer-captura-puntual.ps1 -Video "C:\ruta\al\video.mp4" -Momento "00:45:20" -Salida "C:\...\captura.png"
```

```bash
# 1bis. Catálogo de contenido — obligatorio, no se salta
python scripts/catalogar-capturas.py "Capturas/Rejilla"

# 1ter. Aviso de fotogramas borrosos o casi duplicados (opcional, antes de mirarlos a mano)
python scripts/detectar-redundantes.py "Capturas/Rejilla"

# 2. Transcripción con marca de tiempo por segmento (recomendado antes del guion)
pip install faster-whisper
python scripts/transcribir.py "C:\ruta\al\video.mp4" --idioma es

# 2b. Borrador del mapa del vídeo, cruzando transcripción y catálogo
python scripts/generar-borrador-guion.py "Analisis/transcripcion.tsv" --catalogo "Analisis/Catalogo de capturas.md"

# 4a. Tapar DNI/CIF/tarjeta/email/teléfono y los nombres de la lista (obligatorio)
python scripts/redactar-captura.py "Capturas/Seleccionadas/P02-04.png" "Capturas/Editadas/P02-04-tapada.png" --nombres "nombres-a-tapar.txt"

# 4b. Anotar la ya tapada con círculos numerados -> esta es la definitiva
python scripts/anotar-captura.py "Capturas/Editadas/P02-04-tapada.png" "Capturas/Editadas/P02-04.png" --marca 120,80 --marca 300,200

# 4c. Antes de entregar: segunda comprobación de que no queda nada sin tapar
python scripts/auditar-privacidad.py --textos "Analisis" --ocr "Capturas/Editadas" --nombres "nombres-a-tapar.txt"

# 4c. Empaquetar el manual terminado en un único HTML para el cliente
pip install markdown
python scripts/exportar-manual.py "08-Formacion/P-02 · Circuito de compra.md"

# 3b. Cuando el proyecto ya tiene Analisis/Patrones reutilizables.md, fundirlo aquí
python scripts/consolidar-patrones.py "<proyecto>/Analisis/Patrones reutilizables.md" --proyecto "<nombre del cliente>"
```

Después, sigue `metodologia/de-video-a-guion-y-patrones.md` para el guion y
`metodologia/de-capturas-a-manual.md` para el manual.

## Estructura de este repositorio

| Carpeta | Contenido |
|---|---|
| `scripts/` | Extracción de fotogramas/escenas, hojas de contacto, capturas puntuales, detección de redundantes, catálogo de contenido, borrador del guion, anotación, redacción de datos personales, transcripción, auditoría de privacidad, exportación del manual y consolidación de patrones |
| `plantillas/` | Plantillas del mapa de vídeo, del protocolo/manual y de los patrones reutilizables |
| `metodologia/` | Los dos procedimientos: vídeo → guion y patrones · capturas → manual |
| `conocimiento/` | `patrones-acumulados.md` — el conocimiento reutilizable de todos los vídeos procesados con este repo, no de un proyecto en concreto |
| `.claude/skills/video-a-manual/` | Skill de Claude Code que guía el proceso completo en cualquier proyecto |
| `tests/` | Pruebas de las funciones puras de cada script (`pytest tests/`) |
| `.github/workflows/ci.yml` | Comprueba sintaxis y pasa los tests en cada push |
| `CREDITS.md` | Qué proyectos de terceros inspiraron cada mejora, y bajo qué licencia |

## Cómo usarlo en otro proyecto

```powershell
.\instalar.ps1 -Proyecto "C:\Proyectos\Cliente X"
```

Copia la skill a `.claude/skills/` del proyecto de destino, y `scripts/` +
`plantillas/` + `metodologia/` a `_herramientas/capturadora-de-videos/`
dentro de él (usa `-CarpetaHerramientas` para otra ruta). **Reescribe las
rutas dentro de la skill copiada** para que apunten a esa carpeta, así los
comandos de `SKILL.md` funcionan tal cual en el proyecto de destino, sin
tener que ajustar nada a mano. No copia `conocimiento/`: los patrones
acumulados son de este repo, no de cada proyecto — se consolidan aquí con
`consolidar-patrones.py`, no al revés.

Una vez copiada, Claude Code detecta la skill sola la próxima vez que se
abra en esa carpeta de proyecto — no hace falta ningún paso de registro
aparte. Se puede invocar explícitamente con `/video-a-manual`, o Claude la
usa sola cuando lo que se pide encaja con su descripción (un vídeo del que
sacar capturas, un manual, etc.).

En el proyecto de destino, crea la carpeta de trabajo del vídeo con la
estructura de `metodologia/de-video-a-guion-y-patrones.md` §0, ejecuta el
script de extracción, y sigue la metodología.

No hace falta clonar todo el repo dentro del proyecto de cliente: los datos
de cliente y el vídeo original **no vienen a este repositorio** (ver
`.gitignore`). Aquí solo vive la herramienta.

## Requisitos

- **ffmpeg**: los scripts de extracción lo buscan en el PATH, en
  `_herramientas/ffmpeg/` junto al vídeo, y si no lo encuentran intentan
  instalarlo con `winget` o descargar una copia portable. Puede instalarse a
  mano si algo de eso falla.
- **PowerShell 5.1+** (Windows) para `extraer-capturas.ps1`,
  `extraer-captura-puntual.ps1` e `instalar.ps1`.
- **Python 3.9+** con **Pillow** (`pip install pillow`) para
  `catalogar-capturas.py` (obligatorio en el pipeline),
  `detectar-redundantes.py`, `anotar-captura.py`, `redactar-captura.py` y
  `auditar-privacidad.py`. Además: `transcribir.py` necesita
  `pip install faster-whisper`; `exportar-manual.py` necesita
  `pip install markdown`; `generar-borrador-guion.py` y
  `consolidar-patrones.py` no necesitan nada aparte de la librería estándar.
- El texto OCR de `catalogar-capturas.py`, `redactar-captura.py` (obligatorio,
  no funciona sin OCR) y el modo `--ocr` de `auditar-privacidad.py` necesitan
  además `pip install pytesseract` y el binario
  `winget install --id UB-Mannheim.TesseractOCR`. Sin ellos, los dos
  primeros scripts fallan con un mensaje claro (redactar sin poder leer la
  imagen no tiene sentido); `auditar-privacidad.py --textos` sigue
  funcionando igual porque no depende de OCR.
- **pytest** (`pip install pytest`) solo para correr `tests/`.
