# Patrones acumulados

Generado y actualizado con `scripts/consolidar-patrones.py`. La idea: la
primera vez que aparece un patrón es una anécdota de un proyecto; la
segunda, deja de serlo. Este fichero es donde se nota.

No se edita a mano el contenido de cada patrón — se vuelve a generar si
cambia el `Analisis/Patrones reutilizables.md` de origen. Sí se puede
fusionar a mano el título de dos patrones que resulten ser el mismo visto
en proyectos distintos: mueve las líneas "Visto en" de uno bajo el otro y
borra el duplicado.

<!-- consolidar-patrones.py añade aquí un "## Del proyecto: <nombre>" por
     cada Analisis/Patrones reutilizables.md que procese -->

## Del proyecto: Software DELSOL — ContaSol (tutoriales oficiales)

### Maestros antes del primer asiento
**Visto en**: Tutorial DELSOL «Alta de cuentas contables, clientes y proveedores en Contasol», 2026-10-06
**Se aplica cuando**: se arranca la contabilidad o la facturación de una empresa en un programa nuevo

Dar de alta cuentas, clientes y proveedores habituales antes de contabilizar permite que los conceptos y
contrapartidas predefinidos rellenen los asientos. Conviene cargarlos de golpe desde un listado del
sistema anterior (o por importación) en lugar de crearlos al vuelo, que es donde nacen duplicados.

### Ficha de tercero en lugar de cuenta suelta
**Visto en**: Tutorial DELSOL «Alta de cuentas contables, clientes y proveedores en Contasol», 2026-10-06
**Se aplica cuando**: hay que crear la subcuenta de un cliente o proveedor

Crear la 430/400 desde Clientes o Proveedores, y no desde el plan de cuentas, guarda NIF, tipo de
operación, retención y contrapartida junto a la cuenta. Esos datos alimentan el libro de IVA, el 347 y
el SII; una cuenta suelta obliga a completarlos después a mano.

### Responder «Sí» a los avisos de creación de cuenta
**Visto en**: Tutorial DELSOL «Alta de cuentas contables, clientes y proveedores en Contasol», 2026-10-06
**Se aplica cuando**: el programa avisa de que una cuenta no existe al guardar una ficha o un asiento

ContaSol pregunta dos veces (contrapartida inexistente y creación de la subcuenta en el plan). El equipo
tiende a cerrar avisos con «No»; hay que formar en que «Sí» es lo esperado y revisar la naturaleza
(Debe/Haber) de la cuenta que se crea.

### Consulta en pantalla para comprobar, listado para archivar
**Visto en**: Tutorial DELSOL «Consulta de libro diario, mayor o sumas y saldos en Contasol», 2026-10-06
**Se aplica cuando**: Se forma al equipo de un cliente en la consulta de la contabilidad de ContaSol

ContaSol ofrece dos caminos para los mismos datos: Diario > Consultas (rejilla en pantalla, rápida, sin
copia) e Impresión > Libros (listado con vista previa, PDF, Excel o Portal documental). Conviene enseñar
cada uno para su uso: pantalla para comprobar un apunte o un saldo, listado cuando el documento tiene que
quedar archivado o enviarse al asesor. Evita PDFs sueltos de consultas y también revisiones a ciegas.

### Sumas y saldos como control previo a cada liquidación
**Visto en**: Tutorial DELSOL «Consulta de libro diario, mayor o sumas y saldos en Contasol», 2026-10-06
**Se aplica cuando**: Se monta la rutina mensual o trimestral de contabilidad de un cliente en ContaSol

Antes de liquidar IVA o retenciones, sacar el balance de sumas y saldos del periodo y comprobar que el total
Debe = Haber y que las cuentas de IVA (472/477) y clientes/proveedores tienen saldos lógicos. Es un control
de un minuto que detecta asientos descuadrados o mal imputados antes de que lleguen a un modelo.

### Pactar con el asesor formato y canal de los libros
**Visto en**: Tutorial DELSOL «Consulta de libro diario, mayor o sumas y saldos en Contasol», 2026-10-06
**Se aplica cuando**: El cliente lleva la contabilidad en casa y la gestoría o asesor externo la revisa

El diario sale en tres formatos (oficial, borrador, resumido por cuentas) y cuatro salidas (vista previa,
PDF, Excel, Portal documental). Preguntar al asesor qué formato y qué canal quiere (por ejemplo, diario
oficial y sumas y saldos en PDF por el Portal documental, con encabezado de límites) y dejarlo fijado en el
procedimiento: evita reenvíos y versiones distintas del mismo libro.

