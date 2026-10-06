---
id: PAT-CONTASOL-001
tipo: patron
titulo: Patrones de ContaSol
aliases: []
idioma: es
version: "0.1"
estado: borrador
propietario: Jorge Herrera
revisor:
cliente: comun
aplicacion: ContaSol
audiencia:
  - equipo
creado: 2026-10-06
revisado:
proxima_revision: 2027-10-06
origen: patrones-acumulados
origen_patrones: Software DELSOL — ContaSol (tutoriales oficiales)
tags:
  - doc/patron
  - app/contasol
  - cliente/comun
  - idioma/es
---

# Patrones de ContaSol

> Origen: «Software DELSOL — ContaSol (tutoriales oficiales)» · 28 patrones. Cada apartado es un patrón con su «Visto en» y su «Se aplica cuando».

## Maestros antes del primer asiento
**Visto en**: Tutorial DELSOL «Alta de cuentas contables, clientes y proveedores en Contasol», 2026-10-06
**Se aplica cuando**: se arranca la contabilidad o la facturación de una empresa en un programa nuevo

Dar de alta cuentas, clientes y proveedores habituales antes de contabilizar permite que los conceptos y
contrapartidas predefinidos rellenen los asientos. Conviene cargarlos de golpe desde un listado del
sistema anterior (o por importación) en lugar de crearlos al vuelo, que es donde nacen duplicados.

## Ficha de tercero en lugar de cuenta suelta
**Visto en**: Tutorial DELSOL «Alta de cuentas contables, clientes y proveedores en Contasol», 2026-10-06
**Se aplica cuando**: hay que crear la subcuenta de un cliente o proveedor

Crear la 430/400 desde Clientes o Proveedores, y no desde el plan de cuentas, guarda NIF, tipo de
operación, retención y contrapartida junto a la cuenta. Esos datos alimentan el libro de IVA, el 347 y
el SII; una cuenta suelta obliga a completarlos después a mano.

## Responder «Sí» a los avisos de creación de cuenta
**Visto en**: Tutorial DELSOL «Alta de cuentas contables, clientes y proveedores en Contasol», 2026-10-06
**Se aplica cuando**: el programa avisa de que una cuenta no existe al guardar una ficha o un asiento

ContaSol pregunta dos veces (contrapartida inexistente y creación de la subcuenta en el plan). El equipo
tiende a cerrar avisos con «No»; hay que formar en que «Sí» es lo esperado y revisar la naturaleza
(Debe/Haber) de la cuenta que se crea.

## Consulta en pantalla para comprobar, listado para archivar
**Visto en**: Tutorial DELSOL «Consulta de libro diario, mayor o sumas y saldos en Contasol», 2026-10-06
**Se aplica cuando**: Se forma al equipo de un cliente en la consulta de la contabilidad de ContaSol

ContaSol ofrece dos caminos para los mismos datos: Diario > Consultas (rejilla en pantalla, rápida, sin
copia) e Impresión > Libros (listado con vista previa, PDF, Excel o Portal documental). Conviene enseñar
cada uno para su uso: pantalla para comprobar un apunte o un saldo, listado cuando el documento tiene que
quedar archivado o enviarse al asesor. Evita PDFs sueltos de consultas y también revisiones a ciegas.

## Sumas y saldos como control previo a cada liquidación
**Visto en**: Tutorial DELSOL «Consulta de libro diario, mayor o sumas y saldos en Contasol», 2026-10-06
**Se aplica cuando**: Se monta la rutina mensual o trimestral de contabilidad de un cliente en ContaSol

Antes de liquidar IVA o retenciones, sacar el balance de sumas y saldos del periodo y comprobar que el total
Debe = Haber y que las cuentas de IVA (472/477) y clientes/proveedores tienen saldos lógicos. Es un control
de un minuto que detecta asientos descuadrados o mal imputados antes de que lleguen a un modelo.

## Pactar con el asesor formato y canal de los libros
**Visto en**: Tutorial DELSOL «Consulta de libro diario, mayor o sumas y saldos en Contasol», 2026-10-06
**Se aplica cuando**: El cliente lleva la contabilidad en casa y la gestoría o asesor externo la revisa

El diario sale en tres formatos (oficial, borrador, resumido por cuentas) y cuatro salidas (vista previa,
PDF, Excel, Portal documental). Preguntar al asesor qué formato y qué canal quiere (por ejemplo, diario
oficial y sumas y saldos en PDF por el Portal documental, con encabezado de límites) y dejarlo fijado en el
procedimiento: evita reenvíos y versiones distintas del mismo libro.

