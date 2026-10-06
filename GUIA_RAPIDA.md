# Guía rápida: Capturadora de Vídeos

## En 5 minutos

Tienes un vídeo. Quieres fotogramas, un guion, un manual, o los tres. Aquí está todo automatizado.

### 0. Copia la herramienta a tu proyecto

Desde la carpeta de este repo:

```powershell
.\instalar.ps1 -Proyecto "C:\Proyectos\Tu-Cliente"
```

Listo. La skill está en `.claude/skills/video-a-manual/` del proyecto, y los scripts en `_herramientas/capturadora-de-videos/`. Sin pasos adicionales.

### 0b. ¿El vídeo está en YouTube? Descárgalo

Crea un `enlaces.txt` con una línea por vídeo, con nombre o sin él:

```
Creación de una ficha de cliente = https://youtu.be/ciHgR9xX1PI?si=sqWS...
https://youtu.be/VMM_P4AEcuA
```

```bash
pip install yt-dlp
python scripts/descargar-videos.py --lista enlaces.txt --carpeta "C:\Videos\FactuSol"
```

Sin nombre, el fichero se llama como el título del vídeo. El script quita las comillas tipográficas, los espacios sobrantes, el `?si=...` de los enlaces compartidos y los caracteres que Windows no admite (`:` y `|` pasan a guion; los emojis desaparecen). Si un vídeo falla, sigue con los demás y al final te dice cuáles. Si lo relanzas, se salta los que ya están. También vale con enlaces sueltos: `python scripts/descargar-videos.py "https://youtu.be/..." --carpeta ...`.

Solo vídeos propios, del cliente o con permiso del autor.

### 1. Extrae fotogramas del vídeo

```powershell
scripts/extraer-capturas.ps1 -Video "C:\Videos\demo.mp4" -Trabajo "C:\Tu-Proyecto\Trabajo"
```

Deja fotogramas cada 20 segundos en `Capturas/Rejilla/`, hojas de contacto en `Hojas de contactos/` y un índice en `Analisis/`.

Parámetros opcionales:
- `-Intervalo 10` → cada 10 segundos en lugar de 20
- `-DeteccionEscena` → fotogramas extra en cambios de pantalla
- `-SaltarInicioPct 5` → salta el primer 5% (intro)

**¿Es una videollamada o un webinar (Teams, Zoom, Meet)?** Quita el fondo de la aplicación y la miniatura de la cámara para quedarte solo con la pantalla compartida:

```bash
python scripts/recortar-pantalla.py "Capturas/Rejilla"
```

Sale `Capturas/Rejilla-pantalla/`; los originales no se tocan. Al terminar lista los tamaños de recorte: si alguno es raro (la sala de espera suele serlo), fija su caja con `--forzar-caja "t_0000*.jpg=x0,y0,x1,y1"`. Desde aquí, trabaja con `Rejilla-pantalla`.

### 2. Cataloga lo que capturaste (obligatorio)

```bash
python scripts/catalogar-capturas.py "Capturas/Rejilla"
```

Sale `Analisis/Catalogo de capturas.md`. **Completa la columna "Qué se ve"** — no basta con el OCR, describe lo que ves en cada imagen. Sin esto, nadie sabe qué hay dentro sin abrir 200 imágenes.

### 3. (Opcional) Aviso de fotogramas malos

Si son muchas imágenes:

```bash
python scripts/detectar-redundantes.py "Capturas/Rejilla"
```

Te dice cuáles están borrosas o casi repetidas, para no catalogar lo que vas a tirar. No borra nada.

### 4. Transcribe (si quieres guion o manual)

```bash
pip install faster-whisper
python scripts/transcribir.py "C:\Videos\demo.mp4" --idioma es
```

Sale `Analisis/transcripcion.md` (legible) y `Analisis/transcripcion.tsv` (para procesar).

### 5. Trocea en bloques (guion)

Abre `metodologia/de-video-a-guion-y-patrones.md`, §1-3, y sigue los pasos. Usa la plantilla `plantillas/plantilla-mapa-de-video.md`.

O si quieres un primer borrador automático:

