import streamlit as st
import altair as alt
import pandas as pd
import requests
import json
import sys
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
        print(f"Inicializando Streamlit con API URL: {api_url}")
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
            try:
                # Intentar obtener fecha actual de la API
                response = requests.get(f"{self.api_url}/")
                data = response.json()
                
                st.session_state.current_date = data["current_date"]
            except Exception as e:
                st.error(f"Error al conectar con la API ({self.api_url}): {str(e)}")
                st.session_state.current_date = date.today().isoformat()
                
                # Mostrar información de depuración
                st.info(f"API URL configurada: {self.api_url}")
                st.info(f"Intentando conectar a: {self.api_url}/")
            
            # Inicializar el resto del estado con listas vacías
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
            st.session_state.pending_orders = response.json() if response.ok else []
            
            # Cargar inventario
            response = requests.get(f"{self.api_url}/inventory")
            st.session_state.inventory = response.json() if response.ok else []
            
            # Cargar eventos recientes
            try:
                today = datetime.fromisoformat(st.session_state.current_date).date()
                week_ago = (today - timedelta(days=7)).isoformat()
                
                response = requests.get(
                    f"{self.api_url}/events",
                    params={"start_date": week_ago, "end_date": today.isoformat()}
                )
                st.session_state.events = response.json() if response.ok else []
            except (ValueError, TypeError) as e:
                st.error(f"Error al procesar fechas: {str(e)}")
                st.session_state.events = []
            
        except Exception as e:
            st.error(f"Error al cargar datos: {str(e)}")
    
    def render(self):
        """Renderiza la interfaz de usuario."""
        st.title("🖨️ Simulador de Producción de Impresoras 3D")
        
        # Mostrar información sobre la conexión a la API
        st.sidebar.info(f"Conectado a: {self.api_url}")
        
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
                    if response.ok:
                        data = response.json()
                        st.session_state.current_date = data["new_date"]
                        st.success(data["message"])
                        
                        # Recargar datos
                        self.load_data()
                    else:
                        st.error(f"Error al avanzar día: Status {response.status_code}")
                except Exception as e:
                    st.error(f"Error al avanzar día: {str(e)}")
        
        st.divider()
    
    def render_orders_panel(self):
        """Renderiza el panel de pedidos pendientes."""
        st.subheader("📋 Pedidos Pendientes")
        
        if not st.session_state.pending_orders:
            st.info("No hay pedidos pendientes.")
            return
        
        for order_idx, order in enumerate(st.session_state.pending_orders):
            # Verificar que el orden tiene la estructura esperada
            if not isinstance(order, dict) or 'order' not in order:
                st.error(f"Estructura de orden #{order_idx} no válida")
                continue
                
            order_data = order.get('order', {})
            product_name = order.get('product_name', 'Producto desconocido')
            
            # Verificar que hay un ID de orden
            if 'id' not in order_data:
                st.error(f"Orden sin ID: {product_name}")
                continue
            
            with st.expander(
                f"Pedido #{order_data['id']} - {product_name} ({order_data.get('quantity', 0)} unidades)"
            ):
                st.write(f"**Fecha de creación:** {order_data.get('creation_date', 'Desconocida')}")
                st.write(f"**Estado:** {order_data.get('status', 'Desconocido')}")
                
                # Tabla de materiales
                st.write("**Materiales necesarios:**")
                
                # Verificar que hay materiales en la orden
                materials = order.get("materials", [])
                if not materials:
                    st.info("No hay información de materiales disponible.")
                else:
                    try:
                        # Crear dataframe solo si hay datos
                        materials_df = pd.DataFrame(materials)
                        
                        # Asegurar que las columnas esperadas existen
                        expected_columns = {"id", "name", "required", "available", "sufficient"}
                        if all(col in materials_df.columns for col in expected_columns):
                            # Renombrar columnas
                            materials_df = materials_df.rename(columns={
                                "id": "ID", 
                                "name": "Material", 
                                "required": "Requerido", 
                                "available": "Disponible", 
                                "sufficient": "Suficiente"
                            })
                            
                            # Resaltar filas con inventario insuficiente si la columna existe
                            if "Suficiente" in materials_df.columns:
                                def highlight_insufficient(row):
                                    return ['background-color: #ffcccc' 
                                            if not row.get("Suficiente", True) else '' 
                                            for _ in row]
                                
                                st.dataframe(materials_df.style.apply(highlight_insufficient, axis=1))
                            else:
                                st.dataframe(materials_df)
                        else:
                            st.warning("El formato de los datos de materiales no es el esperado.")
                            st.dataframe(materials_df)
                    except Exception as e:
                        st.error(f"Error al mostrar materiales: {str(e)}")
                        st.json(materials)
                
                # Botón para liberar a producción
                can_produce = order.get("can_produce", False)
                if can_produce:
                    if st.button(
                        f"🚀 Liberar a producción",
                        key=f"release_{order_data['id']}"
                    ):
                        try:
                            response = requests.post(
                                f"{self.api_url}/orders/manufacturing/{order_data['id']}/release"
                            )
                            if response.ok:
                                result = response.json()
                                if result.get("success", False):
                                    st.success(result.get("message", "Orden liberada con éxito"))
                                    # Recargar datos
                                    self.load_data()
                                else:
                                    st.error(result.get("message", "Error al liberar orden"))
                            else:
                                st.error(f"Error al liberar orden: Status {response.status_code}")
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
        
        try:
            # Verificar que los datos tienen el formato esperado antes de crear el dataframe
            expected_columns = {"product_id", "product_name", "product_type", "quantity"}
            
            valid_inventory = []
            for item in st.session_state.inventory:
                if all(col in item for col in expected_columns):
                    valid_inventory.append(item)
            
            if not valid_inventory:
                st.warning("Los datos de inventario no tienen el formato esperado.")
                return
            
            # Filtrar por tipo de producto
            inventory_df = pd.DataFrame(valid_inventory)
            
            # Separar materias primas y productos terminados
            raw_materials = inventory_df[inventory_df["product_type"] == "raw"]
            finished_products = inventory_df[inventory_df["product_type"] == "finished"]
            
            # Mostrar materias primas
            st.write("**Materias Primas:**")
            if raw_materials.empty:
                st.info("No hay materias primas en inventario.")
            else:
                raw_df = raw_materials[["product_name", "quantity"]]
                raw_df.columns = ["Material", "Cantidad"]
                st.dataframe(raw_df)
            
            # Mostrar productos terminados
            st.write("**Productos Terminados:**")
            if finished_products.empty:
                st.info("No hay productos terminados en inventario.")
            else:
                finished_df = finished_products[["product_name", "quantity"]]
                finished_df.columns = ["Producto", "Cantidad"]
                st.dataframe(finished_df)
        
        except Exception as e:
            st.error(f"Error al mostrar inventario: {str(e)}")
            st.json(st.session_state.inventory)
    
    def render_production_panel(self):
        """Renderiza el panel de producción."""
        st.subheader("🏭 Producción")
        
        # Aquí se mostraría información sobre las órdenes en producción
        # Por ahora, mostramos un placeholder
        st.info("Panel de producción - No implementado en el prototipo")
    
    def render_purchase_panel(self):
        """Renderiza el panel de compras."""
        st.subheader("🛒 Compras")
        
        try:
            # Filtrar solo materias primas del inventario
            raw_materials = [
                item for item in st.session_state.inventory 
                if item.get("product_type") == "raw"
            ]
            
            if not raw_materials:
                st.info("No hay materias primas disponibles para comprar.")
                return
            
            # Seleccionar producto para comprar
            product_options = [f"{item.get('product_name', 'Desconocido')} (ID: {item.get('product_id', 0)})" 
                              for item in raw_materials if 'product_id' in item]
            
            if not product_options:
                st.warning("No hay materias primas válidas disponibles.")
                return
                
            selected_product = st.selectbox(
                "Seleccione material a comprar:",
                options=product_options,
                key="purchase_product"
            )
            
            if selected_product:
                try:
                    # Extraer el ID del producto
                    product_id = int(selected_product.split("ID: ")[1].replace(")", ""))
                    
                    # Obtener proveedores para este producto
                    response = requests.get(
                        f"{self.api_url}/products/{product_id}/suppliers"
                    )
                    
                    if not response.ok:
                        st.error(f"Error al obtener proveedores: Status {response.status_code}")
                        return
                        
                    suppliers = response.json()
                    
                    if not suppliers:
                        st.warning("No hay proveedores disponibles para este producto.")
                        return
                    
                    # Verificar formato de proveedores
                    supplier_options = []
                    for s in suppliers:
                        if all(key in s for key in ["id", "name", "unit_cost", "lead_time_days"]):
                            supplier_options.append(
                                f"{s['name']} - {s['unit_cost']}€/unidad - Entrega: {s['lead_time_days']} días (ID: {s['id']})"
                            )
                    
                    if not supplier_options:
                        st.warning("No hay proveedores con formato válido.")
                        return
                        
                    # Seleccionar proveedor
                    selected_supplier = st.selectbox(
                        "Seleccione proveedor:",
                        options=supplier_options,
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
                        supplier = next((s for s in suppliers if s.get("id") == supplier_id), None)
                        if supplier:
                            total_cost = supplier.get("unit_cost", 0) * quantity
                            st.write(f"**Coste total:** {total_cost}€")
                            
                            # Mostrar fecha estimada de entrega
                            if "estimated_arrival" in supplier:
                                try:
                                    delivery_date = datetime.fromisoformat(supplier["estimated_arrival"]).date()
                                    st.write(f"**Fecha estimada de entrega:** {delivery_date.isoformat()}")
                                except ValueError:
                                    st.write(f"**Fecha estimada de entrega:** {supplier['estimated_arrival']}")
                            
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
                                    
                                    if response.ok:
                                        result = response.json()
                                        st.success(f"Orden de compra creada: {result.get('message', 'Orden creada con éxito')}")
                                        
                                        # Recargar datos
                                        self.load_data()
                                    else:
                                        st.error(f"Error al crear orden de compra: Status {response.status_code}")
                                except Exception as e:
                                    st.error(f"Error al crear orden de compra: {str(e)}")
                        else:
                            st.error("No se pudo encontrar la información del proveedor seleccionado.")
                
                except (ValueError, IndexError) as e:
                    st.error(f"Error al procesar selección: {str(e)}")
                except Exception as e:
                    st.error(f"Error inesperado: {str(e)}")
        
        except Exception as e:
            st.error(f"Error al cargar panel de compras: {str(e)}")
    
    def render_charts(self):
        """Renderiza las gráficas de análisis."""
        st.subheader("📊 Análisis")
        
        # Crear datasets para las gráficas
        if not st.session_state.events:
            st.info("No hay suficientes datos para mostrar gráficas. Avance algunos días en la simulación.")
            return
            
        try:
            # Agrupar eventos por día y tipo
            events_by_day = {}
            stock_history = {}
            
            for event in st.session_state.events:
                # Validar estructura del evento
                if not isinstance(event, dict) or 'date' not in event or 'type' not in event:
                    continue
                    
                # Obtener fecha y tipo del evento
                event_date = event.get("date", "").split("T")[0]  # Solo la parte de fecha
                event_type = event.get("type", "unknown")
                
                if not event_date:
                    continue
                
                # Eventos por día
                if event_date not in events_by_day:
                    events_by_day[event_date] = {}
                
                if event_type not in events_by_day[event_date]:
                    events_by_day[event_date][event_type] = 0
                
                events_by_day[event_date][event_type] += 1
                
                # Historial de stock
                if event_type == "stock_level_changed" and 'details' in event:
                    details = event.get("details", {})
                    if isinstance(details, dict) and 'product_id' in details:
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
                            (item.get("product_name", f"Producto ID: {product_id}") 
                             for item in st.session_state.inventory 
                             if item.get("product_id") == product_id),
                            f"Producto ID: {product_id}"
                        )
                        products_with_history.append((product_id, product_name))
                
                if products_with_history:
                    product_options = [f"{name} (ID: {id})" for id, name in products_with_history]
                    
                    selected_product_for_chart = st.selectbox(
                        "Seleccione producto para ver evolución:",
                        options=product_options,
                        key="stock_chart_product"
                    )
                    
                    if selected_product_for_chart:
                        try:
                            # Extraer el ID del producto
                            product_id = int(selected_product_for_chart.split("ID: ")[1].replace(")", ""))
                            
                            # Verificar que el producto tiene historial
                            if product_id in stock_history:
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
                                st.info(f"No hay historial para el producto seleccionado.")
                        except Exception as e:
                            st.error(f"Error al mostrar gráfica: {str(e)}")
                else:
                    st.info("No hay suficientes datos de inventario para mostrar gráficas.")
            else:
                st.info("No hay historial de cambios de inventario para mostrar.")
        except Exception as e:
            st.error(f"Error al generar gráficas: {str(e)}")
            st.write("Detalles del error:", e)

def run_streamlit_app():
    """
    Ejecuta la aplicación Streamlit.
    """
    # Obtener la URL de la API de los argumentos de línea de comando
    api_url = "http://localhost:8000"  # Valor por defecto
    
    # Si hay argumentos de línea de comando, el primero debería ser la URL de la API
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
        print(f"Usando API URL desde argumentos: {api_url}")
    
    app = StreamlitApp(api_url)
    app.render()

if __name__ == "__main__":
    run_streamlit_app()
