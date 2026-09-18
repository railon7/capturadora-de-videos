# Plantilla de protocolo / manual paso a paso

Cada protocolo se llama `<código> · <nombre del proceso>.md` y sigue esta
estructura, sin saltarse epígrafes:

```markdown
# <código> · <nombre del proceso>

| | |
|---|---|
| **Quién lo hace** | Rol o puesto — nunca un nombre propio |
| **Cuándo** | Diario / al recibir / los viernes / en el cierre |
| **Aplicación** | Qué sistema o pantalla |
| **Ámbito** | A quién aplica (una sociedad, un departamento, todos) |
| **Estado** | 🟡 borrador · 🟠 validado internamente · 🟢 validado por el destinatario |
| **Última revisión** | fecha · quién |

## Para qué sirve
Dos o tres frases. Qué problema resuelve y en qué acaba.

## Antes de empezar
Lo que tiene que existir ya para poder ejecutar este paso a paso. Si falta
algo, dónde se consigue.

## Pasos

### 1 · Título del paso
Qué se hace, en imperativo y en una o dos frases.

![](ruta/a/la/captura/editada.png)
> ① El campo que hay que rellenar · ② El botón que hay que pulsar

### 2 · Título del paso
...

## Qué NO hacer
Los errores que ya se sabe que se van a cometer, con la razón. Aquí va todo
lo que cambia respecto al sistema o la costumbre anterior.

## Si algo sale mal
El caso de error con su salida: cómo se corrige y quién puede corregirlo.

## Decisiones detrás de este procedimiento
Una lista corta de por qué se hace así y no de otra forma, con enlace a
dónde se decidió. Evita que alguien "mejore" el procedimiento sin saber lo
que rompe.
```

## Criterios de redacción

**Se escribe para quien va a ejecutar, no para quien lo ha diseñado.** Nada
de "el sistema permite"; sí "pulsa Generar pedido". Voz activa, imperativo,
frases cortas.

**Un paso es un paso.** Si en un paso hay dos decisiones, son dos pasos. Si
un paso necesita tres párrafos de explicación, esa explicación va a
*Decisiones detrás de este procedimiento*.

**Las capturas no se describen, se anotan.** El texto dice "rellena el
plazo de entrega ①", no "en el campo que aparece en la parte superior
derecha de la pantalla". Numeración circulada ①②③, siempre en el mismo
orden de lectura.

**El apartado "Qué NO hacer" es el que más valor tiene.** Es donde va la
memoria del proyecto — lo que ya se sabe que rompe o que confunde. Sin eso,
el equipo reproduce en el sistema nuevo las costumbres del antiguo.

**Los protocolos hablan de papeles, no de personas.** Uno que nombra a
quien hoy ocupa el puesto caduca el día que esa persona cambia de sitio;
uno que dice "lo hace administración" sigue sirviendo. Un glosario de
roles aparte, y la lista de quién ocupa cada rol hoy vive en documentos
internos, no en el manual.

## Criterios para las capturas

- **Una pantalla por paso**, no una por cada cosa que se vio en el vídeo.
- **Recortar a la zona útil.** Una captura a resolución completa pegada
  entera no se lee en un manual.
- **Tapar cualquier dato identificable de terceros** — nombres, importes,
  datos de contacto reales — aunque el ejemplo del vídeo sea ficticio.
- **Nombre del fichero:** `<código>-<orden>-<descripción>.png`, por ejemplo
  `P02-04-comparativo-proveedores.png`.
- Las originales sin tocar se quedan en `Capturas/Seleccionadas`; las
  recortadas y anotadas van a `Capturas/Editadas`. Nunca se edita sobre la
  original.
- **El nombre se pone después de abrir la captura, no antes.** Extraer con
  el nombre de lo que se espera encontrar es un error que cuesta caro:
  algunas van a contener otra cosa, y el enlace del manual queda roto. El
  orden correcto es **extraer → mirar → renombrar → enlazar**.
- Mantén un inventario vivo de qué contiene cada captura (qué pantalla es,
  a qué paso de qué protocolo alimenta, si falta recortar o anotar).

## Aviso sobre el origen de las capturas

Si el vídeo es una demo con datos de ejemplo (un caso ficticio, una empresa
de prueba), dilo explícitamente en el manual: esas capturas explican el
mecanismo, pero no muestran la configuración real del destinatario. En
cuanto exista un entorno real, las capturas de los protocolos más críticos
se rehacen con datos reales.
