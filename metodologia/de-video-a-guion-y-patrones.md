# De vídeo a guion y patrones reutilizables

Qué hacer entre "ya tengo los fotogramas" y "ya sé qué manual escribir": cómo
convertir un vídeo largo (una demo, una reunión grabada, una formación) en un
documento que se puede recorrer sin volver a verlo entero, y en un puñado de
ideas que sirven más allá de ese vídeo concreto.

## 0 · Estructura de carpeta de partida

La que deja `scripts/extraer-capturas.ps1`:

```
<carpeta de trabajo>/
├─ Capturas/
│   ├─ Rejilla/          Un fotograma cada N segundos, t_HHMMSS.jpg — no se toca
│   │                    (y e_HHMMSS.jpg si se usó -DeteccionEscena)
│   ├─ Seleccionadas/    Las pantallas que valen para el manual, en máxima calidad
│   └─ Editadas/         Las mismas, recortadas y anotadas
├─ Hojas de contactos/   Mosaicos de 20 fotogramas para navegar el vídeo de un vistazo
└─ Analisis/             video-info.txt, indice-capturas.txt, indice-escenas.txt,
                         transcripcion.md/.tsv, y el mapa del vídeo
```

El vídeo original no se mueve ni se edita. Todo lo que sale de él vive en
esta carpeta; el manual terminado, si lo hay, es un entregable y va aparte.

## 0ter · Descarta lo redundante (opcional, antes del catálogo)

Con vídeos largos, revisar la Rejilla entera a mano cuesta tiempo.
`scripts/detectar-redundantes.py` avisa de los fotogramas probablemente
borrosos y de los casi duplicados consecutivos, sin borrar ni mover nada:

```bash
python scripts/detectar-redundantes.py "Capturas/Rejilla"
```

Deja `Analisis/Fotogramas a revisar.md`. Es un aviso, no una garantía —
revisa antes de ignorar nada, y hazlo antes del catálogo del paso
siguiente para no perder tiempo describiendo lo que se va a descartar.

## 0bis · Cataloga lo que se ha capturado (obligatorio)

Antes de seguir, **toda imagen capturada tiene que quedar descrita en un
Markdown** — no basta con el nombre por marca de tiempo para saber qué hay
dentro sin abrir la imagen. Esto vale aunque el destino final no sea un
manual: si las imágenes van a usarse "para otra cosa", quien las reciba
necesita el catálogo igual para saber qué hay sin recorrerlas una a una.

```bash
python scripts/catalogar-capturas.py "Capturas/Rejilla"
```

Deja `Analisis/Catalogo de capturas.md` con una fila por imagen: el nombre,
la hora, el texto que se lee en pantalla (OCR automático, si está
disponible) y una columna "Qué se ve" en blanco. **El OCR lee texto, no
interpreta la pantalla** — completa esa columna a mano o pidiéndole a un
LLM que mire las imágenes, no la dejes vacía. Repite para
`Capturas/Seleccionadas` y `Capturas/Editadas` cuando existan.

## 1 · Consigue la transcripción íntegra

La forma recomendada es `scripts/transcribir.py` (Whisper vía
`faster-whisper`), que da la transcripción completa **con marca de tiempo
por segmento** de forma automática:

```
pip install faster-whisper
python scripts/transcribir.py "<vídeo>" --idioma es
```

Deja `Analisis/transcripcion.md` (legible, una línea por segmento con su
`**HH:MM:SS**`) y `Analisis/transcripcion.tsv` (para procesar con otro
script). Si no se puede usar Whisper, el paso se hace igual a mano —
escuchando el vídeo de principio a fin — pero entonces sí hace falta el
método de las hojas de contacto del §3 para poner la marca de tiempo,
porque una transcripción manual normalmente no la trae.

Hace falta el texto completo, no un resumen — el resumen se construye
después, a partir del texto, y si se salta este paso se pierden los
fragmentos literales que luego sirven para localizar el momento exacto.

## 1bis · Borrador automático (opcional, ahorra el cruce manual)

Si la transcripción viene de `transcribir.py` y ya existe
`Analisis/Catalogo de capturas.md`, `scripts/generar-borrador-guion.py`
hace el cruce mecánico: coge cada segmento con su marca de tiempo y sugiere
la captura del catálogo más cercana en el tiempo.

```bash
python scripts/generar-borrador-guion.py "Analisis/transcripcion.tsv" --catalogo "Analisis/Catalogo de capturas.md"
```

