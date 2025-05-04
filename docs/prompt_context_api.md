# Contexto del Prompt para Generación de la API REST

## Objetivo
Crear una API REST utilizando FastAPI para gestionar los datos de un sistema de producción de impresoras, específicamente enfocado en productos y órdenes de producción.

## Contexto Inicial
- El proyecto ya contaba con una base de datos SQLite (`simulador_produccion.db`)
- Existía un archivo `entities.py` con las definiciones de las entidades del sistema
- Se requería implementar servicios para crear y actualizar datos

## Entidades Principales
Las entidades principales definidas en `entities.py` incluyen:

### Gestión de Productos
- `Producto`: Productos (materia prima o producto terminado)
  - Campos: id, nombre, tipo, unidad_medida, espacio_almacen
- `BOM`: Lista de materiales
  - Campos: id, prod_terminado_id, material_id, cantidad

### Gestión de Proveedores
- `Proveedor`: Información de proveedores
  - Campos: id, nombre, direccion, contacto
- `CatalogoProveedor`: Catálogo de productos por proveedor
  - Campos: id, proveedor_id, producto_id, precio_unitario, cantidad_minima, cantidad_paquete, lead_time_dias

### Gestión de Inventario
- `Inventario`: Estado actual del inventario
  - Campos: producto_id, cantidad, fecha_actualizacion
- `HistoricoInventario`: Historial de movimientos de inventario
  - Campos: id, producto_id, fecha, cantidad, tipo_movimiento

### Gestión de Producción
- `PedidoFabricacion`: Órdenes de producción
  - Campos: id, fecha_creacion, producto_id, cantidad, estado, prioridad, fecha_inicio_prod, fecha_fin_prod
- `LineaProduccion`: Líneas de producción disponibles
  - Campos: id, nombre, capacidad_diaria, estado
- `AsignacionProduccion`: Asignación de pedidos a líneas
  - Campos: id, pedido_id, linea_produccion_id, fecha_asignacion, fecha_inicio, fecha_fin_estimada, estado

### Gestión de Compras
- `OrdenCompra`: Órdenes de compra a proveedores
  - Campos: id, proveedor_id, fecha_emision, fecha_entrega_est, estado, costo_total
- `DetalleOrdenCompra`: Detalles de las órdenes de compra
  - Campos: id, orden_compra_id, producto_id, cantidad, precio_unitario, catalogo_proveedor_id

### Simulación y Monitoreo
- `Evento`: Eventos del sistema
  - Campos: id, tipo, fecha_simulacion, entidad_id, entidad_tipo, detalle, resultado
- `ConfiguracionSimulacion`: Configuración de la simulación
  - Campos: id, fecha_actual, media_demanda, varianza_demanda, capacidad_almacen, capacidad_produccion_diaria
- `MetricasRendimiento`: Métricas de rendimiento del sistema
  - Campos: id, fecha, pedidos_completados, pedidos_retrasados, nivel_servicio, rotacion_inventario, costos_totales

## Requisitos de Implementación
1. Crear endpoints REST para todas las entidades del sistema
2. Implementar operaciones CRUD básicas (Create, Read)
3. Utilizar FastAPI como framework
4. Mantener la integridad de los datos con la base de datos SQLite existente
5. Implementar manejo de errores apropiado
6. Proporcionar documentación clara de la API

## Consideraciones Técnicas
- Uso de Pydantic para validación de datos
- Manejo de conexiones a la base de datos
- Implementación de transacciones
- Manejo de errores HTTP apropiados
- Documentación automática de la API
- Nombres de rutas en español
- Auto-incremento de IDs
- Validación de datos con Pydantic

## Resultado
Se implementó una API REST con los siguientes endpoints:

### Productos
- POST /productos/
- GET /productos/
- GET /productos/{producto_id}

### BOM
- POST /bom/
- GET /bom/

### Proveedores
- POST /proveedores/
- GET /proveedores/

### Catálogo de Proveedores
- POST /catalogo-proveedor/
- GET /catalogo-proveedor/

### Inventario
- POST /inventario/
- GET /inventario/

### Pedidos de Fabricación
- POST /pedidos-fabricacion/
- GET /pedidos-fabricacion/

### Órdenes de Compra
- POST /ordenes-compra/
- GET /ordenes-compra/

### Detalles de Órdenes de Compra
- POST /detalles-orden-compra/
- GET /detalles-orden-compra/

### Eventos
- POST /eventos/
- GET /eventos/

### Configuración de Simulación
- POST /configuracion-simulacion/
- GET /configuracion-simulacion/

### Líneas de Producción
- POST /lineas-produccion/
- GET /lineas-produccion/

### Asignaciones de Producción
- POST /asignaciones-produccion/
- GET /asignaciones-produccion/

### Histórico de Inventario
- POST /historico-inventario/
- GET /historico-inventario/

### Métricas de Rendimiento
- POST /metricas-rendimiento/
- GET /metricas-rendimiento/

La implementación incluye:
- Validación de datos
- Manejo de errores
- Documentación automática
- Conexión segura a la base de datos
- Transacciones para mantener la integridad de los datos
- Nombres de rutas en español
- Auto-incremento de IDs
- Validación de datos con Pydantic 