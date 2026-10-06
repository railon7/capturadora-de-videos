# Criterios de redacción de SOP y guías de usuario

Antes de la v1.7 de la skill este fichero era la plantilla única del "protocolo paso a paso", con su propia tabla
de metadatos y su nombre `<código> · <nombre del proceso>.md`. Ahora hay **diez tipos de documento** con su plantilla
en `plantillas/biblioteca/` (MAN, GUI, SOP, TUT, QSG, FAQ, GLO, NOV, DEC, PAT), y los documentos se crean con
`scripts/nuevo-documento.py`, que les da ID, nombre en kebab-case y frontmatter:

```bash
python scripts/nuevo-documento.py --tipo SOP --aplicacion Holded --titulo "Emitir factura rectificativa" \
    --cliente "ClienteX" --biblioteca "ClienteX/Biblioteca"
```

El "protocolo" de antes es ahora un **SOP** (procedimiento del equipo del cliente, con responsable y registro) o una
**GUI** (guía para el usuario final). La estructura de cada uno está en `plantillas/biblioteca/SOP.md` y `GUI.md`.
Los protocolos que ya existen en el formato antiguo se pasan con `scripts/migrar-protocolo.py`.

Lo que sigue son los criterios de redacción y de capturas, que valen para SOP, GUI y TUT. Las plantillas los
llevan resumidos en sus comentarios GUÍA.

## Criterios de redacción

**Se escribe para quien va a ejecutar, no para quien lo ha diseñado.** Nada
de "el sistema permite"; sí "pulsa Generar pedido". Voz activa, imperativo,
frases cortas.

**Un paso es un paso.** Si en un paso hay dos decisiones, son dos pasos. Si
un paso necesita tres párrafos de explicación, esa explicación va a
*Decisiones detrás de este procedimiento* (SOP) o a un manual de aplicación (MAN) al que se enlaza.

**Las capturas no se describen, se anotan.** El texto dice "rellena el
plazo de entrega ①", no "en el campo que aparece en la parte superior
derecha de la pantalla". Numeración circulada ①②③, siempre en el mismo
orden de lectura.

**El apartado "Qué NO hacer" es el que más valor tiene.** Es donde va la
memoria del proyecto — lo que ya se sabe que rompe o que confunde. Sin eso,
el equipo reproduce en el sistema nuevo las costumbres del antiguo.

**Los documentos hablan de papeles, no de personas.** Uno que nombra a
quien hoy ocupa el puesto caduca el día que esa persona cambia de sitio;
uno que dice "lo hace administración" sigue sirviendo. Un glosario de
roles aparte, y la lista de quién ocupa cada rol hoy vive en documentos
internos, no en el manual.

**Se enlaza, no se copia.** Si lo que hay que explicar ya está en el manual de la aplicación (MAN) o en una FAQ,
se enlaza. Un mismo contenido en dos sitios acaba diciendo dos cosas distintas.

**Un documento, un tipo.** Una guía no enseña desde cero (eso es un tutorial) ni describe la aplicación entera
(eso es un manual). Si pide las dos cosas, son dos documentos.

## Criterios para las capturas

- **Una pantalla por paso**, no una por cada cosa que se vio en el vídeo.
- **Recortar a la zona útil.** Una captura a resolución completa pegada
  entera no se lee en un manual.
- **Tapar cualquier dato identificable de terceros** — nombres, importes,
  datos de contacto reales — aunque el ejemplo del vídeo sea ficticio.
- **Nombre del fichero:** `<ID>-<NN>-<descripcion>.png`, por ejemplo
  `SOP-HOLDED-003-04-comparativo-proveedores.png`. El ID es el del documento al que alimenta, con su
  prefijo de tipo. Las definitivas van en `_img/` junto al documento.
- Las originales sin tocar se quedan en `Capturas/Seleccionadas`; las
  recortadas y anotadas van a `Capturas/Editadas`. Nunca se edita sobre la
  original.
- **El nombre se pone después de abrir la captura, no antes.** Extraer con
  el nombre de lo que se espera encontrar es un error que cuesta caro:
  algunas van a contener otra cosa, y el enlace del manual queda roto. El
  orden correcto es **extraer → mirar → renombrar → enlazar**.
- Mantén un inventario vivo de qué contiene cada captura (qué pantalla es,
  a qué paso de qué documento alimenta, si falta recortar o anotar).

## Aviso sobre el origen de las capturas

Si el vídeo es una demo con datos de ejemplo (un caso ficticio, una empresa
de prueba), dilo explícitamente en el documento: esas capturas explican el
mecanismo, pero no muestran la configuración real del destinatario. En
cuanto exista un entorno real, las capturas de los documentos más críticos
se rehacen con datos reales.
