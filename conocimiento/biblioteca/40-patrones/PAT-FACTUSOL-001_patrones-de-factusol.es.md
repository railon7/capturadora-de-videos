---
id: PAT-FACTUSOL-001
tipo: patron
titulo: Patrones de FactuSol
aliases: []
idioma: es
version: "0.1"
estado: borrador
propietario: Jorge Herrera
revisor:
cliente: comun
aplicacion: FactuSol
audiencia:
  - equipo
creado: 2026-10-06
revisado:
proxima_revision: 2027-10-06
origen: patrones-acumulados
origen_patrones: Software DELSOL — FactuSol (tutoriales oficiales)
tags:
  - doc/patron
  - app/factusol
  - cliente/comun
  - idioma/es
---

# Patrones de FactuSol

> Origen: «Software DELSOL — FactuSol (tutoriales oficiales)» · 29 patrones. Cada apartado es un patrón con su «Visto en» y su «Se aplica cuando».

## Decidir el mapa de series antes del primer documento
**Visto en**: Tutorial DELSOL «Creación de un presupuesto», 2026-10-06
**Se aplica cuando**: se pone en marcha la facturación de un cliente con FactuSol (o ContaSol) y hay varias tiendas, líneas de negocio o tipos de venta

FactuSol tiene hasta 9 series independientes por tipo de documento, y cada usuario elige la serie al crear el documento. Si no se fija antes qué serie corresponde a qué (tienda, canal, tipo de cliente), cada persona usa una distinta y luego los informes y la numeración no cuadran. Pregunta al cliente y deja la tabla de series escrita en el manual de arranque.

## Concepto manual solo para lo que no es artículo
**Visto en**: Tutorial DELSOL «Creación de un presupuesto», 2026-10-06
**Se aplica cuando**: el cliente quiere teclear líneas libres en presupuestos, albaranes o facturas

Una línea sin código de artículo (Enter en el código y texto en Descripción) es cómoda, pero no mueve stock, no cuenta en estadísticas por artículo y su IVA se pone a mano. Conviene dar de alta como artículos los servicios recurrentes (portes, mano de obra, preparación) y reservar el concepto manual para textos o casos excepcionales.

## Hacer el presupuesto en el ERP para no volver a teclear
**Visto en**: Tutorial DELSOL «Creación de un presupuesto», 2026-10-06
**Se aplica cuando**: el cliente hace las ofertas en Word o Excel y factura después en FactuSol

Si el presupuesto se hace dentro de FactuSol, al aceptarse se valida en pedido, albarán o factura sin copiar líneas. Es uno de los argumentos de implantación más claros: elimina errores de transcripción y deja la trazabilidad oferta → factura. Rellenar plazo de entrega y validez en Otros datos para que salgan en el impreso.

## Decidir el tipo de gestión antes de crear la empresa
**Visto en**: Tutorial DELSOL «Creación de una empresa en FACTUSOL», 2026-10-06
**Se aplica cuando**: se arranca FactuSol en un cliente nuevo y hay que elegir entre gestión comercial con stock y facturación de servicios

El tipo de gestión cambia menús, documentos y hasta las opciones de la ventana de configuración.
Preguntar al cliente en la reunión de arranque: ¿compra y almacena producto? ¿factura cuotas
periódicas u horas? ¿necesita albaranes y pedidos? Con esas respuestas se elige y se deja escrito;
cambiarlo con documentos ya emitidos obliga a rehacer la empresa.

## La configuración de empresa es un checklist de arranque, no un trámite
**Visto en**: Tutorial DELSOL «Creación de una empresa en FACTUSOL», 2026-10-06
**Se aplica cuando**: se crea una empresa en un programa DELSOL y hay funciones que solo aparecen si se activan

Varias funciones (trazabilidad, tallas y colores, dimensiones, partes de reparación, costes de obra,
abonos, devoluciones, campos de descuento/portes) no existen en los menús hasta marcarlas. Recorrer
cada casilla con el cliente como preguntas cerradas evita la incidencia típica de "el programa no
tiene X" semanas después, y también evita activar de más y cargar la entrada de documentos.

## Alinear el enlace contable con la contabilidad desde el primer día
**Visto en**: Tutorial DELSOL «Creación de una empresa en FACTUSOL», 2026-10-06
**Se aplica cuando**: la facturación (FactuSol) va a traspasar facturas a una contabilidad (ContaSol o la de la asesoría)

El número de dígitos de las subcuentas debe coincidir con el plan de cuentas de la contabilidad.
Preguntarlo a la asesoría antes de crear la empresa y antes de dar de alta clientes, porque las
subcuentas de cliente y proveedor se generan con esa longitud y un desajuste se arrastra a cada traspaso.

