# Esquema de Base de Datos
## Simulador de Producción de Impresoras 3D

Este documento describe la estructura de la base de datos SQLite utilizada por el Simulador de Producción de Impresoras 3D.

## Diagrama Entidad-Relación

```
+----------------+        +----------------+        +----------------+
|    product     |        |      bom       |        |    supplier    |
+----------------+        +----------------+        +----------------+
| id             |<---+   | id             |        | id             |
| name           |    |   | finished_id    |------->| name           |
| type           |    |   | material_id    |------->| product_id     |---+
+----------------+    |   | quantity       |        | unit_cost      |   |
                      |   +----------------+        | lead_time_days |   |
                      |                             +----------------+   |
                      |                                                  |
                      |                                                  |
+----------------+    |                             +----------------+   |
| stock_current  |    |                             | purchase_order |   |
+----------------+    |                             +----------------+   |
| id             |    |                             | id             |   |
| product_id     |----+                             | supplier_id    |---+
| quantity       |                                  | product_id     |---+
+----------------+                                  | quantity       |   |
                                                    | issue_date     |   |
                                                    | estimated_date |   |
                                                    | status         |   |
                      +------------------+          +----------------+   |
                      | manufacturing_order|                             |
                      +------------------+                               |
                      | id              |                                |
                      | creation_date   |                                |
                      | product_id      |--------------------------------+
                      | quantity        |
                      | status          |
                      +------------------+
                              |
                              |
                      +------------------+
                      |      event       |
                      +------------------+
                      | id              |
                      | type            |
                      | event_date      |
                      | details         |
                      +------------------+
```

## Definiciones de Tablas

### products

Almacena información sobre los productos, tanto materias primas como productos terminados.

