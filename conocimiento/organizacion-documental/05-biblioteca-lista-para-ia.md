---
tipo: conocimiento
titulo: Una biblioteca lista para IA
aliases:
  - An AI-ready documentation library
fecha: 2026-10-06
tema: documentacion
tags:
  - pkm/conocimiento
  - tema/documentacion
  - tema/ia
---

# Una biblioteca lista para IA

La biblioteca la va a leer Claude (la skill, los asistentes) además de personas. Lo que se sabe de recuperación de
información para modelos coincide con lo que pide una buena documentación.

## Qué recomiendan las fuentes

- Para documentos estructurados (manuales, documentación de producto, normativa), el **fragmentado consciente de la
  estructura** supera a cortar por tamaño fijo, sin mucha más complejidad.
- En Markdown, **cortar por encabezados** y anteponer los encabezados padre a cada fragmento: un fragmento titulado
  "Política de devoluciones → Pedidos internacionales" lleva los dos para que el modelo sepa de qué trata.
- Un "paquete de conocimiento" abierto (OKF) es una carpeta de ficheros Markdown en Git, **un concepto por
  fichero**, con un bloque de frontmatter YAML de metadatos legibles por máquina.
- Los metadatos de documento (título, responsable, ruta, última modificación) y los de fragmento (ruta de
  secciones, tipo de elemento) mejoran la precisión.
- Hay que **registrar de qué documento y de qué posición sale cada fragmento**, para poder citar y reconstruir.
- Documentos bien formateados, con encabezados descriptivos y listas, rinden mejor que muros de texto.

## Cómo lo cumple la biblioteca

| Recomendación | Qué hay |
|---|---|
| Un concepto por fichero | Un documento por proceso y un SOP, GUI o MAN por tema. Los patrones se agrupan por aplicación, con un `##` por patrón |
| Frontmatter YAML | Obligatorio y comprobado por `validar-biblioteca.py` |
| Encabezados descriptivos | Las plantillas fijan los `##` por tipo ("Pasos", "Qué NO hacer", "Si algo sale mal") |
| Trazabilidad de la fuente | `origen`, `fuente_video` y el ID en el nombre |
| Texto que se pueda citar | El ID identifica el documento; el encabezado, el apartado |
| Frescura | `estado`, `version`, `proxima_revision`. Un asistente puede ignorar lo obsoleto |

## Lo que falta

- **La skill todavía no consulta la biblioteca por sí sola** más allá de lo que se le indica: la versión 1.7 le dice
  que mire la carpeta de la aplicación y los patrones antes de redactar, pero no hay índice de búsqueda. Con pocos
  documentos basta leer la carpeta; si crece, el siguiente paso sería un índice o un RAG sobre `00_Registro.md` y los
  encabezados.
- **Las imágenes** no se pueden leer por texto. El catálogo de capturas (`Analisis/Catalogo de capturas.md`) sigue
  siendo imprescindible para que una IA sepa qué enseña cada una.
- **Datos personales**: nada de la biblioteca debe llevar DNI, CIF ni nombres de personas; es un requisito legal y
  también evita que un asistente repita datos que no debía conocer.
