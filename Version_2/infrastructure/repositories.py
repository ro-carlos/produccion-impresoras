from typing import List, Optional, Dict, Any
import json
from datetime import datetime, date

from domain.models import (
    Product, BOM, Supplier, StockCurrent, 
    ManufacturingOrder, PurchaseOrder, Event,
    ManufacturingOrderStatus, PurchaseOrderStatus, EventType
)
from domain.repositories import (
    ProductRepository, BOMRepository, SupplierRepository, 
    StockRepository, ManufacturingOrderRepository, 
    PurchaseOrderRepository, EventRepository
)
from infrastructure.database import Database

class SQLiteProductRepository(ProductRepository):
    """Implementación SQLite del repositorio de productos."""
    
    def __init__(self, database: Database):
        self.db = database
    
    def get_by_id(self, id: int) -> Optional[Product]:
        """Obtiene un producto por su ID."""
        result = self.db.execute_and_fetchone(
            "SELECT * FROM products WHERE id = ?", (id,)
        )
        if result:
            return Product(**result)
        return None
    
    def get_all(self) -> List[Product]:
        """Obtiene todos los productos."""
        results = self.db.execute_and_fetchall("SELECT * FROM products")
        return [Product(**result) for result in results]
    
    def add(self, entity: Product) -> Product:
        """Añade un nuevo producto."""
        cursor = self.db.execute(
            "INSERT INTO products (name, type) VALUES (?, ?)",
            (entity.name, entity.type)
        )
        entity.id = cursor.lastrowid
        return entity
    
    def update(self, entity: Product) -> Product:
        """Actualiza un producto existente."""
        self.db.execute(
            "UPDATE products SET name = ?, type = ? WHERE id = ?",
            (entity.name, entity.type, entity.id)
        )
        return entity
    
    def delete(self, id: int) -> bool:
        """Elimina un producto por su ID."""
        cursor = self.db.execute("DELETE FROM products WHERE id = ?", (id,))
        return cursor.rowcount > 0
    
    def get_by_type(self, type: str) -> List[Product]:
        """Obtiene productos por su tipo (raw/finished)."""
        results = self.db.execute_and_fetchall(
            "SELECT * FROM products WHERE type = ?", (type,)
        )
        return [Product(**result) for result in results]


class SQLiteBOMRepository(BOMRepository):
    """Implementación SQLite del repositorio de BOM."""
    
    def __init__(self, database: Database):
        self.db = database
    
    def get_by_id(self, id: int) -> Optional[BOM]:
        """Obtiene un registro BOM por su ID."""
        result = self.db.execute_and_fetchone(
            "SELECT * FROM bom WHERE id = ?", (id,)
        )
        if result:
            return BOM(**{k: v for k, v in result.items() if k != 'id'})
        return None
    
    def get_all(self) -> List[BOM]:
        """Obtiene todos los registros BOM."""
        results = self.db.execute_and_fetchall("SELECT * FROM bom")
        return [BOM(**{k: v for k, v in result.items() if k != 'id'}) for result in results]
    
    def add(self, entity: BOM) -> BOM:
        """Añade un nuevo registro BOM."""
        cursor = self.db.execute(
            "INSERT INTO bom (finished_product_id, material_id, quantity) VALUES (?, ?, ?)",
            (entity.finished_product_id, entity.material_id, entity.quantity)
        )
        # No actualizamos el ID ya que el modelo BOM no tiene un campo ID en el dominio
        return entity
    
    def update(self, entity: BOM) -> BOM:
        """Actualiza un registro BOM existente."""
        self.db.execute(
            """
            UPDATE bom 
            SET quantity = ? 
            WHERE finished_product_id = ? AND material_id = ?
            """,
            (entity.quantity, entity.finished_product_id, entity.material_id)
        )
        return entity
    
    def delete(self, id: int) -> bool:
        """Elimina un registro BOM por su ID."""
        cursor = self.db.execute("DELETE FROM bom WHERE id = ?", (id,))
        return cursor.rowcount > 0
    
    def get_by_finished_product(self, finished_product_id: int) -> List[BOM]:
        """Obtiene materiales requeridos para un producto terminado."""
        results = self.db.execute_and_fetchall(
            "SELECT * FROM bom WHERE finished_product_id = ?", 
            (finished_product_id,)
        )
        return [BOM(**{k: v for k, v in result.items() if k != 'id'}) for result in results]