## Fijar el modelo de cuentas anuales según el plan contable del cliente
**Visto en**: Tutorial DELSOL «Consultar Balance de Situación y Balance de Pérdidas y Ganancias en Contasol», 2026-10-06
**Se aplica cuando**: se configura una empresa en ContaSol y se va a sacar balance y PyG para dirección, asesor o Registro Mercantil

ContaSol ofrece una lista larga de modelos (PGC normal, PYMES, abreviados, sectoriales, sin ánimo de lucro)
y el vídeo insiste en elegir «en función del plan general contable que apliques». Hay que preguntar al
cliente o a su asesor qué plan y formato usa, dejarlo anotado en la ficha de la implantación y usar siempre
el mismo modelo en balance y PyG para que los informes sean comparables entre periodos.

## Comprobación cruzada balance ↔ resultado de la PyG
**Visto en**: Tutorial DELSOL «Consultar Balance de Situación y Balance de Pérdidas y Ganancias en Contasol», 2026-10-06
**Se aplica cuando**: se entregan estados financieros intermedios o de cierre generados desde el programa contable

Antes de enviar los informes: activo = patrimonio neto + pasivo, y el «Resultado del ejercicio» del balance
igual al resultado de la PyG del mismo periodo y modelo. Es una comprobación de un minuto que detecta
periodos mal elegidos, cuentas fuera de la estructura del modelo o asientos de cierre pendientes.

## Revisar el libro de IVA antes de liquidar
**Visto en**: Tutorial DELSOL «Consultar libro de IVA en Contasol», 2026-10-06
**Se aplica cuando**: Se implanta la rutina de liquidación de IVA de un cliente en ContaSol

El libro de IVA (repercutido y soportado) se revisa por fecha de registro del periodo justo antes de generar
el 303, y su resumen de base y cuota se cruza con el modelo. Pocas pasadas así detectan facturas con fecha de
registro en el trimestre equivocado o asientos sin registro de IVA, que son los errores más caros de corregir
una vez presentado el modelo.

## Dejar preparado el formato para requerimientos de la AEAT
**Visto en**: Tutorial DELSOL «Consultar libro de IVA en Contasol», 2026-10-06
**Se aplica cuando**: Un cliente puede recibir requerimientos de libros registro y no está en el SII

ContaSol trae formatos específicos de «libro registro de IVA para requerimientos AEAT» y de «facturas
expedidas y de ventas e ingresos». En la implantación conviene enseñar dónde están y probarlos una vez con
datos reales: el día del requerimiento el cliente no pierde tiempo ni entrega el listado básico por error.

## Una consulta en pantalla para cada tipo de IVA, sin mezclar
**Visto en**: Tutorial DELSOL «Consultar libro de IVA en Contasol», 2026-10-06
**Se aplica cuando**: Se forma a personal administrativo nuevo en la consulta del IVA

Repercutido (cliente) y soportado (deudor/proveedor) son libros separados con columnas casi iguales. En la
formación, explicar siempre los dos con el mismo ejemplo de factura emitida y recibida y la columna que cambia:
evita el error habitual de buscar una factura de proveedor en el libro de ventas.

## Contabilizar ventas y compras desde la línea del tercero
**Visto en**: Tutorial DELSOL «Contabilizar asientos en Contasol», 2026-10-06
**Se aplica cuando**: Se forma a un equipo que va a introducir facturas en ContaSol a mano (sin enlace desde FactuSol)

En ContaSol las ventas y compras con IVA están predefinidas: basta con meter la línea del cliente o proveedor con
el total y el programa abre el registro de IVA y el asiento automático. Enseñar solo esa entrada evita el error
típico de quien viene de otro programa: teclear las tres líneas a mano y dejar el libro de IVA vacío.

## Revisar las cuentas por defecto del asiento automático antes de arrancar
**Visto en**: Tutorial DELSOL «Contabilizar asientos en Contasol», 2026-10-06
**Se aplica cuando**: Se pone en marcha la contabilidad de una empresa nueva o migrada en ContaSol

La ventana «Asiento automático de IVA/IGIC» propone cuentas de IVA, ventas, recargo, retenciones y suplidos
(477, 705/700, 473, 555 en la demo). Si no se ajustan en la configuración y en las fichas de clientes antes del
primer asiento, el usuario las acepta sin mirar y hay que reclasificar después. Es una comprobación de la
implantación, no de cada asiento.

## Pedir escrituras y 036 antes de crear la empresa
**Visto en**: Tutorial DELSOL «Creación de empresa en Contasol», 2026-10-06
**Se aplica cuando**: se da de alta una sociedad nueva en un programa contable o de facturación

