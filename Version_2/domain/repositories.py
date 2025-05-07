from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from datetime import date

from domain.models import (
    Product, BOM, Supplier, StockCurrent, 
    ManufacturingOrder, PurchaseOrder, Event
)

T = TypeVar('T')

class Repository(Generic[T], ABC):
    """Interfaz base para todos los repositorios."""
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        pass
    
    @abstractmethod
    def add(self, entity: T) -> T:
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        pass


class ProductRepository(Repository[Product], ABC):
    """Repositorio específico para productos."""
    
    @abstractmethod
    def get_by_type(self, type: str) -> List[Product]:
        """Obtiene productos por su tipo (raw/finished)."""
        pass


class BOMRepository(Repository[BOM], ABC):
    """Repositorio para la lista de materiales (BOM)."""
    
    @abstractmethod
    def get_by_finished_product(self, finished_product_id: int) -> List[BOM]:
        """Obtiene materiales requeridos para un producto terminado."""
        pass


class SupplierRepository(Repository[Supplier], ABC):
    """Repositorio para proveedores."""
    
    @abstractmethod
    def get_by_product(self, product_id: int) -> List[Supplier]:
        """Obtiene proveedores que suministran un producto específico."""
        pass


class StockRepository(Repository[StockCurrent], ABC):
    """Repositorio para el inventario actual."""
    
    @abstractmethod
    def get_by_product(self, product_id: int) -> Optional[StockCurrent]:
        """Obtiene el nivel de inventario para un producto específico."""
        pass
    
    @abstractmethod
    def update_quantity(self, product_id: int, quantity: int) -> StockCurrent:
        """Actualiza la cantidad en inventario de un producto."""
        pass


class ManufacturingOrderRepository(Repository[ManufacturingOrder], ABC):
    """Repositorio para órdenes de fabricación."""
    
    @abstractmethod
    def get_by_status(self, status: str) -> List[ManufacturingOrder]:
        """Obtiene órdenes de fabricación por estado."""
        pass
    
    @abstractmethod
    def get_by_date_range(self, start_date: str, end_date: str) -> List[ManufacturingOrder]:
        """Obtiene órdenes de fabricación dentro de un rango de fechas."""
        pass


class PurchaseOrderRepository(Repository[PurchaseOrder], ABC):
    """Repositorio para órdenes de compra."""
    
    @abstractmethod
    def get_by_status(self, status: str) -> List[PurchaseOrder]:
        """Obtiene órdenes de compra por estado."""
        pass
    
    @abstractmethod
    def get_by_date_range(self, start_date: str, end_date: str) -> List[PurchaseOrder]:
        """Obtiene órdenes de compra dentro de un rango de fechas."""
        pass


class EventRepository(Repository[Event], ABC):
    """Repositorio para eventos del sistema."""
    
    @abstractmethod
    def get_by_type(self, type: str) -> List[Event]:
        """Obtiene eventos por tipo."""
        pass
    
    @abstractmethod
    def get_by_date_range(self, start_date: str, end_date: str) -> List[Event]:
        """Obtiene eventos dentro de un rango de fechas."""
        pass
