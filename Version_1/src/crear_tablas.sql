-- Crear la base de datos
-- En SQLite esto generalmente se hace al conectarse con el archivo

-- Tabla Producto
CREATE TABLE IF NOT EXISTS Producto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    tipo TEXT CHECK(tipo IN ('materia_prima', 'terminado')) NOT NULL,
    unidad_medida TEXT DEFAULT 'unidad',
    espacio_almacen REAL DEFAULT 1.0
);

-- Tabla BOM (Bill of Materials)
CREATE TABLE IF NOT EXISTS BOM (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prod_terminado_id INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    cantidad REAL NOT NULL CHECK(cantidad > 0),
    FOREIGN KEY (prod_terminado_id) REFERENCES Producto(id),
    FOREIGN KEY (material_id) REFERENCES Producto(id)
);

-- Tabla Proveedor
CREATE TABLE IF NOT EXISTS Proveedor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    direccion TEXT,
    contacto TEXT
);

-- Tabla CatalogoProveedor
CREATE TABLE IF NOT EXISTS CatalogoProveedor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proveedor_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    precio_unitario REAL NOT NULL CHECK(precio_unitario > 0),
    cantidad_minima INTEGER DEFAULT 1,
    cantidad_paquete INTEGER DEFAULT 1,
    lead_time_dias INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (proveedor_id) REFERENCES Proveedor(id),
    FOREIGN KEY (producto_id) REFERENCES Producto(id)
);

-- Tabla Inventario
CREATE TABLE IF NOT EXISTS Inventario (
    producto_id INTEGER PRIMARY KEY,
    cantidad REAL NOT NULL DEFAULT 0,
    fecha_actualizacion TEXT NOT NULL,
    FOREIGN KEY (producto_id) REFERENCES Producto(id)
);

-- Tabla PedidoFabricacion
CREATE TABLE IF NOT EXISTS PedidoFabricacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_creacion TEXT NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL CHECK(cantidad > 0),
    estado TEXT CHECK(estado IN ('pendiente', 'en_produccion', 'completado', 'cancelado')) NOT NULL DEFAULT 'pendiente',
    prioridad INTEGER DEFAULT 0,
    fecha_inicio_prod TEXT,
    fecha_fin_prod TEXT,
    FOREIGN KEY (producto_id) REFERENCES Producto(id)
);

-- Tabla OrdenCompra
CREATE TABLE IF NOT EXISTS OrdenCompra (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proveedor_id INTEGER NOT NULL,
    fecha_emision TEXT NOT NULL,
    fecha_entrega_est TEXT NOT NULL,
    estado TEXT CHECK(estado IN ('emitida', 'en_transito', 'recibida', 'cancelada')) NOT NULL DEFAULT 'emitida',
    costo_total REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (proveedor_id) REFERENCES Proveedor(id)
);

-- Tabla DetalleOrdenCompra
CREATE TABLE IF NOT EXISTS DetalleOrdenCompra (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orden_compra_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL CHECK(cantidad > 0),
    precio_unitario REAL NOT NULL CHECK(precio_unitario > 0),
    catalogo_proveedor_id INTEGER NOT NULL,
    FOREIGN KEY (orden_compra_id) REFERENCES OrdenCompra(id),
    FOREIGN KEY (producto_id) REFERENCES Producto(id),
    FOREIGN KEY (catalogo_proveedor_id) REFERENCES CatalogoProveedor(id)
);

-- Tabla Evento
CREATE TABLE IF NOT EXISTS Evento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    fecha_simulacion TEXT NOT NULL,
    entidad_id INTEGER,
    entidad_tipo TEXT,
    detalle TEXT,
    resultado TEXT
);

-- Tabla ConfiguracionSimulacion
CREATE TABLE IF NOT EXISTS ConfiguracionSimulacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_actual TEXT NOT NULL,
    media_demanda REAL NOT NULL DEFAULT 0,
    varianza_demanda REAL NOT NULL DEFAULT 0,
    capacidad_almacen INTEGER NOT NULL DEFAULT 1000,
    capacidad_produccion_diaria INTEGER NOT NULL DEFAULT 10
);

-- Tabla LineaProduccion
CREATE TABLE IF NOT EXISTS LineaProduccion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    capacidad_diaria INTEGER NOT NULL DEFAULT 10,
    estado TEXT CHECK(estado IN ('activa', 'inactiva', 'mantenimiento')) NOT NULL DEFAULT 'activa'
);

-- Tabla AsignacionProduccion
CREATE TABLE IF NOT EXISTS AsignacionProduccion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    linea_produccion_id INTEGER NOT NULL,
    fecha_asignacion TEXT NOT NULL,
    fecha_inicio TEXT NOT NULL,
    fecha_fin_estimada TEXT NOT NULL,
    estado TEXT CHECK(estado IN ('planificada', 'en_proceso', 'completada')) NOT NULL DEFAULT 'planificada',
    FOREIGN KEY (pedido_id) REFERENCES PedidoFabricacion(id),
    FOREIGN KEY (linea_produccion_id) REFERENCES LineaProduccion(id)
);

-- Tabla HistoricoInventario
CREATE TABLE IF NOT EXISTS HistoricoInventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    cantidad REAL NOT NULL,
    tipo_movimiento TEXT CHECK(tipo_movimiento IN ('entrada', 'salida', 'ajuste')) NOT NULL,
    FOREIGN KEY (producto_id) REFERENCES Producto(id)
);

-- Tabla MetricasRendimiento
CREATE TABLE IF NOT EXISTS MetricasRendimiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    pedidos_completados INTEGER NOT NULL DEFAULT 0,
    pedidos_retrasados INTEGER NOT NULL DEFAULT 0,
    nivel_servicio REAL NOT NULL DEFAULT 0, -- Porcentaje
    rotacion_inventario REAL NOT NULL DEFAULT 0,
    costos_totales REAL NOT NULL DEFAULT 0
);

-- Crear índices para mejorar el rendimiento de consultas frecuentes
CREATE INDEX idx_bom_terminado ON BOM(prod_terminado_id);
CREATE INDEX idx_bom_material ON BOM(material_id);
CREATE INDEX idx_catalogo_proveedor ON CatalogoProveedor(proveedor_id, producto_id);
CREATE INDEX idx_pedido_estado ON PedidoFabricacion(estado);
CREATE INDEX idx_orden_compra_estado ON OrdenCompra(estado);
CREATE INDEX idx_evento_fecha ON Evento(fecha_simulacion);
CREATE INDEX idx_historico_producto_fecha ON HistoricoInventario(producto_id, fecha);
