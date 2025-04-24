# src/entities.py

from pydantic import BaseModel, Field
from typing import Literal, Dict, Any, List
from datetime import date, datetime

class Product(BaseModel):
    id: int
    name: str
    type: Literal["raw", "finished"]

class BOMItem(BaseModel):
    finished_product_id: int
    material_id: int
    quantity: float

class Supplier(BaseModel):
    id: int
    product_id: int
    unit_cost: float
    lead_time: int  # days

class InventoryItem(BaseModel):
    product_id: int
    qty: float

class ProductionOrder(BaseModel):
    id: int
    created_date: date
    product_id: int
    quantity: int
    status: Literal["pending", "in_production", "completed", "cancelled"] = "pending"

class PurchaseOrder(BaseModel):
    id: int
    supplier_id: int
    product_id: int
    quantity: int
    order_date: date
    est_delivery_date: date
    status: Literal["pending", "shipped", "received", "cancelled"] = "pending"

class PurchaseOrderDetail(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    unit_price: float

class Event(BaseModel):
    id: int
    event_type: Literal[
        "production",
        "purchase_arrival",
        "order_released",
        "order_created"
    ]
    timestamp: datetime
    details: Dict[str, Any]

class SimulationConfig(BaseModel):
    capacity_per_day: int
    avg_daily_demand: float
    demand_variance: float

class DailyPlan(BaseModel):
    day: int
    orders: List[Dict[str, int]]  # e.g. [{"model": "P3D-Classic", "quantity": 8}, ...]

class SimulationState(BaseModel):
    day: int
    inventory: List[InventoryItem]
    pending_orders: List[ProductionOrder]
    purchase_orders: List[PurchaseOrder]
    events: List[Event]