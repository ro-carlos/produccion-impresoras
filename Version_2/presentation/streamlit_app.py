import streamlit as st
import altair as alt
import pandas as pd
import requests
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional

class StreamlitApp:
    """
    Aplicación Streamlit para la interfaz de usuario del simulador de producción.
    """
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """
        Inicializa la aplicación Streamlit.
        
        Args:
            api_url: URL de la API REST
        """
        self.api_url = api_url
        self.setup_app()
    
    def setup_app(self):
        """Configura la aplicación Streamlit."""
        st.set_page_config(
            page_title="Simulador de Producción de Impresoras 3D",
            page_icon="🖨️",
            layout="wide"
        )
        
        # Inicializar estado de la sesión si no existe
        if 'current_date' not in st.session_state:
            # Obtener fecha actual de la API
            response = requests.get(f"{self.api_url}/")
            data = response.json()
            
            st.session_state.current_date = data["current_date"]
            st.session_state.pending_orders = []
            st.session_state.inventory = []
            st.session_state.events = []
        
        # Cargar los datos actuales
        self.load_data()
    
    def load_data(self):
        """Carga los datos actuales desde la API."""
        try:
            # Cargar pedidos pendientes
            response = requests.get(
                f"{self.api_url}/orders/manufacturing",
                params={"status": "pending"}
            )
            st.session_state.pending_orders = response.json()
            
            # Cargar inventario
            response = requests.get(f"{self.api_url}/inventory")
            st.session_state.inventory = response.json()
            
            # Cargar eventos recientes
            today = datetime.fromisoformat(st.session_state.current_date).date()
            week_ago = (today - timedelta(days=7)).isoformat()
            
            response = requests.get(
                f"{self.api_url}/events",
                params={"start_date": week_ago, "end_date": today.isoformat()}
            )
            st.session_state.events = response.json()
        
        except Exception as e:
            st.error(f"Error al cargar datos: {str(e)}")
    
    def render(self):
        """Renderiza la interfaz de usuario."""
        st.title("🖨️ Simulador de Producción de Impresoras 3D")
        
        # Encabezado con la fecha actual y botón para avanzar día
        self.render_header()
        
        # Layout principal
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Panel de pedidos
            self.render_orders_panel()
            
            # Panel de producción
            self.render_production_panel()
        
        with col2:
            # Panel de inventario
            self.render_inventory_panel()
            
            # Panel de compras
            self.render_purchase_panel()
        
        # Gráficas
        self.render_charts()
    
    def render_header(self):
        """Renderiza el encabezado con la fecha actual y botón para avanzar día."""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(f"📅 Día de simulación: {st.session_state.current_date}")
        
        with col2:
            if st.button("⏭️ Avanzar día", type="primary"):
                try:
                    response = requests.post(f"{self.api_url}/simulation/advance-day")
                    data = response.json()
                    
                    st.session_state.current_date = data["new_date"]
                    st.success(data["message"])
                    
                    # Recargar datos
                    self.load_data()
                except Exception as e:
                    st.error(f"Error al avanzar día: {str(e)}")
        
        st.divider()
    
    def render_orders_panel(self):
        """Renderiza el panel de pedidos pendientes."""
        st.subheader("📋 Pedidos Pendientes")
        
        if not st.session_state.pending_orders:
            st.info("No hay pedidos pendientes.")
            return
        
        for order in st.session_state.pending_orders:
            with st.expander(
                f"Pedido #{order['order']['id']} - {order['product_name']} ({order['order']['quantity']} unidades)"
            ):
                st.write(f"**Fecha de creación:** {order['order']['creation_date']}")
                st.write(f"**Estado:** {order['order']['status']}")
                
                # Tabla de materiales
                st.write("**Materiales necesarios:**")
                materials_df = pd.DataFrame(order["materials"])
                materials_df.columns = [
                    "ID", "Material", "Requerido", "Disponible", "Suficiente"
                ]
                
                # Resaltar filas con inventario insuficiente
                def highlight_insufficient(row):
                    return ['background-color: #ffcccc' if not row["Suficiente"] else '' for _ in row]
                
                st.dataframe(materials_df.style.apply(highlight_insufficient, axis=1))
                
                # Botón para liberar a producción
                if order["can_produce"]:
                    if st.button(
                        f"🚀 Liberar a producción",
                        key=f"release_{order['order']['id']}"
                    ):
                        try:
                            response = requests.post(
                                f"{self.api_url}/orders/manufacturing/{order['order']['id']}/release"
                            )
                            result = response.json()
                            
                            if result["success"]:
                                st.success(result["message"])
                                # Recargar datos
                                self.load_data()
                            else:
                                st.error(result["message"])
                        except Exception as e:
                            st.error(f"Error al liberar orden: {str(e)}")
                else:
                    st.warning("No hay suficientes materiales para producir.")
    
    def render_inventory_panel(self):
        """Renderiza el panel de inventario."""
        st.subheader("📦 Inventario")
        
        if not st.session_state.inventory:
            st.info("No hay elementos en inventario.")
            return
        
        # Filtrar por tipo de producto
        inventory_df = pd.DataFrame(st.session_state.inventory)
        
        # Separar materias primas y productos terminados
        raw_materials = inventory_df[inventory_df["product_type"] == "raw"]
        finished_products = inventory_df[inventory_df["product_type"] == "finished"]
        
        # Mostrar materias primas
        st.write("**Materias Primas:**")
        if not raw_materials.empty:
            raw_df = raw_materials[["product_name", "quantity"]]
            raw_df.columns = ["Material", "Cantidad"]
            st.dataframe(raw_df)
        else:
            st.info("No hay materias primas en inventario.")
        
        # Mostrar productos terminados
        st.write("**Productos Terminados:**")
        if not finished_products.empty:
            finished_df = finished_products[["product_name", "quantity"]]
            finished_df.columns = ["Producto", "Cantidad"]
            st.dataframe(finished_df)
        else:
            st.info("No hay productos terminados en inventario.")
    
    def render_production_panel(self):
        """Renderiza el panel de producción."""
        st.subheader("🏭 Producción")
        
        # Aquí se mostraría información sobre las órdenes en producción
        # Por ahora, mostramos un placeholder
        st.info("Panel de producción - No implementado en el prototipo")
    
    def render_purchase_panel(self):
        """Renderiza el panel de compras."""
        st.subheader("🛒 Compras")
        
        # Filtrar solo materias primas del inventario
        raw_materials = [
            item for item in st.session_state.inventory 
            if item["product_type"] == "raw"
        ]
        
        if not raw_materials:
            st.info("No hay materias primas disponibles para comprar.")
            return
        
        # Seleccionar producto para comprar
        selected_product = st.selectbox(
            "Seleccione material a comprar:",
            options=[f"{item['product_name']} (ID: {item['product_id']})" for item in raw_materials],
            key="purchase_product"
        )
        
        if selected_product:
            # Extraer el ID del producto
            product_id = int(selected_product.split("ID: ")[1].replace(")", ""))
            
            # Obtener proveedores para este producto
            try:
                response = requests.get(
                    f"{self.api_url}/products/{product_id}/suppliers"
                )
                suppliers = response.json()
                
                if not suppliers:
                    st.warning("No hay proveedores disponibles para este producto.")
                    return
                
                # Seleccionar proveedor
                selected_supplier = st.selectbox(
                    "Seleccione proveedor:",
                    options=[
                        f"{s['name']} - {s['unit_cost']}€/unidad - Entrega: {s['lead_time_days']} días (ID: {s['id']})" 
                        for s in suppliers
                    ],
                    key="purchase_supplier"
                )
                
                if selected_supplier:
                    # Extraer el ID del proveedor
                    supplier_id = int(selected_supplier.split("ID: ")[1].replace(")", ""))
                    
                    # Cantidad a comprar
                    quantity = st.number_input(
                        "Cantidad a comprar:", 
                        min_value=1, 
                        value=10,
                        key="purchase_quantity"
                    )
                    
                    # Mostrar coste total
                    supplier = next(s for s in suppliers if s["id"] == supplier_id)
                    total_cost = supplier["unit_cost"] * quantity
                    st.write(f"**Coste total:** {total_cost}€")
                    
                    # Mostrar fecha estimada de entrega
                    delivery_date = datetime.fromisoformat(supplier["estimated_arrival"]).date()
                    st.write(f"**Fecha estimada de entrega:** {delivery_date.isoformat()}")
                    
                    # Botón para realizar la compra
                    if st.button("🛍️ Realizar compra", type="primary"):
                        try:
                            response = requests.post(
                                f"{self.api_url}/orders/purchase",
                                json={
                                    "supplier_id": supplier_id,
                                    "product_id": product_id,
                                    "quantity": quantity
                                }
                            )
                            result = response.json()
                            
                            st.success(f"Orden de compra creada: {result['message']}")
                            
                            # Recargar datos
                            self.load_data()
                        except Exception as e:
                            st.error(f"Error al crear orden de compra: {str(e)}")
            
            except Exception as e:
                st.error(f"Error al obtener proveedores: {str(e)}")
    
    def render_charts(self):
        """Renderiza las gráficas de análisis."""
        st.subheader("📊 Análisis")
        
        # Crear datasets para las gráficas
        if st.session_state.events:
            # Agrupar eventos por día y tipo
            events_by_day = {}
            stock_history = {}
            
            for event in st.session_state.events:
                event_date = event["date"].split("T")[0]  # Solo la parte de fecha
                event_type = event["type"]
                
                # Eventos por día
                if event_date not in events_by_day:
                    events_by_day[event_date] = {}
                
                if event_type not in events_by_day[event_date]:
                    events_by_day[event_date][event_type] = 0
                
                events_by_day[event_date][event_type] += 1
                
                # Historial de stock
                if event_type == "stock_level_changed":
                    details = event["details"]
                    product_id = details.get("product_id")
                    
                    if product_id:
                        if product_id not in stock_history:
                            stock_history[product_id] = []
                        
                        stock_history[product_id].append({
                            "date": event_date,
                            "quantity": details.get("new_quantity", 0)
                        })
            
            # Gráfica de eventos por día
            st.write("**Eventos por día:**")
            
            events_data = []
            for day, events in events_by_day.items():
                for event_type, count in events.items():
                    events_data.append({
                        "day": day,
                        "event_type": event_type,
                        "count": count
                    })
            
            if events_data:
                events_df = pd.DataFrame(events_data)
                
                chart = alt.Chart(events_df).mark_bar().encode(
                    x="day:O",
                    y="count:Q",
                    color="event_type:N",
                    tooltip=["day", "event_type", "count"]
                ).properties(
                    width=700,
                    height=300,
                    title="Eventos por Día"
                )
                
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No hay suficientes datos para mostrar la gráfica de eventos.")
            
            # Gráfica de evolución de inventario
            st.write("**Evolución de inventario:**")
            
            if stock_history:
                # Seleccionar producto para la gráfica
                products_with_history = []
                for product_id, history in stock_history.items():
                    if len(history) > 1:  # Solo mostrar productos con más de un registro
                        # Buscar nombre del producto
                        product_name = next(
                            (item["product_name"] for item in st.session_state.inventory 
                             if item["product_id"] == product_id),
                            f"Producto ID: {product_id}"
                        )
                        products_with_history.append((product_id, product_name))
                
                if products_with_history:
                    selected_product_for_chart = st.selectbox(
                        "Seleccione producto para ver evolución:",
                        options=[f"{name} (ID: {id})" for id, name in products_with_history],
                        key="stock_chart_product"
                    )
                    
                    if selected_product_for_chart:
                        # Extraer el ID del producto
                        product_id = int(selected_product_for_chart.split("ID: ")[1].replace(")", ""))
                        
                        # Crear dataframe para la gráfica
                        stock_data = stock_history[product_id]
                        stock_df = pd.DataFrame(stock_data)
                        
                        chart = alt.Chart(stock_df).mark_line(point=True).encode(
                            x="date:T",
                            y="quantity:Q",
                            tooltip=["date", "quantity"]
                        ).properties(
                            width=700,
                            height=300,
                            title=f"Evolución de Inventario - {selected_product_for_chart.split(' (ID:')[0]}"
                        )
                        
                        st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("No hay suficientes datos de inventario para mostrar gráficas.")
            else:
                st.info("No hay historial de cambios de inventario para mostrar.")
        else:
            st.info("No hay suficientes datos para mostrar gráficas. Avance algunos días en la simulación.")

def run_streamlit_app(api_url: str = "http://localhost:8000"):
    """
    Ejecuta la aplicación Streamlit.
    
    Args:
        api_url: URL de la API REST
    """
    app = StreamlitApp(api_url)
    app.render()

if __name__ == "__main__":
    run_streamlit_app()
