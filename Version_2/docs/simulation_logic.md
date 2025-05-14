# Lógica de Simulación
## Simulador de Producción de Impresoras 3D

Este documento describe en detalle la lógica de simulación utilizada en el Simulador de Producción de Impresoras 3D, explicando los algoritmos implementados, los flujos de eventos discretos y cómo funciona el motor SimPy en el contexto de la aplicación.

## Índice

1. [Fundamentos de la Simulación](#1-fundamentos-de-la-simulación)
2. [Motor de Simulación: SimPy](#2-motor-de-simulación-simpy)
3. [Ciclo Diario de Simulación](#3-ciclo-diario-de-simulación)
4. [Generación de Demanda](#4-generación-de-demanda)
5. [Proceso de Fabricación](#5-proceso-de-fabricación)
6. [Gestión de Inventario](#6-gestión-de-inventario)
7. [Proceso de Compras](#7-proceso-de-compras)
8. [Eventos y Registro](#8-eventos-y-registro)
9. [Parámetros Configurables](#9-parámetros-configurables)
10. [Implementación Técnica](#10-implementación-técnica)

## 1. Fundamentos de la Simulación

### 1.1 Paradigma de Simulación

El simulador utiliza el paradigma de **simulación de eventos discretos**, donde:

- El tiempo avanza de evento en evento, no de manera continua.
- Los estados del sistema cambian solo cuando ocurre un evento.
- Los eventos pueden programarse para ocurrir en momentos específicos del futuro.

Esta aproximación es ideal para modelar procesos de producción, donde los cambios de estado ocurren en momentos discretos (cuando se inicia una producción, cuando llega una orden, etc.).

### 1.2 Unidad de Tiempo

La unidad básica de tiempo en la simulación es el **día**. Cada avance en la simulación representa un día completo de operaciones en la planta de producción de impresoras 3D.

### 1.3 Componentes del Sistema

El sistema modelado consta de los siguientes componentes principales:

- **Productos**: Impresoras 3D terminadas y materias primas.
- **BOM (Bill of Materials)**: Estructura que define qué materiales y en qué cantidades se necesitan para fabricar cada modelo de impresora.
- **Inventario**: Almacén de productos terminados y materias primas.
- **Pedidos**: Solicitudes de fabricación de impresoras.
- **Órdenes de compra**: Solicitudes de materiales a los proveedores.
- **Capacidad de producción**: Cantidad máxima de impresoras que se pueden fabricar por día.

## 2. Motor de Simulación: SimPy

### 2.1 ¿Qué es SimPy?

SimPy es una biblioteca de simulación de eventos discretos basada en procesos para Python. En nuestro sistema, SimPy maneja:

- La gestión del tiempo de simulación
- La planificación y ejecución de eventos
- La coordinación entre procesos concurrentes

### 2.2 Componentes Clave de SimPy

#### 2.2.1 Entorno de Simulación

```python
import simpy

# Crear entorno de simulación
env = simpy.Environment()
```

El entorno (`Environment`) es el controlador central que:
- Mantiene la hora actual de la simulación
- Mantiene la cola de eventos futuros
- Ejecuta los eventos en el orden correcto

#### 2.2.2 Procesos

Los procesos son funciones generadoras de Python que modelan actividades que consumen tiempo:

```python
def fabrication_process(env, order, production_capacity, inventory_service):
    """Proceso de fabricación de un pedido."""
    # Reservar capacidad de producción
    yield env.timeout(1)  # La fabricación toma 1 día
    
    # Completar la orden
    inventory_service.increase_stock(order.product_id, order.quantity)
    order.status = "completed"
```

#### 2.2.3 Recursos

Los recursos modelan restricciones como la capacidad de producción:

```python
# Crear recurso para modelar la capacidad de producción
production_capacity = simpy.Resource(env, capacity=10)

def production_process(env, order, production_capacity):
    # Solicitar uso de capacidad
    with production_capacity.request() as req:
        yield req  # Esperar a que haya capacidad disponible
        # Realizar la producción
        yield env.timeout(1)  # La fabricación toma 1 día
```

#### 2.2.4 Eventos

Los eventos señalan momentos específicos o condiciones en la simulación:

```python
# Crear evento para notificar la llegada de materiales
materials_received = env.event()

# En otro proceso, cuando llegan los materiales:
materials_received.succeed(value=received_materials)

# En un proceso que espera los materiales:
result = yield materials_received
materials = result  # Obtener los materiales recibidos
```

### 2.3 Integración de SimPy en el Sistema

En nuestro simulador, SimPy está encapsulado dentro de la clase `ProductionSimulator`:

```python
class ProductionSimulator:
    def __init__(self, repositories, services):
        self.env = simpy.Environment()
        self.repositories = repositories
        self.services = services
        self.production_capacity = simpy.Resource(
            self.env, 
            capacity=self.services["config"].get_production_capacity()
        )
        
    def run_day(self):
        """Ejecuta un día completo de simulación."""
        # Configurar procesos
        self.env.process(self.generate_orders())
        self.env.process(self.process_manufacturing_orders())
        self.env.process(self.process_purchase_orders())
        
        # Avanzar la simulación un día
        self.env.run(until=self.env.now + 1)
```

## 3. Ciclo Diario de Simulación

### 3.1 Secuencia de Eventos

El ciclo diario de simulación sigue esta secuencia:

1. **Generación de nuevos pedidos**: Se crean automáticamente nuevos pedidos basados en la configuración de demanda.
2. **Procesamiento de pedidos en fabricación**: Los pedidos que ya están en producción avanzan o se completan.
3. **Recepción de materiales**: Se reciben materiales de órdenes de compra que llegan ese día.
4. **Actualización de estados**: Se actualizan todos los estados del sistema.
5. **Registro de eventos**: Se registran todos los eventos ocurridos durante el día.

### 3.2 Implementación del Ciclo Diario

```python
def advance_day(self):
    """Avanza la simulación un día."""
    current_day = self.services["simulation"].get_current_day()
    
    # Ejecutar simulación
    self.services["simulation"].run_day()
    
    # Actualizar día actual
    new_day = current_day + 1
    self.services["simulation"].set_current_day(new_day)
    
    # Obtener nuevos pedidos generados
    new_orders = self.repositories["manufacturing_order"].get_by_creation_date(
        self.services["date"].get_current_date()
    )
    
    return {
        "status": "success",
        "current_day": new_day,
        "new_orders": new_orders
    }
```

## 4. Generación de Demanda

### 4.1 Modelo Estocástico

La generación de demanda utiliza un modelo estocástico basado en la distribución normal:

```python
def generate_orders(self):
    """Genera nuevos pedidos basados en un modelo de demanda estocástico."""
    # Obtener parámetros de configuración
    demand_config = self.services["config"].get_demand_configuration()
    mean = demand_config["mean"]
    variance = demand_config["variance"]
    
    # Generar demanda aleatoria usando distribución normal
    quantity_p3d_classic = max(0, int(random.normalvariate(mean, math.sqrt(variance))))
    quantity_p3d_pro = max(0, int(random.normalvariate(mean-2, math.sqrt(variance))))
    
    # Crear pedidos
    if quantity_p3d_classic > 0:
        self._create_order(1, quantity_p3d_classic)  # P3D-Classic
    
    if quantity_p3d_pro > 0:
        self._create_order(2, quantity_p3d_pro)  # P3D-Pro
        
    # Simular el paso del tiempo para este proceso
    yield self.env.timeout(0)  # La generación es instantánea
```

### 4.2 Parámetros de Demanda

La demanda se configura mediante dos parámetros principales:

- **Media (mean)**: Número esperado de unidades demandadas por día.
- **Varianza (variance)**: Variabilidad de la demanda.

Estos parámetros pueden ajustarse en la configuración:

```json
{
  "demand": {
    "mean": 7,
    "variance": 2
  }
}
```

### 4.3 Distribución por Tipo de Producto

Por defecto, la demanda se distribuye entre los modelos de impresora con un ligero sesgo:

- **P3D-Classic**: Media configurada (por defecto 7)
- **P3D-Pro**: Media ligeramente menor (por defecto 5, calculada como mean-2)

Esta distribución refleja que el modelo básico suele tener más demanda que el modelo profesional.

## 5. Proceso de Fabricación

### 5.1 Capacidad de Producción

La capacidad de producción define cuántas impresoras pueden fabricarse simultáneamente:

```python
# En la inicialización del simulador
self.production_capacity = simpy.Resource(
    self.env, 
    capacity=self.services["config"].get_production_capacity()
)
```

Por defecto, la capacidad es de 10 unidades por día, lo que significa que se pueden fabricar hasta 10 impresoras (de cualquier modelo) simultáneamente.

### 5.2 Liberación de Pedidos

Cuando el usuario libera un pedido a producción, ocurre la siguiente secuencia:

1. **Verificación de materiales**:
   ```python
   def check_material_availability(self, product_id, quantity):
       """Verifica si hay suficientes materiales para fabricar un producto."""
       # Obtener BOM del producto
       bom_items = self.repositories["bom"].get_by_finished_product(product_id)
       
       # Verificar disponibilidad de cada material
       missing_materials = []
       for bom_item in bom_items:
           required_qty = bom_item.quantity * quantity
           stock = self.repositories["stock"].get_by_product_id(bom_item.material_id)
           
           if stock.quantity < required_qty:
               missing_materials.append({
                   "material_id": bom_item.material_id,
                   "required": required_qty,
                   "available": stock.quantity,
                   "missing": required_qty - stock.quantity
               })
       
       return missing_materials
   ```

2. **Consumo de materiales**:
   ```python
   def consume_materials(self, product_id, quantity):
       """Consume los materiales necesarios para fabricar un producto."""
       # Obtener BOM del producto
       bom_items = self.repositories["bom"].get_by_finished_product(product_id)
       
       # Consumir cada material
       for bom_item in bom_items:
           required_qty = bom_item.quantity * quantity
           self.repositories["stock"].decrease(bom_item.material_id, required_qty)
   ```

3. **Programación de la fabricación**:
   ```python
   def release_order(self, order_id):
       """Libera un pedido a producción."""
       order = self.repositories["manufacturing_order"].get_by_id(order_id)
       
       # Verificar disponibilidad
       missing = self.check_material_availability(order.product_id, order.quantity)
       if missing:
           return {"status": "error", "missing_materials": missing}
       
       # Consumir materiales
       self.consume_materials(order.product_id, order.quantity)
       
       # Actualizar estado del pedido
       order.status = "in_progress"
       self.repositories["manufacturing_order"].update(order)
       
       # Agregar proceso a la simulación
       self.env.process(self.fabrication_process(order))
       
       return {"status": "success"}
   ```

### 5.3 Proceso de Fabricación

El proceso de fabricación modela el tiempo que toma completar un pedido:

```python
def fabrication_process(self, order):
    """Proceso de fabricación de un pedido."""
    # Solicitar capacidad de producción
    with self.production_capacity.request() as req:
        yield req  # Esperar a que haya capacidad disponible
        
        # La fabricación toma 1 día
        yield self.env.timeout(1)
        
        # Completar pedido
        order.status = "completed"
        self.repositories["manufacturing_order"].update(order)
        
        # Aumentar inventario de producto terminado
        self.repositories["stock"].increase(order.product_id, order.quantity)
        
        # Registrar evento
        self.record_event(
            type="production_completed",
            details={"order_id": order.id, "product_id": order.product_id, "quantity": order.quantity}
        )
```

## 6. Gestión de Inventario

### 6.1 Modelo de Inventario

El inventario se modela como una simple tabla que asocia productos con cantidades:

```python
class StockRepository:
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def get_by_product_id(self, product_id):
        """Obtiene el nivel de stock para un producto específico."""
        cursor = self.db_connection.cursor()
        cursor.execute(
            "SELECT product_id, quantity FROM stock_current WHERE product_id = ?",
            (product_id,)
        )
        row = cursor.fetchone()
        if not row:
            return Stock(product_id=product_id, quantity=0)
        
        return Stock(product_id=row[0], quantity=row[1])
    
    def increase(self, product_id, quantity):
        """Aumenta el nivel de stock de un producto."""
        cursor = self.db_connection.cursor()
        cursor.execute(
            "UPDATE stock_current SET quantity = quantity + ? WHERE product_id = ?",
            (quantity, product_id)
        )
        if cursor.rowcount == 0:
            cursor.execute(
                "INSERT INTO stock_current (product_id, quantity) VALUES (?, ?)",
                (product_id, quantity)
            )
        self.db_connection.commit()
    
    def decrease(self, product_id, quantity):
        """Disminuye el nivel de stock de un producto."""
        cursor = self.db_connection.cursor()
        cursor.execute(
            "UPDATE stock_current SET quantity = quantity - ? WHERE product_id = ?",
            (quantity, product_id)
        )
        self.db_connection.commit()
```

### 6.2 Flujos de Inventario

El nivel de inventario cambia en respuesta a los siguientes eventos:

1. **Consumo de materiales**: Cuando se libera un pedido a producción, los materiales necesarios se consumen del inventario.
2. **Finalización de producción**: Cuando se completa un pedido, los productos terminados se añaden al inventario.
3. **Recepción de materiales**: Cuando llega una orden de compra, los materiales se añaden al inventario.

### 6.3 Verificación de Disponibilidad

Antes de liberar un pedido a producción, se verifica si hay suficientes materiales disponibles:

```python
def check_availability(self, product_id, quantity):
    """Verifica si hay suficientes materiales para producir una cantidad de un producto."""
    # Obtener BOM del producto
    bom_items = self.bom_repository.get_by_finished_product(product_id)
    
    # Verificar disponibilidad de cada material
    missing_materials = []
    for bom_item in bom_items:
        required_qty = bom_item.quantity * quantity
        stock = self.stock_repository.get_by_product_id(bom_item.material_id)
        
        if stock.quantity < required_qty:
            product = self.product_repository.get_by_id(bom_item.material_id)
            missing_materials.append({
                "material_id": bom_item.material_id,
                "material_name": product.name,
                "required": required_qty,
                "available": stock.quantity,
                "missing": required_qty - stock.quantity
            })
    
    return missing_materials
```

## 7. Proceso de Compras

### 7.1 Modelo de Proveedores

Cada proveedor se asocia con un material específico y tiene sus propias características:

```python
class Supplier(BaseModel):
    id: Optional[int] = None
    name: str
    product_id: int  # El material que provee
    unit_cost: float  # Costo por unidad
    lead_time_days: int  # Tiempo de entrega en días
```

### 7.2 Emisión de Órdenes de Compra

Cuando el usuario emite una orden de compra, se calcula la fecha de entrega basada en el tiempo de entrega del proveedor:

```python
def create_purchase_order(self, supplier_id, product_id, quantity):
    """Crea una nueva orden de compra."""
    # Obtener proveedor
    supplier = self.supplier_repository.get_by_id(supplier_id)
    
    # Calcular fecha actual y fecha estimada de entrega
    current_date = self.date_service.get_current_date()
    delivery_date = self.date_service.add_days(current_date, supplier.lead_time_days)
    
    # Crear orden de compra
    order = PurchaseOrder(
        supplier_id=supplier_id,
        product_id=product_id,
        quantity=quantity,
        issue_date=current_date,
        estimated_delivery_date=delivery_date,
        status="pending"
    )
    
    # Guardar en la base de datos
    order_id = self.purchase_order_repository.create(order)
    
    # Registrar evento
    self.event_repository.create(
        type="purchase_order_created",
        event_date=current_date,
        details=json.dumps({
            "order_id": order_id,
            "supplier_id": supplier_id,
            "product_id": product_id,
            "quantity": quantity,
            "cost": supplier.unit_cost * quantity
        })
    )
    
    return order_id
```

### 7.3 Recepción de Materiales

Al avanzar cada día, se verifica si alguna orden de compra debe recibirse:

```python
def process_purchase_orders(self):
    """Procesa las órdenes de compra pendientes."""
    current_date = self.services["date"].get_current_date()
    
    # Obtener órdenes pendientes
    pending_orders = self.repositories["purchase_order"].get_by_status("pending")
    
    for order in pending_orders:
        # Verificar si ha llegado la fecha de entrega
        if order.estimated_delivery_date <= current_date:
            # Actualizar estado de la orden
            order.status = "received"
            self.repositories["purchase_order"].update(order)
            
            # Aumentar inventario
            self.repositories["stock"].increase(order.product_id, order.quantity)
            
            # Registrar evento
            self.record_event(
                type="materials_received",
                details={
                    "order_id": order.id,
                    "product_id": order.product_id,
                    "quantity": order.quantity
                }
            )
    
    # Simular el paso del tiempo para este proceso
    yield self.env.timeout(0)  # El procesamiento es instantáneo
```

## 8. Eventos y Registro

### 8.1 Tipos de Eventos

El sistema registra varios tipos de eventos para análisis histórico:

- **order_created**: Cuando se genera un nuevo pedido de fabricación.
- **production_started**: Cuando se libera un pedido a producción.
- **production_completed**: Cuando se completa la fabricación de un pedido.
- **purchase_order_created**: Cuando se emite una orden de compra.
- **materials_received**: Cuando se reciben materiales de una orden de compra.

### 8.2 Estructura de Eventos

Cada evento tiene la siguiente estructura:

```python
class Event(BaseModel):
    id: Optional[int] = None
    type: str  # Tipo de evento
    event_date: str  # Fecha del evento en formato ISO (YYYY-MM-DD)
    details: str  # Detalles del evento en formato JSON
```

### 8.3 Registro de Eventos

El registro de eventos se realiza mediante el método `record_event`:

```python
def record_event(self, type, details):
    """Registra un evento en el sistema."""
    current_date = self.services["date"].get_current_date()
    
    # Crear evento
    event = Event(
        type=type,
        event_date=current_date,
        details=json.dumps(details)
    )
    
    # Guardar en la base de datos
    self.repositories["event"].create(event)
```

## 9. Parámetros Configurables

El comportamiento de la simulación puede ajustarse mediante varios parámetros configurables:

### 9.1 Configuración General

Los parámetros generales se almacenan en `data/config.json`:

```json
{
  "production_capacity": 10,
  "demand": {
    "mean": 7,
    "variance": 2
  },
  "initial_stock": {
    "raw_materials": {
      "kit_piezas": 30,
      "pcb_v2": 20,
      "pcb_v3": 10,
      "extrusor": 25,
      "sensor_autonivel": 15,
      "cables_conexion": 50,
      "transformador_24v": 20,
      "enchufe_schuko": 30
    },
    "finished_products": {
      "P3D-Classic": 0,
      "P3D-Pro": 0
    }
  }
}
```

### 9.2 Parámetros Clave

- **production_capacity**: Número máximo de impresoras que pueden fabricarse por día.
- **demand.mean**: Media de la distribución normal para la generación de demanda.
- **demand.variance**: Varianza de la distribución normal para la generación de demanda.
- **initial_stock**: Niveles iniciales de inventario para materias primas y productos terminados.

### 9.3 Modificación de Parámetros

Los parámetros pueden modificarse mediante:

1. **Edición directa del archivo de configuración**:
   ```bash
   nano data/config.json
   ```

2. **API de configuración**:
   ```python
   @app.put("/api/config/production-capacity")
   def update_production_capacity(capacity: int):
       config_service = container.get_config_service()
       config_service.set_production_capacity(capacity)
       return {"status": "success", "production_capacity": capacity}
   ```

3. **Interfaz de usuario**:
   ```python
   def show_config_editor():
       st.header("Configuración de Simulación")
       
       # Obtener configuración actual
       response = requests.get(f"{API_URL}/config")
       config = response.json()
       
       # Editor de capacidad de producción
       new_capacity = st.number_input(
           "Capacidad de producción diaria", 
           min_value=1, 
           max_value=50, 
           value=config["production_capacity"]
       )
       
       # Otros parámetros...
       
       # Botón para guardar cambios
       if st.button("Guardar cambios"):
           requests.put(
               f"{API_URL}/config/production-capacity", 
               json=new_capacity
           )
           st.success("Configuración actualizada")
   ```

## 10. Implementación Técnica

### 10.1 Clase Principal de Simulación

La implementación técnica se centra en la clase `ProductionSimulator`:

```python
class ProductionSimulator:
    def __init__(self, repositories, services):
        """Inicializa el simulador de producción."""
        self.env = simpy.Environment()
        self.repositories = repositories
        self.services = services
        
        # Configurar recursos
        capacity = self.services["config"].get_production_capacity()
        self.production_capacity = simpy.Resource(self.env, capacity=capacity)
    
    def run_day(self):
        """Ejecuta un día completo de simulación."""
        # Configurar procesos
        self.env.process(self.generate_orders())
        self.env.process(self.process_manufacturing_orders())
        self.env.process(self.process_purchase_orders())
        
        # Avanzar la simulación un día
        self.env.run(until=self.env.now + 1)
    
    def generate_orders(self):
        """Genera nuevos pedidos de fabricación."""
        # Implementación...
        yield self.env.timeout(0)
    
    def process_manufacturing_orders(self):
        """Procesa pedidos en producción."""
        # Implementación...
        yield self.env.timeout(0)
    
    def process_purchase_orders(self):
        """Procesa órdenes de compra pendientes."""
        # Implementación...
        yield self.env.timeout(0)
    
    def fabrication_process(self, order):
        """Modelado del proceso de fabricación."""
        # Implementación...
        yield self.env.timeout(1)
    
    def record_event(self, type, details):
        """Registra un evento en el sistema."""
        # Implementación...
```

### 10.2 Integración con el Resto del Sistema

La clase `ProductionSimulator` se integra con el resto del sistema a través del contenedor de inyección de dependencias:

```python
class DIContainer:
    def __init__(self):
        self.db_connection = None
        self.repositories = {}
        self.services = {}
    
    def initialize(self):
        # Configurar conexión a BD
        self.db_connection = create_db_connection()
        
        # Crear repositorios
        self.repositories["product"] = SQLiteProductRepository(self.db_connection)
        self.repositories["bom"] = SQLiteBOMRepository(self.db_connection)
        # ... otros repositorios
        
        # Crear servicios básicos
        self.services["date"] = DateService()
        self.services["config"] = ConfigurationService()
        
        # Crear simulador
        self.services["simulation"] = ProductionSimulator(self.repositories, self.services)
        
        # Crear servicios de aplicación
        self.services["inventory"] = InventoryService(
            self.repositories["product"],
            self.repositories["bom"],
            self.repositories["stock"]
        )
        # ... otros servicios
```

### 10.3 Estructura de Datos en Memoria

Durante la simulación, los datos se mantienen principalmente en la base de datos, pero algunos estados temporales se mantienen en memoria:

```python
# Estado temporal del simulador
self.env = simpy.Environment()  # Entorno de simulación
self.production_capacity = simpy.Resource(self.env, capacity=capacity)  # Recurso de capacidad

# Los procesos en ejecución se mantienen como referencias a generadores
self.active_processes = []  # Lista de procesos activos
```

Los procesos de fabricación se modelan como generadores de Python y se programan en el entorno de SimPy, que mantiene internamente una cola de eventos futuros ordenada por tiempo.

## Conclusión

La lógica de simulación del Simulador de Producción de Impresoras 3D utiliza el paradigma de simulación de eventos discretos implementado a través de SimPy para modelar los procesos de producción, gestión de inventario y compras. 

El sistema está diseñado para ser configurable y extensible, permitiendo ajustar parámetros como la capacidad de producción, la demanda esperada y su variabilidad. La arquitectura modular facilita la adición de nuevas funcionalidades o la modificación de las reglas de negocio existentes.

La combinación de un modelo de dominio claro con un motor de simulación potente proporciona una base sólida para simular escenarios realistas y ayudar a los usuarios a practicar y mejorar sus habilidades de planificación de producción.