# Simulador de Producción de Impresoras 3D

## [PORTADA]
*Título: Simulador de Producción de Impresoras 3D*  
*Nombres: [Espacio para nombres de integrantes]*  
*Fecha: [Fecha de entrega]*  
*Asignatura: Sistemas de Información*

---

## Índice
1. [Introducción](#introducción)
2. [Objetivos del proyecto](#objetivos-del-proyecto)
3. [Análisis de requisitos](#análisis-de-requisitos)
4. [Modelo de datos](#modelo-de-datos)
5. [Tecnologías empleadas](#tecnologías-empleadas)
6. [Arquitectura del sistema](#arquitectura-del-sistema)
7. [Implementación](#implementación)
8. [Pruebas](#pruebas)
9. [Manual de usuario](#manual-de-usuario)
10. [Conclusiones](#conclusiones)
11. [Referencias](#referencias)
12. [Anexos](#anexos)

---

## Introducción

Este documento describe el desarrollo de un simulador de producción para una planta que fabrica impresoras 3D. El sistema permite gestionar el ciclo completo de producción día a día, centrándose en la gestión de inventarios, compras y planificación de la producción. El usuario asume el rol de planificador, tomando decisiones sobre qué fabricar y qué comprar.

---

## Objetivos del proyecto

- Desarrollar un sistema que simule el funcionamiento diario de una planta de producción de impresoras 3D.
- Implementar mecanismos para la gestión eficiente de inventarios y compras.
- Permitir la planificación de la producción basada en la demanda.
- Proporcionar una interfaz de usuario intuitiva y funcional.
- Generar datos históricos y métricas de rendimiento.
- Ofrecer una API REST para integración con otros sistemas.

---

## Análisis de requisitos

### Requisitos funcionales

1. Definición de condiciones iniciales:
   - Plan de producción (materiales necesarios y tiempo en cadena de montaje)
   - Catálogo de proveedores (productos, precios por cantidades, tiempos de entrega)
   - Capacidad de almacén (1 unidad de material = 1 unidad de almacenaje)

2. Generación de demanda:
   - Creación aleatoria de pedidos al inicio de cada día
   - Parámetros configurables: media y varianza

3. Tablero de control:
   - Visualización de pedidos pendientes
   - Lista de materiales (BOM) por pedido
   - Nivel de inventario actual

4. Decisiones del usuario:
   - Liberación de pedidos a producción
   - Emisión de órdenes de compra (producto, proveedor, cantidad, fecha)

5. Simulación de eventos:
   - Consumo de materias primas
   - Fabricación limitada por capacidad diaria
   - Llegada de compras según lead time

6. Avance de calendario:
   - Botón "Avanzar día" que ejecuta 24h de simulación

7. Registro de eventos para históricos y gráficas

8. Exportación/importación JSON de inventario y eventos

9. API REST documentada con SWAGGER/OpenAPI

### Requisitos no funcionales

1. Rendimiento: Ejecución fluida de la simulación
2. Usabilidad: Interfaz intuitiva y responsive
3. Fiabilidad: Consistencia en los datos y resultados
4. Mantenibilidad: Código modular y bien documentado
5. Escalabilidad: Capacidad para añadir nuevas funcionalidades

---

## Modelo de datos

### Entidades y justificación

#### Producto
```
Producto(
    id, 
    nombre, 
    tipo,  # "materia_prima" o "terminado"
    unidad_medida,  # "unidad", "kg", etc.
    espacio_almacen  # Por defecto 1, cuánto espacio ocupa en almacén
)
```

**Justificación**: Esta entidad es fundamental para representar tanto las materias primas como los productos terminados (impresoras 3D). Se amplió con campos para unidad de medida y espacio de almacén para facilitar la gestión del inventario y el cálculo de capacidad de almacenamiento.

#### BOM (Lista de Materiales)
```
BOM(
    id,
    prod_terminado_id,  # FK a Producto
    material_id,        # FK a Producto
    cantidad            # Cantidad necesaria del material
)
```

**Justificación**: El BOM define la estructura de fabricación de cada producto terminado, especificando qué materiales y en qué cantidad se necesitan para fabricar una unidad de producto. Es esencial para calcular los requerimientos de materiales y planificar la producción.

#### Proveedor
```
Proveedor(
    id,
    nombre,
    direccion,
    contacto
)
```

**Justificación**: Almacena la información de los proveedores que suministran materias primas. Se separó de la información de catálogo para permitir que un proveedor pueda ofrecer múltiples productos con diferentes condiciones.

#### CatalogoProveedor
```
CatalogoProveedor(
    id,
    proveedor_id,       # FK a Proveedor
    producto_id,        # FK a Producto
    precio_unitario,
    cantidad_minima,    # Cantidad mínima de compra
    cantidad_paquete,   # Tamaño del paquete (por ej. 1000 unidades)
    lead_time_dias      # Tiempo de entrega en días
)
```

**Justificación**: Esta entidad permite modelar con precisión las diferentes ofertas de cada proveedor, incluyendo condiciones comerciales como precios por volumen, cantidades mínimas de pedido y tiempos de entrega. Facilita la comparación entre proveedores y la toma de decisiones de compra.

#### Inventario
```
Inventario(
    producto_id,        # FK a Producto
    cantidad,
    fecha_actualizacion
)
```

**Justificación**: Representa el estado actual del inventario para cada producto. Es fundamental para el control de stock y para determinar cuándo se necesita realizar nuevas compras.

#### PedidoFabricacion
```
PedidoFabricacion(
    id,
    fecha_creacion,
    producto_id,        # FK a Producto
    cantidad,
    estado,             # "pendiente", "en_produccion", "completado", "cancelado"
    prioridad,          # Opcional: para establecer orden de fabricación
    fecha_inicio_prod,  # Fecha en que comenzó la producción
    fecha_fin_prod      # Fecha estimada/real de finalización
)
```

**Justificación**: Representa los pedidos de fabricación generados por la demanda. El campo estado permite seguir el progreso del pedido a través del ciclo de producción. Se añadieron campos para fechas y prioridad para facilitar la planificación y seguimiento.

#### OrdenCompra
```
OrdenCompra(
    id,
    proveedor_id,       # FK a Proveedor
    fecha_emision,
    fecha_entrega_est,
    estado,             # "emitida", "en_transito", "recibida", "cancelada"
    costo_total         # Para seguimiento financiero
)
```

**Justificación**: Representa las órdenes de compra emitidas a los proveedores. Se separó en cabecera (OrdenCompra) y detalle (DetalleOrdenCompra) para permitir órdenes con múltiples productos.

#### DetalleOrdenCompra
```
DetalleOrdenCompra(
    id,
    orden_compra_id,    # FK a OrdenCompra
    producto_id,        # FK a Producto
    cantidad,
    precio_unitario,
    catalogo_proveedor_id  # FK a CatalogoProveedor
)
```

**Justificación**: Permite detallar los productos específicos incluidos en cada orden de compra, con sus respectivas cantidades y precios. La referencia a CatalogoProveedor facilita el rastreo de las condiciones comerciales aplicadas.

#### Evento
```
Evento(
    id,
    tipo,               # "compra", "produccion", "entrega", "demanda", etc.
    fecha_simulacion,
    entidad_id,         # ID de la entidad relacionada (pedido, orden, etc.)
    entidad_tipo,       # Tipo de entidad ("PedidoFabricacion", "OrdenCompra", etc.)
    detalle,            # Descripción detallada
    resultado           # Resultado o impacto del evento
)
```

**Justificación**: Permite registrar todos los eventos significativos que ocurren durante la simulación. Esta información es crucial para análisis históricos, generación de gráficas y para entender el comportamiento del sistema.

#### ConfiguracionSimulacion
```
ConfiguracionSimulacion(
    id,
    fecha_actual,       # Fecha actual de la simulación
    media_demanda,      # Parámetros para generación aleatoria
    varianza_demanda,
    capacidad_almacen,
    capacidad_produccion_diaria  # Cuántos productos se pueden fabricar por día
)
```

**Justificación**: Centraliza los parámetros de configuración de la simulación, facilitando su ajuste y permitiendo guardar diferentes escenarios.

#### LineaProduccion
```
LineaProduccion(
    id,
    nombre,
    capacidad_diaria,   # Cuántos productos puede procesar por día
    estado              # "activa", "inactiva", "mantenimiento"
)
```

**Justificación**: Representa las líneas de producción disponibles en la planta. Permite modelar restricciones de capacidad más realistas y gestionar la asignación de pedidos a líneas específicas.

#### AsignacionProduccion
```
AsignacionProduccion(
    id,
    pedido_id,          # FK a PedidoFabricacion
    linea_produccion_id, # FK a LineaProduccion
    fecha_asignacion,
    fecha_inicio,
    fecha_fin_estimada,
    estado              # "planificada", "en_proceso", "completada"
)
```

**Justificación**: Establece la relación entre pedidos de fabricación y líneas de producción, permitiendo planificar y hacer seguimiento de la carga de trabajo en cada línea.

#### HistoricoInventario
```
HistoricoInventario(
    id,
    producto_id,        # FK a Producto
    fecha,
    cantidad,
    tipo_movimiento     # "entrada", "salida", "ajuste"
)
```

**Justificación**: Registra todos los movimientos de inventario, facilitando el análisis histórico, la identificación de tendencias y la generación de informes.

#### MetricasRendimiento
```
MetricasRendimiento(
    id,
    fecha,
    pedidos_completados,
    pedidos_retrasados,
    nivel_servicio,     # Porcentaje de pedidos entregados a tiempo
    rotacion_inventario,
    costos_totales
)
```

**Justificación**: Almacena métricas clave de rendimiento calculadas diariamente, permitiendo evaluar la eficiencia de las decisiones de planificación y compra.

### Relaciones entre entidades

- **Producto - BOM**: Un producto terminado está compuesto por varios materiales especificados en el BOM.
- **Proveedor - CatalogoProveedor**: Un proveedor ofrece múltiples productos con diferentes condiciones comerciales.
- **Producto - Inventario**: Cada producto tiene un registro en el inventario que indica su disponibilidad actual.
- **PedidoFabricacion - Producto**: Cada pedido de fabricación solicita un tipo específico de producto terminado.
- **OrdenCompra - Proveedor**: Cada orden de compra se emite a un proveedor específico.
- **OrdenCompra - DetalleOrdenCompra**: Una orden de compra contiene uno o más detalles de productos.
- **LineaProduccion - AsignacionProduccion**: Las líneas de producción reciben asignaciones de pedidos de fabricación.
- **Evento - Diversas entidades**: Los eventos pueden estar relacionados con cualquier entidad del sistema.

---

## Tecnologías empleadas

### Base de datos: SQLite

**Justificación**: 
SQLite se eligió como sistema de gestión de base de datos por varias razones:

1. **Autonomía**: SQLite es una base de datos de archivo único que no requiere un servidor separado, lo que facilita la distribución y ejecución del simulador sin dependencias externas.

2. **Rendimiento adecuado**: Para las dimensiones esperadas del simulador, SQLite ofrece un rendimiento más que suficiente, con capacidad para manejar miles de registros sin problemas.

3. **Simplicidad**: Su configuración y mantenimiento son extremadamente sencillos, permitiendo que el equipo se centre en el desarrollo de la lógica del simulador.

4. **Transacciones ACID**: A pesar de su ligereza, SQLite garantiza transacciones atómicas, consistentes, aisladas y duraderas, lo que es crucial para mantener la integridad de los datos de la simulación.

5. **Portabilidad**: Al ser un archivo único, la base de datos puede ser fácilmente respaldada, transferida o restaurada.

6. **Compatibilidad**: SQLite es compatible con prácticamente cualquier lenguaje de programación moderno, lo que facilita el desarrollo y la integración.

7. **Bajo consumo de recursos**: Ideal para aplicaciones de simulación que pueden requerir recursos para cálculos complejos.

8. **Cero configuración**: No requiere instalación ni configuración del servidor, lo que simplifica el despliegue.

Las tablas se implementarán siguiendo el modelo de datos definido anteriormente, utilizando tipos de datos nativos de SQLite y aprovechando sus características de integridad referencial para mantener la consistencia de los datos.

[SECCIÓN EN DESARROLLO - Se añadirán más tecnologías según avance el proyecto]

---

## Arquitectura del sistema

[SECCIÓN EN DESARROLLO]

---

## Implementación

[SECCIÓN EN DESARROLLO]

---

## Pruebas

[SECCIÓN EN DESARROLLO]

---

## Manual de usuario

[SECCIÓN EN DESARROLLO]

---

## Conclusiones

[SECCIÓN EN DESARROLLO]

---

## Referencias

[SECCIÓN EN DESARROLLO]

---

## Anexos

[SECCIÓN EN DESARROLLO]