| Columna | Tipo    | Descripción                             | Restricciones    |
|---------|---------|----------------------------------------|------------------|
| id      | INTEGER | Identificador único del producto       | PRIMARY KEY      |
| name    | TEXT    | Nombre del producto                    | NOT NULL, UNIQUE |
| type    | TEXT    | Tipo de producto: "raw" o "finished"   | NOT NULL         |

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL CHECK (type IN ('raw', 'finished'))
);
```

### bom (Bill of Materials)

Define la composición de los productos terminados, especificando qué materiales y en qué cantidades se necesitan.

| Columna       | Tipo    | Descripción                                  | Restricciones                       |
|---------------|---------|----------------------------------------------|-------------------------------------|
| id            | INTEGER | Identificador único                          | PRIMARY KEY                         |
| finished_id   | INTEGER | ID del producto terminado                    | NOT NULL, FOREIGN KEY (products.id) |
| material_id   | INTEGER | ID del material o componente                 | NOT NULL, FOREIGN KEY (products.id) |
| quantity      | INTEGER | Cantidad necesaria del material              | NOT NULL, CHECK (quantity > 0)      |

```sql
CREATE TABLE bom (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    finished_id INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    FOREIGN KEY (finished_id) REFERENCES products (id),
    FOREIGN KEY (material_id) REFERENCES products (id),
    UNIQUE (finished_id, material_id)
);
```

### suppliers

Almacena información sobre los proveedores de materias primas.

| Columna        | Tipo    | Descripción                              | Restricciones                       |
|----------------|---------|------------------------------------------|-------------------------------------|
| id             | INTEGER | Identificador único del proveedor        | PRIMARY KEY                         |
| name           | TEXT    | Nombre del proveedor                     | NOT NULL                            |
| product_id     | INTEGER | ID del producto que provee               | NOT NULL, FOREIGN KEY (products.id) |
| unit_cost      | REAL    | Costo unitario del producto              | NOT NULL, CHECK (unit_cost > 0)     |
| lead_time_days | INTEGER | Tiempo de entrega en días                | NOT NULL, CHECK (lead_time_days > 0)|

```sql
CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    product_id INTEGER NOT NULL,
    unit_cost REAL NOT NULL CHECK (unit_cost > 0),
    lead_time_days INTEGER NOT NULL CHECK (lead_time_days > 0),
    FOREIGN KEY (product_id) REFERENCES products (id)
);
```

### stock_current

Registra el nivel actual de inventario para cada producto.

| Columna    | Tipo    | Descripción                               | Restricciones                       |
|------------|---------|-------------------------------------------|-------------------------------------|
| id         | INTEGER | Identificador único                       | PRIMARY KEY                         |
| product_id | INTEGER | ID del producto                           | NOT NULL, FOREIGN KEY (products.id) |
| quantity   | INTEGER | Cantidad disponible en inventario         | NOT NULL, DEFAULT 0                 |

```sql
CREATE TABLE stock_current (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products (id),
    UNIQUE (product_id)
);
```

### manufacturing_orders

Almacena las órdenes de fabricación de productos terminados.

| Columna       | Tipo    | Descripción                                | Restricciones                       |
|---------------|---------|--------------------------------------------|------------------------------------|
| id            | INTEGER | Identificador único del pedido             | PRIMARY KEY                        |
| creation_date | TEXT    | Fecha de creación (YYYY-MM-DD)             | NOT NULL                           |
| product_id    | INTEGER | ID del producto a fabricar                 | NOT NULL, FOREIGN KEY (products.id)|
| quantity      | INTEGER | Cantidad a fabricar                        | NOT NULL, CHECK (quantity > 0)     |
| status        | TEXT    | Estado del pedido                          | NOT NULL                           |

```sql
CREATE TABLE manufacturing_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creation_date TEXT NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    status TEXT NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    FOREIGN KEY (product_id) REFERENCES products (id)
);
```

### purchase_orders

Almacena las órdenes de compra emitidas a los proveedores.

| Columna                | Tipo    | Descripción                                | Restricciones                        |
|------------------------|---------|--------------------------------------------|------------------------------------|
| id                     | INTEGER | Identificador único de la orden            | PRIMARY KEY                         |
| supplier_id            | INTEGER | ID del proveedor                           | NOT NULL, FOREIGN KEY (suppliers.id)|
| product_id             | INTEGER | ID del producto a comprar                  | NOT NULL, FOREIGN KEY (products.id) |
| quantity               | INTEGER | Cantidad a comprar                         | NOT NULL, CHECK (quantity > 0)      |
| issue_date             | TEXT    | Fecha de emisión (YYYY-MM-DD)              | NOT NULL                            |
| estimated_delivery_date| TEXT    | Fecha estimada de entrega (YYYY-MM-DD)     | NOT NULL                            |
| status                 | TEXT    | Estado de la orden                         | NOT NULL                            |

```sql
CREATE TABLE purchase_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    issue_date TEXT NOT NULL,
    estimated_delivery_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'received', 'cancelled')),
    FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
);
```

### events

Registra todos los eventos que ocurren en el sistema para análisis histórico.

| Columna    | Tipo    | Descripción                               | Restricciones |
|------------|---------|-------------------------------------------|---------------|
| id         | INTEGER | Identificador único del evento            | PRIMARY KEY   |
| type       | TEXT    | Tipo de evento                            | NOT NULL      |
| event_date | TEXT    | Fecha del evento (YYYY-MM-DD)             | NOT NULL      |
| details    | TEXT    | Detalles adicionales del evento (JSON)    | NOT NULL      |

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    event_date TEXT NOT NULL,
    details TEXT NOT NULL
);
```

### simulation_state

Almacena el estado actual de la simulación.

| Columna       | Tipo    | Descripción                        | Restricciones |
|---------------|---------|------------------------------------|--------------| 
| id            | INTEGER | Identificador único                | PRIMARY KEY  |
| current_day   | INTEGER | Día actual de la simulación        | NOT NULL     |
| config        | TEXT    | Configuración de la simulación     | NOT NULL     |

```sql
CREATE TABLE simulation_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    current_day INTEGER NOT NULL DEFAULT 1,
    config TEXT NOT NULL
);
```

## Índices

Para optimizar el rendimiento de las consultas más frecuentes, se han definido los siguientes índices:

