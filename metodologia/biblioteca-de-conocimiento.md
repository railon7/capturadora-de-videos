# Biblioteca de conocimiento: tipos, nombres y ciclo de vida

Cómo se guardan los documentos que salen de la capturadora (manuales, guías, SOP, tutoriales...)
para que haya una biblioteca ordenada, en español e inglés, que se pueda buscar, versionar y
mantener. El porqué de cada decisión está en `conocimiento/organizacion-documental/`.

## 1 · Dos bibliotecas

| Biblioteca | Qué lleva | Dónde vive |
|---|---|---|
| **Común** | Manuales de aplicación, tutoriales, guías rápidas, FAQ, notas de versión, glosario y patrones. Nada de un cliente concreto. | `conocimiento/biblioteca/` de este repo, o la ruta de la variable `BIBLIOTECA_TAZUKE` |
| **De cliente** | Guías de usuario y SOP de ese cliente. Enlazan al manual de la aplicación en lugar de copiarlo. | `<Cliente>/Biblioteca/` dentro de la carpeta del cliente |

**Se escribe una vez y se enlaza.** Si el manual de Holded explica qué es una factura rectificativa,
la guía de ClienteX dice qué hace su equipo y enlaza al manual, sin repetir la explicación.

## 2 · Tipos de documento

| Código | Español | English | Diátaxis | Lector |
|---|---|---|---|---|
| MAN | Manual de aplicación | Application manual | Referencia + explicación | Equipo y cliente |
| GUI | Guía de usuario | User guide | Cómo hacer | Cliente final |
| SOP | Procedimiento normalizado de trabajo (PNT) | Standard operating procedure | Cómo hacer, con control | Equipo del cliente |
| TUT | Tutorial de formación | Training tutorial | Tutorial | Usuario nuevo |
| QSG | Guía rápida | Quick-start guide | Tutorial corto | Usuario nuevo |
| FAQ | Preguntas frecuentes y resolución de problemas | FAQ and troubleshooting | Cómo hacer | Todos |
| GLO | Glosario ES-EN | Glossary | Referencia | Todos |
| NOV | Notas de versión | Release notes | Referencia | Todos |
| DEC | Registro de decisión | Decision record | Explicación | Equipo |
| PAT | Patrón reutilizable | Reusable pattern | Explicación | Interno |

### Cómo elegir el tipo

Dos preguntas, tomadas de Diátaxis:

1. ¿El texto **hace actuar** al lector (pasos) o **le informa** (hechos, contexto)?
2. ¿El lector está **aprendiendo** o está **trabajando**?

| | Aprendiendo | Trabajando |
|---|---|---|
| **Actuar** | TUT, QSG | GUI, SOP, FAQ |
| **Informar** | DEC, PAT, la parte explicativa del MAN | MAN (referencia), GLO, NOV |

**Un documento, un tipo.** Un tutorial no explica el porqué; un manual no manda hacer cosas paso a paso;
una guía no enseña desde cero. Si un texto necesita las dos cosas, son dos documentos que se enlazan.
Un SOP es una guía con control: dice además quién lo hace, cuándo y qué registro deja.

El "protocolo paso a paso" de versiones anteriores de la skill es un **SOP** (uso interno del equipo del
cliente) o una **GUI** (lo recibe el usuario final). Se decide al empezar.

## 3 · Identificador y nombre de fichero

**ID** = `<TIPO>-<ÁMBITO>-<NNN>`

- `TIPO`: el código de la tabla (3 letras).
- `ÁMBITO`: de 2 a 8 letras o cifras en mayúsculas. La aplicación (`HOLDED`, `FACTUSOL`) o, si el documento no es de una
  aplicación, el área (`ADM`, `FIN`). Lo propone `nuevo-documento.py` y se puede fijar con `--ambito`.
- `NNN`: número correlativo dentro de ese tipo y ámbito. Nunca se reutiliza, ni siquiera de un documento archivado.

**El ID es el mismo en los dos idiomas.** La versión en inglés de `SOP-HOLDED-003` también es `SOP-HOLDED-003`.

**Fichero** = `<ID>_<slug>.<idioma>.md`

| Está bien | Está mal | Por qué |
|---|---|---|
| `SOP-HOLDED-003_emitir-factura-rectificativa.es.md` | `P-02 · Circuito de compra.md` | Sin ID, con espacios y con `·`: rompe enlaces y ordena mal |
| `SOP-HOLDED-003_issue-corrective-invoice.en.md` | `SOP-HOLDED-003_Emitir Factura.es.md` | El slug va en minúsculas y con guiones |
| `GUI-FACTUSOL-012_cerrar-ejercicio.es.md` | `GUI-FACTUSOL-12_cerrar-ejercicio.md` | Número de tres cifras y sufijo de idioma |