El alta pide NIF, forma jurídica, Registro Mercantil, apoderados, IAE y CNAE: todo sale de las
escrituras y del alta censal. Pedir esos documentos al cliente antes de la sesión evita dejar campos "de
la que dispongamos" que luego faltan en modelos, libros y cuentas anuales.

## Decisiones irreversibles primero: plan contable, ejercicio y dígitos
**Visto en**: Tutorial DELSOL «Creación de empresa en Contasol», 2026-10-06
**Se aplica cuando**: se configura una contabilidad nueva cuya estructura de cuentas no se podrá cambiar sin coste

El plan (Pymes o normal), el ejercicio (natural o partido) y el número de dígitos de las cuentas
auxiliares se fijan al crear la empresa y cambiarlos con asientos ya hechos obliga a reestructurar. Se
pregunta y se deja por escrito con la asesoría del cliente antes de pulsar Aceptar.

## Revisar los apartados que el tutorial se salta
**Visto en**: Tutorial DELSOL «Creación de empresa en Contasol», 2026-10-06
**Se aplica cuando**: se usa un tutorial del fabricante como base de un procedimiento de configuración

El vídeo pasa por Datos contables, Representantes, Actividades y Cuentas anuales y deja Bloqueos,
Impuestos, Preferencias y Sociedades mercantiles "para vídeos futuros". Impuestos (régimen y
periodicidad de IVA) condiciona el 303 y el 111: en la implantación se recorre cada apartado de la
configuración aunque el tutorial no lo haga.

## Inventario de licencia antes de prometer funciones
**Visto en**: Tutorial DELSOL «Descubre CONTASOL», 2026-10-06
**Se aplica cuando**: el material del fabricante (vídeos, fichas comerciales) muestra funciones que el cliente da por incluidas

El vídeo presenta OCR de facturas, Digital Box, Atenea, SII y presentación por lotes como parte de
ContaSol, pero varias dependen de la licencia o de servicios aparte. Antes de diseñar procesos sobre
ellas, se hace una lista de funciones contratadas frente a funciones vistas y se valida con el
distribuidor; así no se forma al equipo en algo que luego no tiene.

## Guía de orientación como puerta de entrada a la serie de manuales
**Visto en**: Tutorial DELSOL «Descubre CONTASOL», 2026-10-06
**Se aplica cuando**: se implanta una aplicación con muchos módulos y se van a entregar varios manuales paso a paso

Un documento corto (CS-00) que enumera qué hace la aplicación y enlaza cada función con el manual que la
desarrolla evita que el usuario busque en el manual equivocado y deja claro qué queda fuera del
alcance. Funciona aunque el vídeo de origen sea publicitario y no enseñe pantallas de trabajo.

## Configuración AEAT de la empresa antes del primer modelo
**Visto en**: Tutorial DELSOL «Generar y contabilizar liquidación de IVA en Contasol», 2026-10-06
**Se aplica cuando**: Se da de alta una empresa en ContaSol que va a presentar modelos desde el programa

Los modelos oficiales salen con los datos de «Configuración de datos para modelos oficiales» (NIF, razón
social, domicilio, contacto, domiciliación bancaria). Conviene rellenarlos en la implantación, con el
cliente delante y la cuenta de domiciliación confirmada, y no el día del primer vencimiento: es el origen
típico de ficheros rechazados por la AEAT.

## Preguntar por los conceptos que no salen de los registros
**Visto en**: Tutorial DELSOL «Generar y contabilizar liquidación de IVA en Contasol», 2026-10-06
**Se aplica cuando**: Se monta la liquidación periódica de IVA de un cliente en cualquier programa contable

Regularización de inversiones, IVA a la importación liquidado en aduana, prorrata o cuotas a compensar de
periodos anteriores no salen de los registros de IVA y hay que meterlos a mano. En la toma de requisitos hay
que preguntar si el cliente importa, si tiene prorrata o si arrastra saldos a compensar, y dejar quién aporta
esos importes cada trimestre.

## Cerrar el ciclo: presentar y contabilizar en la misma sesión
**Visto en**: Tutorial DELSOL «Generar y contabilizar liquidación de IVA en Contasol», 2026-10-06
**Se aplica cuando**: Se diseña el procedimiento trimestral de impuestos de un cliente

La secuencia que funciona es calcular → grabar → presentar → guardar justificante → generar el asiento de
liquidación desde el propio programa. Si el asiento se deja «para luego» o se mete a mano, las cuentas 472/477
quedan con saldo y la siguiente liquidación arrastra el descuadre. La etiqueta «Generado» de la liquidación es el
control de que el ciclo está cerrado.