### Fijar el modelo de cuentas anuales según el plan contable del cliente
**Visto en**: Tutorial DELSOL «Consultar Balance de Situación y Balance de Pérdidas y Ganancias en Contasol», 2026-10-06
**Se aplica cuando**: se configura una empresa en ContaSol y se va a sacar balance y PyG para dirección, asesor o Registro Mercantil

ContaSol ofrece una lista larga de modelos (PGC normal, PYMES, abreviados, sectoriales, sin ánimo de lucro)
y el vídeo insiste en elegir «en función del plan general contable que apliques». Hay que preguntar al
cliente o a su asesor qué plan y formato usa, dejarlo anotado en la ficha de la implantación y usar siempre
el mismo modelo en balance y PyG para que los informes sean comparables entre periodos.

### Comprobación cruzada balance ↔ resultado de la PyG
**Visto en**: Tutorial DELSOL «Consultar Balance de Situación y Balance de Pérdidas y Ganancias en Contasol», 2026-10-06
**Se aplica cuando**: se entregan estados financieros intermedios o de cierre generados desde el programa contable

Antes de enviar los informes: activo = patrimonio neto + pasivo, y el «Resultado del ejercicio» del balance
igual al resultado de la PyG del mismo periodo y modelo. Es una comprobación de un minuto que detecta
periodos mal elegidos, cuentas fuera de la estructura del modelo o asientos de cierre pendientes.

### Revisar el libro de IVA antes de liquidar
**Visto en**: Tutorial DELSOL «Consultar libro de IVA en Contasol», 2026-10-06
**Se aplica cuando**: Se implanta la rutina de liquidación de IVA de un cliente en ContaSol

El libro de IVA (repercutido y soportado) se revisa por fecha de registro del periodo justo antes de generar
el 303, y su resumen de base y cuota se cruza con el modelo. Pocas pasadas así detectan facturas con fecha de
registro en el trimestre equivocado o asientos sin registro de IVA, que son los errores más caros de corregir
una vez presentado el modelo.

### Dejar preparado el formato para requerimientos de la AEAT
**Visto en**: Tutorial DELSOL «Consultar libro de IVA en Contasol», 2026-10-06
**Se aplica cuando**: Un cliente puede recibir requerimientos de libros registro y no está en el SII

ContaSol trae formatos específicos de «libro registro de IVA para requerimientos AEAT» y de «facturas
expedidas y de ventas e ingresos». En la implantación conviene enseñar dónde están y probarlos una vez con
datos reales: el día del requerimiento el cliente no pierde tiempo ni entrega el listado básico por error.

### Una consulta en pantalla para cada tipo de IVA, sin mezclar
**Visto en**: Tutorial DELSOL «Consultar libro de IVA en Contasol», 2026-10-06
**Se aplica cuando**: Se forma a personal administrativo nuevo en la consulta del IVA

Repercutido (cliente) y soportado (deudor/proveedor) son libros separados con columnas casi iguales. En la
formación, explicar siempre los dos con el mismo ejemplo de factura emitida y recibida y la columna que cambia:
evita el error habitual de buscar una factura de proveedor en el libro de ventas.

### Contabilizar ventas y compras desde la línea del tercero
**Visto en**: Tutorial DELSOL «Contabilizar asientos en Contasol», 2026-10-06
**Se aplica cuando**: Se forma a un equipo que va a introducir facturas en ContaSol a mano (sin enlace desde FactuSol)

En ContaSol las ventas y compras con IVA están predefinidas: basta con meter la línea del cliente o proveedor con
el total y el programa abre el registro de IVA y el asiento automático. Enseñar solo esa entrada evita el error
típico de quien viene de otro programa: teclear las tres líneas a mano y dejar el libro de IVA vacío.

### Revisar las cuentas por defecto del asiento automático antes de arrancar
**Visto en**: Tutorial DELSOL «Contabilizar asientos en Contasol», 2026-10-06
**Se aplica cuando**: Se pone en marcha la contabilidad de una empresa nueva o migrada en ContaSol

La ventana «Asiento automático de IVA/IGIC» propone cuentas de IVA, ventas, recargo, retenciones y suplidos
(477, 705/700, 473, 555 en la demo). Si no se ajustan en la configuración y en las fichas de clientes antes del
primer asiento, el usuario las acepta sin mirar y hay que reclasificar después. Es una comprobación de la
implantación, no de cada asiento.

