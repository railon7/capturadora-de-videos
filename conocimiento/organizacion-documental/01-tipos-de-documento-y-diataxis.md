---
tipo: conocimiento
titulo: Tipos de documento y Diátaxis
aliases:
  - Document types and Diátaxis
fecha: 2026-10-06
tema: documentacion
tags:
  - pkm/conocimiento
  - tema/documentacion
---

# Tipos de documento y Diátaxis

## Diátaxis: cuatro necesidades, cuatro formas

Diátaxis identifica cuatro necesidades de quien usa un producto y una forma de documentación para cada una.
Cada forma tiene su propósito, su estilo y **debe mantenerse separada de las otras**.

| | Estudio (aprender) | Trabajo (aplicar) |
|---|---|---|
| **Acción** | Tutorial: una lección en la que la persona hace algo guiada | Cómo hacer: pasos concretos para un problema real |
| **Cognición** | Explicación: contexto y porqués, desde varios ángulos | Referencia: descripción técnica neutral y exacta |

Dos preguntas bastan para clasificar un texto: si **hace actuar** o **informa**, y si el lector está
**estudiando** o **trabajando**.

Reglas de estilo que se desprenden:

- El **tutorial** lo conduce un instructor ausente: camino único, resultado visible en cada paso, sin desvíos
  explicativos.
- El **cómo hacer** es para quien ya es competente y tiene un problema concreto. No enseña desde cero.
- La **referencia** describe sin interpretar y su estructura refleja la del sistema que describe.
- La **explicación** responde al porqué y puede opinar.

## DITA: tres tipos de tema y reutilización

DITA es el estándar XML de OASIS para documentación técnica. Sus tres tipos de tema son **concepto** (entender),
**tarea** (hacer) y **referencia** (consultar datos). Se parecen a los de Diátaxis. Su aportación es otra:
los temas son pequeños, se escriben una vez y se ensamblan en varios documentos (escribir una vez, usar muchas).
No hace falta XML para aprovecharlo: basta con que la guía de un cliente enlace al manual de la aplicación en lugar
de copiarlo.

## The Good Docs Project: plantillas ya pensadas

Ofrece plantillas en Markdown, publicadas con licencia Zero-Clause BSD. Las del paquete principal:
concept, how-to, README, reference, release notes, troubleshooting y tutorial. Fuera del paquete principal hay
quickstart, installation guide, glossary, style guide y terminology system, entre otras. El how-to es "un conjunto
conciso de pasos numerados para una tarea" y el tutorial es "instrucciones para montar un proyecto de ejemplo" con
fines de aprendizaje.

## ISO/IEC/IEEE 26514

Fija requisitos de estructura, contenido y formato de la documentación de usuario de software, impresa o en
pantalla, y orientación de estilo. Se cita como marco general. No se ha leído el texto de la norma ni se ha adoptado: el contenido de las
plantillas sale de la práctica habitual y de The Good Docs Project.

## Cómo quedó la lista de tipos

Se parte de Diátaxis para el reparto y se completa con los tipos que una consultora de implantación necesita y que
ninguna fuente trae hechos:

| Código | Tipo | Cuadrante | Equivalente en las fuentes |
|---|---|---|---|
| MAN | Manual de aplicación | Referencia + explicación | Reference + concept |
| GUI | Guía de usuario | Cómo hacer | How-to |
| SOP | Procedimiento normalizado (PNT) | Cómo hacer, con control | How-to + control documental ISO |
| TUT | Tutorial de formación | Tutorial | Tutorial |
| QSG | Guía rápida | Tutorial corto | Quickstart |
| FAQ | Preguntas y resolución de problemas | Cómo hacer | Troubleshooting |
| GLO | Glosario ES-EN | Referencia | Glossary / terminology system |
| NOV | Notas de versión | Referencia | Release notes |
| DEC | Registro de decisión | Explicación | Decision record (práctica común de ingeniería) |
| PAT | Patrón reutilizable | Explicación | Propio de la capturadora |

La diferencia entre **GUI** y **SOP** no la traen las fuentes de documentación técnica, viene del control documental:
un SOP añade quién lo hace, cuándo y qué registro deja, y se revisa con periodicidad fija.

## Lo que ya tenía la capturadora y se conserva

La plantilla de protocolo tenía dos apartados que ninguna plantilla de las fuentes trae y que son lo más valioso:
**Qué NO hacer** (la memoria del proyecto: lo que ya se sabe que rompe) y **Decisiones detrás de este
procedimiento** (evita que alguien "mejore" el procedimiento sin saber lo que rompe). Pasan a las plantillas SOP y GUI.
