# src/entities.py

from pydantic import BaseModel # type: ignore
from typing import Literal, Optional

class Producto(BaseModel):
    id: Optional[int] = None
    nombre: str
    tipo: Literal["materia_prima", "terminado"]
    unidad_medida: str = "unidad"
    espacio_almacen: float = 1.0

class BOM(BaseModel):
    id: Optional[int] = None
    prod_terminado_id: int
    material_id: int
    cantidad: float

class Proveedor(BaseModel):
    id: Optional[int] = None
    nombre: str
    direccion: Optional[str] = None
    contacto: Optional[str] = None

class CatalogoProveedor(BaseModel):
    id: Optional[int] = None
    proveedor_id: int
    producto_id: int
    precio_unitario: float
    cantidad_minima: int = 1
    cantidad_paquete: int = 1
    lead_time_dias: int = 1

class Inventario(BaseModel):
    producto_id: int
    cantidad: float = 0
    fecha_actualizacion: str

class PedidoFabricacion(BaseModel):
    id: Optional[int] = None
    fecha_creacion: str
    producto_id: int
    cantidad: int
    estado: Literal["pendiente", "en_produccion", "completado", "cancelado"] = "pendiente"
    prioridad: int = 0
    fecha_inicio_prod: Optional[str] = None
    fecha_fin_prod: Optional[str] = None

class OrdenCompra(BaseModel):
    id: Optional[int] = None
    proveedor_id: int
    fecha_emision: str
    fecha_entrega_est: str
    estado: Literal["emitida", "en_transito", "recibida", "cancelada"] = "emitida"
    costo_total: float = 0

class DetalleOrdenCompra(BaseModel):
    id: Optional[int] = None
    orden_compra_id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    catalogo_proveedor_id: int

class Evento(BaseModel):
    id: Optional[int] = None
    tipo: str
    fecha_simulacion: str
    entidad_id: Optional[int] = None
    entidad_tipo: Optional[str] = None
    detalle: Optional[str] = None
    resultado: Optional[str] = None

class ConfiguracionSimulacion(BaseModel):
    id: Optional[int] = None
    fecha_actual: str
    media_demanda: float = 0
    varianza_demanda: float = 0
    capacidad_almacen: int = 1000
    capacidad_produccion_diaria: int = 10

class LineaProduccion(BaseModel):
    id: Optional[int] = None
    nombre: str
    capacidad_diaria: int = 10
    estado: Literal["activa", "inactiva", "mantenimiento"] = "activa"

class AsignacionProduccion(BaseModel):
    id: Optional[int] = None
    pedido_id: int
    linea_produccion_id: int
    fecha_asignacion: str
    fecha_inicio: str
    fecha_fin_estimada: str
    estado: Literal["planificada", "en_proceso", "completada"] = "planificada"

class HistoricoInventario(BaseModel):
    id: Optional[int] = None
    producto_id: int
    fecha: str
    cantidad: float
    tipo_movimiento: Literal["entrada", "salida", "ajuste"]

class MetricasRendimiento(BaseModel):
    id: Optional[int] = None
    fecha: str
    pedidos_completados: int = 0
    pedidos_retrasados: int = 0
    nivel_servicio: float = 0
    rotacion_inventario: float = 0
    costos_totales: float = 0