## Una empresa, muchos ejercicios
**Visto en**: Tutorial DELSOL «Creación de una empresa en FACTUSOL», 2026-10-06
**Se aplica cuando**: el cliente viene de programas o costumbres en las que se duplicaba la empresa cada año

En los programas DELSOL el código de empresa vale para todos sus ejercicios; el cambio de año se hace
dentro de la misma empresa. Conviene decirlo en la formación inicial y fijar un código de empresa
corto y estable, porque es la referencia para copias, enlaces y soporte.

## Validar documentos en lugar de copiarlos
**Visto en**: Tutorial DELSOL «Creación de una factura validando un presupuesto», 2026-10-06
**Se aplica cuando**: el cliente encadena documentos de venta o compra (presupuesto → pedido → albarán → factura)

En FactuSol cualquier documento posterior puede «validar» las líneas de uno anterior del mismo cliente (icono Validar del grupo Líneas). Así no se reteclea nada, se pueden traer solo algunas líneas y el documento de origen permanece enlazado. Hay que enseñarlo desde el primer día: si el equipo copia a mano, aparecen precios distintos y documentos de origen que nunca se cierran.

## Cliente primero, documento de origen después
**Visto en**: Tutorial DELSOL «Creación de una factura validando un presupuesto», 2026-10-06
**Se aplica cuando**: se forma a usuarios en la facturación desde documentos previos

La ventana de validación solo ofrece documentos del cliente que ya está en la cabecera (y del ejercicio elegido). El orden correcto es serie → cliente → Validar → tipo y número. Cuando un usuario dice «no me sale el presupuesto», casi siempre es otro cliente u otro ejercicio.

## Revisar Totales antes de grabar una factura que viene de otro documento
**Visto en**: Tutorial DELSOL «Creación de una factura validando un presupuesto», 2026-10-06
**Se aplica cuando**: se factura validando presupuestos o pedidos antiguos

Las líneas llegan del documento de origen, pero la forma de pago, los vencimientos y los descuentos de pie pueden no ser los vigentes. El propio tutorial recomienda abrir Totales y Otros datos antes de guardar; en una factura esto afecta a cobros y, con Verifactu, una vez emitida ya no se corrige sin rectificativa.

## Código de cliente automático y código contable solo por excepción
**Visto en**: Tutorial DELSOL «Creación de una ficha de cliente», 2026-10-06
**Se aplica cuando**: se definen las reglas de alta de clientes o proveedores en un programa de facturación enlazado con contabilidad

Dejar que el programa asigne el código evita huecos y duplicados, y que el código de cliente sea la
subcuenta contable mantiene una correspondencia directa con ContaSol. El código contable propio solo
se usa cuando la asesoría ya tiene subcuentas que hay que respetar (por ejemplo, migraciones). Conviene
decidirlo con la asesoría antes de cargar el fichero de clientes.

## Ficha completa en el alta, no en la primera factura
**Visto en**: Tutorial DELSOL «Creación de una ficha de cliente», 2026-10-06
**Se aplica cuando**: el equipo de administración empieza a dar de alta clientes en un programa nuevo

La forma de pago, la tarifa, los impuestos especiales y las opciones (factura electrónica, recibo al
facturar) se heredan en cada documento desde la ficha. Recorrer las vistas General, Comercial y Otros
datos en el alta evita facturas con vencimientos o impuestos mal y correcciones posteriores. Una
checklist corta de datos a pedir al cliente (NIF, nombre fiscal exacto, email de facturación, forma
de pago, IBAN) acelera el alta.

## Buscar antes de crear
**Visto en**: Tutorial DELSOL «Creación de una ficha de cliente», 2026-10-06
**Se aplica cuando**: varias personas dan de alta terceros en el mismo fichero

El fichero de clientes se abre con la lista de los ya existentes y un buscador: comprobar por NIF antes
de pulsar Nuevo evita fichas duplicadas que parten el histórico de ventas, los riesgos y el modelo 347.
Es una regla de una línea que conviene poner en la formación y en el manual del cliente.

## Copiar el modelo de fábrica, nunca editarlo
**Visto en**: Tutorial DELSOL «Diseño de un modelo de factura», 2026-10-06
**Se aplica cuando**: hay que personalizar facturas, albaranes, presupuestos o informes en software con plantillas de fábrica

El modelo propio se crea con Nuevo a partir de un modelo base (estilo e impuestos), con código y nombre
propios. Así el de fábrica queda intacto para volver a empezar si el diseño se estropea, y las actualizaciones
del programa no pisan el trabajo hecho. Elegir bien el modelo base (IVA, IVA + IRPF, IGIC) ahorra rehacer campos.

