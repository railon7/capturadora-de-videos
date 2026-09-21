# Ejemplos de uso real

## Proyecto típico: Manual de cliente

Cliente X, demo de 30 minutos.

### Carpeta de trabajo

```
C:\Proyectos\ClienteX\
├─ Trabajo-Demo/
│  ├─ Capturas/
│  │  ├─ Rejilla/             (fotogramas, no tocar)
│  │  ├─ Seleccionadas/       (calidad alta, elegidas)
│  │  └─ Editadas/            (recortadas, anotadas)
│  ├─ Hojas de contactos/     (mosaicos, no tocar)
│  └─ Analisis/
│     ├─ transcripcion.md     (texto completo)
│     ├─ Catalogo de capturas.md
│     ├─ Mapa del video — bloques y pantallas.md
│     └─ nombres-a-tapar.txt
└─ 08-Formacion/
   ├─ P-01-Login.md           (protocolo)
   ├─ P-02-Compras.md
   └─ P-03-Facturacion.md
```

### Paso a paso

**Semana 1: Captura y catálogo**

```powershell
# En C:\Proyectos\ClienteX\
cd _herramientas/capturadora-de-videos

# Extrae
scripts\extraer-capturas.ps1 -Video "C:\Videos\ClienteX-Demo.mp4" -Trabajo "Trabajo-Demo" -DeteccionEscena
```

Espera a que termine (30 min de vídeo, 2-3 minutos).

```bash
# Cataloga
python scripts/catalogar-capturas.py "Trabajo-Demo/Capturas/Rejilla"

# Mira el catálogo
Trabajo-Demo/Analisis/Catalogo de capturas.md
# Rellena la columna "Qué se ve" — abre cada imagen si no se entiende
```

Tarda una hora si tienes que mirar 90 imágenes.

**Semana 2: Guion**

```bash
# Transcribe
python scripts/transcribir.py "C:\Videos\ClienteX-Demo.mp4" --idioma es

# Primer borrador automático
python scripts/generar-borrador-guion.py "Trabajo-Demo/Analisis/transcripcion.tsv" --catalogo "Trabajo-Demo/Analisis/Catalogo de capturas.md"

# Edita a mano — abre esto y trocea en bloques y actos
Trabajo-Demo/Analisis/Mapa del video — bloques y pantallas.md
# Usa plantilla: plantillas/plantilla-mapa-de-video.md
```

**Semana 3: Manual**

```bash
# Identifica qué nombre aparecen en el vídeo (o pídele a un LLM que lea la transcripción)
# Crea una lista
cat > Trabajo-Demo/Analisis/nombres-a-tapar.txt << EOF
Novality
Juan Pérez
Acme Corp
admin@clientex.com
EOF

# Extrae cada pantalla en calidad alta
scripts\extraer-captura-puntual.ps1 -Video "C:\Videos\ClienteX-Demo.mp4" -Momento "00:05:20" -Salida "Trabajo-Demo/Capturas/Seleccionadas/P01-01-login.png"

# Tapa datos
python scripts/redactar-captura.py "Trabajo-Demo/Capturas/Seleccionadas/P01-01-login.png" "Trabajo-Demo/Capturas/Editadas/P01-01-login.png" --nombres "Trabajo-Demo/Analisis/nombres-a-tapar.txt"

# Anota con círculos (si hace falta)
python scripts/anotar-captura.py "Trabajo-Demo/Capturas/Editadas/P01-01-login.png" "Trabajo-Demo/Capturas/Final/P01-01-login.png" --marca 150,200 --marca 400,350

# Escribe el protocolo (usa plantilla: plantillas/plantilla-protocolo.md)
# Crea 08-Formacion/P-01-Login.md

# Audita antes de entregar
python scripts/auditar-privacidad.py --textos "Trabajo-Demo/Analisis" --ocr "Trabajo-Demo/Capturas/Editadas" --nombres "Trabajo-Demo/Analisis/nombres-a-tapar.txt"

# Empaqueta
python scripts/exportar-manual.py "08-Formacion/P-01-Login.md"
# Sale 08-Formacion/P-01-Login.html — entrega esto
```

---

## Casos especiales

### Solo quiero fotogramas, sin manual

```powershell
scripts\extraer-capturas.ps1 -Video "video.mp4" -Trabajo "trabajo" -Intervalo 10
python scripts/catalogar-capturas.py "trabajo/Capturas/Rejilla"
# Fin. Ya tienes 200 fotogramas catalogados cada 10 segundos.
```

### Vídeo muy largo (>2 horas), muchas imágenes

```bash
# Antes de catalogar, aviso de lo malo
python scripts/detectar-redundantes.py "trabajo/Capturas/Rejilla"
# Mira Analisis/Fotogramas a revisar.md — te dice cuáles están borrosas o duplicadas
# Elimina esas de Capturas/Rejilla manualmente
# Luego cataloga
python scripts/catalogar-capturas.py "trabajo/Capturas/Rejilla"
```

### Quiero OCR en las capturas, no solo en texto

```bash
# Asegúrate de tener Tesseract
winget install --id UB-Mannheim.TesseractOCR

# El catálogo lo hará automáticamente
python scripts/catalogar-capturas.py "trabajo/Capturas/Rejilla"
# La columna "Texto detectado (OCR)" se rellena sola
```

### La lista de nombres es muy larga o la genero automáticamente

```bash
# Usa un LLM para extraer nombres de la transcripción
cat Analisis/transcripcion.md | claude "Extrae todos los nombres propios y empresas que aparecen"
# Copia el resultado a Analisis/nombres-a-tapar.txt

# Luego redacta todo de una pasada (carpeta completa)
python scripts/redactar-captura.py "Capturas/Seleccionadas" "Capturas/Redactadas" --carpeta --nombres "Analisis/nombres-a-tapar.txt"
```

### Quiero exportar el manual a PDF

```bash
# HTML se sale solo
python scripts/exportar-manual.py "08-Formacion/P-01-Login.md"

# Para PDF, descarga pandoc
winget install pandoc

# El script lo detecta y genera PDF también
python scripts/exportar-manual.py "08-Formacion/P-01-Login.md" --pdf
```

---

## Patrones reutilizables

Cuando termines un proyecto, guarda los patrones que descubriste:

```bash
# Crea Trabajo-Demo/Analisis/Patrones reutilizables.md (usa plantilla)
# Luego fúndelos en el repo central
python scripts/consolidar-patrones.py "Trabajo-Demo/Analisis/Patrones reutilizables.md" --proyecto "ClienteX"
```

El siguiente proyecto que tenga un patrón parecido, el script te avisa y te sugiere si fusionarlo.