class SQLiteSupplierRepository(SupplierRepository):
    """Implementación SQLite del repositorio de proveedores."""
    
    def __init__(self, database: Database):
        self.db = database
    
    def get_by_id(self, id: int) -> Optional[Supplier]:
        """Obtiene un proveedor por su ID."""
        result = self.db.execute_and_fetchone(
            "SELECT * FROM suppliers WHERE id = ?", (id,)
        )
        if result:
            return Supplier(**result)
        return None
    
    def get_all(self) -> List[Supplier]:
        """Obtiene todos los proveedores."""
        results = self.db.execute_and_fetchall("SELECT * FROM suppliers")
        return [Supplier(**result) for result in results]
    
    def add(self, entity: Supplier) -> Supplier:
        """Añade un nuevo proveedor."""
        cursor = self.db.execute(
            """
            INSERT INTO suppliers (name, product_id, unit_cost, lead_time_days) 
            VALUES (?, ?, ?, ?)
            """,
            (entity.name, entity.product_id, entity.unit_cost, entity.lead_time_days)
        )
        entity.id = cursor.lastrowid
        return entity
    
    def update(self, entity: Supplier) -> Supplier:
        """Actualiza un proveedor existente."""
        self.db.execute(
            """
            UPDATE suppliers 
            SET name = ?, product_id = ?, unit_cost = ?, lead_time_days = ? 
            WHERE id = ?
            """,
            (
                entity.name, entity.product_id, entity.unit_cost, 
                entity.lead_time_days, entity.id
            )
        )
        return entity
    
    def delete(self, id: int) -> bool:
        """Elimina un proveedor por su ID."""
        cursor = self.db.execute("DELETE FROM suppliers WHERE id = ?", (id,))
        return cursor.rowcount > 0
    
    def get_by_product(self, product_id: int) -> List[Supplier]:
        """Obtiene proveedores que suministran un producto específico."""
        results = self.db.execute_and_fetchall(
            "SELECT * FROM suppliers WHERE product_id = ?", 
            (product_id,)
        )
        return [Supplier(**result) for result in results]


class SQLiteStockRepository(StockRepository):
    """Implementación SQLite del repositorio de inventario."""
    
    def __init__(self, database: Database):
        self.db = database
    
    def get_by_id(self, id: int) -> Optional[StockCurrent]:
        """Obtiene un registro de inventario por su ID."""
        result = self.db.execute_and_fetchone(
            "SELECT * FROM stock_current WHERE id = ?", (id,)
        )
        if result:
            return StockCurrent(**{k: v for k, v in result.items() if k != 'id'})
        return None
    
    def get_all(self) -> List[StockCurrent]:
        """Obtiene todos los registros de inventario."""
        results = self.db.execute_and_fetchall("SELECT * FROM stock_current")
        return [StockCurrent(**{k: v for k, v in result.items() if k != 'id'}) for result in results]
    
    def add(self, entity: StockCurrent) -> StockCurrent:
        """Añade un nuevo registro de inventario."""
        cursor = self.db.execute(
            "INSERT INTO stock_current (product_id, quantity) VALUES (?, ?)",
            (entity.product_id, entity.quantity)
        )
        # No actualizamos el ID ya que el modelo StockCurrent no tiene un campo ID en el dominio
        return entity
    
    def update(self, entity: StockCurrent) -> StockCurrent:
        """Actualiza un registro de inventario existente."""
        self.db.execute(
            "UPDATE stock_current SET quantity = ? WHERE product_id = ?",
            (entity.quantity, entity.product_id)
        )
        return entity
    
    def delete(self, id: int) -> bool:
        """Elimina un registro de inventario por su ID."""
        cursor = self.db.execute("DELETE FROM stock_current WHERE id = ?", (id,))
        return cursor.rowcount > 0
    
    def get_by_product(self, product_id: int) -> Optional[StockCurrent]:
        """Obtiene el nivel de inventario para un producto específico."""
        result = self.db.execute_and_fetchone(
            "SELECT * FROM stock_current WHERE product_id = ?", 
            (product_id,)
        )
        if result:
            return StockCurrent(**{k: v for k, v in result.items() if k != 'id'})
        return None
    
    def update_quantity(self, product_id: int, quantity: int) -> StockCurrent:
        """Actualiza la cantidad en inventario de un producto."""
        # Verificar si ya existe un registro para este producto
        existing = self.get_by_product(product_id)
        
        if existing:
            # Actualizar registro existente
            existing.quantity = quantity
            self.update(existing)
            return existing
        else:
            # Crear nuevo registro
            new_stock = StockCurrent(product_id=product_id, quantity=quantity)
            self.add(new_stock)
            return new_stock


