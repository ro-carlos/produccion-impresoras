from typing import List, Dict, Optional, Tuple
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
from datetime import datetime, date, timedelta
import json

class InventoryService:
    """Servicio para gestionar el inventario."""
    
    def __init__(
        self, 
        stock_repository: StockRepository,
        product_repository: ProductRepository,
        event_repository: EventRepository
    ):
        self.stock_repository = stock_repository
        self.product_repository = product_repository
        self.event_repository = event_repository
    
    def get_current_stock(self, product_id: int) -> Optional[StockCurrent]:
        """Obtiene el nivel actual de stock para un producto."""
        return self.stock_repository.get_by_product(product_id)
    
    def update_stock(self, product_id: int, quantity_change: int, reason: str) -> StockCurrent:
        """
        Actualiza el stock de un producto.
        
        Args:
            product_id: ID del producto
            quantity_change: Cambio en la cantidad (+ para aumentar, - para disminuir)
            reason: Motivo del cambio para registro en eventos
        """
        current_stock = self.stock_repository.get_by_product(product_id)
        
        if current_stock:
            new_quantity = current_stock.quantity + quantity_change
            if new_quantity < 0:
                raise ValueError(f"Stock insuficiente para el producto {product_id}")
            
            updated_stock = self.stock_repository.update_quantity(product_id, new_quantity)
            
            # Registrar evento
            event_details = {
                "product_id": product_id,
                "previous_quantity": current_stock.quantity,
                "new_quantity": new_quantity,
                "change": quantity_change,
                "reason": reason
            }
            
            # Crear el evento (esto es aproximado, el repositorio real manejaría el ID)
            event = Event(
                id=0,  # Será asignado por el repositorio
                type=EventType.STOCK_LEVEL_CHANGED,
                event_date=datetime.now().isoformat(),
                details=json.dumps(event_details)
            )
            self.event_repository.add(event)
            
            return updated_stock
        else:
            # Si no existe, crear nuevo registro de stock
            product = self.product_repository.get_by_id(product_id)
            if not product:
                raise ValueError(f"Producto con ID {product_id} no existe")
            
            if quantity_change < 0:
                raise ValueError("No se puede iniciar con stock negativo")
            
            new_stock = StockCurrent(product_id=product_id, quantity=quantity_change)
            added_stock = self.stock_repository.add(new_stock)
            
            # Registrar evento
            event_details = {
                "product_id": product_id,
                "previous_quantity": 0,
                "new_quantity": quantity_change,
                "change": quantity_change,
                "reason": reason
            }
            
            event = Event(
                id=0,  # Será asignado por el repositorio
                type=EventType.STOCK_LEVEL_CHANGED,
                event_date=datetime.now().isoformat(),
                details=json.dumps(event_details)
            )
            self.event_repository.add(event)
            
            return added_stock
    
    def check_stock_availability(self, product_id: int, required_quantity: int) -> bool:
        """Verifica si hay suficiente stock disponible."""
        current_stock = self.stock_repository.get_by_product(product_id)
        if not current_stock:
            return False
        return current_stock.quantity >= required_quantity


class BOMService:
    """Servicio para gestionar las listas de materiales (BOM)."""
    
    def __init__(
        self,
        bom_repository: BOMRepository,
        product_repository: ProductRepository
    ):
        self.bom_repository = bom_repository
        self.product_repository = product_repository
    
    def get_materials_for_product(self, product_id: int) -> List[Tuple[Product, int]]:
        """
        Obtiene la lista de materiales necesarios para fabricar un producto.
        
        Returns:
            Lista de tuplas (Producto, Cantidad requerida)
        """
        bom_entries = self.bom_repository.get_by_finished_product(product_id)
        result = []
        
        for bom_entry in bom_entries:
            material = self.product_repository.get_by_id(bom_entry.material_id)
            if material:
                result.append((material, bom_entry.quantity))
        
        return result
    
    def calculate_materials_needed(self, product_id: int, quantity: int) -> Dict[int, int]:
        """
        Calcula la cantidad total de materiales necesarios para fabricar 
        una cantidad específica de un producto.
        
        Returns:
            Diccionario {material_id: cantidad_requerida}
        """
        materials = self.get_materials_for_product(product_id)
        result = {}
        
        for material, req_quantity in materials:
            result[material.id] = req_quantity * quantity
        
        return result