El slug va en kebab-case: minúsculas, sin tildes, la ñ como n, guiones entre palabras y 60 caracteres como máximo.
Los ficheros que empiezan por `00_` (registro, índices) y los `LEEME.md` no son documentos y no siguen este nombre.

**Imágenes**: `<ID>-<NN>-<descripcion>.png` dentro de `_img/`, junto al documento (`SOP-HOLDED-003-04-comparativo-proveedores.png`).
Las dos versiones de idioma comparten imagen si la captura no tiene texto de idioma. Si la pantalla cambia con el idioma,
una captura por idioma: `SOP-HOLDED-003-04-comparativo-en.png`.

## 4 · Metadatos (frontmatter YAML)

Las claves van en español y en snake_case, como las de las fichas `00_Index_*` que genera el orquestador PKM.

| Campo | Obligatorio | Contenido |
|---|---|---|
| `id` | sí | El ID. Tiene que coincidir con el del nombre |
| `tipo` | sí | `manual-aplicacion`, `guia-usuario`, `sop`, `tutorial`, `guia-rapida`, `faq`, `glosario`, `notas-version`, `decision`, `patron` |
| `titulo` | sí | Título en el idioma del documento |
| `aliases` | no | Título en el otro idioma, y el nombre antiguo si se migró |
| `idioma` | sí | `es` o `en`. Coincide con el sufijo del nombre |
| `version` | sí | `mayor.menor`, entre comillas (`"1.0"`). 0.x mientras no esté aprobado |
| `estado` | sí | `borrador`, `revision`, `aprobado`, `obsoleto` |
| `propietario` | sí | Quien responde del documento |
| `revisor` / `revisado` | al aprobar | Quién lo validó y en qué fecha |
| `cliente` | sí | Nombre del cliente o `comun` |
| `aplicacion` | sí | Aplicación o sistema que describe (`general` si no es de una) |
| `audiencia` | no | `equipo`, `cliente`, `usuario-nuevo`... |
| `creado` | no (lo pone el script) | Fecha de creación AAAA-MM-DD |
| `proxima_revision` | sí | Fecha AAAA-MM-DD. El script la pone a un año; se ajusta al aprobar |
| `traduccion` | si hay pareja | Nombre del fichero de la otra versión. Los dos se enlazan entre sí |
| `traduccion_estado` | en la derivada | `pendiente`, `borrador-ia`, `revisada` |
| `origen`, `fuente_video` | no | De dónde sale: `video`, `reunion`, `patrones-acumulados`, `protocolo-antiguo` |
| `sustituido_por` | si es obsoleto y lo hay | ID del documento que lo reemplaza |
| `tags` | no | Anidados: `doc/sop`, `app/holded`, `cliente/clientex`, `idioma/es` |

```yaml
---
id: SOP-HOLDED-003
tipo: sop
titulo: Emitir factura rectificativa
aliases:
  - Issue a corrective invoice
idioma: es
version: "1.0"
estado: aprobado
propietario: Jorge Herrera
revisor: Administración del cliente
cliente: ClienteX
aplicacion: Holded
creado: 2026-10-06
revisado: 2026-10-20
proxima_revision: 2027-10-20
traduccion: SOP-HOLDED-003_issue-corrective-invoice.en.md
tags:
  - doc/sop
  - app/holded
  - cliente/clientex
  - idioma/es
---
```

## 5 · Ciclo de vida

```
borrador (0.x) ──► revision (0.x) ──► aprobado (1.0) ──► obsoleto
      ▲                                    │
      └────────── cambio (1.1 en revision) ┘
```

- **Borrador**: se está escribiendo. Puede tener comentarios GUÍA y huecos. El PDF sale con marca de agua.
- **Revisión**: lo revisa otra persona. Sin comentarios GUÍA ni marcadores `{{...}}`.
- **Aprobado**: tiene revisor, fecha de revisión y versión 1.0 o superior. Sin marca de agua.
- **Obsoleto**: ya no vale. Se mueve a `90-archivo/` y, si lo hay, se indica `sustituido_por`. No se borra.
- Un cambio menor sube el segundo número (1.0 a 1.1) y un cambio de fondo el primero (1.1 a 2.0). Un documento aprobado que se
  modifica vuelve a `revision` hasta que alguien lo valida otra vez.
- Cada versión deja una fila en **Historial de cambios**, al final del documento.
- **Revisión periódica**: un SOP o una guía de cliente, una vez al año aunque no cambie nada (se anota igual). Un manual de
  aplicación, cada vez que cambia la versión de la aplicación (lo avisa una nota de versión NOV).

**Roles** (los tres que recomienda la investigación): **propietario** (responde del documento), **curador** (mantiene
una aplicación o un cliente entero y el glosario) y **colaborador** (propone cambios). Hoy los asume una sola
persona; los campos están para cuando no sea así.

