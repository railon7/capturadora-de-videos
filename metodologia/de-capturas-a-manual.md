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
  alta no se lee dentro de un manual.
- Tapa cualquier dato identificable de terceros — nombre real, importe,
  contacto — aunque el ejemplo del vídeo sea ficticio.
- Numera las referencias con círculos (①②③) en el mismo orden en que el
  texto del paso las menciona.

## 5 · Escribe el protocolo

Con `plantillas/plantilla-protocolo.md`. El texto referencia las capturas
por su numeración circulada ("rellena el plazo de entrega ①"), no las
describe ("en el campo de la parte superior derecha"). El apartado **Qué NO
hacer** es el que más vale: ahí va todo lo que ya se sabe que confunde o que
cambia respecto a la costumbre anterior — sin eso, quien lea el manual
reproduce los hábitos del sistema viejo en el nuevo.

## 6 · Mantén el inventario

Un fichero vivo (`Analisis/Estado de las capturas.md` o similar) con qué
contiene cada captura, a qué protocolo y paso alimenta, y si le falta
recortar, anotar o revisar. Cuando el número de capturas pasa de una
docena, sin este inventario se pierde la cuenta de qué falta.

## 7 · Auditoría de privacidad automática (opcional, antes de entregar)

Antes de mandar el manual o las capturas seleccionadas a alguien fuera del
equipo, `scripts/auditar-privacidad.py` da una segunda opinión automática
además de la revisión a ojo del paso 4:

```bash
# Rápido, sin dependencias: busca email / teléfono / DNI-NIE / tarjeta en
# la transcripción, el mapa del vídeo y demás texto de Analisis/
python scripts/auditar-privacidad.py --textos "Analisis"

# Más lento (varios segundos por imagen): pasa cada captura por OCR y
# busca lo mismo en el texto que aparece EN la pantalla capturada
python scripts/auditar-privacidad.py --ocr "Capturas/Editadas"
```

Deja un informe (`aviso-privacidad.md`) con los hallazgos enmascarados. Es
un aviso heurístico, no una garantía: no detecta nombres propios ni
importes sin formato reconocible, y puede dar algún falso positivo. No
sustituye la revisión humana del paso 4 — la complementa para el caso en
que a alguien se le pase un dato en una captura con mucho texto.

## Cuando las capturas son de un entorno de ejemplo

Si el vídeo muestra una demo o un entorno de prueba con datos inventados,
dilo explícitamente en el manual (por ejemplo, en la cabecera o en una nota
al principio): esas capturas explican el mecanismo, no la configuración real
del destinatario final. En cuanto exista un entorno real, las capturas de
los protocolos más críticos se rehacen con datos reales — las del vídeo de
ejemplo se quedan solo donde lo que importa es explicar el concepto.
