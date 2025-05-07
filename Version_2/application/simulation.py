import simpy
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, date, timedelta
import random
import json
from dataclasses import dataclass

from domain.models import (
    ManufacturingOrder, PurchaseOrder, Event,
    EventType, SimulationConfig
)

from domain.services import (
    InventoryService, BOMService, 
    ManufacturingService, PurchasingService
)

@dataclass
class SimulationState:
    """Estado actual de la simulación."""
    current_date: date
    events_today: List[Event] = None
    
    def __post_init__(self):
        if self.events_today is None:
            self.events_today = []


class ProductionSimulator:
    """
    Simulador de producción de impresoras 3D utilizando SimPy.
    """
    
    def __init__(
        self,
        inventory_service: InventoryService,
        bom_service: BOMService,
        manufacturing_service: ManufacturingService,
        purchasing_service: PurchasingService,
        config: SimulationConfig,
        product_repository=None  # Añadimos el repositorio de productos
    ):
        self.inventory_service = inventory_service
        self.bom_service = bom_service
        self.manufacturing_service = manufacturing_service
        self.purchasing_service = purchasing_service
        self.config = config
        self.product_repository = product_repository  # Guardamos la referencia
        
        # Estado de la simulación
        self.state = SimulationState(current_date=config.initial_day)
        
        # Entorno SimPy
        self.env = simpy.Environment()
        
        # Recursos
        self.production_capacity = simpy.Resource(
            self.env, capacity=config.production_capacity_per_day
        )
        
        # Cola de órdenes en producción
        self.production_queue = []
        
        # Cola de órdenes de compra pendientes
        self.purchase_queue = []
        
        # Callbacks para notificaciones
        self.day_advanced_callbacks = []
    
    def advance_day(self) -> date:
        """
        Avanza un día en la simulación.
        
        Returns:
            La nueva fecha actual
        """
        
    
    def register_day_advanced_callback(self, callback: Callable[[SimulationState], None]) -> None:
        """
        Registra un callback para ser notificado cuando avance el día.
        
        Args:
            callback: Función a llamar cuando avance el día
        """
        
    
    def release_manufacturing_order(self, order_id: int) -> ManufacturingOrder:
        """
        Libera una orden de fabricación para producción.
        
        Args:
            order_id: ID de la orden a liberar
            
        Returns:
            La orden actualizada
        """
        
    
    def create_purchase_order(
        self, supplier_id: int, product_id: int, quantity: int
    ) -> PurchaseOrder:
        """
        Crea una nueva orden de compra.
        
        Args:
            supplier_id: ID del proveedor
            product_id: ID del producto
            quantity: Cantidad a comprar
            
        Returns:
            La orden de compra creada
        """
        
    
    def _generate_random_orders(self) -> None:
        """
        Genera órdenes de fabricación aleatorias según la configuración.
        """
           
    def _production_process(self, order: ManufacturingOrder) -> None:
        """
        Proceso de producción para una orden (generador SimPy).
        
        Args:
            order: Orden de fabricación
        """
       
    
    def _process_manufacturing_completions(self) -> None:
        """
        Procesa las órdenes de fabricación completadas.
        """
       
    
    def _process_purchase_arrivals(self) -> None:
        """
        Procesa las llegadas de órdenes de compra.
        """
       