### Pedir escrituras y 036 antes de crear la empresa
**Visto en**: Tutorial DELSOL «Creación de empresa en Contasol», 2026-10-06
**Se aplica cuando**: se da de alta una sociedad nueva en un programa contable o de facturación

El alta pide NIF, forma jurídica, Registro Mercantil, apoderados, IAE y CNAE: todo sale de las
escrituras y del alta censal. Pedir esos documentos al cliente antes de la sesión evita dejar campos "de
la que dispongamos" que luego faltan en modelos, libros y cuentas anuales.

### Decisiones irreversibles primero: plan contable, ejercicio y dígitos
**Visto en**: Tutorial DELSOL «Creación de empresa en Contasol», 2026-10-06
**Se aplica cuando**: se configura una contabilidad nueva cuya estructura de cuentas no se podrá cambiar sin coste

El plan (Pymes o normal), el ejercicio (natural o partido) y el número de dígitos de las cuentas
auxiliares se fijan al crear la empresa y cambiarlos con asientos ya hechos obliga a reestructurar. Se
pregunta y se deja por escrito con la asesoría del cliente antes de pulsar Aceptar.

### Revisar los apartados que el tutorial se salta
**Visto en**: Tutorial DELSOL «Creación de empresa en Contasol», 2026-10-06
**Se aplica cuando**: se usa un tutorial del fabricante como base de un procedimiento de configuración

El vídeo pasa por Datos contables, Representantes, Actividades y Cuentas anuales y deja Bloqueos,
Impuestos, Preferencias y Sociedades mercantiles "para vídeos futuros". Impuestos (régimen y
periodicidad de IVA) condiciona el 303 y el 111: en la implantación se recorre cada apartado de la
configuración aunque el tutorial no lo haga.

### Inventario de licencia antes de prometer funciones
**Visto en**: Tutorial DELSOL «Descubre CONTASOL», 2026-10-06
**Se aplica cuando**: el material del fabricante (vídeos, fichas comerciales) muestra funciones que el cliente da por incluidas

El vídeo presenta OCR de facturas, Digital Box, Atenea, SII y presentación por lotes como parte de
ContaSol, pero varias dependen de la licencia o de servicios aparte. Antes de diseñar procesos sobre
ellas, se hace una lista de funciones contratadas frente a funciones vistas y se valida con el
distribuidor; así no se forma al equipo en algo que luego no tiene.

### Guía de orientación como puerta de entrada a la serie de manuales
**Visto en**: Tutorial DELSOL «Descubre CONTASOL», 2026-10-06
**Se aplica cuando**: se implanta una aplicación con muchos módulos y se van a entregar varios manuales paso a paso

Un documento corto (CS-00) que enumera qué hace la aplicación y enlaza cada función con el manual que la
desarrolla evita que el usuario busque en el manual equivocado y deja claro qué queda fuera del
alcance. Funciona aunque el vídeo de origen sea publicitario y no enseñe pantallas de trabajo.

### Configuración AEAT de la empresa antes del primer modelo
**Visto en**: Tutorial DELSOL «Generar y contabilizar liquidación de IVA en Contasol», 2026-10-06
**Se aplica cuando**: Se da de alta una empresa en ContaSol que va a presentar modelos desde el programa

Los modelos oficiales salen con los datos de «Configuración de datos para modelos oficiales» (NIF, razón
social, domicilio, contacto, domiciliación bancaria). Conviene rellenarlos en la implantación, con el
cliente delante y la cuenta de domiciliación confirmada, y no el día del primer vencimiento: es el origen
típico de ficheros rechazados por la AEAT.

### Preguntar por los conceptos que no salen de los registros
**Visto en**: Tutorial DELSOL «Generar y contabilizar liquidación de IVA en Contasol», 2026-10-06
**Se aplica cuando**: Se monta la liquidación periódica de IVA de un cliente en cualquier programa contable

Regularización de inversiones, IVA a la importación liquidado en aduana, prorrata o cuotas a compensar de
periodos anteriores no salen de los registros de IVA y hay que meterlos a mano. En la toma de requisitos hay
que preguntar si el cliente importa, si tiene prorrata o si arrastra saldos a compensar, y dejar quién aporta
esos importes cada trimestre.

### Cerrar el ciclo: presentar y contabilizar en la misma sesión
**Visto en**: Tutorial DELSOL «Generar y contabilizar liquidación de IVA en Contasol», 2026-10-06
**Se aplica cuando**: Se diseña el procedimiento trimestral de impuestos de un cliente

