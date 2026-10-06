---
tipo: conocimiento
titulo: Documentación bilingüe español e inglés
aliases:
  - Bilingual documentation, Spanish and English
fecha: 2026-10-06
tema: documentacion
tags:
  - pkm/conocimiento
  - tema/documentacion
---

# Documentación bilingüe ES-EN

## Lo que dicen las convenciones

- Para documentación como código, el patrón común es un **sufijo de idioma en el nombre del fichero**:
  `api.md` y `api.zh.md`, y el sitio enruta cada idioma.
- Los códigos de idioma (BCP 47) se mantienen **lo más cortos posible**: `es` y `en`, sin región, salvo que la
  región aporte algo (`es-MX`).
- Cada fichero debe tener un nombre único y descriptivo; evitar esquemas donde varios ficheros comparten el mismo
  nombre base sin marca de idioma.
- En Obsidian, un **alias** es un nombre alternativo de la nota: sirve para siglas, apodos o el nombre en otro idioma.
  Es la pieza que hace buscable en inglés una nota titulada en español.
- Las guías de propiedades de Obsidian recomiendan claves en kebab-case, plurales para listas y singulares para
  valores únicos, y apuntar las convenciones en una nota del propio vault. Para vaults multilingües sugieren claves
  en inglés.

## Decisiones

| Decisión | Motivo |
|---|---|
| Mismo ID en los dos idiomas | La pareja se reconoce a simple vista y un enlace por ID vale para los dos |
| `<ID>_<slug>.<idioma>.md`, con `es` o `en` | Sufijo corto antes de la extensión, que es lo habitual en documentación multilingüe |
| Título en el otro idioma como `aliases` | Se encuentra buscando en cualquiera de los dos |
| Campo `traduccion` en ambos ficheros | Navegación y validación en los dos sentidos |
| `traduccion_estado`: pendiente, borrador-ia, revisada | La traducción automática se distingue de la revisada por una persona |
| Claves del frontmatter en español | Las fichas `00_Index_*` del orquestador PKM ya usan `tipo`, `cliente`, `estado`. Mezclar idiomas en las claves sería peor que ir en contra de la recomendación general |
| El español primero, el inglés derivado | Las capturas, los vídeos y los clientes son en español |
| Traducir solo lo que lo necesite | El coste de mantener la pareja al día es real; el validador avisa si se desfasan |

## Terminología

Un documento bilingüe es tan bueno como su glosario. Dos reglas:

1. **Un término preferido por concepto** en cada idioma, recogido en el glosario `GLO` (columnas español e inglés).
2. **Los nombres de pantallas, menús y botones se traducen como los llama la interfaz de la aplicación** en ese idioma,
   no como suenen mejor. Si la aplicación no existe en inglés, el término original va entre comillas.

La plantilla `GLO` sigue la idea del "terminology system" y del "glossary" de The Good Docs Project.

## Flujo

1. Se escribe y aprueba la versión española.
2. `nuevo-documento.py --titulo-en` deja la pareja creada con los encabezados en inglés y `pendiente`.
3. Claude traduce siguiendo el glosario, sin añadir ni quitar contenido, y la deja en `borrador-ia`.
4. Una persona la revisa y la marca `revisada`.
5. Si cambia el español, la inglesa queda desfasada y el validador lo dice.

## Lo que no se resolvió

- Las capturas con texto de interfaz: si la aplicación se usa en español, no hay captura "en inglés" que hacer. Se
  comparte la imagen y se anota en el texto qué dice cada elemento.
- Un tercer idioma: la estructura lo admite (el sufijo y la lista `IDIOMAS` de `scripts/biblioteca.py`), pero hoy
  solo hay dos y el validador solo acepta esos.
