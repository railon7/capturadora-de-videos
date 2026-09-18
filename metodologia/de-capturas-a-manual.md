# De capturas a manual

Cómo pasar de "ya sé en qué momento está cada pantalla" (el mapa del vídeo,
con sus tiempos) a un manual paso a paso terminado.

## 1 · Decide qué manuales hacen falta

No se escribe un manual por vídeo: se escribe uno por proceso que alguien
tenga que ejecutar sin haber visto el vídeo. Agrupa los bloques del mapa por
la columna "Destino" (ver `plantilla-mapa-de-video.md`) y verás los
protocolos que se forman solos.

Si hay muchos, ordénalos por lo que bloquea antes: primero los procesos de
mayor volumen o los que son condición para arrancar algo, después el resto.

## 2 · Saca las capturas en máxima calidad

Con los tiempos ya localizados en el mapa del vídeo:

```powershell
.\scripts\extraer-captura-puntual.ps1 -Video "<vídeo>" -Momento "00:45:20" -Salida "Capturas\Seleccionadas\<nombre-provisional>.png"
```

**Una pantalla por paso del procedimiento**, no una por cada cosa que se vio
en el vídeo. Si un paso necesitaría dos capturas para explicarse, puede que
en realidad sean dos pasos.

## 3 · Mira antes de nombrar

**El nombre se pone después de abrir la captura, no antes.** Extraer con el
nombre de lo que se espera encontrar es un error que sale caro: algunas
capturas van a contener otra cosa de la que se pensaba, y si ya está
enlazada en el manual con ese nombre, el enlace queda roto sin que se note
hasta la revisión. El orden es siempre:

**extraer → mirar → renombrar → enlazar**

Nombra con `<código-de-protocolo>-<orden>-<descripción>.png`.

## 4 · Recorta y anota

Las originales sin tocar se quedan en `Capturas/Seleccionadas`; el recorte y
la anotación van a una copia en `Capturas/Editadas`. Nunca se edita sobre la
original — si hace falta rehacer el recorte, se parte de nuevo de la
seleccionada.

- Recorta a la zona útil de la pantalla: una captura completa a resolución
  alta no se lee dentro de un manual. El recorte se hace con cualquier
  editor de imágenes — no hay script para esto, es una decisión de
  encuadre que no merece la pena automatizar.
- **Tapa cualquier dato identificable de terceros** — DNI, CIF, nombre real,
  importe, contacto — aunque el ejemplo del vídeo sea ficticio. Es
  obligatorio por protección de datos, no una recomendación de estilo.
  `scripts/redactar-captura.py` lo automatiza en parte:

  ```bash
  python scripts/redactar-captura.py "Capturas/Seleccionadas/P02-04.png" "Capturas/Editadas/P02-04-tapada.png" --nombres "nombres-a-tapar.txt"
  ```

  DNI, NIE, CIF, tarjeta, email y teléfono se detectan solos (tienen dígito
  de control verificable). **Los nombres propios y de empresa no** — van en
  `nombres-a-tapar.txt` (uno por línea), que rellena quien conoce los
  nombres reales del vídeo: mira la transcripción, el acta o el propio
  vídeo y anota qué personas y empresas aparecen. **Esto no es una
  garantía legal por sí solo**: el script avisa de lo que ha tapado, pero
  revisa la imagen de todas formas antes de darla por buena — el OCR
  puede fallar, sobre todo con letra pequeña o mala resolución.
- Numera las referencias con círculos en el mismo orden en que el texto del
  paso las menciona, con `scripts/anotar-captura.py`, **a partir de la
  imagen ya tapada** (nunca antes: numerar antes de tapar arriesga a que el
  círculo tape justo lo que había que numerar):

  ```bash
  python scripts/anotar-captura.py "Capturas/Editadas/P02-04-tapada.png" "Capturas/Editadas/P02-04.png" --marca 120,80 --marca 300,200
  ```

  El primer `--marca` es el círculo ①, el segundo el ②, y así sucesivamente
  — en el mismo orden en que el texto los va a citar. `P02-04.png` (sin
  "-tapada") es la versión definitiva; el intermedio se puede borrar
  después. Ningún script apunta nunca a `Seleccionadas` como salida: las
  dos se niegan salvo `--forzar`, precisamente para no perder la original
  si el resultado no convence.

