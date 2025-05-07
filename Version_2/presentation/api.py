from fastapi import FastAPI, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
from datetime import date, datetime

from application.services import SimulationApplicationService
from domain.models import (
    ManufacturingOrderStatus, PurchaseOrderStatus, EventType
)

# Modelos Pydantic para la API

class ProductResponse(BaseModel):
    id: int
    name: str
    type: str

class SupplierResponse(BaseModel):
    id: int
    name: str
    product_id: int
    unit_cost: float
    lead_time_days: int
    estimated_arrival: str

class MaterialRequirement(BaseModel):
    id: int
    name: str
    required: int
    available: int
    sufficient: bool

class ManufacturingOrderResponse(BaseModel):
    id: int
    creation_date: str
    product_id: int
    product_name: str
    quantity: int
    status: str
    materials: List[MaterialRequirement]
    can_produce: bool

class StockResponse(BaseModel):
    product_id: int
    product_name: str
    product_type: str
    quantity: int

class PurchaseOrderRequest(BaseModel):
    supplier_id: int
    product_id: int
    quantity: int

class PurchaseOrderResponse(BaseModel):
    id: int
    supplier_id: int
    supplier_name: str
    product_id: int
    product_name: str
    quantity: int
    issue_date: str
    estimated_delivery_date: str
    status: str
    total_cost: float

class EventResponse(BaseModel):
    id: int
    type: str
    date: str
    details: Dict[str, Any]

class AdvanceDayResponse(BaseModel):
    new_date: str
    events_count: int
    message: str

# Función para crear la API
def create_api(simulation_service: SimulationApplicationService) -> FastAPI:
    app = FastAPI(
        title="Simulador de Producción de Impresoras 3D API",
        description="API REST para interactuar con el simulador de producción",
        version="1.0.0"
    )
    
    # Dependencia para obtener el servicio de simulación
    def get_simulation_service() -> SimulationApplicationService:
        return simulation_service
    
    @app.get("/", tags=["General"])
    async def read_root():
        """Endpoint principal."""
        return {
            "name": "Simulador de Producción de Impresoras 3D API",
            "version": "1.0.0",
            "current_date": simulation_service.get_current_date().isoformat()
        }
    
    @app.post("/simulation/advance-day", response_model=AdvanceDayResponse, tags=["Simulation"])
    async def advance_day(
        service: SimulationApplicationService = Depends(get_simulation_service)
    ):
        """Avanza un día en la simulación."""
        new_date = service.advance_day()
        
        return {
            "new_date": new_date.isoformat(),
            "events_count": len(service.get_events_history(
                start_date=new_date.isoformat(),
                end_date=new_date.isoformat()
            )),
            "message": f"Día avanzado correctamente a {new_date.isoformat()}"
        }
    
    @app.get("/products", response_model=List[ProductResponse], tags=["Products"])
    async def get_products(
        service: SimulationApplicationService = Depends(get_simulation_service)
    ):
        """Obtiene todos los productos."""
        return [
            {
                "id": p.id,
                "name": p.name,
                "type": p.type
            } 
            for p in service.product_repository.get_all()
        ]
    
    @app.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
    async def get_product(
        product_id: int,
        service: SimulationApplicationService = Depends(get_simulation_service)
    ):
        """Obtiene un producto por su ID."""
        product = service.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        return {
            "id": product.id,
            "name": product.name,
            "type": product.type
        }
    
    @app.get("/products/{product_id}/suppliers", response_model=List[SupplierResponse], tags=["Products"])
    async def get_product_suppliers(
        product_id: int,
        service: SimulationApplicationService = Depends(get_simulation_service)
    ):
        """Obtiene los proveedores para un producto."""
        supplier_data = service.get_suppliers_for_product(product_id)
        result = []
        
        for supplier_info in supplier_data:
            # Extraer la información del proveedor del campo "supplier"
            supplier = supplier_info["supplier"]
            
            # Crear objeto de respuesta con el formato correcto
            result.append({
                "id": supplier["id"],
                "name": supplier["name"],
                "product_id": supplier["product_id"],
                "unit_cost": supplier["unit_cost"],
                "lead_time_days": supplier["lead_time_days"],
                "estimated_arrival": supplier_info["estimated_arrival"]
            })
        
        return result
    
    @app.get("/inventory", response_model=List[StockResponse], tags=["Inventory"])
    async def get_inventory(
        service: SimulationApplicationService = Depends(get_simulation_service)
    ):
        """Obtiene el inventario actual."""
        return service.get_current_inventory()
    
    @app.get("/orders/manufacturing", tags=["Manufacturing"])
    async def get_manufacturing_orders(
        status: Optional[str] = Query(None, description="Filtro por estado"),
        service: SimulationApplicationService = Depends(get_simulation_service)
    ):
        """Obtiene las órdenes de fabricación."""
        if status == "pending":
            return service.get_pending_manufacturing_orders()
        else:
            # Aquí se implementaría la lógica para otros estados
            return []
    
    @app.post(
        "/orders/manufacturing/{order_id}/release", 
        tags=["Manufacturing"]
    )
    async def release_manufacturing_order(
        order_id: int,
        service: SimulationApplicationService = Depends(get_simulation_service)
    ):
        """Libera una orden de fabricación a producción."""
        result = service.release_order_to_production(order_id)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    
    @app.post(
        "/orders/purchase", 
        tags=["Purchasing"]
    )
    async def create_purchase_order(
        order: PurchaseOrderRequest,
        service: SimulationApplicationService = Depends(get_simulation_service)
    ):
        """Crea una nueva orden de compra."""
        result = service.create_purchase_order(
            order.supplier_id, order.product_id, order.quantity
        )
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        # Devolver el resultado tal como lo envía el servicio
        # sin forzar la validación con el modelo PurchaseOrderResponse
        return result
    
    @app.get("/events", response_model=List[EventResponse], tags=["Events"])
    async def get_events(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        event_type: Optional[str] = None,
        service: SimulationApplicationService = Depends(get_simulation_service)
    ):
        """Obtiene el historial de eventos."""
        return service.get_events_history(start_date, end_date, event_type)
    
    return app
