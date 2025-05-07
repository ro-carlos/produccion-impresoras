import simpy
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, date, timedelta
import random
import json
from dataclasses import dataclass

from domain.models import (
    Product, BOM, Supplier, StockCurrent, 
    ManufacturingOrder, PurchaseOrder, Event,
    ManufacturingOrderStatus, PurchaseOrderStatus, EventType,
    SimulationConfig
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
        # Crear órdenes aleatorias de fabricación
        self._generate_random_orders()
        
        # Procesar un día de simulación
        self.env.run(until=self.env.now + 24)  # 24 horas
        
        # Avanzar la fecha
        self.state.current_date += timedelta(days=1)
        
        # Procesar llegadas de órdenes de compra
        self._process_purchase_arrivals()
        
        # Completar órdenes de fabricación
        self._process_manufacturing_completions()
        
        # Registrar evento de avance de día
        event_details = {
            "previous_date": (self.state.current_date - timedelta(days=1)).isoformat(),
            "new_date": self.state.current_date.isoformat()
        }
        
        event = Event(
            id=0,  # Será asignado por el repositorio
            type=EventType.DAY_ADVANCED,
            event_date=datetime.now().isoformat(),
            details=json.dumps(event_details)
        )
        
        self.state.events_today.append(event)
        
        # Notificar a los callbacks
        for callback in self.day_advanced_callbacks:
            callback(self.state)
        
        return self.state.current_date
    
    def register_day_advanced_callback(self, callback: Callable[[SimulationState], None]) -> None:
        """
        Registra un callback para ser notificado cuando avance el día.
        
        Args:
            callback: Función a llamar cuando avance el día
        """
        self.day_advanced_callbacks.append(callback)
    
    def release_manufacturing_order(self, order_id: int) -> ManufacturingOrder:
        """
        Libera una orden de fabricación para producción.
        
        Args:
            order_id: ID de la orden a liberar
            
        Returns:
            La orden actualizada
        """
        # Usar el servicio para liberar la orden y consumir materiales
        order = self.manufacturing_service.release_order_to_production(order_id)
        
        # Añadir a la cola de producción
        self.production_queue.append(order)
        
        # Iniciar proceso de fabricación
        production_process = self._production_process(order)
        self.env.process(production_process)
        
        return order
    
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
        # Usar el servicio para crear la orden
        order = self.purchasing_service.create_purchase_order(
            supplier_id, product_id, quantity
        )
        
        # Añadir a la cola de compras pendientes
        self.purchase_queue.append(order)
        
        return order
    
    def _generate_random_orders(self) -> None:
        """
        Genera órdenes de fabricación aleatorias según la configuración.
        """
        # Obtener productos terminados
        if self.product_repository:
            finished_products = self.product_repository.get_by_type("finished")
        else:
            finished_products = []
        
        if not finished_products:
            # Si no hay productos terminados disponibles, no generar órdenes
            return
        
        # Determinar cuántas órdenes generar (distribución normal)
        num_orders = max(0, round(random.normalvariate(
            self.config.demand_mean, self.config.demand_std_dev
        )))
        
        print(f"Generando {num_orders} órdenes aleatorias...")
        
        for _ in range(num_orders):
            # Seleccionar un producto aleatorio
            product = random.choice(finished_products)
            
            # Determinar cantidad (entre 1 y 10)
            quantity = random.randint(1, 10)
            
            # Crear la orden
            try:
                self.manufacturing_service.create_manufacturing_order(
                    product.id, quantity
                )
                print(f"Orden creada para {quantity} unidades de {product.name}")
            except Exception as e:
                print(f"Error al crear orden: {str(e)}")
    
    def _production_process(self, order: ManufacturingOrder) -> None:
        """
        Proceso de producción para una orden (generador SimPy).
        
        Args:
            order: Orden de fabricación
        """
        # Solicitar capacidad de producción
        with self.production_capacity.request() as req:
            yield req
            
            # Simulamos el tiempo de producción (1 día por unidad, hasta un máximo)
            production_time = min(24, order.quantity * 2)  # Horas
            yield self.env.timeout(production_time)
            
            # La orden quedará completada en el siguiente avance de día
    
    def _process_manufacturing_completions(self) -> None:
        """
        Procesa las órdenes de fabricación completadas.
        """
        # Verificar qué órdenes han completado su tiempo de fabricación
        completed_orders = []
        remaining_orders = []
        
        for order in self.production_queue:
            # Simplificación: consideramos que todas las órdenes en producción
            # se completan después de un día
            completed_orders.append(order)
        
        # Actualizar la cola
        self.production_queue = remaining_orders
        
        # Marcar órdenes como completadas
        for order in completed_orders:
            try:
                self.manufacturing_service.complete_order(order.id)
                print(f"Orden #{order.id} completada")
            except Exception as e:
                print(f"Error al completar orden #{order.id}: {str(e)}")
    
    def _process_purchase_arrivals(self) -> None:
        """
        Procesa las llegadas de órdenes de compra.
        """
        arrived_orders = []
        remaining_orders = []
        
        for order in self.purchase_queue:
            # Convertir fechas de string a objetos date
            estimated_delivery = datetime.fromisoformat(order.estimated_delivery_date).date()
            
            # Verificar si la fecha de entrega estimada es hoy o antes
            if estimated_delivery <= self.state.current_date:
                arrived_orders.append(order)
            else:
                remaining_orders.append(order)
        
        # Actualizar la cola
        self.purchase_queue = remaining_orders
        
        # Procesar órdenes llegadas
        for order in arrived_orders:
            try:
                self.purchasing_service.receive_purchase_order(order.id)
                print(f"Orden de compra #{order.id} recibida")
            except Exception as e:
                print(f"Error al recibir orden de compra #{order.id}: {str(e)}")
