from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import json

from domain.models import (
    Product, BOM, Supplier, StockCurrent, 
    ManufacturingOrder, PurchaseOrder, Event,
    ManufacturingOrderStatus, PurchaseOrderStatus, EventType,
    SimulationConfig
)

from domain.repositories import (
    ProductRepository, BOMRepository, SupplierRepository,
    StockRepository, ManufacturingOrderRepository,
    PurchaseOrderRepository, EventRepository
)

from domain.services import (
    InventoryService, BOMService,
    ManufacturingService, PurchasingService
)

from application.simulation import ProductionSimulator, SimulationState

class SimulationApplicationService:
    """
    Servicio de aplicación para coordinar la simulación.
    """
    
    def __init__(
        self,
        inventory_service: InventoryService,
        bom_service: BOMService,
        manufacturing_service: ManufacturingService,
        purchasing_service: PurchasingService,
        
        product_repository: ProductRepository,
        bom_repository: BOMRepository,
        supplier_repository: SupplierRepository,
        stock_repository: StockRepository,
        manufacturing_repository: ManufacturingOrderRepository,
        purchase_repository: PurchaseOrderRepository,
        event_repository: EventRepository,
        
        config: SimulationConfig
    ):
        # Servicios de dominio
        self.inventory_service = inventory_service
        self.bom_service = bom_service
        self.manufacturing_service = manufacturing_service
        self.purchasing_service = purchasing_service
        
        # Repositorios
        self.product_repository = product_repository
        self.bom_repository = bom_repository
        self.supplier_repository = supplier_repository
        self.stock_repository = stock_repository
        self.manufacturing_repository = manufacturing_repository
        self.purchase_repository = purchase_repository
        self.event_repository = event_repository
        
        # Configuración
        self.config = config
        
        # Simulador
        self.simulator = ProductionSimulator(
            inventory_service=inventory_service,
            bom_service=bom_service,
            manufacturing_service=manufacturing_service,
            purchasing_service=purchasing_service,
            config=config,
            product_repository=product_repository  # Pasamos el repositorio de productos
        )
        
        # Registrar callback para procesar eventos
        self.simulator.register_day_advanced_callback(self._process_simulation_events)
    
    def start_simulation(self) -> None:
        """Inicializa y arranca la simulación."""
        # Realizar tareas de inicialización si son necesarias
        pass
    
    def advance_day(self) -> date:
        """
        Avanza un día en la simulación.
        
        Returns:
            La nueva fecha actual
        """
        return self.simulator.advance_day()
    
    def get_current_date(self) -> date:
        """
        Obtiene la fecha actual de la simulación.
        
        Returns:
            Fecha actual
        """
        return self.simulator.state.current_date
    
    def get_pending_manufacturing_orders(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las órdenes de fabricación pendientes con detalles.
        
        Returns:
            Lista de órdenes con información ampliada
        """
        orders = self.manufacturing_service.get_pending_orders()
        result = []
        
        for order in orders:
            product = self.product_repository.get_by_id(order.product_id)
            product_name = product.name if product else f"Producto ID: {order.product_id}"
            
            # Calcular materiales necesarios
            materials_needed = self.bom_service.calculate_materials_needed(
                order.product_id, order.quantity
            )
            
            materials_info = []
            can_produce = True
            
            for material_id, quantity in materials_needed.items():
                material = self.product_repository.get_by_id(material_id)
                material_name = material.name if material else f"Material ID: {material_id}"
                
                stock = self.inventory_service.get_current_stock(material_id)
                available = stock.quantity if stock else 0
                
                if available < quantity:
                    can_produce = False
                
                materials_info.append({
                    "id": material_id,
                    "name": material_name,
                    "required": quantity,
                    "available": available,
                    "sufficient": available >= quantity
                })
            
            result.append({
                "order": order.dict(),
                "product_name": product_name,
                "materials": materials_info,
                "can_produce": can_produce
            })
        
        return result
    
    def get_current_inventory(self) -> List[Dict[str, Any]]:
        """
        Obtiene el inventario actual con detalles.
        
        Returns:
            Lista de items de inventario con información ampliada
        """
        stock_items = self.stock_repository.get_all()
        result = []
        
        for stock in stock_items:
            product = self.product_repository.get_by_id(stock.product_id)
            product_name = product.name if product else f"Producto ID: {stock.product_id}"
            product_type = product.type if product else "unknown"
            
            result.append({
                "product_id": stock.product_id,
                "product_name": product_name,
                "product_type": product_type,
                "quantity": stock.quantity
            })
        
        return result
    
    def get_suppliers_for_product(self, product_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene los proveedores para un producto con detalles.
        
        Args:
            product_id: ID del producto
            
        Returns:
            Lista de proveedores con información ampliada
        """
        suppliers = self.purchasing_service.get_suppliers_for_product(product_id)
        result = []
        
        for supplier in suppliers:
            result.append({
                "supplier": supplier.dict(),
                "total_lead_time": supplier.lead_time_days,
                "estimated_arrival": (
                    self.simulator.state.current_date + 
                    timedelta(days=supplier.lead_time_days)
                ).isoformat()
            })
        
        return result
    
    def release_order_to_production(self, order_id: int) -> Dict[str, Any]:
        """
        Libera una orden a producción.
        
        Args:
            order_id: ID de la orden a liberar
            
        Returns:
            Información sobre la orden liberada
        """
        try:
            order = self.simulator.release_manufacturing_order(order_id)
            
            product = self.product_repository.get_by_id(order.product_id)
            product_name = product.name if product else f"Producto ID: {order.product_id}"
            
            return {
                "success": True,
                "order": order.dict(),
                "product_name": product_name,
                "status": "in_production",
                "message": f"Orden {order_id} liberada a producción"
            }
        except Exception as e:
            return {
                "success": False,
                "order_id": order_id,
                "message": str(e)
            }
    
    def create_purchase_order(
        self, supplier_id: int, product_id: int, quantity: int
    ) -> Dict[str, Any]:
        """
        Crea una nueva orden de compra.
        
        Args:
            supplier_id: ID del proveedor
            product_id: ID del producto
            quantity: Cantidad a comprar
            
        Returns:
            Información sobre la orden creada
        """
        try:
            order = self.simulator.create_purchase_order(
                supplier_id, product_id, quantity
            )
            
            supplier = self.supplier_repository.get_by_id(supplier_id)
            supplier_name = supplier.name if supplier else f"Proveedor ID: {supplier_id}"
            
            product = self.product_repository.get_by_id(product_id)
            product_name = product.name if product else f"Producto ID: {product_id}"
            
            return {
                "success": True,
                "order": order.dict(),
                "supplier_name": supplier_name,
                "product_name": product_name,
                "total_cost": 
                    supplier.unit_cost * quantity if supplier else None,
                "message": f"Orden de compra creada para {quantity} unidades de {product_name}"
            }
        except Exception as e:
            return {
                "success": False,
                "supplier_id": supplier_id,
                "product_id": product_id,
                "quantity": quantity,
                "message": str(e)
            }
    
    def get_events_history(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de eventos con filtros opcionales.
        
        Args:
            start_date: Fecha de inicio para filtrar (formato ISO)
            end_date: Fecha de fin para filtrar (formato ISO)
            event_type: Tipo de evento para filtrar
            
        Returns:
            Lista de eventos con detalles
        """
        if event_type:
            events = self.event_repository.get_by_type(event_type)
        elif start_date and end_date:
            events = self.event_repository.get_by_date_range(start_date, end_date)
        else:
            events = self.event_repository.get_all()
        
        result = []
        
        for event in events:
            # Intentar parsear los detalles como JSON
            try:
                details = json.loads(event.details)
            except:
                details = event.details
            
            result.append({
                "id": event.id,
                "type": event.type,
                "date": event.event_date,
                "details": details
            })
        
        return result
    
    def _process_simulation_events(self, state: SimulationState) -> None:
        """
        Procesa los eventos generados durante la simulación.
        
        Args:
            state: Estado actual de la simulación
        """
        # Guardar los eventos en el repositorio
        for event in state.events_today:
            self.event_repository.add(event)
        
        # Limpiar la lista de eventos para el día
        state.events_today = []
