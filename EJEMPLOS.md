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
└─ ClienteX-Biblioteca/       (biblioteca del cliente: nuevo-documento.py --iniciar cliente)
   ├─ _img/                   (capturas definitivas: SOP-ERP-001-01-login.png...)
   ├─ entregables/            (HTML y PDF para entregar)
   ├─ 90-archivo/             (obsoletos)
   ├─ SOP-ERP-001_login.es.md          (un SOP, y su pareja SOP-ERP-001_login.en.md si hace falta)
   ├─ SOP-ERP-002_compras.es.md
   └─ GUI-ERP-001_facturacion.es.md    (una guía de usuario)
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
scripts\extraer-captura-puntual.ps1 -Video "C:\Videos\ClienteX-Demo.mp4" -Momento "00:05:20" -Salida "Trabajo-Demo/Capturas/Seleccionadas/SOP-ERP-001-01-login.png"

# Tapa datos
python scripts/redactar-captura.py "Trabajo-Demo/Capturas/Seleccionadas/SOP-ERP-001-01-login.png" "Trabajo-Demo/Capturas/Editadas/SOP-ERP-001-01-login.png" --nombres "Trabajo-Demo/Analisis/nombres-a-tapar.txt"

# Anota con círculos (si hace falta)
python scripts/anotar-captura.py "Trabajo-Demo/Capturas/Editadas/SOP-ERP-001-01-login.png" "Trabajo-Demo/Capturas/Final/SOP-ERP-001-01-login.png" --marca 150,200 --marca 400,350

# Crea el documento (ID, nombre, frontmatter y plantilla de su tipo) y rellénalo.
# Los criterios de redacción están en plantillas/plantilla-protocolo.md
python scripts/nuevo-documento.py --tipo SOP --aplicacion ERP --titulo "Login" --cliente ClienteX --biblioteca "ClienteX-Biblioteca" --propietario "Tu Nombre"
# Mueve las capturas definitivas a ClienteX-Biblioteca/_img/ con el nombre <ID>-<NN>-<descripcion>.png

# Comprueba nombres, metadatos, imágenes y enlaces
python scripts/validar-biblioteca.py "ClienteX-Biblioteca" --registro

# Audita antes de entregar
python scripts/auditar-privacidad.py --textos "Trabajo-Demo/Analisis" --ocr "Trabajo-Demo/Capturas/Editadas" --nombres "Trabajo-Demo/Analisis/nombres-a-tapar.txt"

# Empaqueta
python scripts/exportar-manual.py "ClienteX-Biblioteca/SOP-ERP-001_login.es.md" --pdf
# Sale ClienteX-Biblioteca/entregables/SOP-ERP-001_login.es.html (y el .pdf) — entrega esto.
# Mientras el documento no esté aprobado, lleva marca de agua BORRADOR o EN REVISIÓN.
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
# HTML: sale solo
python scripts/exportar-manual.py "ClienteX-Biblioteca/SOP-ERP-001_login.es.md"

# PDF: con Chrome o Edge instalados no hace falta nada más
python scripts/exportar-manual.py "ClienteX-Biblioteca/SOP-ERP-001_login.es.md" --pdf
# Si no los encuentra, prueba con pandoc (winget install pandoc). Sin ninguno, el HTML sigue valiendo: Ctrl+P en el navegador.
```

### Quiero el documento en español y en inglés

```bash
# Crea las dos versiones con el mismo ID: la española lista para rellenar y la inglesa con los encabezados traducidos
python scripts/nuevo-documento.py --tipo SOP --aplicacion Holded --titulo "Emitir factura rectificativa" --titulo-en "Issue a corrective invoice" --cliente ClienteX --biblioteca "ClienteX-Biblioteca"
# Crea SOP-HOLDED-001_emitir-factura-rectificativa.es.md y SOP-HOLDED-001_issue-a-corrective-invoice.en.md
# Aprueba el español, pídele a Claude la traducción (queda en borrador-ia) y que una persona la revise.
```

### Tengo protocolos en el formato antiguo (P-02 · Nombre.md)

```bash
# Prueba primero: no escribe nada
python scripts/migrar-protocolo.py "08-Formacion/P-02 · Circuito de compra.md" --tipo SOP --cliente ClienteX --biblioteca "ClienteX-Biblioteca" --simular
# Si el resultado es el esperado, quita --simular. El original no se toca; las imágenes se copian a _img/ con su nombre nuevo.
```

### Quiero ver los patrones por aplicación y no en un solo fichero

```bash
python scripts/patrones-a-biblioteca.py          # un PAT por cada "Del proyecto: ..." de conocimiento/patrones-acumulados.md
python scripts/validar-biblioteca.py --registro  # regenera conocimiento/biblioteca/00-gobierno/00_Registro.md
```
Se puede repetir: si un apartado no cambió no se toca, y si cambió se actualiza el PAT y sube su versión.

---

## Patrones reutilizables

Cuando termines un proyecto, guarda los patrones que descubriste:

```bash
# Crea Trabajo-Demo/Analisis/Patrones reutilizables.md (usa plantilla)
# Luego fúndelos en el repo central
python scripts/consolidar-patrones.py "Trabajo-Demo/Analisis/Patrones reutilizables.md" --proyecto "ClienteX"
```

El siguiente proyecto que tenga un patrón parecido, el script te avisa y te sugiere si fusionarlo.
