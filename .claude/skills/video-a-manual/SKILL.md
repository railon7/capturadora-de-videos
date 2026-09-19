---
name: video-a-manual
description: Convierte un vídeo (una demo, una reunión grabada, una formación) en fotogramas navegables, en un guion con marcas de tiempo, en patrones reutilizables y, si hace falta, en un manual paso a paso con capturas limpias. Úsala cuando alguien diga "tengo un vídeo del que sacar capturas", "saca el manual de este vídeo", "procesa esta grabación" o "necesito las imágenes de esta demo".
---

# Vídeo → capturas → guion → manual

Pipeline de cuatro pasos, independientes entre sí: para en el que haga falta.
No asumas que el objetivo final es siempre un manual — a veces solo hacen
falta las imágenes, o solo el guion de lo que se dijo.

```
1. CAPTURAS   scripts/extraer-capturas.ps1   (+ detectar-redundantes.py, opcional)
1bis. CATÁLOGO   scripts/catalogar-capturas.py       (obligatorio, siempre)
2. GUION      metodologia/de-video-a-guion-y-patrones.md  §1-3   (+ generar-borrador-guion.py, opcional)
3. PATRONES   metodologia/de-video-a-guion-y-patrones.md  §4     (+ consolidar-patrones.py)
4. MANUAL     metodologia/de-capturas-a-manual.md   (+ redactar-captura.py OBLIGATORIO, anotar-captura.py, exportar-manual.py)
```

## Antes de nada: ¿qué hace falta de verdad?

Pregunta si no está claro:

- **Solo imágenes** de momentos concretos (para otra cosa, no un manual) →
  pasos 1 y 1bis, y si hacen falta pantallas puntuales en calidad, usa
  `scripts/extraer-captura-puntual.ps1` con el minuto que indique quien pide.
- **Un manual de cliente / protocolo paso a paso** → los cinco pasos.
- **Solo el guion de lo que se dijo**, sin manual → pasos 1, 1bis, 2-3.
- **Patrones o lecciones reutilizables**, sin necesidad de manual → pasos 1,
  1bis, 2-3, centrado en el §4 de `metodologia/de-video-a-guion-y-patrones.md`.

**El paso 1bis no se salta nunca, sea cual sea el destino final.** Sin un
catálogo del contenido, ni la persona ni ningún LLM que retome el trabajo
después sabe qué hay en las capturas sin abrirlas una por una.

## 1 · Extraer capturas

Comprueba que hay un vídeo accesible y localizable, y una carpeta de trabajo
(si no la dan, propón `Capturas-<nombre del video>` junto al vídeo). Ejecuta:

```powershell
scripts/extraer-capturas.ps1 -Video "<ruta al vídeo>" -Trabajo "<carpeta de trabajo>"
```

Parámetros opcionales: `-Intervalo` (segundos entre fotograma, por defecto
20) y `-AnchoMax` (por defecto 1600 px). Un intervalo más corto tiene sentido
si el vídeo cambia de pantalla muy rápido; uno más largo si es una reunión
larga con pocas pantallas. Además:

- `-DeteccionEscena` saca fotogramas extra en cada cambio de pantalla real
  (filtro de escena de ffmpeg), útil si hay transiciones más rápidas que el
  intervalo — van aparte, en `e_HHMMSS.jpg` y `Analisis/indice-escenas.txt`.
- `-SaltarInicioPct` / `-SaltarFinalPct` saltan automáticamente intro/outro.
- `-SoloKeyframes` evita fotogramas borrosos (útil en vídeo HEVC), a cambio
  de que la marca de tiempo del nombre sea aproximada, no exacta.

El script no toca el vídeo original y puede tardar bastante en vídeos
grandes: avisa de que se va a quedar corriendo.

Al terminar hay: `Capturas/Rejilla/` (fotogramas), `Hojas de contactos/`
(mosaicos para navegar) y `Analisis/indice-capturas.txt`.

Si el vídeo es largo, antes de catalogar pasa
`python scripts/detectar-redundantes.py "Capturas/Rejilla"`: avisa de
fotogramas borrosos o casi duplicados en `Analisis/Fotogramas a
revisar.md`, para no perder tiempo describiendo lo que se va a descartar.
Es un aviso, no borra nada — revísalo antes de ignorar algo.

## 1bis · Catalogar el contenido (obligatorio)

```bash
python scripts/catalogar-capturas.py "Capturas/Rejilla"
```

Deja `Analisis/Catalogo de capturas.md` con el texto OCR de cada imagen (si
hay OCR disponible) y una columna "Qué se ve" en blanco. **Complétala** —
mirando las imágenes tú misma/o si puedes, o pidiendo confirmación de qué
se ve — antes de dar el paso por terminado. No la dejes en blanco ni la
sustituyas por el texto OCR sin más: el OCR lee texto de la pantalla, no
dice qué pantalla es. Repite sobre `Capturas/Seleccionadas` y
`Capturas/Editadas` más adelante, cuando existan.

## 2-3 · Guion y patrones

Sigue `metodologia/de-video-a-guion-y-patrones.md` exactamente en su orden:

1. Consigue la transcripción íntegra del vídeo — preferiblemente con
   `python scripts/transcribir.py "<vídeo>" --idioma es` (requiere
   `pip install faster-whisper`), que da marca de tiempo por segmento sola.
   Si no es posible, a mano, pero entonces sin marcas de tiempo automáticas.
