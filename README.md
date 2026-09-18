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
  │
  ├─► 2. GUION — metodologia/de-video-a-guion-y-patrones.md
  │     scripts/transcribir.py (Whisper) da la transcripción con
  │     marca de tiempo por segmento; de ahí, un mapa por bloques
  │     con plantillas/plantilla-mapa-de-video.md
  │
  ├─► 3. PATRONES — (mismo documento, segunda mitad)
  │     Qué de lo visto es reutilizable más allá de este caso concreto.
  │
  └─► 4. MANUAL — metodologia/de-capturas-a-manual.md
        Capturas seleccionadas → recortadas y anotadas → protocolo,
        usando plantillas/plantilla-protocolo.md, con
        scripts/auditar-privacidad.py como aviso antes de entregar.
```

Los pasos son independientes: si solo hace falta la imagen (por ejemplo,
para alimentar otra cosa que no es un manual), se para en el paso 1. Si
hace falta el guion de lo que se dijo sin escribir manual, se para en el 2-3.

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
# 1b. Transcripción con marca de tiempo por segmento (recomendado antes del guion)
pip install faster-whisper
python scripts/transcribir.py "C:\ruta\al\video.mp4" --idioma es

# 4b. Antes de entregar: aviso heurístico de datos identificables
python scripts/auditar-privacidad.py --textos "Analisis" --ocr "Capturas/Editadas"
```

Después, sigue `metodologia/de-video-a-guion-y-patrones.md` para el guion y
`metodologia/de-capturas-a-manual.md` para el manual.

## Estructura de este repositorio

| Carpeta | Contenido |
|---|---|
| `scripts/` | Extracción de fotogramas/escenas, hojas de contacto, capturas puntuales (PowerShell + ffmpeg), transcripción (Python + Whisper) y auditoría de privacidad (Python) |
| `plantillas/` | Plantilla del mapa de vídeo (guion) y plantilla del protocolo/manual |
| `metodologia/` | Los dos procedimientos: vídeo → guion y patrones · capturas → manual |
| `.claude/skills/video-a-manual/` | Skill de Claude Code que guía el proceso completo en cualquier proyecto |
| `CREDITS.md` | Qué proyectos de terceros inspiraron cada mejora, y bajo qué licencia |

## Cómo usarlo en otro proyecto

Este repo es la fuente. Para usarlo en un proyecto de cliente concreto:

1. Copia `.claude/skills/video-a-manual/` a `.claude/skills/` del proyecto,
   y `scripts/` y `plantillas/` a donde le convenga a ese proyecto (por
   ejemplo `_herramientas/`).
2. En el proyecto, crea la carpeta de trabajo del vídeo con la estructura de
   `metodologia/de-video-a-guion-y-patrones.md` §1.
3. Ejecuta el script de extracción, luego sigue la metodología.

No hace falta clonar todo el repo dentro del proyecto de cliente: los datos
de cliente y el vídeo original **no vienen a este repositorio** (ver
`.gitignore`). Aquí solo vive la herramienta.

## Requisitos

- **ffmpeg**: los scripts de extracción lo buscan en el PATH, en
  `_herramientas/ffmpeg/` junto al vídeo, y si no lo encuentran intentan
  instalarlo con `winget` o descargar una copia portable. Puede instalarse a
  mano si algo de eso falla.
- **PowerShell 5.1+** (Windows) para `extraer-capturas.ps1` y
  `extraer-captura-puntual.ps1`.
- **Python 3.9+** solo si se usan `transcribir.py` (`pip install
  faster-whisper`) o `auditar-privacidad.py` en modo `--ocr` (`pip install
  pytesseract pillow`, y el binario `winget install --id
  UB-Mannheim.TesseractOCR`). El modo `--textos` de la auditoría de
  privacidad no necesita nada aparte de Python.
