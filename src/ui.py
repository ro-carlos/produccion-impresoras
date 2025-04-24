import streamlit as st
from datetime import datetime

# Data mocks (luego se conectan a modelos reales)
sim_day = 1
inventory = {
    "kit_piezas": 22,
    "pcb": 18,
    "extrusor": 15,
    "cables_conexion": 30,
    "transformador_24v": 10,
    "enchufe_schuko": 12
}
pending_orders = [
    {"id": 1, "modelo": "P3D-Classic", "cantidad": 8},
    {"id": 2, "modelo": "P3D-Pro", "cantidad": 5},
]

# --- UI ---

st.set_page_config(page_title="Simulador de Producción 3D", layout="wide")
st.title("🖨️ Simulador de Producción de Impresoras 3D")

st.markdown(f"### Día simulado: {sim_day}")
if st.button("🚀 Avanzar día"):
    st.success("Simulación del día completada.")  # Aquí se llama al simulador

# Panel de pedidos
st.subheader("📦 Pedidos pendientes")
for pedido in pending_orders:
    with st.expander(f"Pedido #{pedido['id']} - {pedido['modelo']} ({pedido['cantidad']} u)"):
        st.button(f"✅ Liberar pedido #{pedido['id']}", key=f"liberar_{pedido['id']}")

# Panel de inventario
st.subheader("📊 Inventario actual")
cols = st.columns(len(inventory))
for i, (producto, cantidad) in enumerate(inventory.items()):
    cols[i].metric(label=producto, value=str(cantidad))

# Panel de compras
st.subheader("🛒 Emitir orden de compra")
productos = list(inventory.keys())
producto = st.selectbox("Producto", productos)
cantidad = st.number_input("Cantidad", min_value=1, step=1)
proveedor = st.selectbox("Proveedor", ["Proveedor A", "Proveedor B"])
if st.button("📤 Emitir orden"):
    st.success(f"Orden emitida para {cantidad} unidades de {producto} a {proveedor}")

# Panel de gráficas
st.subheader("📈 Históricos de producción (demo)")
st.line_chart([10, 8, 9, 7, 11])  # Reemplazar con datos reales

st.markdown("---")
st.caption(f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
