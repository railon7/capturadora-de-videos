---
tipo: conocimiento
titulo: Organización documental, conclusiones de la investigación
aliases:
  - Documentation organization, research conclusions
fecha: 2026-10-06
tema: documentacion
tags:
  - pkm/conocimiento
  - tema/documentacion
---

# Organización documental: conclusiones

Resultado de investigar cómo se organizan manuales de aplicación, manuales de cliente, SOP y bases de
conocimiento, para decidir cómo guardar lo que produce la capturadora. El detalle está en los ficheros
numerados de esta carpeta. La norma que se aplica en el repo está en
`metodologia/biblioteca-de-conocimiento.md`.

## Las diez conclusiones

1. **Cada documento responde a una sola necesidad del lector.** Aprender, resolver una tarea, consultar un dato o
   entender un porqué son cuatro necesidades distintas y cada una pide su propio tipo de documento (Diátaxis).
   Mezclarlas es lo que hace que un manual no sirva para nada. → `01`
2. **Un tipo de documento no basta.** La capturadora solo producía protocolos paso a paso. Una biblioteca útil
   necesita al menos manual de aplicación, guía de usuario, SOP, tutorial, guía rápida, FAQ, glosario, notas de
   versión, decisión y patrón. → `01`
3. **Escribir una vez y enlazar.** Los manuales de aplicación son comunes y las guías de cliente enlazan a ellos en
   lugar de copiarlos. Es la idea de reutilización de contenido de DITA. → `01`
4. **La norma no impone nombres, pero sí identificación.** ISO 9001 pide que cada documento sea identificable, no un
   formato concreto. Lo habitual es prefijo de tipo, ámbito y número, más versión mayor.menor. → `02`
5. **El control documental es poco y siempre igual:** identificador, versión, estado, propietario, fecha efectiva,
   revisión periódica y archivo de obsoletos fuera del acceso normal. → `02`
6. **Jerarquía corta más metadatos.** Entre cinco y nueve categorías, tres o cuatro niveles como mucho, y todo lo
   demás se filtra con campos (aplicación, cliente, idioma, estado, tipo). → `03`
7. **Sin gobierno, la biblioteca se degrada.** Hace falta alguien responsable de cada documento y una rutina de
   revisión mensual, trimestral y anual. → `03`
8. **Bilingüe con el mismo identificador.** Un ID neutro, un fichero por idioma con sufijo corto, títulos cruzados
   como alias y un glosario de términos preferidos. → `04`
9. **Lo que sirve a una persona sirve a una IA.** Un concepto por fichero, metadatos en YAML y encabezados
   descriptivos que marcan los límites de cada fragmento. → `05`
10. **Una convención que no se comprueba no se cumple.** Por eso hay un script que crea los documentos ya bien
    nombrados y otro que valida la biblioteca entera. → `06`

## Qué se aplicó en la capturadora

| Conclusión | Dónde quedó |
|---|---|
| Tipos y brújula de elección | `metodologia/biblioteca-de-conocimiento.md` §2, plantillas en `plantillas/biblioteca/` |
| ID, nombre kebab-case, ES/EN | `scripts/biblioteca.py`, `scripts/nuevo-documento.py` |
| Metadatos y ciclo de vida | Frontmatter de las plantillas, `scripts/validar-biblioteca.py` |
| Registro y revisiones vencidas | `00_Registro.md`, generado con `validar-biblioteca.py --registro` |
| Entrega con versión y marca de borrador | `scripts/exportar-manual.py` |
| Documentos que ya existían | `scripts/migrar-protocolo.py`, `scripts/patrones-a-biblioteca.py` |
| La skill pregunta el tipo y publica | `.claude/skills/video-a-manual/SKILL.md` (v1.7) |

## Lo que queda abierto

- Dónde vive la biblioteca común de verdad: se parte de `conocimiento/biblioteca/` en este repo. → `06`
- Cuántos documentos van realmente en inglés: la herramienta lo permite, la decisión es de negocio.
- Si se quiere la biblioteca también en Notion. No se ha hecho. Habría que respetar la regla de responsables de las
  tareas y páginas que se creen allí.