La secuencia que funciona es calcular → grabar → presentar → guardar justificante → generar el asiento de
liquidación desde el propio programa. Si el asiento se deja «para luego» o se mete a mano, las cuentas 472/477
quedan con saldo y la siguiente liquidación arrastra el descuadre. La etiqueta «Generado» de la liquidación es el
control de que el ciclo está cerrado.

### Datos fiscales de la empresa como requisito de arranque
**Visto en**: Tutorial DELSOL «Generar y contabilizar modelo 111», 2026-10-06
**Se aplica cuando**: se pone en marcha la presentación de modelos oficiales (111, 303, 115…) desde ContaSol para una empresa nueva

La «Configuración de datos para modelos oficiales» (NIF, razón social, domicilio, contacto, cuenta de
domiciliación y datos AEAT) es común a todos los modelos y el vídeo la marca como paso previo. Conviene
cumplimentarla y validarla con el cliente en la implantación, no en el primer vencimiento: es la causa más
habitual de rechazo en la sede y de cargos en una cuenta equivocada.

### El modelo solo es tan bueno como lo contabilizado
**Visto en**: Tutorial DELSOL «Generar y contabilizar modelo 111», 2026-10-06
**Se aplica cuando**: el cliente quiere que ContaSol calcule los impuestos a partir de la contabilidad

ContaSol calcula el 111 leyendo el diario, el libro de IVA soportado (registros con retención) y el fichero
de retenciones o de personal. La secuencia que hay que respetar es contabilizar todo el periodo → calcular →
cuadrar con el saldo de la 4751 → presentar. En la implantación hay que preguntar al cliente quién mete las
nóminas y las facturas de profesionales y en qué fecha, para fijar un corte antes del día 20.

### Cerrar el ciclo contable del impuesto con el asiento de pago
**Visto en**: Tutorial DELSOL «Generar y contabilizar modelo 111», 2026-10-06
**Se aplica cuando**: se definen los procedimientos trimestrales de impuestos en ContaSol

El circuito completo es generar → presentar → «Asentar pago» con la fecha real del cargo y un concepto
normalizado («Liquidación modelo 111 3T»). Dejar el asiento al propio programa evita cuentas mal elegidas,
y anotar el número de asiento junto al justificante de la AEAT deja trazabilidad para el punteo bancario y
para las revisiones del asesor.

### La ficha del cliente bien hecha automatiza el asiento
**Visto en**: Tutorial DELSOL «Registro de asientos de ventas en Contasol», 2026-10-06
**Se aplica cuando**: Se dan de alta clientes y proveedores en ContaSol antes de empezar a contabilizar

El concepto («cliente + N. FRA:»), el NIF, el tipo de operación, la inclusión en el 347 y el tipo de IVA del
registro salen de la ficha del tercero. Si el concepto no se rellena solo, el alta está mal. Conviene revisar las
fichas en la implantación: cada dato que falta se convierte en un dato que se teclea (y se equivoca) en cada factura.

### Buscar siempre la cuenta con F1, nunca por coincidencia de texto
**Visto en**: Tutorial DELSOL «Registro de asientos de ventas en Contasol», 2026-10-06
**Se aplica cuando**: Se forma a usuarios que introducen asientos con muchos terceros de nombre parecido

Al escribir un texto en la columna Cuenta y pulsar Intro, ContaSol coge la primera cuenta que coincide (en el
vídeo, «Cliente de contado» en vez del cliente real). Formar en F1 / Más opciones › Buscar cuenta y en comprobar
el número evita asientos a terceros equivocados que luego descuadran mayores y el 347.

### Comprobar los tipos de IVA cargados en la empresa
**Visto en**: Tutorial DELSOL «Registro de asientos de ventas en Contasol», 2026-10-06
**Se aplica cuando**: Se crea o migra una empresa en ContaSol que factura a más de un tipo de IVA

En la empresa de demostración «Varios tipos de IVA» no traía el 21/10/4 cargados: es configuración de la empresa.
Antes de que el cliente contabilice, verificar que los tipos están configurados y probar una factura multitipo;
explicar además que el aviso de descuadre no salta mientras se edita la línea y que al corregir una base hay que
forzar el recálculo de la cuota siguiente.

### Decidir en la implantación efectos, departamentos y cuentas de ventas separadas
**Visto en**: Tutorial DELSOL «Registro de asientos de ventas en Contasol», 2026-10-06
**Se aplica cuando**: Se configura el circuito de ventas de un cliente en ContaSol

