from fastapi import FastAPI, HTTPException
from entities import (
    Producto, BOM, Proveedor, CatalogoProveedor, Inventario,
    PedidoFabricacion, OrdenCompra, DetalleOrdenCompra, Evento,
    ConfiguracionSimulacion, LineaProduccion, AsignacionProduccion,
    HistoricoInventario, MetricasRendimiento
)
import sqlite3
from typing import List
from src.simulator import advance_day, simular_operaciones_diarias
from fastapi.responses import JSONResponse

app = FastAPI(title="Sistema de Producción de Impresoras")

def get_db():
    conn = sqlite3.connect('simulador_produccion.db')
    conn.row_factory = sqlite3.Row
    return conn

# Endpoints para Producto
@app.post("/productos/", response_model=Producto)
async def create_producto(producto: Producto):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO Producto (nombre, tipo, unidad_medida, espacio_almacen)
            VALUES (?, ?, ?, ?)
            """,
            (producto.nombre, producto.tipo, producto.unidad_medida, producto.espacio_almacen)
        )
        producto.id = cursor.lastrowid
        db.commit()
        return producto
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/productos/", response_model=List[Producto])
async def get_productos():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM Producto")
        productos = cursor.fetchall()
        return [
            Producto(
                id=row['id'],
                nombre=row['nombre'],
                tipo=row['tipo'],
                unidad_medida=row['unidad_medida'],
                espacio_almacen=row['espacio_almacen']
            ) for row in productos
        ]
    finally:
        db.close()

@app.get("/productos/{producto_id}", response_model=Producto)
async def get_producto(producto_id: int):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM Producto WHERE id = ?", (producto_id,))
        producto = cursor.fetchone()
        if producto is None:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return Producto(
            id=producto['id'],
            nombre=producto['nombre'],
            tipo=producto['tipo'],
            unidad_medida=producto['unidad_medida'],
            espacio_almacen=producto['espacio_almacen']
        )
    finally:
        db.close()

# Endpoints para BOM
@app.post("/bom/", response_model=BOM)
async def create_bom(bom: BOM):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO BOM (prod_terminado_id, material_id, cantidad)
            VALUES (?, ?, ?)
            """,
            (bom.prod_terminado_id, bom.material_id, bom.cantidad)
        )
        bom.id = cursor.lastrowid
        db.commit()
        return bom
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/bom/", response_model=List[BOM])
async def get_bom():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM BOM")
        bom_items = cursor.fetchall()
        return [
            BOM(
                id=row['id'],
                prod_terminado_id=row['prod_terminado_id'],
                material_id=row['material_id'],
                cantidad=row['cantidad']
            ) for row in bom_items
        ]
    finally:
        db.close()