class SQLiteManufacturingOrderRepository(ManufacturingOrderRepository):
    """Implementación SQLite del repositorio de órdenes de fabricación."""
    
    def __init__(self, database: Database):
        self.db = database
    
    def get_by_id(self, id: int) -> Optional[ManufacturingOrder]:
        """Obtiene una orden de fabricación por su ID."""
        result = self.db.execute_and_fetchone(
            "SELECT * FROM manufacturing_orders WHERE id = ?", (id,)
        )
        if result:
            return ManufacturingOrder(**result)
        return None
    
    def get_all(self) -> List[ManufacturingOrder]:
        """Obtiene todas las órdenes de fabricación."""
        results = self.db.execute_and_fetchall("SELECT * FROM manufacturing_orders")
        return [ManufacturingOrder(**result) for result in results]
    
    def add(self, entity: ManufacturingOrder) -> ManufacturingOrder:
        """Añade una nueva orden de fabricación."""
        cursor = self.db.execute(
            """
            INSERT INTO manufacturing_orders 
            (creation_date, product_id, quantity, status) 
            VALUES (?, ?, ?, ?)
            """,
            (
                entity.creation_date, entity.product_id, 
                entity.quantity, entity.status
            )
        )
        entity.id = cursor.lastrowid
        return entity
    
    def update(self, entity: ManufacturingOrder) -> ManufacturingOrder:
        """Actualiza una orden de fabricación existente."""
        self.db.execute(
            """
            UPDATE manufacturing_orders 
            SET creation_date = ?, product_id = ?, quantity = ?, status = ? 
            WHERE id = ?
            """,
            (
                entity.creation_date, entity.product_id, 
                entity.quantity, entity.status, entity.id
            )
        )
        return entity
    
    def delete(self, id: int) -> bool:
        """Elimina una orden de fabricación por su ID."""
        cursor = self.db.execute("DELETE FROM manufacturing_orders WHERE id = ?", (id,))
        return cursor.rowcount > 0
    
    def get_by_status(self, status: str) -> List[ManufacturingOrder]:
        """Obtiene órdenes de fabricación por estado."""
        results = self.db.execute_and_fetchall(
            "SELECT * FROM manufacturing_orders WHERE status = ?", 
            (status,)
        )
        return [ManufacturingOrder(**result) for result in results]
    
    def get_by_date_range(self, start_date: str, end_date: str) -> List[ManufacturingOrder]:
        """Obtiene órdenes de fabricación dentro de un rango de fechas."""
        results = self.db.execute_and_fetchall(
            """
            SELECT * FROM manufacturing_orders 
            WHERE creation_date BETWEEN ? AND ?
            """, 
            (start_date, end_date)
        )
        return [ManufacturingOrder(**result) for result in results]


