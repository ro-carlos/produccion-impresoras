import simpy
from datetime import datetime, timedelta

# SimPy environment
env = simpy.Environment()
current_day = 0

# Estado del sistema (normalmente esto se conectaría a tu base de datos)
inventario = {
    'Kit de piezas': 30,
    'Extrusor': 20,
    'Motor': 15,
    # Agrega más ítems según tu estructura real
}

# Lista de pedidos de fabricación pendientes (cada pedido es un dict)
pedidos_fabricacion = [
    {'id': 1, 'modelo': 'P3D-Classic', 'estado': 'liberado'},
    {'id': 2, 'modelo': 'P3D-Maxi', 'estado': 'liberado'},
    # ...
]

# Lista de órdenes de compra pendientes de recibir
ordenes_compra = [
    {'id': 101, 'producto': 'Kit de piezas', 'cantidad': 10, 'fecha_entrega': 3},
    {'id': 102, 'producto': 'Extrusor', 'cantidad': 5, 'fecha_entrega': 2},
    # ...
]

# Producción máxima por día
CAPACIDAD_DIARIA = 10

# Definición de la lista de materiales (BOM) por modelo
BOM = {
    'P3D-Classic': {
        'Kit de piezas': 1,
        'Extrusor': 1,
    },
    'P3D-Maxi': {
        'Kit de piezas': 2,
        'Extrusor': 1,
        'Motor': 1,
    },
    # Agrega más modelos aquí
}

# Registro de eventos
eventos = []

def advance_day():
    """Avanza un día en la simulación"""
    global current_day
    current_day += 1
    env.run(until=current_day)
    eventos_hoy = simular_operaciones_diarias()
    eventos.extend(eventos_hoy)
    return eventos_hoy

def simular_operaciones_diarias():
    eventos_dia = []

    # 1. Recibir órdenes de compra si llegan hoy
    for orden in list(ordenes_compra):
        if orden['fecha_entrega'] == current_day:
            inventario[orden['producto']] = inventario.get(orden['producto'], 0) + orden['cantidad']
            eventos_dia.append(f"[Día {current_day}] Llegó orden de compra #{orden['id']} - {orden['producto']} x{orden['cantidad']}")
            ordenes_compra.remove(orden)

    # 2. Procesar pedidos liberados hasta capacidad diaria
    producidos_hoy = 0
    for pedido in list(pedidos_fabricacion):
        if pedido['estado'] != 'liberado':
            continue
        if producidos_hoy >= CAPACIDAD_DIARIA:
            break

        modelo = pedido['modelo']
        bom = BOM.get(modelo, {})
        if hay_stock(bom):
            consumir(bom)
            producidos_hoy += 1
            eventos_dia.append(f"[Día {current_day}] Pedido #{pedido['id']} - {modelo} producido.")
            pedidos_fabricacion.remove(pedido)
        else:
            eventos_dia.append(f"[Día {current_day}] Pedido #{pedido['id']} no producido: falta inventario.")

    return eventos_dia

def hay_stock(bom):
    """Verifica si hay stock suficiente para un BOM"""
    return all(inventario.get(item, 0) >= qty for item, qty in bom.items())

def consumir(bom):
    """Descuenta del inventario los insumos utilizados en la producción"""
    for item, qty in bom.items():
        inventario[item] -= qty

# Función para agregar nuevos pedidos (usado por la API)
def agregar_pedido(id, modelo):
    pedidos_fabricacion.append({'id': id, 'modelo': modelo, 'estado': 'liberado'})

# Función para emitir nueva orden de compra (usado por la API)
def emitir_orden(id, producto, cantidad, lead_time):
    fecha_entrega = current_day + lead_time
    ordenes_compra.append({
        'id': id,
        'producto': producto,
        'cantidad': cantidad,
        'fecha_entrega': fecha_entrega
    })

# Obtener estado actual (inventario, pedidos, eventos)
def estado_actual():
    return {
        'dia_actual': current_day,
        'inventario': inventario,
        'pedidos_fabricacion': pedidos_fabricacion,
        'ordenes_compra': ordenes_compra,
        'eventos': eventos[-10:]  # últimos 10 eventos
    }