```sql
-- Índice para búsquedas por tipo de producto
CREATE INDEX idx_products_type ON products(type);

-- Índice para búsquedas de componentes en BOM
CREATE INDEX idx_bom_finished_id ON bom(finished_id);
CREATE INDEX idx_bom_material_id ON bom(material_id);

-- Índice para búsquedas de proveedores por producto
CREATE INDEX idx_suppliers_product_id ON suppliers(product_id);

-- Índice para búsquedas de órdenes por estado y fecha
CREATE INDEX idx_manufacturing_orders_status ON manufacturing_orders(status);
CREATE INDEX idx_manufacturing_orders_creation_date ON manufacturing_orders(creation_date);

-- Índice para búsquedas de órdenes de compra por estado y fecha
CREATE INDEX idx_purchase_orders_status ON purchase_orders(status);
CREATE INDEX idx_purchase_orders_issue_date ON purchase_orders(issue_date);
CREATE INDEX idx_purchase_orders_delivery_date ON purchase_orders(estimated_delivery_date);

-- Índice para búsquedas de eventos por tipo y fecha
CREATE INDEX idx_events_type ON events(type);
CREATE INDEX idx_events_date ON events(event_date);
```

## Restricciones y Validaciones

Además de las restricciones definidas en la estructura de las tablas, se implementan las siguientes validaciones a nivel de aplicación:

1. **Validación de BOM**: Un producto "finished" debe tener al menos un componente en la tabla BOM.
2. **Validación de tipo de producto en BOM**: En la tabla BOM, finished_id debe corresponder a un producto de tipo "finished" y material_id a un producto de tipo "raw".
3. **Validación de tipo de producto en suppliers**: En la tabla suppliers, product_id debe corresponder a un producto de tipo "raw".
4. **Validación de tipo de producto en manufacturing_orders**: En la tabla manufacturing_orders, product_id debe corresponder a un producto de tipo "finished".
5. **Validación de disponibilidad**: Antes de cambiar el estado de una orden de fabricación a "in_progress", se verifica la disponibilidad de todos los materiales requeridos.

## Datos de Inicialización

La base de datos se inicializa con los siguientes datos básicos:

### Productos

```sql
INSERT INTO products (id, name, type) VALUES 
(1, 'P3D-Classic', 'finished'),
(2, 'P3D-Pro', 'finished'),
(3, 'kit_piezas', 'raw'),
(4, 'pcb_v2', 'raw'),
(5, 'pcb_v3', 'raw'),
(6, 'extrusor', 'raw'),
(7, 'sensor_autonivel', 'raw'),
(8, 'cables_conexion', 'raw'),
(9, 'transformador_24v', 'raw'),
(10, 'enchufe_schuko', 'raw');
```

### BOM (Lista de Materiales)

```sql
-- BOM para P3D-Classic
INSERT INTO bom (finished_id, material_id, quantity) VALUES
(1, 3, 1),  -- 1 kit_piezas
(1, 4, 1),  -- 1 pcb_v2
(1, 6, 1),  -- 1 extrusor
(1, 8, 2),  -- 2 cables_conexion
(1, 9, 1),  -- 1 transformador_24v
(1, 10, 1); -- 1 enchufe_schuko

-- BOM para P3D-Pro
INSERT INTO bom (finished_id, material_id, quantity) VALUES
(2, 3, 1),  -- 1 kit_piezas
(2, 5, 1),  -- 1 pcb_v3
(2, 6, 1),  -- 1 extrusor
(2, 7, 1),  -- 1 sensor_autonivel
(2, 8, 3),  -- 3 cables_conexion
(2, 9, 1),  -- 1 transformador_24v
(2, 10, 1); -- 1 enchufe_schuko
```

### Proveedores

```sql
INSERT INTO suppliers (name, product_id, unit_cost, lead_time_days) VALUES
('Proveedor A', 3, 90.0, 3),
('Proveedor B', 3, 85.0, 5),
('Proveedor C', 4, 15.0, 2),
('Proveedor D', 5, 25.0, 2),
('Proveedor E', 6, 45.0, 4),
('Proveedor F', 7, 30.0, 3),
('Proveedor G', 8, 5.0, 1),
('Proveedor H', 9, 20.0, 2),
('Proveedor I', 10, 3.0, 1);
```

### Inventario Inicial