## Datos fiscales de la empresa como requisito de arranque
**Visto en**: Tutorial DELSOL «Generar y contabilizar modelo 111», 2026-10-06
**Se aplica cuando**: se pone en marcha la presentación de modelos oficiales (111, 303, 115…) desde ContaSol para una empresa nueva

La «Configuración de datos para modelos oficiales» (NIF, razón social, domicilio, contacto, cuenta de
domiciliación y datos AEAT) es común a todos los modelos y el vídeo la marca como paso previo. Conviene
cumplimentarla y validarla con el cliente en la implantación, no en el primer vencimiento: es la causa más
habitual de rechazo en la sede y de cargos en una cuenta equivocada.

## El modelo solo es tan bueno como lo contabilizado
**Visto en**: Tutorial DELSOL «Generar y contabilizar modelo 111», 2026-10-06
**Se aplica cuando**: el cliente quiere que ContaSol calcule los impuestos a partir de la contabilidad

ContaSol calcula el 111 leyendo el diario, el libro de IVA soportado (registros con retención) y el fichero
de retenciones o de personal. La secuencia que hay que respetar es contabilizar todo el periodo → calcular →
cuadrar con el saldo de la 4751 → presentar. En la implantación hay que preguntar al cliente quién mete las
nóminas y las facturas de profesionales y en qué fecha, para fijar un corte antes del día 20.

## Cerrar el ciclo contable del impuesto con el asiento de pago
**Visto en**: Tutorial DELSOL «Generar y contabilizar modelo 111», 2026-10-06
**Se aplica cuando**: se definen los procedimientos trimestrales de impuestos en ContaSol

El circuito completo es generar → presentar → «Asentar pago» con la fecha real del cargo y un concepto
normalizado («Liquidación modelo 111 3T»). Dejar el asiento al propio programa evita cuentas mal elegidas,
y anotar el número de asiento junto al justificante de la AEAT deja trazabilidad para el punteo bancario y
para las revisiones del asesor.

## La ficha del cliente bien hecha automatiza el asiento
**Visto en**: Tutorial DELSOL «Registro de asientos de ventas en Contasol», 2026-10-06
**Se aplica cuando**: Se dan de alta clientes y proveedores en ContaSol antes de empezar a contabilizar

El concepto («cliente + N. FRA:»), el NIF, el tipo de operación, la inclusión en el 347 y el tipo de IVA del
registro salen de la ficha del tercero. Si el concepto no se rellena solo, el alta está mal. Conviene revisar las
fichas en la implantación: cada dato que falta se convierte en un dato que se teclea (y se equivoca) en cada factura.

## Buscar siempre la cuenta con F1, nunca por coincidencia de texto
**Visto en**: Tutorial DELSOL «Registro de asientos de ventas en Contasol», 2026-10-06
**Se aplica cuando**: Se forma a usuarios que introducen asientos con muchos terceros de nombre parecido

Al escribir un texto en la columna Cuenta y pulsar Intro, ContaSol coge la primera cuenta que coincide (en el
vídeo, «Cliente de contado» en vez del cliente real). Formar en F1 / Más opciones › Buscar cuenta y en comprobar
el número evita asientos a terceros equivocados que luego descuadran mayores y el 347.

## Comprobar los tipos de IVA cargados en la empresa
**Visto en**: Tutorial DELSOL «Registro de asientos de ventas en Contasol», 2026-10-06
**Se aplica cuando**: Se crea o migra una empresa en ContaSol que factura a más de un tipo de IVA

En la empresa de demostración «Varios tipos de IVA» no traía el 21/10/4 cargados: es configuración de la empresa.
Antes de que el cliente contabilice, verificar que los tipos están configurados y probar una factura multitipo;
explicar además que el aviso de descuadre no salta mientras se edita la línea y que al corregir una base hay que
forzar el recálculo de la cuota siguiente.

## Decidir en la implantación efectos, departamentos y cuentas de ventas separadas
**Visto en**: Tutorial DELSOL «Registro de asientos de ventas en Contasol», 2026-10-06
**Se aplica cuando**: Se configura el circuito de ventas de un cliente en ContaSol

Cada asiento de venta puede abrir el diálogo de departamento y el de efecto a cobrar, y el usuario puede crear
cuentas de ventas por tipo de operación al vuelo. Preguntar al cliente si lleva cartera de cobros y analítica por
departamentos, y si quiere ventas intracomunitarias o exportaciones en cuentas propias (el libro de IVA ya da esa
información). Lo que no se use, se desactiva o se documenta como «cerrar sin guardar» en el manual.

## Historial de cambios

| Versión | Fecha | Cambio | Autoría |
|---|---|---|---|
| 0.1 | 2026-10-06 | Creado desde patrones-acumulados.md | Jorge Herrera |