# Endpoints para Proveedor
@app.post("/proveedores/", response_model=Proveedor)
async def create_proveedor(proveedor: Proveedor):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO Proveedor (nombre, direccion, contacto)
            VALUES (?, ?, ?)
            """,
            (proveedor.nombre, proveedor.direccion, proveedor.contacto)
        )
        proveedor.id = cursor.lastrowid
        db.commit()
        return proveedor
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/proveedores/", response_model=List[Proveedor])
async def get_proveedores():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM Proveedor")
        proveedores = cursor.fetchall()
        return [
            Proveedor(
                id=row['id'],
                nombre=row['nombre'],
                direccion=row['direccion'],
                contacto=row['contacto']
            ) for row in proveedores
        ]
    finally:
        db.close()

# Endpoints para CatalogoProveedor
@app.post("/catalogo-proveedor/", response_model=CatalogoProveedor)
async def create_catalogo_proveedor(catalogo: CatalogoProveedor):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO CatalogoProveedor 
            (proveedor_id, producto_id, precio_unitario, cantidad_minima, cantidad_paquete, lead_time_dias)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (catalogo.proveedor_id, catalogo.producto_id, catalogo.precio_unitario,
             catalogo.cantidad_minima, catalogo.cantidad_paquete, catalogo.lead_time_dias)
        )
        catalogo.id = cursor.lastrowid
        db.commit()
        return catalogo
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/catalogo-proveedor/", response_model=List[CatalogoProveedor])
async def get_catalogo_proveedor():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM CatalogoProveedor")
        catalogos = cursor.fetchall()
        return [
            CatalogoProveedor(
                id=row['id'],
                proveedor_id=row['proveedor_id'],
                producto_id=row['producto_id'],
                precio_unitario=row['precio_unitario'],
                cantidad_minima=row['cantidad_minima'],
                cantidad_paquete=row['cantidad_paquete'],
                lead_time_dias=row['lead_time_dias']
            ) for row in catalogos
        ]
    finally:
        db.close()

# Endpoints para Inventario
@app.post("/inventario/", response_model=Inventario)
async def create_inventario(inventario: Inventario):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO Inventario (producto_id, cantidad, fecha_actualizacion)
            VALUES (?, ?, ?)
            """,
            (inventario.producto_id, inventario.cantidad, inventario.fecha_actualizacion)
        )
        db.commit()
        return inventario
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/inventario/", response_model=List[Inventario])
async def get_inventario():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM Inventario")
        inventario = cursor.fetchall()
        return [
            Inventario(
                producto_id=row['producto_id'],
                cantidad=row['cantidad'],
                fecha_actualizacion=row['fecha_actualizacion']
            ) for row in inventario
        ]
    finally:
        db.close()

# Endpoints para PedidoFabricacion
@app.post("/pedidos-fabricacion/", response_model=PedidoFabricacion)
async def create_pedido_fabricacion(pedido: PedidoFabricacion):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO PedidoFabricacion 
            (fecha_creacion, producto_id, cantidad, estado, prioridad, fecha_inicio_prod, fecha_fin_prod)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (pedido.fecha_creacion, pedido.producto_id, pedido.cantidad,
             pedido.estado, pedido.prioridad, pedido.fecha_inicio_prod, pedido.fecha_fin_prod)
        )
        pedido.id = cursor.lastrowid
        db.commit()
        return pedido
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/pedidos-fabricacion/", response_model=List[PedidoFabricacion])
async def get_pedidos_fabricacion():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM PedidoFabricacion")
        pedidos = cursor.fetchall()
        return [
            PedidoFabricacion(
                id=row['id'],
                fecha_creacion=row['fecha_creacion'],
                producto_id=row['producto_id'],
                cantidad=row['cantidad'],
                estado=row['estado'],
                prioridad=row['prioridad'],
                fecha_inicio_prod=row['fecha_inicio_prod'],
                fecha_fin_prod=row['fecha_fin_prod']
            ) for row in pedidos
        ]
    finally:
        db.close()