```sql
INSERT INTO stock_current (product_id, quantity) VALUES
(1, 0),  -- 0 unidades de P3D-Classic en stock
(2, 0),  -- 0 unidades de P3D-Pro en stock
(3, 30), -- 30 unidades de kit_piezas
(4, 20), -- 20 unidades de pcb_v2
(5, 10), -- 10 unidades de pcb_v3
(6, 25), -- 25 unidades de extrusor
(7, 15), -- 15 unidades de sensor_autonivel
(8, 50), -- 50 unidades de cables_conexion
(9, 20), -- 20 unidades de transformador_24v
(10, 30); -- 30 unidades de enchufe_schuko
```

### Estado Inicial de la Simulación

```sql
INSERT INTO simulation_state (id, current_day, config) VALUES
(1, 1, '{"production_capacity": 10, "demand_mean": 7, "demand_variance": 2}');
```

## Scripts SQL Principales

### Inicialización de la Base de Datos

El script `init_db.py` se encarga de crear todas las tablas e insertar los datos iniciales:

```python
def init_db():
    """Inicializa la base de datos con la estructura y datos iniciales."""
    conn = sqlite3.connect('data/simulator.db')
    c = conn.cursor()
    
    # Crear tablas
    c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        type TEXT NOT NULL CHECK (type IN ('raw', 'finished'))
    )
    ''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS bom (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        finished_id INTEGER NOT NULL,
        material_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL CHECK (quantity > 0),
        FOREIGN KEY (finished_id) REFERENCES products (id),
        FOREIGN KEY (material_id) REFERENCES products (id),
        UNIQUE (finished_id, material_id)
    )
    ''')
    
    # ... resto de las tablas
    
    # Insertar datos iniciales
    # ... inserciones
    
    conn.commit()
    conn.close()
```

### Consultas Comunes

#### Verificar Disponibilidad de Materiales

```python
def check_availability(product_id, quantity):
    """Verifica si hay suficientes materiales para producir una cantidad de un producto."""
    conn = sqlite3.connect('data/simulator.db')
    c = conn.cursor()
    
    # Obtener todos los materiales necesarios
    c.execute('''
    SELECT b.material_id, b.quantity * ?, p.name
    FROM bom b
    JOIN products p ON b.material_id = p.id
    WHERE b.finished_id = ?
    ''', (quantity, product_id))
    
    required_materials = c.fetchall()
    
    # Verificar disponibilidad
    missing_materials = []
    for material_id, required_qty, material_name in required_materials:
        c.execute('SELECT quantity FROM stock_current WHERE product_id = ?', (material_id,))
        current_qty = c.fetchone()[0]
        
        if current_qty < required_qty:
            missing_materials.append({
                'material_id': material_id,
                'material_name': material_name,
                'required': required_qty,
                'available': current_qty,
                'missing': required_qty - current_qty
            })
    
    conn.close()
    return missing_materials
```

#### Liberar Orden a Producción

```python
def release_order(order_id):
    """Libera una orden a producción, consumiendo los materiales necesarios."""
    conn = sqlite3.connect('data/simulator.db')
    c = conn.cursor()
    
    # Obtener información de la orden
    c.execute('''
    SELECT o.product_id, o.quantity
    FROM manufacturing_orders o
    WHERE o.id = ? AND o.status = 'pending'
    ''', (order_id,))
    
    order_info = c.fetchone()
    if not order_info:
        conn.close()
        return {'status': 'error', 'message': 'Order not found or not in pending status'}
    
    product_id, quantity = order_info
    
    # Verificar disponibilidad
    missing_materials = check_availability(product_id, quantity)
    if missing_materials:
        conn.close()
        return {
            'status': 'error', 
            'message': 'Insufficient materials',
            'missing_materials': missing_materials
        }
    
    # Consumir materiales
    c.execute('''
    SELECT b.material_id, b.quantity * ?, p.name
    FROM bom b
    JOIN products p ON b.material_id = p.id
    WHERE b.finished_id = ?
    ''', (quantity, product_id))
    
    materials_to_consume = c.fetchall()
    consumed_materials = []
    
    for material_id, qty_to_consume, material_name in materials_to_consume:
        c.execute('''
        UPDATE stock_current 
        SET quantity = quantity - ? 
        WHERE product_id = ?
        ''', (qty_to_consume, material_id))
        
        consumed_materials.append({
            'material_id': material_id,
            'material_name': material_name,
            'quantity': qty_to_consume
        })
    
    # Actualizar estado de la orden
    c.execute('''
    UPDATE manufacturing_orders 
    SET status = 'in_progress' 
    WHERE id = ?
    ''', (order_id,))
    
    # Registrar evento
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('''
    INSERT INTO events (type, event_date, details)
    VALUES (?, ?, ?)
    ''', ('production_started', today, json.dumps({
        'order_id': order_id,
        'product_id': product_id,
        'quantity': quantity,
        'materials_consumed': consumed_materials
    })))
    
    conn.commit()
    conn.close()
    
    return {
        'status': 'success',
        'message': 'Order released to production',
        'order_id': order_id,
        'materials_consumed': consumed_materials
    }
```