## Pedir el logotipo y los textos legales antes de la sesión de diseño
**Visto en**: Tutorial DELSOL «Diseño de un modelo de factura», 2026-10-06
**Se aplica cuando**: se prepara la puesta en marcha de la facturación de un cliente nuevo

El diseño necesita el archivo de logotipo en una ruta estable (en el tutorial se carga desde una carpeta
del disco con Examinar; por prudencia se trata como si dependiera de esa ruta) y los textos que debe llevar la factura (garantías, condiciones, pie legal).
Pedirlos en la toma de requisitos evita sesiones de diseño a medias y logos que desaparecen al mover carpetas.

## Una sola ventana de emisión para todos los informes
**Visto en**: Tutorial DELSOL «Emisión de un informe», 2026-10-06
**Se aplica cuando**: hay que formar a usuarios en la obtención de listados en programas de Software DELSOL

Todos los listados (solapa Impresión, grupos Compras, Ventas, Almacén, Administración) comparten la misma
ventana: salida a la izquierda (impresora, vista previa, PDF, Excel/Calc, RTF/DOC, Portal Documental),
Opciones, Ordenación, Clasificación, Intervalos y Encabezado. Se enseña una vez con un informe que el cliente
use de verdad y el resto se aprende solo.

## Acordar con la asesoría qué informe y qué intervalos se le envían
**Visto en**: Tutorial DELSOL «Emisión de un informe», 2026-10-06
**Se aplica cuando**: el cliente envía periódicamente listados de facturación a su asesoría o a dirección

El mismo listado tiene varios formatos (libro de facturas emitidas, rectificativas, oficial, listado
auxiliar) y los intervalos por defecto cubren todo el ejercicio. Conviene fijar por escrito qué formato,
orden e intervalos se mandan cada periodo y comprobarlos siempre en vista previa, para no enviar el informe
equivocado o un periodo de más.

## Elegir el método de facturación de albaranes según el ritmo del cliente
**Visto en**: Tutorial DELSOL «Facturación automática de albaranes», 2026-10-06
**Se aplica cuando**: el cliente sirve con albarán y factura después (distribución, mayoristas, servicios recurrentes)

FactuSol ofrece tres caminos: validar un albarán en una factura nueva (al momento), seleccionar albaranes en su fichero y pulsar Factura (un cliente o pocos), y Administración > Generación (cierre de periodo masivo, por fechas, clientes, forma de pago o agentes). En la implantación hay que decidir con el cliente cuál es el proceso estándar y escribirlo; mezclar los tres sin criterio provoca albaranes olvidados o facturados dos veces.

## Pregunta clave: ¿una factura por albarán o agrupada?
**Visto en**: Tutorial DELSOL «Facturación automática de albaranes», 2026-10-06
**Se aplica cuando**: se configura la facturación periódica de albaranes de un cliente

Los modos de Generación existen «con» y «sin» agrupar. Antes del primer cierre hay que preguntar al cliente qué espera recibir cada uno de sus clientes (factura mensual con todos los albaranes o una por entrega) y reflejarlo en el procedimiento; es la causa más común de quejas en el primer mes.

## Traspasar los cobros del albarán a la factura
**Visto en**: Tutorial DELSOL «Facturación automática de albaranes», 2026-10-06
**Se aplica cuando**: hay albaranes cobrados total o parcialmente en la entrega (contado, tarjeta)

La ventana de facturación por número de albarán trae marcada la opción «Traspasar movimientos de cobro de albaranes a facturas». Debe quedarse así: si se desmarca, la factura nace pendiente de cobro aunque el albarán ya estuviera pagado, y la cartera de cobros y las reclamaciones salen mal.

## Revisar «Pendientes de facturar» antes de cada cierre
**Visto en**: Tutorial DELSOL «Facturación automática de albaranes», 2026-10-06
**Se aplica cuando**: se hace el cierre de facturación mensual o quincenal con FactuSol

El fichero de albaranes filtra por estado (Pendientes de facturar / Facturados) y muestra la columna FACT. Antes de lanzar la generación masiva conviene revisar esa lista (precios a cero, clientes equivocados, albaranes que no tocan) y después comprobar que ha quedado vacía. Es la secuencia que evita facturas erróneas que, con Verifactu, solo se arreglan con abonos.

## Configurar el catálogo antes de cargar conceptos recurrentes
**Visto en**: Tutorial DELSOL «Facturación periódica», 2026-10-06
**Se aplica cuando**: un cliente factura cuotas fijas (igualas, mantenimientos, asesoría) y se va a montar la facturación periódica

FactuSol obliga a decidir primero, en la configuración del fichero de clientes, si los conceptos salen del
fichero de artículos o del de servicios, si el precio es modificable por cliente y qué tipos de concepto
existen (hasta seis). Cambiar esa decisión con cientos de conceptos cargados es caro, así que se fija en la
primera sesión de implantación junto con el catálogo de servicios.