2. Si hay transcripción con tiempos y catálogo, genera el borrador con
   `python scripts/generar-borrador-guion.py "Analisis/transcripcion.tsv"
   --catalogo "Analisis/Catalogo de capturas.md"` — ahorra teclear tiempos
   y buscar la pantalla más cercana a mano. **No lo confundas con el mapa
   final**: cada fila es un segmento, no un bloque con sentido, y la
   pantalla sugerida es solo la más cercana en el tiempo.
3. Trocea en bloques y actos con criterio (fundiendo filas del borrador si
   lo hay, o desde cero), con cita literal de cada bloque — usa
   `plantillas/plantilla-mapa-de-video.md`.
4. Si la transcripción trae tiempos (Whisper), cópialos directamente. Si no,
   localízalos recorriendo las hojas de contacto en el mismo orden que los
   bloques del guion — y revisa `Analisis/indice-escenas.txt` si existe.
5. Con el mapa ya completo, haz una segunda lectura buscando qué es
   reutilizable más allá de este vídeo concreto (ver los criterios del §4 de
   la metodología). Escríbelo con `plantillas/plantilla-patrones.md` como
   `Analisis/Patrones reutilizables.md`, y si el proyecto ya está avanzado,
   funde ese fichero en el conocimiento acumulado de este repo con
   `python scripts/consolidar-patrones.py "<ruta>/Analisis/Patrones
   reutilizables.md" --proyecto "<nombre del cliente>"`.

Guarda el mapa como `Analisis/Mapa del video — bloques y pantallas.md`.

**No inventes marcas de tiempo.** Si no se han podido localizar todavía,
la columna se deja vacía — nunca una estimación por proporción del vídeo.

## 4 · Manual

Sigue `metodologia/de-capturas-a-manual.md`. Resumen del orden que importa:

1. Agrupa los bloques del mapa por a qué manual alimentan.
2. Saca cada captura en máxima calidad con `scripts/extraer-captura-puntual.ps1` en
   el momento ya localizado.
3. **Mira la captura antes de ponerle nombre** — nunca al revés. El orden es
   extraer → mirar → renombrar → enlazar.
4. Recorta a la zona útil con cualquier editor de imágenes.
5. **Tapa DNI/CIF/tarjeta/email/teléfono y nombres — obligatorio, por
   protección de datos, antes de anotar.** Si no tienes ya una lista de
   nombres propios y de empresa del proyecto, constrúyela leyendo la
   transcripción/actas (los nombres NO se detectan solos, hace falta la
   lista) y guárdala como `nombres-a-tapar.txt`. Luego:
   `python scripts/redactar-captura.py "<seleccionada>" "<tapada>"
   --nombres "nombres-a-tapar.txt"`.
6. Numera las referencias con círculos sobre la imagen ya tapada — nunca
   antes, para no numerar encima de algo que luego se cubre — con
   `python scripts/anotar-captura.py "<tapada>" "<editada>" --marca
   x1,y1 --marca x2,y2 ...`, un `--marca` por referencia en el orden en que
   el texto del paso las va a citar (la primera es ①). Ni este paso ni el
   anterior tocan nunca la `Seleccionada` original.
7. Escribe el protocolo con `plantillas/plantilla-protocolo.md`, en
   imperativo, un paso por decisión, con su apartado "Qué NO hacer".
8. Antes de entregar, pasa `scripts/auditar-privacidad.py --textos
   "Analisis" --ocr "Capturas/Editadas" --nombres "nombres-a-tapar.txt"`
   como segunda comprobación — no sustituye el paso 5, confirma que no se
   dejó nada sin tapar.
9. Empaqueta el entregable: `pip install markdown` y `python
   scripts/exportar-manual.py "<protocolo>.md"` — deja un HTML autocontenido
   con las imágenes incrustadas, listo para mandar o imprimir a PDF.

## Reglas que no se aflojan

- **Toda imagen capturada se cataloga en un .md.** No basta con el nombre
  por marca de tiempo — sin el catálogo, nadie entiende el contenido sin
  abrir cada imagen. Esto aplica siempre, no solo cuando el destino es un
  manual.
- **El vídeo original no se mueve ni se edita.** Todo lo que sale de él vive
  en la carpeta de trabajo; el vídeo se queda donde estaba.
- **Cita literal, no resumen**, al trocear el guion — el resumen no se puede
  volver a localizar en la transcripción ni reconocer en una hoja de
  contacto.
- **DNI, CIF, nombres propios y de empresa no pueden aparecer en una
  captura del manual — es ley de protección de datos, no estilo.** Lo
  verificable (DNI/CIF/tarjeta/email/teléfono) se tapa solo con
  `redactar-captura.py`; los nombres necesitan la lista `--nombres`, que
  alguien tiene que rellenar a mano — no des el paso por hecho solo porque
  el script corrió sin la lista.
- **Sin nombres de personas** en un manual que vaya a un destinatario externo,
  salvo que se confirme expresamente — usa roles ("administración",
  "compras"), no nombres propios.
- **El nombre del fichero se pone después de mirar la captura.** Es el error
  que más revisión cuesta cuando se salta.

Termina indicando en qué paso del pipeline se ha quedado el trabajo y cuál
es la siguiente acción concreta.

---

*Skill v1.4 · repositorio Capturadora de Vídeos*
