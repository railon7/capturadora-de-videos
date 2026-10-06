---
tipo: conocimiento
titulo: Control documental y nomenclatura
aliases:
  - Document control and naming
fecha: 2026-10-06
tema: documentacion
tags:
  - pkm/conocimiento
  - tema/documentacion
---

# Control documental y nomenclatura

## Lo que pide ISO 9001 y lo que no

- La norma **no fija nombres ni formatos**: solo que cada documento sea fácilmente identificable.
- Lo más práctico, y lo que recomiendan las consultoras, es añadir una referencia como prefijo o sufijo del título.
- El tipo se distingue con un prefijo (SOP para procedimiento, POL para política...). La numeración puede ser
  correlativa o con significado: por ejemplo, `SOP-1007` sería el séptimo procedimiento del departamento 1000.
- Cada documento necesita título, identificador único, fecha y, casi siempre, autor o propietario.

## Campos de la cabecera de control

Según las guías de control de versiones de SOP: número de documento (alfanumérico, con prefijo de departamento o
categoría), versión en formato **mayor.menor** (2.1), fecha efectiva y título. Un cambio importante sube el primer
número; un ajuste menor, el segundo.

## Estados y revisión

- Cuatro estados: borrador, aprobado o activo, obsoleto y en revisión.
- Revisión en un intervalo definido, normalmente **anual**, y se documenta aunque no haya cambios.
- Cada documento importante lleva una **tabla de versiones** con fecha y qué cambió.
- Las versiones antiguas **se archivan y salen del acceso activo**, para que nadie use sin querer un documento caducado.

## Decisiones que se tomaron

| Decisión | Motivo |
|---|---|
| ID `TIPO-ÁMBITO-NNN`, con el ámbito como la aplicación | Se busca por aplicación casi siempre. El prefijo de tipo ordena la carpeta |
| Tres cifras para el número | Ordena bien hasta 999 por tipo y ámbito, que sobra |
| El número no se reutiliza nunca | Un enlace antiguo no puede acabar apuntando a otro documento |
| Versión `"1.0"` entre comillas en el YAML | Sin comillas, `1.10` se lee como `1.1` |
| Aprobado solo desde 1.0, y con revisor y fecha | Un aprobado sin quién lo aprobó no vale como control |
| Obsoleto se mueve a `90-archivo/`, no se borra | Hace falta poder ver qué decía un procedimiento en una fecha |
| Nombre de fichero con ID, slug y idioma | Ordena por tipo, se entiende sin abrirlo y no rompe enlaces con espacios ni símbolos |

## El nombre de fichero

`<ID>_<slug-kebab>.<idioma>.md`, por ejemplo `SOP-HOLDED-003_emitir-factura-rectificativa.es.md`.

- El guion bajo separa el ID del título; los guiones separan palabras del título.
- Minúsculas, sin tildes, la ñ como n, máximo 60 caracteres. Windows y OneDrive tienen un límite de ruta total
  y los nombres largos se comen ese margen.
- El sufijo de idioma va antes de la extensión, como en las convenciones de documentación multilingüe.

## Lo que había antes y por qué se cambia

El protocolo antiguo se llamaba `P-02 · Circuito de compra.md`, con espacios y un punto medio, y sus imágenes
`P02-04-...` (el código sin guion). Tres cosas fallaban: no había un ID único entre clientes, el código se escribía
de dos maneras y el nombre con símbolos complica enlaces y herramientas. `scripts/migrar-protocolo.py` convierte los
existentes sin tocar los originales.