```bash
python scripts/generar-borrador-guion.py "Analisis/transcripcion.tsv" --catalogo "Analisis/Catalogo de capturas.md"
```

Te deja un fichero con la transcripción cruzada con el catálogo — todavía tienes que agrupar en bloques con criterio, pero ahorra teclear tiempos y buscar pantallas a mano.

### 6. (Si quieres manual) Tapa datos sensibles

**DNI, CIF, nombres propios no pueden salir.**

```bash
python scripts/redactar-captura.py "Capturas/Seleccionadas/SOP-ERP-001-01.png" "Capturas/Editadas/SOP-ERP-001-01.png" --nombres "nombres-a-tapar.txt"
```

Dónde `nombres-a-tapar.txt` es:
```
Novality
Juan Pérez
Acme Corp
```

Tapa todo automáticamente (DNI, email, teléfono se detectan solos; nombres van por lista). Nunca toca el original.

### 7. Anota con círculos numerados

```bash
python scripts/anotar-captura.py "Capturas/Editadas/SOP-ERP-001-01.png" "Capturas/Final/SOP-ERP-001-01.png" --marca 120,80 --marca 300,200
```

Dibuja ① ② ③ en los lugares que le indiques. Úsalo después de tapar datos.

### 8. Crea y escribe el documento

Decide el tipo (SOP, guía de usuario, tutorial...) y créalo con su ID y su plantilla:

```bash
python scripts/nuevo-documento.py --tipo SOP --aplicacion ERP --titulo "Login" --cliente ClienteX --biblioteca "ClienteX-Biblioteca"
```

Rellénalo siguiendo los criterios de `plantillas/plantilla-protocolo.md`. Las capturas definitivas van a `_img/` con el
nombre `<ID>-<NN>-<descripcion>.png`.

### 9. Antes de entregar, audita privacidad

```bash
python scripts/auditar-privacidad.py --textos "Analisis" --ocr "Capturas/Editadas" --nombres "nombres-a-tapar.txt"
```

Segunda opinión automática. No es garantía legal, **revisa a ojo antes de mandar nada a cliente**.

### 10. Valida la biblioteca

```bash
python scripts/validar-biblioteca.py "ClienteX-Biblioteca" --registro
```

Comprueba nombres, metadatos, imágenes y enlaces, y regenera `00_Registro.md`. Sin errores antes de pasar a revisión.

### 11. (Opcional) Empaqueta en un HTML y un PDF

```bash
pip install markdown
python scripts/exportar-manual.py "ClienteX-Biblioteca/SOP-ERP-001_login.es.md" --pdf
```

Sale en `entregables/` con todas las imágenes incrustadas; el PDF lo hace Chrome o Edge. Si el documento no está aprobado,
lleva marca de agua BORRADOR o EN REVISIÓN.

---

## Flujos típicos

### Solo quiero fotogramas navegables
→ Pasos 1, 2. Listo.

### Quiero el guion de lo que se dijo
→ Pasos 1, 2, 4, 5.

### Quiero un manual para cliente
→ Pasos 1–11. Dedica tiempo al paso 2 (catálogo) y paso 6 (redacción de datos).

---

## Requisitos

- **ffmpeg** — el script lo busca en el PATH, en `_herramientas/ffmpeg/`, o lo descarga
- **PowerShell 5.1+** para extraer fotogramas
- **Python 3.9+** con **pillow** para todo lo demás
- **Tesseract-OCR** (opcional) si quieres OCR en catálogo y redacción: `winget install --id UB-Mannheim.TesseractOCR`
- **faster-whisper** (opcional) para transcripción: `pip install faster-whisper`
- **markdown** (opcional) para exportar HTML: `pip install markdown`

---

## Prompt para Claude Code

Abre Claude Code en tu carpeta de proyecto. Copia esto en el chat:

```
Tengo un vídeo de una demo / reunión grabada / formación. 
Quiero [fotogramas / un guion / un manual con fotos anotadas].

El vídeo está en: [ruta al vídeo]
La carpeta de trabajo está en: [ruta de carpeta de trabajo]

¿Qué pasos doy primero?
```

Claude te guiará con la skill `/video-a-manual` que ya está instalada en tu proyecto.