## Tipos de concepto como líneas de negocio para facturar por lotes
**Visto en**: Tutorial DELSOL «Facturación periódica», 2026-10-06
**Se aplica cuando**: la empresa tiene varias líneas de servicio (laboral, contable, fiscal, seguros…) que se facturan en momentos o con criterios distintos

Los tipos de concepto facturables permiten lanzar la generación periódica solo para una o varias líneas
(en el tutorial, Laboral y Contable) y acotar por rango de clientes. Conviene preguntar al cliente cómo
agrupa hoy su facturación y trasladarlo a tipos e identificadores antes de cargar conceptos.

## Generación masiva con red de seguridad
**Visto en**: Tutorial DELSOL «Facturación periódica», 2026-10-06
**Se aplica cuando**: se lanza un proceso que crea muchas facturas de golpe en cualquier software de facturación

Tres protecciones que conviene dejar fijadas en el procedimiento: numeración desde el contador de la serie
(factura inicial a 0), «No facturar conceptos ya facturados» siempre marcada y fecha de factura igual a la
del periodo, no a la del día de ejecución. Y revisar el informe previo o las facturas generadas antes de
enviarlas.

## Suplidos fuera de la base imponible, en su casilla
**Visto en**: Tutorial DELSOL «Gestión de suplidos en empresas de facturación de servicios», 2026-10-06
**Se aplica cuando**: el cliente (asesoría, gestoría, despacho) adelanta pagos en nombre de sus clientes y los repercute en factura

FactuSol separa los suplidos de las líneas: se registran en Totales > Suplidos (hasta seis por factura) con
fecha, perceptor, NIF, factura del perceptor, concepto e importe, y suman al total sin entrar en la base del
IVA. En la implantación hay que detectar si el cliente hoy los mete como líneas con IVA y cortar esa
costumbre desde el primer día.

## Una funcionalidad nueva obliga a revisar el diseño de impresión
**Visto en**: Tutorial DELSOL «Gestión de suplidos en empresas de facturación de servicios», 2026-10-06
**Se aplica cuando**: se activa en FactuSol o ContaSol un dato nuevo en los documentos (suplidos, retenciones, textos legales)

Que un dato esté grabado no significa que salga impreso: el campo tiene que estar en el modelo de impresión.
Cada vez que se pone en marcha un dato nuevo en las facturas, el checklist de implantación incluye abrir el
diseño, añadir el campo y comprobar en vista previa con una factura real antes de enviarla.

## El tipo de empresa decide la interfaz
**Visto en**: Tutorial DELSOL «Introduccion a FACTUSOL - Conoce su interfaz», 2026-10-06
**Se aplica cuando**: se da de alta una empresa en FactuSol y hay que elegir entre gestión comercial con stock y facturación de servicios

El tipo elegido al crear la empresa cambia las solapas: en servicios desaparece Almacén y aparecen gastos,
servicios y facturación periódica. Hay que preguntar al cliente si vende producto con stock, servicios o
ambos **antes** de crear la empresa, y documentar la elección: los manuales y la formación dependen de ella.

## Formar por solapa y grupo, no por botón
**Visto en**: Tutorial DELSOL «Introduccion a FACTUSOL - Conoce su interfaz», 2026-10-06
**Se aplica cuando**: se forma a usuarios nuevos o se escriben manuales de ContaSol/FactuSol (interfaz de cinta)

La cinta de DELSOL agrupa los botones en grupos con nombre (Compras, Ventas, Cobros, Ficheros…). Enseñar
«solapa → grupo → botón» da al usuario un mapa estable que aguanta cambios de versión y le permite encontrar
solo lo que no se le ha enseñado. Una sesión inicial de 15 minutos de recorrido de solapas ahorra consultas
después.

## Comprobar empresa y ejercicio en la barra de título
**Visto en**: Tutorial DELSOL «Introduccion a FACTUSOL - Conoce su interfaz», 2026-10-06
**Se aplica cuando**: el cliente tiene varias empresas o varios ejercicios abiertos en el mismo programa

La barra de título muestra código de empresa, nombre y ejercicio activo. Convertir «mirar la barra de título
antes de grabar» en hábito (y ponerlo como primer paso de cada protocolo de grabación) evita el error más caro
del arranque: documentos en la empresa o el ejercicio equivocados, sobre todo en el cambio de año.

## Historial de cambios

| Versión | Fecha | Cambio | Autoría |
|---|---|---|---|
| 0.1 | 2026-10-06 | Creado desde patrones-acumulados.md | Jorge Herrera |
