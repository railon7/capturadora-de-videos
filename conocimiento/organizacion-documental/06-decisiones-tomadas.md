---
tipo: conocimiento
titulo: Decisiones tomadas y supuestos
aliases:
  - Decisions taken and assumptions
fecha: 2026-10-06
tema: documentacion
tags:
  - pkm/conocimiento
  - tema/documentacion
---

# Decisiones tomadas y supuestos

Cinco decisiones quedaron abiertas en el plan. Se aplicó la propuesta de cada una; aquí están el supuesto, la
alternativa y cómo cambiarlo si no vale.

| # | Decisión | Se aplicó | Alternativa | Para cambiarlo |
|---|---|---|---|---|
| 1 | "kpbo" en la petición original | Se leyó como **kebab-case** | Otro formato de nombres | Cambiar `slugify` en `scripts/biblioteca.py` y la expresión del nombre |
| 2 | Dónde vive la biblioteca común | **`conocimiento/biblioteca/`** de este repo | Una carpeta en la raíz del vault, fuera del repo | Variable `BIBLIOTECA_TAZUKE` o `--biblioteca`; no hay que tocar código |
| 3 | Idioma de las claves del frontmatter | **Español**, como las fichas PKM | Inglés, que es lo habitual en vaults multilingües | Renombrar los campos en `biblioteca.py`, el validador y las plantillas |
| 4 | Idioma de origen | **Español primero**, inglés derivado | Ambos desde el vídeo | Es un hábito, no una restricción de la herramienta |
| 5 | Bilingüe siempre o a demanda | **A demanda**: `--titulo-en` crea la pareja solo si se pide | Pareja obligatoria | Añadir al validador una comprobación de que cada documento aprobado tenga pareja (hoy no la hay) |

### Por qué la biblioteca común está dentro del repo (decisión 2)

- El repo ya está dentro del vault de Obsidian, así que los documentos se ven y se enlazan desde él.
- `conocimiento/` ya era el sitio de lo reutilizable y sin datos de cliente, que es justo la definición de la
  biblioteca común.
- El riesgo: los documentos de cliente no deben acabar aquí. El `.gitignore` ya excluye vídeos, capturas y carpetas
  de trabajo, y las guías de cliente van en `<Cliente>/Biblioteca/`, fuera del repo.
- Si la biblioteca crece o se quiere versionar aparte, se mueve la carpeta y se apunta la variable de entorno.

### Otras decisiones de diseño

- **Solo librería estándar.** Los scripts nuevos no añaden dependencias. El frontmatter se lee con un lector propio
  que cubre el subconjunto que usan las plantillas, y la CI no instala PyYAML.
- **Nunca sobrescribir.** `nuevo-documento.py`, `migrar-protocolo.py` y `patrones-a-biblioteca.py` fallan si el
  fichero existe. La excepción es la actualización de un PAT existente, que conserva su historial.
- **El validador separa error de aviso.** Error: la biblioteca no cumple la convención. Aviso: conviene mirarlo
  (una imagen que falta en un borrador, una revisión vencida, una traducción desfasada).
- **El PDF sale con Chrome o Edge**, que ya están en los equipos de trabajo y dan la maqueta de marca del kit
  comercial. Pandoc queda como respaldo.
- **Borrador con marca de agua.** Nadie debería entregar a un cliente un documento sin aprobar sin darse cuenta.
- **El protocolo antiguo se migra a una copia.** El original no se toca por si hay que volver atrás.

### Supuestos que conviene confirmar

- Que el propietario por defecto sea el `user.name` de git. Para otro, `--propietario` o `BIBLIOTECA_PROPIETARIO`.
- Que un año sea el plazo de revisión para SOP y guías de cliente.
- Que el glosario común (`GLO-GEN-001`) sea el único: términos de una aplicación concreta irían en su MAN.