Cada asiento de venta puede abrir el diálogo de departamento y el de efecto a cobrar, y el usuario puede crear
cuentas de ventas por tipo de operación al vuelo. Preguntar al cliente si lleva cartera de cobros y analítica por
departamentos, y si quiere ventas intracomunitarias o exportaciones en cuentas propias (el libro de IVA ya da esa
información). Lo que no se use, se desactiva o se documenta como «cerrar sin guardar» en el manual.


## Del proyecto: Software DELSOL — FactuSol (tutoriales oficiales)

### Decidir el mapa de series antes del primer documento
**Visto en**: Tutorial DELSOL «Creación de un presupuesto», 2026-10-06
**Se aplica cuando**: se pone en marcha la facturación de un cliente con FactuSol (o ContaSol) y hay varias tiendas, líneas de negocio o tipos de venta

FactuSol tiene hasta 9 series independientes por tipo de documento, y cada usuario elige la serie al crear el documento. Si no se fija antes qué serie corresponde a qué (tienda, canal, tipo de cliente), cada persona usa una distinta y luego los informes y la numeración no cuadran. Pregunta al cliente y deja la tabla de series escrita en el manual de arranque.

### Concepto manual solo para lo que no es artículo
**Visto en**: Tutorial DELSOL «Creación de un presupuesto», 2026-10-06
**Se aplica cuando**: el cliente quiere teclear líneas libres en presupuestos, albaranes o facturas

Una línea sin código de artículo (Enter en el código y texto en Descripción) es cómoda, pero no mueve stock, no cuenta en estadísticas por artículo y su IVA se pone a mano. Conviene dar de alta como artículos los servicios recurrentes (portes, mano de obra, preparación) y reservar el concepto manual para textos o casos excepcionales.

### Hacer el presupuesto en el ERP para no volver a teclear
**Visto en**: Tutorial DELSOL «Creación de un presupuesto», 2026-10-06
**Se aplica cuando**: el cliente hace las ofertas en Word o Excel y factura después en FactuSol

Si el presupuesto se hace dentro de FactuSol, al aceptarse se valida en pedido, albarán o factura sin copiar líneas. Es uno de los argumentos de implantación más claros: elimina errores de transcripción y deja la trazabilidad oferta → factura. Rellenar plazo de entrega y validez en Otros datos para que salgan en el impreso.

### Decidir el tipo de gestión antes de crear la empresa
**Visto en**: Tutorial DELSOL «Creación de una empresa en FACTUSOL», 2026-10-06
**Se aplica cuando**: se arranca FactuSol en un cliente nuevo y hay que elegir entre gestión comercial con stock y facturación de servicios

El tipo de gestión cambia menús, documentos y hasta las opciones de la ventana de configuración.
Preguntar al cliente en la reunión de arranque: ¿compra y almacena producto? ¿factura cuotas
periódicas u horas? ¿necesita albaranes y pedidos? Con esas respuestas se elige y se deja escrito;
cambiarlo con documentos ya emitidos obliga a rehacer la empresa.

### La configuración de empresa es un checklist de arranque, no un trámite
**Visto en**: Tutorial DELSOL «Creación de una empresa en FACTUSOL», 2026-10-06
**Se aplica cuando**: se crea una empresa en un programa DELSOL y hay funciones que solo aparecen si se activan

Varias funciones (trazabilidad, tallas y colores, dimensiones, partes de reparación, costes de obra,
abonos, devoluciones, campos de descuento/portes) no existen en los menús hasta marcarlas. Recorrer
cada casilla con el cliente como preguntas cerradas evita la incidencia típica de "el programa no
tiene X" semanas después, y también evita activar de más y cargar la entrada de documentos.

### Alinear el enlace contable con la contabilidad desde el primer día
**Visto en**: Tutorial DELSOL «Creación de una empresa en FACTUSOL», 2026-10-06
**Se aplica cuando**: la facturación (FactuSol) va a traspasar facturas a una contabilidad (ContaSol o la de la asesoría)

El número de dígitos de las subcuentas debe coincidir con el plan de cuentas de la contabilidad.
Preguntarlo a la asesoría antes de crear la empresa y antes de dar de alta clientes, porque las
subcuentas de cliente y proveedor se generan con esa longitud y un desajuste se arrastra a cada traspaso.

### Una empresa, muchos ejercicios
**Visto en**: Tutorial DELSOL «Creación de una empresa en FACTUSOL», 2026-10-06
**Se aplica cuando**: el cliente viene de programas o costumbres en las que se duplicaba la empresa cada año

