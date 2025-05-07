import json
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime, date
import os
from pathlib import Path

from domain.models import (
    Product, BOM, Supplier, StockCurrent, 
    ManufacturingOrder, PurchaseOrder, Event,
    SimulationConfig
)

from domain.repositories import (
    ProductRepository, BOMRepository, SupplierRepository, 
    StockRepository, ManufacturingOrderRepository, 
    PurchaseOrderRepository, EventRepository
)

class DataExporter:
    """Clase para exportar datos del simulador a JSON."""
    
    def __init__(
        self,
        product_repository: ProductRepository,
        bom_repository: BOMRepository,
        supplier_repository: SupplierRepository,
        stock_repository: StockRepository,
        manufacturing_repository: ManufacturingOrderRepository,
        purchase_repository: PurchaseOrderRepository,
        event_repository: EventRepository
    ):
        self.product_repository = product_repository
        self.bom_repository = bom_repository
        self.supplier_repository = supplier_repository
        self.stock_repository = stock_repository
        self.manufacturing_repository = manufacturing_repository
        self.purchase_repository = purchase_repository
        self.event_repository = event_repository
    
    def export_all_data(self, file_path: str) -> None:
        """
        Exporta todos los datos del simulador a un archivo JSON.
        
        Args:
            file_path: Ruta donde guardar el archivo JSON
        """
        data = {
            "products": [product.dict() for product in self.product_repository.get_all()],
            "bom": [bom.dict() for bom in self.bom_repository.get_all()],
            "suppliers": [supplier.dict() for supplier in self.supplier_repository.get_all()],
            "stock": [stock.dict() for stock in self.stock_repository.get_all()],
            "manufacturing_orders": [order.dict() for order in self.manufacturing_repository.get_all()],
            "purchase_orders": [order.dict() for order in self.purchase_repository.get_all()],
            "events": [event.dict() for event in self.event_repository.get_all()]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def export_inventory(self, file_path: str) -> None:
        """
        Exporta solo los datos de inventario a un archivo JSON.
        
        Args:
            file_path: Ruta donde guardar el archivo JSON
        """
        all_stock = self.stock_repository.get_all()
        stock_data = []
        
        for stock_item in all_stock:
            product = self.product_repository.get_by_id(stock_item.product_id)
            if product:
                stock_data.append({
                    "product_id": stock_item.product_id,
                    "product_name": product.name,
                    "product_type": product.type,
                    "quantity": stock_item.quantity
                })
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(stock_data, f, indent=2, ensure_ascii=False)
    
    def export_events(self, file_path: str) -> None:
        """
        Exporta solo los eventos a un archivo JSON.
        
        Args:
            file_path: Ruta donde guardar el archivo JSON
        """
        all_events = self.event_repository.get_all()
        events_data = [event.dict() for event in all_events]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(events_data, f, indent=2, ensure_ascii=False)


class DataImporter:
    """Clase para importar datos del simulador desde JSON."""
    
    def __init__(
        self,
        product_repository: ProductRepository,
        bom_repository: BOMRepository,
        supplier_repository: SupplierRepository,
        stock_repository: StockRepository,
        manufacturing_repository: ManufacturingOrderRepository,
        purchase_repository: PurchaseOrderRepository,
        event_repository: EventRepository
    ):
        self.product_repository = product_repository
        self.bom_repository = bom_repository
        self.supplier_repository = supplier_repository
        self.stock_repository = stock_repository
        self.manufacturing_repository = manufacturing_repository
        self.purchase_repository = purchase_repository
        self.event_repository = event_repository
    
    def import_all_data(self, file_path: str) -> None:
        """
        Importa todos los datos del simulador desde un archivo JSON.
        
        Args:
            file_path: Ruta del archivo JSON a importar
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Importar productos primero (dependencia básica)
        for product_data in data.get("products", []):
            product = Product(**product_data)
            self.product_repository.add(product)
        
        # Importar BOM
        for bom_data in data.get("bom", []):
            bom = BOM(**bom_data)
            self.bom_repository.add(bom)
        
        # Importar proveedores
        for supplier_data in data.get("suppliers", []):
            supplier = Supplier(**supplier_data)
            self.supplier_repository.add(supplier)
        
        # Importar inventario
        for stock_data in data.get("stock", []):
            stock = StockCurrent(**stock_data)
            self.stock_repository.add(stock)
        
        # Importar órdenes de fabricación
        for order_data in data.get("manufacturing_orders", []):
            order = ManufacturingOrder(**order_data)
            self.manufacturing_repository.add(order)
        
        # Importar órdenes de compra
        for order_data in data.get("purchase_orders", []):
            order = PurchaseOrder(**order_data)
            self.purchase_repository.add(order)
        
        # Importar eventos
        for event_data in data.get("events", []):
            event = Event(**event_data)
            self.event_repository.add(event)
    
    def import_from_json_string(self, json_string: str) -> None:
        """
        Importa datos desde una cadena JSON.
        
        Args:
            json_string: Cadena JSON con los datos a importar
        """
        data = json.loads(json_string)
        
        # Importar productos primero (dependencia básica)
        for product_data in data.get("products", []):
            product = Product(**product_data)
            self.product_repository.add(product)
        
        # Continuar con el resto de los datos como en import_all_data
        # ...