# Endpoints para OrdenCompra
@app.post("/ordenes-compra/", response_model=OrdenCompra)
async def create_orden_compra(orden: OrdenCompra):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO OrdenCompra 
            (proveedor_id, fecha_emision, fecha_entrega_est, estado, costo_total)
            VALUES (?, ?, ?, ?, ?)
            """,
            (orden.proveedor_id, orden.fecha_emision, orden.fecha_entrega_est,
             orden.estado, orden.costo_total)
        )
        orden.id = cursor.lastrowid
        db.commit()
        return orden
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/ordenes-compra/", response_model=List[OrdenCompra])
async def get_ordenes_compra():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM OrdenCompra")
        ordenes = cursor.fetchall()
        return [
            OrdenCompra(
                id=row['id'],
                proveedor_id=row['proveedor_id'],
                fecha_emision=row['fecha_emision'],
                fecha_entrega_est=row['fecha_entrega_est'],
                estado=row['estado'],
                costo_total=row['costo_total']
            ) for row in ordenes
        ]
    finally:
        db.close()

# Endpoints para DetalleOrdenCompra
@app.post("/detalles-orden-compra/", response_model=DetalleOrdenCompra)
async def create_detalle_orden_compra(detalle: DetalleOrdenCompra):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO DetalleOrdenCompra 
            (orden_compra_id, producto_id, cantidad, precio_unitario, catalogo_proveedor_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (detalle.orden_compra_id, detalle.producto_id, detalle.cantidad,
             detalle.precio_unitario, detalle.catalogo_proveedor_id)
        )
        detalle.id = cursor.lastrowid
        db.commit()
        return detalle
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/detalles-orden-compra/", response_model=List[DetalleOrdenCompra])
async def get_detalles_orden_compra():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM DetalleOrdenCompra")
        detalles = cursor.fetchall()
        return [
            DetalleOrdenCompra(
                id=row['id'],
                orden_compra_id=row['orden_compra_id'],
                producto_id=row['producto_id'],
                cantidad=row['cantidad'],
                precio_unitario=row['precio_unitario'],
                catalogo_proveedor_id=row['catalogo_proveedor_id']
            ) for row in detalles
        ]
    finally:
        db.close()

# Endpoints para Evento
@app.post("/eventos/", response_model=Evento)
async def create_evento(evento: Evento):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO Evento 
            (tipo, fecha_simulacion, entidad_id, entidad_tipo, detalle, resultado)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (evento.tipo, evento.fecha_simulacion, evento.entidad_id,
             evento.entidad_tipo, evento.detalle, evento.resultado)
        )
        evento.id = cursor.lastrowid
        db.commit()
        return evento
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/eventos/", response_model=List[Evento])
async def get_eventos():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM Evento")
        eventos = cursor.fetchall()
        return [
            Evento(
                id=row['id'],
                tipo=row['tipo'],
                fecha_simulacion=row['fecha_simulacion'],
                entidad_id=row['entidad_id'],
                entidad_tipo=row['entidad_tipo'],
                detalle=row['detalle'],
                resultado=row['resultado']
            ) for row in eventos
        ]
    finally:
        db.close()

# Endpoints para ConfiguracionSimulacion
@app.post("/configuracion-simulacion/", response_model=ConfiguracionSimulacion)
async def create_configuracion_simulacion(config: ConfiguracionSimulacion):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO ConfiguracionSimulacion 
            (fecha_actual, media_demanda, varianza_demanda, capacidad_almacen, capacidad_produccion_diaria)
            VALUES (?, ?, ?, ?, ?)
            """,
            (config.fecha_actual, config.media_demanda, config.varianza_demanda,
             config.capacidad_almacen, config.capacidad_produccion_diaria)
        )
        config.id = cursor.lastrowid
        db.commit()
        return config
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/configuracion-simulacion/", response_model=List[ConfiguracionSimulacion])
async def get_configuracion_simulacion():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM ConfiguracionSimulacion")
        configs = cursor.fetchall()
        return [
            ConfiguracionSimulacion(
                id=row['id'],
                fecha_actual=row['fecha_actual'],
                media_demanda=row['media_demanda'],
                varianza_demanda=row['varianza_demanda'],
                capacidad_almacen=row['capacidad_almacen'],
                capacidad_produccion_diaria=row['capacidad_produccion_diaria']
            ) for row in configs
        ]
    finally:
        db.close()

