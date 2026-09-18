---
name: video-a-manual
description: Convierte un vídeo (una demo, una reunión grabada, una formación) en fotogramas navegables, en un guion con marcas de tiempo, en patrones reutilizables y, si hace falta, en un manual paso a paso con capturas limpias. Úsala cuando alguien diga "tengo un vídeo del que sacar capturas", "saca el manual de este vídeo", "procesa esta grabación" o "necesito las imágenes de esta demo".
---

# Vídeo → capturas → guion → manual

Pipeline de cuatro pasos, independientes entre sí: para en el que haga falta.
No asumas que el objetivo final es siempre un manual — a veces solo hacen
falta las imágenes, o solo el guion de lo que se dijo.

```
1. CAPTURAS   scripts/extraer-capturas.ps1
2. GUION      metodologia/de-video-a-guion-y-patrones.md  §1-3
3. PATRONES   metodologia/de-video-a-guion-y-patrones.md  §4
4. MANUAL     metodologia/de-capturas-a-manual.md
```

## Antes de nada: ¿qué hace falta de verdad?

Pregunta si no está claro:

- **Solo imágenes** de momentos concretos (para otra cosa, no un manual) →
  paso 1, y si hacen falta pantallas puntuales en calidad, usa
  `extraer-captura-puntual.ps1` con el minuto que indique quien pide.
- **Un manual de cliente / protocolo paso a paso** → los cuatro pasos.
- **Solo el guion de lo que se dijo**, sin manual → pasos 1-3.
- **Patrones o lecciones reutilizables**, sin necesidad de manual → pasos 1-3,
  centrado en el §4 de `de-video-a-guion-y-patrones.md`.

## 1 · Extraer capturas

Comprueba que hay un vídeo accesible y localizable, y una carpeta de trabajo
(si no la dan, propón `Capturas-<nombre del video>` junto al vídeo). Ejecuta:

```powershell
.\scripts\extraer-capturas.ps1 -Video "<ruta al vídeo>" -Trabajo "<carpeta de trabajo>"
```

Parámetros opcionales: `-Intervalo` (segundos entre fotograma, por defecto
20) y `-AnchoMax` (por defecto 1600 px). Un intervalo más corto tiene sentido
si el vídeo cambia de pantalla muy rápido; uno más largo si es una reunión
larga con pocas pantallas.

El script no toca el vídeo original y puede tardar bastante en vídeos
grandes: avisa de que se va a quedar corriendo.

Al terminar hay: `Capturas/Rejilla/` (fotogramas), `Hojas de contactos/`
(mosaicos para navegar) y `Analisis/indice-capturas.txt`.

## 2-3 · Guion y patrones

Sigue `metodologia/de-video-a-guion-y-patrones.md` exactamente en su orden:

1. Consigue la transcripción íntegra del vídeo (no un resumen).
2. Trocéala en bloques y actos, con cita literal de cada bloque — usa
   `plantillas/plantilla-mapa-de-video.md` — y **sin rellenar todavía los
   tiempos**.
3. Localiza los tiempos recorriendo las hojas de contacto en el mismo orden
   que los bloques del guion.
4. Con el mapa ya completo, haz una segunda lectura buscando qué es
   reutilizable más allá de este vídeo concreto (ver los criterios del §4 de
   la metodología) y anótalo aparte.

Guarda el mapa como `Analisis/Mapa del video — bloques y pantallas.md`.

**No inventes marcas de tiempo.** Si no se han podido localizar todavía,
la columna se deja vacía — nunca una estimación por proporción del vídeo.

## 4 · Manual

Sigue `metodologia/de-capturas-a-manual.md`. Resumen del orden que importa:

1. Agrupa los bloques del mapa por a qué manual alimentan.
2. Saca cada captura en máxima calidad con `extraer-captura-puntual.ps1` en
   el momento ya localizado.
3. **Mira la captura antes de ponerle nombre** — nunca al revés. El orden es
   extraer → mirar → renombrar → enlazar.
4. Recorta a la zona útil y numera las referencias con círculos (①②③) en
   una copia; la original no se toca.
5. Escribe el protocolo con `plantillas/plantilla-protocolo.md`, en
   imperativo, un paso por decisión, con su apartado "Qué NO hacer".

## Reglas que no se aflojan

- **El vídeo original no se mueve ni se edita.** Todo lo que sale de él vive
  en la carpeta de trabajo; el vídeo se queda donde estaba.
- **Cita literal, no resumen**, al trocear el guion — el resumen no se puede
  volver a localizar en la transcripción ni reconocer en una hoja de
  contacto.
- **Tapa cualquier dato identificable de terceros** en las capturas del
  manual, aunque el vídeo sea de un entorno de ejemplo.
- **Sin nombres de personas** en un manual que vaya a un destinatario externo,
  salvo que se confirme expresamente — usa roles ("administración",
  "compras"), no nombres propios.
- **El nombre del fichero se pone después de mirar la captura.** Es el error
  que más revisión cuesta cuando se salta.

Termina indicando en qué paso del pipeline se ha quedado el trabajo y cuál
es la siguiente acción concreta.

---

*Skill v1.0 · repositorio Capturadora de Vídeos*
