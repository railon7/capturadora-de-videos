# Prompt listo para Claude Code

Abre Claude Code en tu carpeta de proyecto (donde ya instalaste la skill) y copia/pega uno de estos prompts en el chat.

---

## "Tengo un vídeo y quiero empezar el flujo"

```
Tengo un vídeo de una demo/reunión grabada que quiero procesar.
El vídeo está en: [RUTA AL VIDEO]
La carpeta de trabajo está en: [RUTA CARPETA DE TRABAJO]
Quiero: fotogramas catalogados, guion, y manual con capturas anotadas.

¿Qué pasos doy primero? Guíame paso a paso.
```

Claude usará la skill `/video-a-manual` automáticamente.

---

## "Los vídeos están en YouTube"

```
Tengo estos vídeos en YouTube (son nuestros / del cliente / tengo permiso):
[Nombre = URL, uno por línea]

Descárgalos en: [RUTA CARPETA]
y luego pásalos por la capturadora: fotogramas, transcripción y una ficha de conocimiento.
```

Claude usará `scripts/descargar-videos.py` para bajarlos y seguirá con el flujo normal.

---

## "Solo quiero fotogramas navegables"

```
Tengo un vídeo que quiero convertir en fotogramas navegables cada 20 segundos.
El vídeo está en: [RUTA AL VIDEO]
Carpeta de trabajo: [RUTA CARPETA DE TRABAJO]

¿Cómo extraigo fotogramas y los catalogo?
```

---

## "Tengo fotogramas, ahora quiero un guion"

```
Ya tengo fotogramas extraídos en: Trabajo/Capturas/Rejilla/
Y el catálogo en: Trabajo/Analisis/Catalogo de capturas.md

El vídeo está en: [RUTA AL VIDEO]

Quiero: transcripción, primer borrador del guion, y que me ayudes a trocear en bloques.

¿Por dónde empiezo?
```

---

## "Estoy en el paso de anotación, necesito ayuda"

```
Tengo un protocolo casi terminado. Necesito:
1. Redactar (tapar) datos sensibles en las capturas
2. Anotar con círculos numerados
3. Auditar privacidad antes de entregar

El vídeo tenía estos nombres: [LISTA DE NOMBRES]
Las capturas sin redactar están en: Trabajo/Capturas/Seleccionadas/
El protocolo está en: 08-Formacion/P-01-Compras.md

Guíame por los pasos, command by command.
```

---

## "Voy a procesar múltiples vídeos, dame workflow"

```
Voy a procesar 5 vídeos de demos diferentes, todos con clientes distintos.

Quiero un workflow que:
- Extraiga fotogramas de cada vídeo con nombres consistentes
- Genere el catálogo automáticamente
- Me guíe en la parte manual (troceado, redacción)
- Me avise si encuentro patrones reutilizables

¿Me describes los pasos y los comandos exactos para cada vídeo?
Vídeos:
1. Demo ClienteA: [ruta]
2. Demo ClienteB: [ruta]
3. etc.
```

---

## "Tengo un manual terminado, quiero exportarlo"

```
Tengo un manual escrito en Markdown en: 08-Formacion/P-01-Procedimiento.md

Quiero:
1. Empaquetarlo en un HTML autocontenido (con imágenes incrustadas)
2. Que se vea profesional
3. Poder imprimirlo a PDF desde el navegador

¿Cómo lo hago?
```

---

## "Descubrí patrones reutilizables, quiero compartirlos"

```
En este vídeo de ClienteX descubrí varias formas de hacer cosas que 
podrían servir en futuros proyectos.

Archivos relevantes:
- Trabajo/Analisis/Patrones reutilizables.md (ya escrito, con plantilla)
- Vídeo analizado: [descripción breve]
- Conceptos clave: [lista de patrones]

¿Cómo fundo esto en la base de conocimiento acumulada del repo?
¿El sistema detecta si hay patrones similares ya registrados?
```

---

## "La próxima vez que use esto, ¿cómo lo instalo en un proyecto nuevo?"

```
¿Cómo instalo la herramienta "Capturadora de Vídeos" en un proyecto nuevo?

Tengo:
- La herramienta en: C:\...\Capturadora de Videos (el repo)
- Proyecto nuevo en: C:\Proyectos\ClienteNuevo

Pasos exactos, por favor.
```

---

## Tips

- **Siempre llama a la skill por nombre** — escribir `/video-a-manual` en el chat la invoca explícitamente.
- **Usa rutas absolutes** — relativas confunden. Ejemplo: `C:\Users\tu-usuario\OneDrive - Nanopyme SL\Implantaciones Tazuke\Tu-Proyecto\Trabajo`
- **Pon el nombre del cliente** — ayuda a Claude a mantener contexto.
- **Si algo falla, copia el error completo** — el script te lo dirá si falta algo (Tesseract, Whisper, etc.).
- **Comparte el paso anterior si empiezas a mitad** — "ya tengo fotogramas" es útil; "aquí está el catálogo" es mejor.

---

## Qué pasa después

Claude va a:
1. **Entender qué quieres** — fotogramas, guion, manual, o los tres
2. **Guiarte paso a paso** — comando por comando
3. **Ejecutar los scripts** — directamente desde Claude Code
4. **Revisar resultados** — mirar el catálogo, el borrador del guion, etc.
5. **Ajustar si hace falta** — si el OCR no lee bien, si le falta una pantalla, etc.

No tienes que estar pendiente. Claude te dirá cuándo pasar al siguiente paso.