**Esto no sustituye el paso 2.** El resultado es una fila por segmento de
transcripción, no un bloque con sentido — hay que fundir filas, agruparlas
en actos y corregir la pantalla sugerida cuando la más cercana en el tiempo
no sea la correcta. Ahorra teclear tiempos y buscar capturas a mano; no
ahorra el criterio de qué es un bloque.

## 2 · Trocea en bloques y actos — el mapa del vídeo

Con la transcripción completa delante (o el borrador del paso anterior ya
revisado), una sola pasada de principio a fin:

1. Corta en **bloques**: cada vez que cambia el tema, la pantalla o quien
   habla. Un bloque es tan corto como haga falta — a veces es una frase.
2. Agrupa los bloques en **actos**: la unidad más grande con sentido propio
   (p. ej. "presupuesto", "compras", "cierre contable").
3. Para cada bloque, anota una **cita literal**, no un resumen. Un resumen no
   se puede buscar después en la transcripción ni reconocer en una hoja de
   contacto; una frase textual sí.
4. Deja la columna de marca de tiempo **vacía** en esta pasada si la
   transcripción no la trae. Se rellena después — nunca por memoria ni por
   proporción estimada del vídeo.

Usa `plantillas/plantilla-mapa-de-video.md` y guarda el resultado como
`Analisis/Mapa del video — bloques y pantallas.md`.

## 3 · Localiza los tiempos

**Si la transcripción viene de `transcribir.py`**, cada bloque ya trae su
segundo: busca la cita literal en `Analisis/transcripcion.md` y copia la
marca de tiempo de esa línea. Las hojas de contacto quedan como
verificación visual rápida (confirmar que en ese segundo se ve lo que se
espera), no como método de búsqueda.

**Si la transcripción es manual y no trae tiempos**, recorre las hojas de
contacto: la secuencia de bloques es el guion, así que el bloque 2 está por
la hoja 01, el 5 por la 02, y así sucesivamente. En cuanto se ubican tres o
cuatro bloques, el resto se sitúa solo por proximidad.

Fórmula para traducir una miniatura de una hoja a segundo exacto:

```
índice = (nº de hoja − 1) × 20 + posición-en-la-hoja
segundo = (índice − 1) × intervalo
```

Con los tiempos localizados, ya se puede pedir la captura en máxima calidad
con `scripts/extraer-captura-puntual.ps1` en lugar de conformarse con el
fotograma de rejilla. Si el vídeo tiene transiciones más rápidas que el
intervalo de muestreo, revisa también `Analisis/indice-escenas.txt` (si se
extrajo con `-DeteccionEscena`): puede que ahí ya esté el fotograma exacto
que las hojas de contacto no llegaron a capturar.

## 4 · Saca los patrones reutilizables

Esto es lo que distingue un mapa de vídeo de una metodología: una segunda
lectura del mapa completo, ya troceado, buscando **qué de lo que se ha visto
no depende del caso concreto**.

Preguntas que ayudan a encontrarlos:

- ¿Hay una solución a un problema que reaparece en otros clientes o casos, no
  solo en este?
- ¿Hay una decisión de diseño que, explicada de forma abstracta, sirve como
  regla general ("para un fabricante que en realidad ensambla…")?
- ¿Hay una pregunta que debería estar en la lista de comprobación de la
  *próxima* vez que se haga algo parecido, porque aquí faltó hacerla o
  llegó tarde?
- ¿Hay un límite o una trampa del sistema/proceso que conviene que quede
  escrita antes de que alguien la descubra por las malas?

Cada patrón se escribe corto: una frase que lo nombra, en qué caso concreto
apareció (como ejemplo, no como condición), y a qué tipo de situación se
aplicaría en general. Usa `plantillas/plantilla-patrones.md` y guárdalo como
`Analisis/Patrones reutilizables.md` — ese nombre y esa estructura de
encabezados son los que espera `scripts/consolidar-patrones.py`.

Cuando el proyecto ya tiene ese fichero, fúndelo en el conocimiento
acumulado de este mismo repo (no del proyecto):

```bash
python scripts/consolidar-patrones.py "<proyecto>/Analisis/Patrones reutilizables.md" --proyecto "<nombre del cliente>"
```

Deja los patrones en `conocimiento/patrones-acumulados.md` y avisa si el
nombre de un patrón nuevo se parece a uno que ya existe, para fundirlos a
mano si son el mismo. Esto es lo que va alimentando una base de
conocimiento propia con el tiempo: la segunda vez que aparece el mismo
patrón en otro vídeo, deja de ser una anécdota de un solo cliente.

## 5 · De ahí al manual

El mapa de vídeo con los tiempos rellenos es la materia prima para elegir
qué capturas sacar y qué protocolos escribir. Sigue con
`de-capturas-a-manual.md`.