En los programas DELSOL el código de empresa vale para todos sus ejercicios; el cambio de año se hace
dentro de la misma empresa. Conviene decirlo en la formación inicial y fijar un código de empresa
corto y estable, porque es la referencia para copias, enlaces y soporte.

### Validar documentos en lugar de copiarlos
**Visto en**: Tutorial DELSOL «Creación de una factura validando un presupuesto», 2026-10-06
**Se aplica cuando**: el cliente encadena documentos de venta o compra (presupuesto → pedido → albarán → factura)

En FactuSol cualquier documento posterior puede «validar» las líneas de uno anterior del mismo cliente (icono Validar del grupo Líneas). Así no se reteclea nada, se pueden traer solo algunas líneas y el documento de origen permanece enlazado. Hay que enseñarlo desde el primer día: si el equipo copia a mano, aparecen precios distintos y documentos de origen que nunca se cierran.

### Cliente primero, documento de origen después
**Visto en**: Tutorial DELSOL «Creación de una factura validando un presupuesto», 2026-10-06
**Se aplica cuando**: se forma a usuarios en la facturación desde documentos previos

La ventana de validación solo ofrece documentos del cliente que ya está en la cabecera (y del ejercicio elegido). El orden correcto es serie → cliente → Validar → tipo y número. Cuando un usuario dice «no me sale el presupuesto», casi siempre es otro cliente u otro ejercicio.

### Revisar Totales antes de grabar una factura que viene de otro documento
**Visto en**: Tutorial DELSOL «Creación de una factura validando un presupuesto», 2026-10-06
**Se aplica cuando**: se factura validando presupuestos o pedidos antiguos

Las líneas llegan del documento de origen, pero la forma de pago, los vencimientos y los descuentos de pie pueden no ser los vigentes. El propio tutorial recomienda abrir Totales y Otros datos antes de guardar; en una factura esto afecta a cobros y, con Verifactu, una vez emitida ya no se corrige sin rectificativa.

### Código de cliente automático y código contable solo por excepción
**Visto en**: Tutorial DELSOL «Creación de una ficha de cliente», 2026-10-06
**Se aplica cuando**: se definen las reglas de alta de clientes o proveedores en un programa de facturación enlazado con contabilidad

Dejar que el programa asigne el código evita huecos y duplicados, y que el código de cliente sea la
subcuenta contable mantiene una correspondencia directa con ContaSol. El código contable propio solo
se usa cuando la asesoría ya tiene subcuentas que hay que respetar (por ejemplo, migraciones). Conviene
decidirlo con la asesoría antes de cargar el fichero de clientes.

### Ficha completa en el alta, no en la primera factura
**Visto en**: Tutorial DELSOL «Creación de una ficha de cliente», 2026-10-06
**Se aplica cuando**: el equipo de administración empieza a dar de alta clientes en un programa nuevo

La forma de pago, la tarifa, los impuestos especiales y las opciones (factura electrónica, recibo al
facturar) se heredan en cada documento desde la ficha. Recorrer las vistas General, Comercial y Otros
datos en el alta evita facturas con vencimientos o impuestos mal y correcciones posteriores. Una
checklist corta de datos a pedir al cliente (NIF, nombre fiscal exacto, email de facturación, forma
de pago, IBAN) acelera el alta.

### Buscar antes de crear
**Visto en**: Tutorial DELSOL «Creación de una ficha de cliente», 2026-10-06
**Se aplica cuando**: varias personas dan de alta terceros en el mismo fichero

El fichero de clientes se abre con la lista de los ya existentes y un buscador: comprobar por NIF antes
de pulsar Nuevo evita fichas duplicadas que parten el histórico de ventas, los riesgos y el modelo 347.
Es una regla de una línea que conviene poner en la formación y en el manual del cliente.

### Copiar el modelo de fábrica, nunca editarlo
**Visto en**: Tutorial DELSOL «Diseño de un modelo de factura», 2026-10-06
**Se aplica cuando**: hay que personalizar facturas, albaranes, presupuestos o informes en software con plantillas de fábrica

El modelo propio se crea con Nuevo a partir de un modelo base (estilo e impuestos), con código y nombre
propios. Así el de fábrica queda intacto para volver a empezar si el diseño se estropea, y las actualizaciones
del programa no pisan el trabajo hecho. Elegir bien el modelo base (IVA, IVA + IRPF, IGIC) ahorra rehacer campos.

### Pedir el logotipo y los textos legales antes de la sesión de diseño
**Visto en**: Tutorial DELSOL «Diseño de un modelo de factura», 2026-10-06
**Se aplica cuando**: se prepara la puesta en marcha de la facturación de un cliente nuevo