#### Avanzar Día de Simulación

```python
def advance_day():
    """Avanza la simulación un día, procesando órdenes y entregas."""
    conn = sqlite3.connect('data/simulator.db')
    c = conn.cursor()
    
    # Obtener día actual
    c.execute('SELECT current_day, config FROM simulation_state WHERE id = 1')
    current_day, config_json = c.fetchone()
    config = json.loads(config_json)
    
    # Avanzar al siguiente día
    next_day = current_day + 1
    c.execute('UPDATE simulation_state SET current_day = ? WHERE id = 1', (next_day,))
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Procesar órdenes en producción
    c.execute('''
    SELECT id, product_id, quantity 
    FROM manufacturing_orders 
    WHERE status = 'in_progress'
    ''')
    
    in_progress_orders = c.fetchall()
    for order_id, product_id, quantity in in_progress_orders:
        # Simular finalización de producción (simplificado)
        # En una implementación real, esto dependería de la capacidad y tiempos
        c.execute('''
        UPDATE manufacturing_orders 
        SET status = 'completed' 
        WHERE id = ?
        ''', (order_id,))
        
        # Aumentar inventario de producto terminado
        c.execute('''
        UPDATE stock_current 
        SET quantity = quantity + ? 
        WHERE product_id = ?
        ''', (quantity, product_id))
        
        # Registrar evento
        c.execute('''
        INSERT INTO events (type, event_date, details)
        VALUES (?, ?, ?)
        ''', ('production_completed', today, json.dumps({
            'order_id': order_id,
            'product_id': product_id,
            'quantity': quantity
        })))
    
    # Procesar órdenes de compra pendientes
    c.execute('''
    SELECT id, product_id, quantity, estimated_delivery_date 
    FROM purchase_orders 
    WHERE status = 'pending'
    ''')
    
    pending_purchases = c.fetchall()
    for order_id, product_id, quantity, delivery_date in pending_purchases:
        if delivery_date <= today:
            # Recibir materiales
            c.execute('''
            UPDATE purchase_orders 
            SET status = 'received' 
            WHERE id = ?
            ''', (order_id,))
            
            # Aumentar inventario
            c.execute('''
            UPDATE stock_current 
            SET quantity = quantity + ? 
            WHERE product_id = ?
            ''', (quantity, product_id))
            
            # Registrar evento
            c.execute('''
            INSERT INTO events (type, event_date, details)
            VALUES (?, ?, ?)
            ''', ('materials_received', today, json.dumps({
                'order_id': order_id,
                'product_id': product_id,
                'quantity': quantity
            })))
    
    # Generar nuevos pedidos aleatorios
    # ... lógica de generación de pedidos
    
    conn.commit()
    conn.close()
    
    return {
        'status': 'success',
        'current_day': next_day,
        'new_orders': new_orders
    }
```

## Consultas para Análisis

### Histórico de Nivel de Inventario

```sql
SELECT 
    e.event_date,
    p.id AS product_id,
    p.name AS product_name,
    (
        SELECT SUM(CASE 
            WHEN json_extract(e2.details, '$.product_id') = p.id AND e2.type = 'materials_received' THEN json_extract(e2.details, '$.quantity')
            WHEN json_extract(e2.details, '$.product_id') = p.id AND e2.type = 'production_completed' THEN json_extract(e2.details, '$.quantity')
            WHEN json_extract(e2.details, '$.materials_consumed') LIKE '%"material_id":' || p.id || '%' THEN -json_extract(
                json_extract(e2.details, '$.materials_consumed'), 
                '$[?(@.material_id==' || p.id || ')].quantity'
            )
            ELSE 0
        END) 
        FROM events e2 
        WHERE e2.event_date <= e.event_date
    ) AS cumulative_quantity
FROM 
    events e
CROSS JOIN 
    products p
WHERE 
    p.type = 'raw'
GROUP BY 
    e.event_date, p.id
ORDER BY 
    e.event_date, p.name;
```

