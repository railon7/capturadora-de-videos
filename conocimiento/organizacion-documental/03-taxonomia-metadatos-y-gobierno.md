---
tipo: conocimiento
titulo: Taxonomía, metadatos y gobierno
aliases:
  - Taxonomy, metadata and governance
fecha: 2026-10-06
tema: documentacion
tags:
  - pkm/conocimiento
  - tema/documentacion
---

# Taxonomía, metadatos y gobierno

Las cifras de esta nota vienen de blogs de proveedores de software de gestión del conocimiento. Son una guía de
orden de magnitud, no medidas independientes.

## Jerarquía para navegar, facetas para filtrar

El enfoque que recomiendan es híbrido:

| Capa | Para qué | Límite |
|---|---|---|
| Jerarquía de carpetas | Explorar y orientarse | De 5 a 9 categorías de primer nivel, 3 o 4 niveles como mucho |
| Facetas (metadatos) | Filtrar sin forzar categorías artificiales | Dimensiones independientes: producto, audiencia, región, idioma, tipo de contenido |

Una faceta evita duplicar un documento en dos carpetas: la guía de un cliente para una aplicación no vive "en el
cliente" y "en la aplicación", vive en un sitio y se filtra por los dos campos. Los proveedores citan tasas de éxito
de búsqueda superiores al 85 % con taxonomías híbridas.

## Esquema de metadatos

Campos estructurados en cada documento, porque son los que alimentan la búsqueda, los informes y los asistentes de IA:

- **Clasificación**: producto o aplicación, tipo de contenido, audiencia, región o idioma.
- **Ciclo de vida**: creado por, fecha de revisión, fecha de caducidad, etapa.
- **Acceso**: a quién va dirigido y si hay restricciones.

Etiquetas útiles: tema, audiencia o rol, mercado, producto, fase del flujo, tipo de contenido y fecha de revisión.

## Vocabulario controlado

Tres piezas: **términos preferidos con sinónimos** (WiFi como preferido, y "wireless" o "WLAN" apuntando a él),
**notas de alcance** que dicen qué incluye cada categoría, y **referencias cruzadas** entre categorías relacionadas.
En la biblioteca eso es el glosario `GLO-GEN-001` y los `aliases` de Obsidian.

## Gobierno: tres roles

| Rol | Hace |
|---|---|
| Propietario de la taxonomía | Aprueba cambios estructurales y resuelve conflictos |
| Curadores de categoría | Mantienen un área y afinan su vocabulario |
| Colaboradores | Etiquetan con las opciones existentes, sin inventar dimensiones nuevas |

Sin esta estructura, las fuentes estiman que la taxonomía se degrada en 6 a 12 meses.

## Rutina de mantenimiento

| Cuándo | Qué |
|---|---|
| Cada mes | Revisar qué se busca y no se encuentra |
| Cada trimestre | Auditar categorías, quitar las vacías |
| Cada año | Revisión estratégica según cambios del negocio |
| Por evento | Lanzamientos, nuevas versiones de una aplicación, incorporaciones |

## Cómo se aplicó

- Primer nivel de la biblioteca común: `00-gobierno`, `10-aplicaciones`, `40-patrones`, `90-archivo`. Cuatro carpetas;
  hay hueco (20 y 30) para crecer sin renumerar.
- Dentro de cada aplicación no hay subcarpetas por tipo: el prefijo del ID ordena y el campo `tipo` filtra.
- Frontmatter con clasificación (`tipo`, `aplicacion`, `cliente`, `audiencia`, `idioma`), ciclo de vida (`creado`,
  `revisado`, `proxima_revision`, `estado`, `version`) y trazabilidad (`origen`, `fuente_video`).
- `00_Registro.md`, generado, hace de cuadro de mando mensual: revisiones vencidas y traducciones pendientes.
- Obsidian: los tags anidados (`doc/sop`, `app/holded`, `cliente/clientex`) son la forma de usar las facetas
  sin salir de la herramienta.