class ManufacturingService:
    """Servicio para gestionar la producción."""
    
    def __init__(
        self,
        manufacturing_repository: ManufacturingOrderRepository,
        bom_service: BOMService,
        inventory_service: InventoryService,
        event_repository: EventRepository,
        product_repository: ProductRepository
    ):
        self.manufacturing_repository = manufacturing_repository
        self.bom_service = bom_service
        self.inventory_service = inventory_service
        self.event_repository = event_repository
        self.product_repository = product_repository
    
    def create_manufacturing_order(self, product_id: int, quantity: int) -> ManufacturingOrder:
        """Crea una nueva orden de fabricación."""
        product = self.product_repository.get_by_id(product_id)
        if not product or product.type != "finished":
            raise ValueError("Producto no válido para fabricación")
        
        # Crear orden (repositorio asignará ID real)
        order = ManufacturingOrder(
            id=0,  # Será asignado por el repositorio
            creation_date=datetime.now().isoformat(),
            product_id=product_id,
            quantity=quantity,
            status=ManufacturingOrderStatus.PENDING
        )
        
        created_order = self.manufacturing_repository.add(order)
        
        # Registrar evento
        event_details = {
            "manufacturing_order_id": created_order.id,
            "product_id": product_id,
            "quantity": quantity
        }
        
        event = Event(
            id=0,  # Será asignado por el repositorio
            type=EventType.MANUFACTURING_ORDER_CREATED,
            event_date=datetime.now().isoformat(),
            details=json.dumps(event_details)
        )
        self.event_repository.add(event)
        
        return created_order
    
    def release_order_to_production(self, order_id: int) -> ManufacturingOrder:
        """
        Libera una orden a producción si hay materiales disponibles.
        Esto consumirá los materiales del inventario.
        """
        order = self.manufacturing_repository.get_by_id(order_id)
        if not order or order.status != ManufacturingOrderStatus.PENDING:
            raise ValueError("Orden no válida o no está en estado pendiente")
        
        # Calcular materiales necesarios
        materials_needed = self.bom_service.calculate_materials_needed(
            order.product_id, order.quantity
        )
        
        # Verificar disponibilidad de todos los materiales
        for material_id, quantity_needed in materials_needed.items():
            if not self.inventory_service.check_stock_availability(material_id, quantity_needed):
                product = self.product_repository.get_by_id(material_id)
                product_name = product.name if product else f"ID: {material_id}"
                raise ValueError(f"Stock insuficiente de {product_name}")
        
        # Consumir materiales
        for material_id, quantity_needed in materials_needed.items():
            self.inventory_service.update_stock(
                material_id, 
                -quantity_needed, 
                f"Consumido para orden de fabricación #{order.id}"
            )
        
        # Actualizar estado de la orden
        order.status = ManufacturingOrderStatus.IN_PRODUCTION
        updated_order = self.manufacturing_repository.update(order)
        
        # Registrar evento
        event_details = {
            "manufacturing_order_id": order.id,
            "product_id": order.product_id,
            "quantity": order.quantity,
            "materials_consumed": materials_needed
        }
        
        event = Event(
            id=0,  # Será asignado por el repositorio
            type=EventType.MANUFACTURING_ORDER_STARTED,
            event_date=datetime.now().isoformat(),
            details=json.dumps(event_details)
        )
        self.event_repository.add(event)
        
        return updated_order
    
    def complete_order(self, order_id: int) -> ManufacturingOrder:
        """
        Marca una orden como completada y añade productos terminados al inventario.
        Esta función sería llamada por el simulador cuando una orden termine su tiempo 
        de fabricación.
        """
        order = self.manufacturing_repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Orden con ID {order_id} no encontrada")
            
        if order.status != ManufacturingOrderStatus.IN_PRODUCTION:
            raise ValueError(f"Orden con ID {order_id} no está en producción (estado actual: {order.status})")
        
        # Actualizar estado de la orden
        order.status = ManufacturingOrderStatus.COMPLETED
        updated_order = self.manufacturing_repository.update(order)
        
        # Añadir productos terminados al inventario
        self.inventory_service.update_stock(
            order.product_id,
            order.quantity,
            f"Producido por orden de fabricación #{order.id}"
        )
        
        # Registrar evento
        event_details = {
            "manufacturing_order_id": order.id,
            "product_id": order.product_id,
            "quantity": order.quantity
        }
        
        event = Event(
            id=0,  # Será asignado por el repositorio
            type=EventType.MANUFACTURING_ORDER_COMPLETED,
            event_date=datetime.now().isoformat(),
            details=json.dumps(event_details)
        )
        self.event_repository.add(event)
        
        return updated_order
    
    def get_pending_orders(self) -> List[ManufacturingOrder]:
        """Obtiene todas las órdenes pendientes."""
        return self.manufacturing_repository.get_by_status(ManufacturingOrderStatus.PENDING.value)
    
    def get_in_production_orders(self) -> List[ManufacturingOrder]:
        """Obtiene todas las órdenes en producción."""
        return self.manufacturing_repository.get_by_status(ManufacturingOrderStatus.IN_PRODUCTION.value)