# Endpoints para LineaProduccion
@app.post("/lineas-produccion/", response_model=LineaProduccion)
async def create_linea_produccion(linea: LineaProduccion):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO LineaProduccion (nombre, capacidad_diaria, estado)
            VALUES (?, ?, ?)
            """,
            (linea.nombre, linea.capacidad_diaria, linea.estado)
        )
        linea.id = cursor.lastrowid
        db.commit()
        return linea
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/lineas-produccion/", response_model=List[LineaProduccion])
async def get_lineas_produccion():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM LineaProduccion")
        lineas = cursor.fetchall()
        return [
            LineaProduccion(
                id=row['id'],
                nombre=row['nombre'],
                capacidad_diaria=row['capacidad_diaria'],
                estado=row['estado']
            ) for row in lineas
        ]
    finally:
        db.close()

# Endpoints para AsignacionProduccion
@app.post("/asignaciones-produccion/", response_model=AsignacionProduccion)
async def create_asignacion_produccion(asignacion: AsignacionProduccion):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO AsignacionProduccion 
            (pedido_id, linea_produccion_id, fecha_asignacion, fecha_inicio, fecha_fin_estimada, estado)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (asignacion.pedido_id, asignacion.linea_produccion_id, asignacion.fecha_asignacion,
             asignacion.fecha_inicio, asignacion.fecha_fin_estimada, asignacion.estado)
        )
        asignacion.id = cursor.lastrowid
        db.commit()
        return asignacion
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/asignaciones-produccion/", response_model=List[AsignacionProduccion])
async def get_asignaciones_produccion():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM AsignacionProduccion")
        asignaciones = cursor.fetchall()
        return [
            AsignacionProduccion(
                id=row['id'],
                pedido_id=row['pedido_id'],
                linea_produccion_id=row['linea_produccion_id'],
                fecha_asignacion=row['fecha_asignacion'],
                fecha_inicio=row['fecha_inicio'],
                fecha_fin_estimada=row['fecha_fin_estimada'],
                estado=row['estado']
            ) for row in asignaciones
        ]
    finally:
        db.close()

# Endpoints para HistoricoInventario
@app.post("/historico-inventario/", response_model=HistoricoInventario)
async def create_historico_inventario(historico: HistoricoInventario):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO HistoricoInventario 
            (producto_id, fecha, cantidad, tipo_movimiento)
            VALUES (?, ?, ?, ?)
            """,
            (historico.producto_id, historico.fecha, historico.cantidad, historico.tipo_movimiento)
        )
        historico.id = cursor.lastrowid
        db.commit()
        return historico
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/historico-inventario/", response_model=List[HistoricoInventario])
async def get_historico_inventario():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM HistoricoInventario")
        historico = cursor.fetchall()
        return [
            HistoricoInventario(
                id=row['id'],
                producto_id=row['producto_id'],
                fecha=row['fecha'],
                cantidad=row['cantidad'],
                tipo_movimiento=row['tipo_movimiento']
            ) for row in historico
        ]
    finally:
        db.close()

# Endpoints para MetricasRendimiento
@app.post("/metricas-rendimiento/", response_model=MetricasRendimiento)
async def create_metricas_rendimiento(metricas: MetricasRendimiento):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO MetricasRendimiento 
            (fecha, pedidos_completados, pedidos_retrasados, nivel_servicio, rotacion_inventario, costos_totales)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (metricas.fecha, metricas.pedidos_completados, metricas.pedidos_retrasados,
             metricas.nivel_servicio, metricas.rotacion_inventario, metricas.costos_totales)
        )
        metricas.id = cursor.lastrowid
        db.commit()
        return metricas
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/metricas-rendimiento/", response_model=List[MetricasRendimiento])
async def get_metricas_rendimiento():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM MetricasRendimiento")
        metricas = cursor.fetchall()
        return [
            MetricasRendimiento(
                id=row['id'],
                fecha=row['fecha'],
                pedidos_completados=row['pedidos_completados'],
                pedidos_retrasados=row['pedidos_retrasados'],
                nivel_servicio=row['nivel_servicio'],
                rotacion_inventario=row['rotacion_inventario'],
                costos_totales=row['costos_totales']
            ) for row in metricas
        ]
    finally:
        db.close() 

#SIMULATOR

@app.post("/simulacion/avanzar-dia/")
async def avanzar_dia():
    try:
        resultado = advance_day()
        return JSONResponse(content={"mensaje": "Simulación avanzada en un día", "resultado": resultado})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/simulacion/estado/")
async def estado_simulacion():
    try:
        estado = simular_operaciones_diarias()
        return JSONResponse(content=estado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))