## 5 · Escribe el protocolo

Con `plantillas/plantilla-protocolo.md`. El texto referencia las capturas
por su numeración circulada ("rellena el plazo de entrega ①"), no las
describe ("en el campo de la parte superior derecha"). El apartado **Qué NO
hacer** es el que más vale: ahí va todo lo que ya se sabe que confunde o que
cambia respecto a la costumbre anterior — sin eso, quien lea el manual
reproduce los hábitos del sistema viejo en el nuevo.

## 6 · Mantén el inventario

Un fichero vivo (`Analisis/Estado de las capturas.md` o similar) con a qué
protocolo y paso alimenta cada captura seleccionada, y si le falta recortar,
anotar o revisar. Cuando el número de capturas pasa de una docena, sin este
inventario se pierde la cuenta de qué falta.

Esto es distinto del `Analisis/Catalogo de capturas.md` del §0bis de
`de-video-a-guion-y-patrones.md`: aquél describe **qué se ve** en cada
imagen capturada del vídeo (para entender el contenido sin abrirlas); este
inventario dice **para qué sirve** cada una de las ya seleccionadas para el
manual. Actualiza el catálogo si recortas/editas una imagen y cambia lo que
se ve en ella (por ejemplo, al tapar un dato).

## 7 · Auditoría de privacidad automática (opcional, antes de entregar)

Antes de mandar el manual o las capturas seleccionadas a alguien fuera del
equipo, `scripts/auditar-privacidad.py` da una segunda opinión automática
además de la revisión a ojo del paso 4 — esto es para comprobar que el
tapado del paso 4 no dejó nada, no un sustituto de `redactar-captura.py`:

```bash
# Rápido, sin dependencias: busca email / teléfono / DNI-NIE-CIF / tarjeta
# en la transcripción, el mapa del vídeo y demás texto de Analisis/
python scripts/auditar-privacidad.py --textos "Analisis" --nombres "nombres-a-tapar.txt"

# Más lento (varios segundos por imagen): pasa cada captura por OCR y
# busca lo mismo en el texto que aparece EN la pantalla capturada
python scripts/auditar-privacidad.py --ocr "Capturas/Editadas" --nombres "nombres-a-tapar.txt"
```

Deja un informe (`aviso-privacidad.md`) con los hallazgos enmascarados. Usa
el mismo `nombres-a-tapar.txt` que `redactar-captura.py`, así que si algo
sale en este informe sobre `Capturas/Editadas` es que el tapado se saltó
algo — revísalo antes de entregar. Es un aviso heurístico, no una garantía:
sin `--nombres` no detecta nombres propios ni de empresa, y no detecta
importes sin formato reconocible. No sustituye la revisión humana del
paso 4 — la complementa.

## 8 · Empaqueta el entregable

El protocolo vive como Markdown + imágenes sueltas mientras se escribe —
así se edita mejor — pero eso no es lo que se le manda a alguien fuera del
equipo, porque las rutas relativas a las imágenes se rompen en cuanto el
fichero sale de su carpeta. `scripts/exportar-manual.py` empaqueta las dos
cosas en un único HTML, con las imágenes incrustadas:

```bash
pip install markdown
python scripts/exportar-manual.py "08-Formacion/P-02 · Circuito de compra.md"
```

El HTML resultante se abre en cualquier navegador tal cual, y desde ahí se
imprime a PDF (Ctrl+P → Guardar como PDF) si hace falta ese formato. Con
`--pdf` intenta generarlo directamente vía `pandoc`, si está instalado —
si no lo encuentra, no es un error: el HTML ya es un entregable válido por
sí solo.

## Cuando las capturas son de un entorno de ejemplo

Si el vídeo muestra una demo o un entorno de prueba con datos inventados,
dilo explícitamente en el manual (por ejemplo, en la cabecera o en una nota
al principio): esas capturas explican el mecanismo, no la configuración real
del destinatario final. En cuanto exista un entorno real, las capturas de
los protocolos más críticos se rehacen con datos reales — las del vídeo de
ejemplo se quedan solo donde lo que importa es explicar el concepto.