class SQLitePurchaseOrderRepository(PurchaseOrderRepository):
    """Implementación SQLite del repositorio de órdenes de compra."""
    
    def __init__(self, database: Database):
        self.db = database
    
    def get_by_id(self, id: int) -> Optional[PurchaseOrder]:
        """Obtiene una orden de compra por su ID."""
        result = self.db.execute_and_fetchone(
            "SELECT * FROM purchase_orders WHERE id = ?", (id,)
        )
        if result:
            return PurchaseOrder(**result)
        return None
    
    def get_all(self) -> List[PurchaseOrder]:
        """Obtiene todas las órdenes de compra."""
        results = self.db.execute_and_fetchall("SELECT * FROM purchase_orders")
        return [PurchaseOrder(**result) for result in results]
    
    def add(self, entity: PurchaseOrder) -> PurchaseOrder:
        """Añade una nueva orden de compra."""
        cursor = self.db.execute(
            """
            INSERT INTO purchase_orders 
            (supplier_id, product_id, quantity, issue_date, estimated_delivery_date, status) 
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                entity.supplier_id, entity.product_id, entity.quantity,
                entity.issue_date, entity.estimated_delivery_date, entity.status
            )
        )
        entity.id = cursor.lastrowid
        return entity
    
    def update(self, entity: PurchaseOrder) -> PurchaseOrder:
        """Actualiza una orden de compra existente."""
        self.db.execute(
            """
            UPDATE purchase_orders 
            SET supplier_id = ?, product_id = ?, quantity = ?, 
                issue_date = ?, estimated_delivery_date = ?, status = ? 
            WHERE id = ?
            """,
            (
                entity.supplier_id, entity.product_id, entity.quantity,
                entity.issue_date, entity.estimated_delivery_date, 
                entity.status, entity.id
            )
        )
        return entity
    
    def delete(self, id: int) -> bool:
        """Elimina una orden de compra por su ID."""
        cursor = self.db.execute("DELETE FROM purchase_orders WHERE id = ?", (id,))
        return cursor.rowcount > 0
    
    def get_by_status(self, status: str) -> List[PurchaseOrder]:
        """Obtiene órdenes de compra por estado."""
        results = self.db.execute_and_fetchall(
            "SELECT * FROM purchase_orders WHERE status = ?", 
            (status,)
        )
        return [PurchaseOrder(**result) for result in results]
    
    def get_by_date_range(self, start_date: str, end_date: str) -> List[PurchaseOrder]:
        """Obtiene órdenes de compra dentro de un rango de fechas."""
        results = self.db.execute_and_fetchall(
            """
            SELECT * FROM purchase_orders 
            WHERE issue_date BETWEEN ? AND ?
            """, 
            (start_date, end_date)
        )
        return [PurchaseOrder(**result) for result in results]


class SQLiteEventRepository(EventRepository):
    """Implementación SQLite del repositorio de eventos."""
    
    def __init__(self, database: Database):
        self.db = database
    
    def get_by_id(self, id: int) -> Optional[Event]:
        """Obtiene un evento por su ID."""
        result = self.db.execute_and_fetchone(
            "SELECT * FROM events WHERE id = ?", (id,)
        )
        if result:
            return Event(**result)
        return None
    
    def get_all(self) -> List[Event]:
        """Obtiene todos los eventos."""
        results = self.db.execute_and_fetchall("SELECT * FROM events")
        return [Event(**result) for result in results]
    
    def add(self, entity: Event) -> Event:
        """Añade un nuevo evento."""
        cursor = self.db.execute(
            "INSERT INTO events (type, event_date, details) VALUES (?, ?, ?)",
            (entity.type, entity.event_date, entity.details)
        )
        entity.id = cursor.lastrowid
        return entity
    
    def update(self, entity: Event) -> Event:
        """Actualiza un evento existente."""
        self.db.execute(
            "UPDATE events SET type = ?, event_date = ?, details = ? WHERE id = ?",
            (entity.type, entity.event_date, entity.details, entity.id)
        )
        return entity
    
    def delete(self, id: int) -> bool:
        """Elimina un evento por su ID."""
        cursor = self.db.execute("DELETE FROM events WHERE id = ?", (id,))
        return cursor.rowcount > 0
    
    def get_by_type(self, type: str) -> List[Event]:
        """Obtiene eventos por tipo."""
        results = self.db.execute_and_fetchall(
            "SELECT * FROM events WHERE type = ?", 
            (type,)
        )
        return [Event(**result) for result in results]
    
    def get_by_date_range(self, start_date: str, end_date: str) -> List[Event]:
        """Obtiene eventos dentro de un rango de fechas."""
        results = self.db.execute_and_fetchall(
            "SELECT * FROM events WHERE event_date BETWEEN ? AND ?", 
            (start_date, end_date)
        )
        return [Event(**result) for result in results]