El diseño necesita el archivo de logotipo en una ruta estable (en el tutorial se carga desde una carpeta
del disco con Examinar; por prudencia se trata como si dependiera de esa ruta) y los textos que debe llevar la factura (garantías, condiciones, pie legal).
Pedirlos en la toma de requisitos evita sesiones de diseño a medias y logos que desaparecen al mover carpetas.

### Una sola ventana de emisión para todos los informes
**Visto en**: Tutorial DELSOL «Emisión de un informe», 2026-10-06
**Se aplica cuando**: hay que formar a usuarios en la obtención de listados en programas de Software DELSOL

Todos los listados (solapa Impresión, grupos Compras, Ventas, Almacén, Administración) comparten la misma
ventana: salida a la izquierda (impresora, vista previa, PDF, Excel/Calc, RTF/DOC, Portal Documental),
Opciones, Ordenación, Clasificación, Intervalos y Encabezado. Se enseña una vez con un informe que el cliente
use de verdad y el resto se aprende solo.

### Acordar con la asesoría qué informe y qué intervalos se le envían
**Visto en**: Tutorial DELSOL «Emisión de un informe», 2026-10-06
**Se aplica cuando**: el cliente envía periódicamente listados de facturación a su asesoría o a dirección

El mismo listado tiene varios formatos (libro de facturas emitidas, rectificativas, oficial, listado
auxiliar) y los intervalos por defecto cubren todo el ejercicio. Conviene fijar por escrito qué formato,
orden e intervalos se mandan cada periodo y comprobarlos siempre en vista previa, para no enviar el informe
equivocado o un periodo de más.

### Elegir el método de facturación de albaranes según el ritmo del cliente
**Visto en**: Tutorial DELSOL «Facturación automática de albaranes», 2026-10-06
**Se aplica cuando**: el cliente sirve con albarán y factura después (distribución, mayoristas, servicios recurrentes)

FactuSol ofrece tres caminos: validar un albarán en una factura nueva (al momento), seleccionar albaranes en su fichero y pulsar Factura (un cliente o pocos), y Administración > Generación (cierre de periodo masivo, por fechas, clientes, forma de pago o agentes). En la implantación hay que decidir con el cliente cuál es el proceso estándar y escribirlo; mezclar los tres sin criterio provoca albaranes olvidados o facturados dos veces.

### Pregunta clave: ¿una factura por albarán o agrupada?
**Visto en**: Tutorial DELSOL «Facturación automática de albaranes», 2026-10-06
**Se aplica cuando**: se configura la facturación periódica de albaranes de un cliente

Los modos de Generación existen «con» y «sin» agrupar. Antes del primer cierre hay que preguntar al cliente qué espera recibir cada uno de sus clientes (factura mensual con todos los albaranes o una por entrega) y reflejarlo en el procedimiento; es la causa más común de quejas en el primer mes.

### Traspasar los cobros del albarán a la factura
**Visto en**: Tutorial DELSOL «Facturación automática de albaranes», 2026-10-06
**Se aplica cuando**: hay albaranes cobrados total o parcialmente en la entrega (contado, tarjeta)

La ventana de facturación por número de albarán trae marcada la opción «Traspasar movimientos de cobro de albaranes a facturas». Debe quedarse así: si se desmarca, la factura nace pendiente de cobro aunque el albarán ya estuviera pagado, y la cartera de cobros y las reclamaciones salen mal.

### Revisar «Pendientes de facturar» antes de cada cierre
**Visto en**: Tutorial DELSOL «Facturación automática de albaranes», 2026-10-06
**Se aplica cuando**: se hace el cierre de facturación mensual o quincenal con FactuSol

El fichero de albaranes filtra por estado (Pendientes de facturar / Facturados) y muestra la columna FACT. Antes de lanzar la generación masiva conviene revisar esa lista (precios a cero, clientes equivocados, albaranes que no tocan) y después comprobar que ha quedado vacía. Es la secuencia que evita facturas erróneas que, con Verifactu, solo se arreglan con abonos.

### Configurar el catálogo antes de cargar conceptos recurrentes
**Visto en**: Tutorial DELSOL «Facturación periódica», 2026-10-06
**Se aplica cuando**: un cliente factura cuotas fijas (igualas, mantenimientos, asesoría) y se va a montar la facturación periódica