## 6 · Carpetas

```
Biblioteca común                      Biblioteca de un cliente
00-gobierno/   glosario, decisiones,  (raíz)        GUI, SOP, QSG propios
               00_Registro.md         _img/         capturas tapadas y anotadas
10-aplicaciones/<app>/                entregables/  HTML y PDF para entregar
               MAN TUT QSG FAQ NOV    90-archivo/   obsoletos
40-patrones/   PAT
90-archivo/    obsoletos
```

Hasta cinco categorías de primer nivel y no más de tres niveles. Lo demás se filtra con los metadatos (aplicación,
cliente, estado, idioma), no con más carpetas. El prefijo del ID ya ordena por tipo dentro de cada carpeta.

## 7 · Bilingüe ES-EN

1. **El español se escribe primero.** Es el idioma de las capturas y de los vídeos de origen.
2. **El inglés es una derivada**, con el mismo ID: `nuevo-documento.py --titulo-en "..."` crea la pareja con los
   encabezados ya traducidos y `traduccion_estado: pendiente`.
3. **La traducción la hace Claude** a partir de la versión española aprobada: mismos pasos y mismas imágenes, mismos
   términos del glosario (`GLO-GEN-001`), sin añadir ni quitar contenido. Queda como `borrador-ia`.
4. **Una persona la revisa** y la pasa a `revisada`. Mientras no lo esté, el validador avisa si la española ya está aprobada.
5. **Los términos de la aplicación** se traducen como los llama la propia aplicación en su interfaz en inglés, no como
   suenen mejor. Si no hay interfaz en inglés, se deja el término original entre comillas.
6. Se traduce solo lo que va a leer alguien en inglés. La biblioteca no obliga a que todo tenga pareja.
7. Si cambia la versión española, la inglesa queda desfasada: el validador avisa cuando las versiones no coinciden.

## 8 · Herramientas

| Quiero | Comando |
|---|---|
| Crear la estructura de una biblioteca | `python scripts/nuevo-documento.py --iniciar comun --biblioteca "<ruta>"` (o `cliente`) |
| Crear un documento | `python scripts/nuevo-documento.py --tipo SOP --aplicacion Holded --titulo "..." --titulo-en "..." --cliente "<Cliente>" --biblioteca "<Cliente>/Biblioteca"` |
| Comprobar la biblioteca y regenerar el registro | `python scripts/validar-biblioteca.py "<ruta>" --registro` |
| Entregar un documento | `python scripts/exportar-manual.py "<fichero>.md" --pdf` |
| Migrar un protocolo antiguo | `python scripts/migrar-protocolo.py "08-Formacion/P-02 · Circuito de compra.md" --tipo SOP --aplicacion Holded --cliente "<Cliente>" --biblioteca "<Cliente>/Biblioteca"` |
| Pasar los patrones acumulados a la biblioteca | `python scripts/patrones-a-biblioteca.py` |

La biblioteca por defecto es `conocimiento/biblioteca/` de este repo. Para trabajar con otra, `--biblioteca` o
`BIBLIOTECA_TAZUKE`. El propietario por defecto es `BIBLIOTECA_PROPIETARIO` o el `user.name` de git.

## 9 · Mantenimiento

| Cuándo | Qué |
|---|---|
| Cada documento nuevo | `validar-biblioteca.py` sin errores antes de pasar a revisión |
| Cada mes | Mirar `00_Registro.md`: revisiones vencidas y traducciones pendientes |
| Cada trimestre | Categorías vacías o con un solo documento, términos del glosario sin usar, obsoletos que sigan fuera del archivo |
| Cada año | Revisar la convención entera: tipos que sobran o faltan, nombres que no se respetan |
| Cuando sale una versión de una aplicación | Crear la nota de versión (NOV) y revisar los MAN, GUI y SOP que cita |

Sin esto, según los estudios de taxonomía, la biblioteca se degrada en seis a doce meses.

## 10 · Antes de pasar a "aprobado"

- [ ] Sin comentarios GUÍA ni marcadores `{{...}}`.
- [ ] Capturas tapadas (DNI, CIF, nombres) y auditadas con `auditar-privacidad.py`.
- [ ] Roles en vez de nombres de persona en el texto.
- [ ] Cada paso con una sola decisión; apartado "Qué NO hacer" rellenado (SOP y GUI).
- [ ] Enlaces al manual de la aplicación y a la FAQ, no copias de su contenido.
- [ ] `revisor` y `revisado` rellenados; versión a 1.0 o superior; historial de cambios al día.
- [ ] `validar-biblioteca.py` sin errores.
- [ ] Si tiene pareja en inglés: `traduccion_estado: revisada` o aviso asumido.