class PurchasingService:
    """Servicio para gestionar compras."""
    
    def __init__(
        self,
        purchase_repository: PurchaseOrderRepository,
        supplier_repository: SupplierRepository,
        inventory_service: InventoryService,
        event_repository: EventRepository,
        product_repository: ProductRepository
    ):
        self.purchase_repository = purchase_repository
        self.supplier_repository = supplier_repository
        self.inventory_service = inventory_service
        self.event_repository = event_repository
        self.product_repository = product_repository
    
    def create_purchase_order(
        self, supplier_id: int, product_id: int, quantity: int
    ) -> PurchaseOrder:
        """Crea una nueva orden de compra."""
        supplier = self.supplier_repository.get_by_id(supplier_id)
        if not supplier or supplier.product_id != product_id:
            raise ValueError("Proveedor no válido para este producto")
        
        product = self.product_repository.get_by_id(product_id)
        if not product or product.type != "raw":
            raise ValueError("Solo se pueden comprar materias primas")
        
        issue_date = datetime.now()
        estimated_delivery = issue_date + timedelta(days=supplier.lead_time_days)
        
        # Crear orden (repositorio asignará ID real)
        order = PurchaseOrder(
            id=0,  # Será asignado por el repositorio
            supplier_id=supplier_id,
            product_id=product_id,
            quantity=quantity,
            issue_date=issue_date.isoformat(),
            estimated_delivery_date=estimated_delivery.isoformat(),
            status=PurchaseOrderStatus.ORDERED
        )
        
        created_order = self.purchase_repository.add(order)
        
        # Registrar evento
        event_details = {
            "purchase_order_id": created_order.id,
            "supplier_id": supplier_id,
            "product_id": product_id,
            "quantity": quantity,
            "estimated_delivery": estimated_delivery.isoformat(),
            "unit_cost": supplier.unit_cost,
            "total_cost": supplier.unit_cost * quantity
        }
        
        event = Event(
            id=0,  # Será asignado por el repositorio
            type=EventType.PURCHASE_ORDER_CREATED,
            event_date=datetime.now().isoformat(),
            details=json.dumps(event_details)
        )
        self.event_repository.add(event)
        
        return created_order
    
    def receive_purchase_order(self, order_id: int) -> PurchaseOrder:
        """
        Marca una orden de compra como recibida y añade los materiales al inventario.
        Esta función sería llamada por el simulador cuando una orden de compra llegue
        después del tiempo de entrega.
        """
        order = self.purchase_repository.get_by_id(order_id)
        if not order or order.status != PurchaseOrderStatus.ORDERED:
            raise ValueError("Orden no válida o no está en estado ordenado")
        
        # Actualizar estado de la orden
        order.status = PurchaseOrderStatus.RECEIVED
        updated_order = self.purchase_repository.update(order)
        
        # Añadir materiales al inventario
        self.inventory_service.update_stock(
            order.product_id,
            order.quantity,
            f"Recibido por orden de compra #{order.id}"
        )
        
        # Registrar evento
        event_details = {
            "purchase_order_id": order.id,
            "supplier_id": order.supplier_id,
            "product_id": order.product_id,
            "quantity": order.quantity
        }
        
        event = Event(
            id=0,  # Será asignado por el repositorio
            type=EventType.PURCHASE_ORDER_RECEIVED,
            event_date=datetime.now().isoformat(),
            details=json.dumps(event_details)
        )
        self.event_repository.add(event)
        
        return updated_order
    
    def get_suppliers_for_product(self, product_id: int) -> List[Supplier]:
        """Obtiene todos los proveedores que suministran un producto específico."""
        return self.supplier_repository.get_by_product(product_id)
    
    def get_pending_orders(self) -> List[PurchaseOrder]:
        """Obtiene todas las órdenes de compra pendientes."""
        return self.purchase_repository.get_by_status(PurchaseOrderStatus.ORDERED.value)