### Tiempo de Ciclo de Producción

```sql
SELECT 
    mo.id AS order_id,
    mo.product_id,
    p.name AS product_name,
    mo.quantity,
    mo.creation_date,
    (
        SELECT e.event_date
        FROM events e
        WHERE e.type = 'production_completed' 
        AND json_extract(e.details, '$.order_id') = mo.id
        LIMIT 1
    ) AS completion_date,
    julianday(
        (
            SELECT e.event_date
            FROM events e
            WHERE e.type = 'production_completed' 
            AND json_extract(e.details, '$.order_id') = mo.id
            LIMIT 1
        )
    ) - julianday(mo.creation_date) AS cycle_time_days
FROM 
    manufacturing_orders mo
JOIN 
    products p ON mo.product_id = p.id
WHERE 
    mo.status = 'completed';
```

## Notas sobre Rendimiento

1. **Indexación**: Los índices definidos optimizan las consultas más frecuentes, especialmente las relacionadas con búsquedas por estado y fecha.

2. **Desnormalización Selectiva**: Algunas entidades incluyen campos desnormalizados (como nombres) cuando se requiere un mejor rendimiento en las consultas más comunes.

3. **Transacciones**: Todas las operaciones que modifican múltiples tablas (como liberar una orden a producción) se ejecutan dentro de transacciones para garantizar la integridad de los datos.

4. **Tamaño de la Base de Datos**: Dado que SQLite se utiliza como motor de base de datos, se espera que el tamaño de la base de datos se mantenga en niveles manejables incluso después de semanas de simulación.

5. **Estrategia de Purga**: Para simulaciones muy largas, puede implementarse una estrategia de purga para eventos antiguos, manteniendo resúmenes estadísticos en lugar de datos detallados.

## Migración y Respaldo

### Exportación de Datos

El sistema incluye funcionalidad para exportar todos los datos en formato JSON, lo que facilita la migración a otros sistemas o el respaldo:

```python
def export_data():
    """Exporta todos los datos del sistema en formato JSON."""
    conn = sqlite3.connect('data/simulator.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    data = {}
    
    # Exportar productos
    c.execute('SELECT * FROM products')
    data['products'] = [dict(row) for row in c.fetchall()]
    
    # Exportar BOM
    c.execute('SELECT * FROM bom')
    data['bom'] = [dict(row) for row in c.fetchall()]
    
    # ... resto de tablas
    
    conn.close()
    return data
```

### Importación de Datos

De manera similar, el sistema permite la importación de datos previamente exportados:

```python
def import_data(data):
    """Importa datos al sistema desde un formato JSON."""
    conn = sqlite3.connect('data/simulator.db')
    c = conn.cursor()
    
    # Iniciar transacción
    conn.execute('BEGIN TRANSACTION')
    
    try:
        # Importar productos
        for product in data.get('products', []):
            c.execute('''
            INSERT OR REPLACE INTO products (id, name, type)
            VALUES (?, ?, ?)
            ''', (product['id'], product['name'], product['type']))
        
        # ... resto de entidades
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
```

## Conclusión

La base de datos SQLite utilizada por el Simulador de Producción de Impresoras 3D está diseñada para ser:

1. **Simple**: Utilizando un esquema claro y fácil de entender.
2. **Eficiente**: Con índices adecuados para las consultas más comunes.
3. **Flexible**: Permitiendo la fácil extensión para nuevos tipos de productos y reglas de negocio.
4. **Portable**: Utilizando SQLite para facilitar la distribución y uso sin configuraciones complejas.
5. **Respaldable**: Con capacidades incorporadas de exportación e importación.

Este diseño admite todos los requisitos funcionales del simulador mientras mantiene un rendimiento adecuado para sus casos de uso previstos.