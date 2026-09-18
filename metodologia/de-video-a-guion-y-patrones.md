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
│   ├─ Seleccionadas/    Las pantallas que valen para el manual, en máxima calidad
│   └─ Editadas/         Las mismas, recortadas y anotadas
├─ Hojas de contactos/   Mosaicos de 20 fotogramas para navegar el vídeo de un vistazo
└─ Analisis/             video-info.txt, indice-capturas.txt, y el mapa del vídeo
```

El vídeo original no se mueve ni se edita. Todo lo que sale de él vive en
esta carpeta; el manual terminado, si lo hay, es un entregable y va aparte.

## 1 · Consigue la transcripción íntegra

Este paso no lo hace un script: se hace escuchando el vídeo (o pasándolo por
un transcriptor) de principio a fin. Hace falta el texto completo, no un
resumen — el resumen se construye después, a partir del texto, y si se salta
este paso se pierden los fragmentos literales que luego sirven para localizar
el momento exacto en las hojas de contacto.

## 2 · Trocea en bloques y actos — el mapa del vídeo

Con la transcripción completa delante, una sola pasada de principio a fin:

1. Corta en **bloques**: cada vez que cambia el tema, la pantalla o quien
   habla. Un bloque es tan corto como haga falta — a veces es una frase.
2. Agrupa los bloques en **actos**: la unidad más grande con sentido propio
   (p. ej. "presupuesto", "compras", "cierre contable").
3. Para cada bloque, anota una **cita literal**, no un resumen. Un resumen no
   se puede buscar después en la transcripción ni reconocer en una hoja de
   contacto; una frase textual sí.
4. Deja la columna de marca de tiempo **vacía** en esta pasada. Se rellena
   después, mirando las hojas de contacto o el índice — nunca por memoria ni
   por proporción estimada del vídeo.

Usa `plantillas/plantilla-mapa-de-video.md` y guarda el resultado como
`Analisis/Mapa del video — bloques y pantallas.md`.

## 3 · Localiza los tiempos

Con el mapa de bloques ya escrito, recorre las hojas de contacto: la
secuencia de bloques es el guion, así que el bloque 2 está por la hoja 01, el
5 por la 02, y así sucesivamente. En cuanto se ubican tres o cuatro bloques,
el resto se sitúa solo por proximidad.

Fórmula para traducir una miniatura de una hoja a segundo exacto:

```
índice = (nº de hoja − 1) × 20 + posición-en-la-hoja
segundo = (índice − 1) × intervalo
```

Con los tiempos localizados, ya se puede pedir la captura en máxima calidad
con `scripts/extraer-captura-puntual.ps1` en lugar de conformarse con el
fotograma de rejilla.

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
aplicaría en general. Este documento — los patrones — es el que va
alimentando una base de conocimiento propia con el tiempo: la segunda vez
que aparece el mismo patrón en otro vídeo, dejó de ser una anécdota.

## 5 · De ahí al manual

El mapa de vídeo con los tiempos rellenos es la materia prima para elegir
qué capturas sacar y qué protocolos escribir. Sigue con
`de-capturas-a-manual.md`.
