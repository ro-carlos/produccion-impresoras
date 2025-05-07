from typing import Literal
from pydantic import BaseModel
from datetime import date
from enum import Enum

# Enumeraciones para estados
class ManufacturingOrderStatus(str, Enum):
    PENDING = "pending"
    IN_PRODUCTION = "in_production"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PurchaseOrderStatus(str, Enum):
    PENDING = "pending"
    ORDERED = "ordered"
    RECEIVED = "received"
    CANCELLED = "cancelled"

class EventType(str, Enum):
    MANUFACTURING_ORDER_CREATED = "manufacturing_order_created"
    MANUFACTURING_ORDER_STARTED = "manufacturing_order_started"
    MANUFACTURING_ORDER_COMPLETED = "manufacturing_order_completed"
    PURCHASE_ORDER_CREATED = "purchase_order_created"
    PURCHASE_ORDER_RECEIVED = "purchase_order_received"
    STOCK_LEVEL_CHANGED = "stock_level_changed"
    DAY_ADVANCED = "day_advanced"

# Productos
class Product(BaseModel):
    id: int
    name: str
    type: Literal["raw", "finished"]  # Tipo de producto
    
    def __str__(self) -> str:
        return f"{self.name} ({self.id})"

# Composición de productos (Bill of Materials)
class BOM(BaseModel):
    finished_product_id: int
    material_id: int
    quantity: int

# Proveedores
class Supplier(BaseModel):
    id: int
    name: str
    product_id: int  # Producto que provee
    unit_cost: float
    lead_time_days: int  # Tiempo de entrega en días
    
    def __str__(self) -> str:
        return f"{self.name} ({self.id})"

# Inventario actual
class StockCurrent(BaseModel):
    product_id: int
    quantity: int

# Pedidos de fabricación
class ManufacturingOrder(BaseModel):
    id: int
    creation_date: str  # ISO 8601 o formato consistente
    product_id: int
    quantity: int
    status: ManufacturingOrderStatus

# Órdenes de compra
class PurchaseOrder(BaseModel):
    id: int
    supplier_id: int
    product_id: int
    quantity: int
    issue_date: str
    estimated_delivery_date: str
    status: PurchaseOrderStatus

# Eventos
class Event(BaseModel):
    id: int
    type: EventType
    event_date: str
    details: str

# Clase para configuración del simulador
class SimulationConfig(BaseModel):
    initial_day: date
    demand_mean: float
    demand_std_dev: float
    production_capacity_per_day: int
    warehouse_capacity: int