FactuSol obliga a decidir primero, en la configuración del fichero de clientes, si los conceptos salen del
fichero de artículos o del de servicios, si el precio es modificable por cliente y qué tipos de concepto
existen (hasta seis). Cambiar esa decisión con cientos de conceptos cargados es caro, así que se fija en la
primera sesión de implantación junto con el catálogo de servicios.

### Tipos de concepto como líneas de negocio para facturar por lotes
**Visto en**: Tutorial DELSOL «Facturación periódica», 2026-10-06
**Se aplica cuando**: la empresa tiene varias líneas de servicio (laboral, contable, fiscal, seguros…) que se facturan en momentos o con criterios distintos

Los tipos de concepto facturables permiten lanzar la generación periódica solo para una o varias líneas
(en el tutorial, Laboral y Contable) y acotar por rango de clientes. Conviene preguntar al cliente cómo
agrupa hoy su facturación y trasladarlo a tipos e identificadores antes de cargar conceptos.

### Generación masiva con red de seguridad
**Visto en**: Tutorial DELSOL «Facturación periódica», 2026-10-06
**Se aplica cuando**: se lanza un proceso que crea muchas facturas de golpe en cualquier software de facturación

Tres protecciones que conviene dejar fijadas en el procedimiento: numeración desde el contador de la serie
(factura inicial a 0), «No facturar conceptos ya facturados» siempre marcada y fecha de factura igual a la
del periodo, no a la del día de ejecución. Y revisar el informe previo o las facturas generadas antes de
enviarlas.

### Suplidos fuera de la base imponible, en su casilla
**Visto en**: Tutorial DELSOL «Gestión de suplidos en empresas de facturación de servicios», 2026-10-06
**Se aplica cuando**: el cliente (asesoría, gestoría, despacho) adelanta pagos en nombre de sus clientes y los repercute en factura

FactuSol separa los suplidos de las líneas: se registran en Totales > Suplidos (hasta seis por factura) con
fecha, perceptor, NIF, factura del perceptor, concepto e importe, y suman al total sin entrar en la base del
IVA. En la implantación hay que detectar si el cliente hoy los mete como líneas con IVA y cortar esa
costumbre desde el primer día.

### Una funcionalidad nueva obliga a revisar el diseño de impresión
**Visto en**: Tutorial DELSOL «Gestión de suplidos en empresas de facturación de servicios», 2026-10-06
**Se aplica cuando**: se activa en FactuSol o ContaSol un dato nuevo en los documentos (suplidos, retenciones, textos legales)

Que un dato esté grabado no significa que salga impreso: el campo tiene que estar en el modelo de impresión.
Cada vez que se pone en marcha un dato nuevo en las facturas, el checklist de implantación incluye abrir el
diseño, añadir el campo y comprobar en vista previa con una factura real antes de enviarla.

### El tipo de empresa decide la interfaz
**Visto en**: Tutorial DELSOL «Introduccion a FACTUSOL - Conoce su interfaz», 2026-10-06
**Se aplica cuando**: se da de alta una empresa en FactuSol y hay que elegir entre gestión comercial con stock y facturación de servicios

El tipo elegido al crear la empresa cambia las solapas: en servicios desaparece Almacén y aparecen gastos,
servicios y facturación periódica. Hay que preguntar al cliente si vende producto con stock, servicios o
ambos **antes** de crear la empresa, y documentar la elección: los manuales y la formación dependen de ella.

### Formar por solapa y grupo, no por botón
**Visto en**: Tutorial DELSOL «Introduccion a FACTUSOL - Conoce su interfaz», 2026-10-06
**Se aplica cuando**: se forma a usuarios nuevos o se escriben manuales de ContaSol/FactuSol (interfaz de cinta)

La cinta de DELSOL agrupa los botones en grupos con nombre (Compras, Ventas, Cobros, Ficheros…). Enseñar
«solapa → grupo → botón» da al usuario un mapa estable que aguanta cambios de versión y le permite encontrar
solo lo que no se le ha enseñado. Una sesión inicial de 15 minutos de recorrido de solapas ahorra consultas
después.

### Comprobar empresa y ejercicio en la barra de título
**Visto en**: Tutorial DELSOL «Introduccion a FACTUSOL - Conoce su interfaz», 2026-10-06
**Se aplica cuando**: el cliente tiene varias empresas o varios ejercicios abiertos en el mismo programa

La barra de título muestra código de empresa, nombre y ejercicio activo. Convertir «mirar la barra de título
antes de grabar» en hábito (y ponerlo como primer paso de cada protocolo de grabación) evita el error más caro
del arranque: documentos en la empresa o el ejercicio equivocados, sobre todo en el cambio de año.

