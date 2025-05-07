# Product Requirements Document (PRD)
# Simulador de Producción de Impresoras 3D

## 1. Visión General

El Simulador de Producción de Impresoras 3D es una aplicación de software diseñada para simular día a día el ciclo completo de operación de una planta de fabricación de impresoras 3D. El sistema se enfoca principalmente en tres aspectos clave: gestión de inventarios, compras y planificación de la producción. Los usuarios asumirán el rol de planificadores, tomando decisiones sobre qué fabricar y qué comprar para satisfacer la demanda generada.

## 2. Objetivos del Producto

- Desarrollar un simulador que modele de manera realista el proceso de producción de impresoras 3D.
- Diseñar la arquitectura base de un sistema MRP escalable.
- Permitir a los usuarios practicar y mejorar sus habilidades de planificación de producción.
- Proporcionar una herramienta interactiva con interfaz de usuario intuitiva.
- Ofrecer acceso a toda la funcionalidad e información a través de una API REST.

## 3. Usuarios Objetivo

- Estudiantes en el campo de ingeniería de sistemas, producción o gestión de operaciones.
- Arquitectos de sistemas de información que tengan como objetivo construir un MRP escalable.
- Profesionales en formación en gestión de cadena de suministro.
- Educadores que buscan herramientas didácticas para enseñar conceptos de planificación de producción.

## 4. Requisitos Funcionales

### 4.1 Configuración Inicial
- **Definición de condiciones iniciales:**
  - Plan de producción: materiales necesarios para cada tipo de impresora y tiempo en la cadena de montaje.
  - Catálogo de proveedores: productos disponibles, precios por cantidades, tiempo de entrega.
  - Capacidad de almacén: 1 unidad de cualquier material = 1 unidad de almacenaje.

### 4.2 Generación de Demanda
- Creación aleatoria de pedidos de fabricación al inicio de cada día.
- Parámetros configurables: media y varianza de la demanda.

### 4.3 Tablero de Control
- Visualización de pedidos pendientes.
- Visualización de la lista de materiales (BOM) para cada pedido.
- Monitoreo del nivel de inventario actual.

### 4.4 Interacción del Usuario
- **Decisiones de producción:**
  - Liberar pedidos a producción según capacidad disponible.
- **Decisiones de compra:**
  - Emitir órdenes de compra especificando producto, proveedor, cantidad y fecha.

### 4.5 Simulación de Eventos
- Consumo de materias primas basado en órdenes liberadas.
- Fabricación limitada por la capacidad diaria de producción.
- Recepción de materiales comprados según el lead time de cada proveedor.

### 4.6 Gestión del Tiempo
- Función "Avanzar día" para ejecutar 24 horas de simulación.
- Actualización de todos los parámetros del sistema tras el avance de tiempo.

### 4.7 Almacenamiento de Datos
- Registro de todos los eventos para análisis histórico.
- Generación de gráficas basadas en datos almacenados.

### 4.8 Import/Export de Datos
- Exportación de inventario y eventos en formato JSON.
- Importación de datos previamente guardados.

### 4.9 API REST
- Exposición de toda la funcionalidad mediante una API REST.
- Documentación completa con SWAGGER/OpenAPI.

## 5. Requisitos No Funcionales

### 5.1 Calidad de Código
- Código claro y bien comentado.
- Versionado completo con Git.

### 5.2 Accesibilidad
- Interfaz web sencilla y accesible.
- Sin necesidad de instalaciones complejas en el cliente.

### 5.3 Despliegue
- Contenedores Docker orquestados con Docker Compose


## 6. Modelo de Datos

### 6.1 Entidades Principales

#### Productos
- **Products** (id, name, type: "raw" or "finished")

#### Composición de Productos
- **BOM** (finished_product_id, material_id, quantity)

#### Proveedores
- **Suppliers** (id, name, product_id, unit_cost, lead_time_days)

#### Inventario
- **StockCurrent** (product_id, quantity)

#### Pedidos
- **ManufacturingOrders**  (id, creation_date, product_id, quantity, status)

#### Compras
- **PurchaseOrders** (id, supplier_id, product_id, quantity, issue_date, estimated_delivery_date, status)

#### Eventos
- **Events** (id, type, event_date, details)

### 6.2 Modelos de Impresoras 3D
- **P3D-Classic**: Modelo base con componentes estándar.
- **P3D-Pro**: Modelo avanzado con sensores adicionales.

### 6.3 BOM (Lista de Materiales) por Modelo

#### P3D-Classic
- 1 kit_piezas
- 1 pcb (CTRL-V2)
- 1 extrusor
- 2 cables_conexion
- 1 transformador_24v
- 1 enchufe_schuko

#### P3D-Pro
- 1 kit_piezas
- 1 pcb (CTRL-V3)
- 1 extrusor
- 1 sensor_autonivel
- 3 cables_conexion
- 1 transformador_24v
- 1 enchufe_schuko

## 7. Interfaz de Usuario

### 7.1 Componentes Principales
- **Encabezado:** Muestra el día actual de simulación y el botón "Avanzar día".
- **Panel de Pedidos:** Tabla de pedidos pendientes con cálculo automático de BOM.
- **Panel de Inventario:** Niveles actuales y alertas de faltantes.
- **Panel de Compras:** Selección de proveedores, campo de cantidad, botón para emitir órdenes.
- **Panel de Producción:** Visualización de capacidad diaria, pedidos en cola y en proceso.
- **Gráficas:** Visualización de nivel de stock y número de pedidos completados en el tiempo.

## 8. Arquitectura Técnica

### 8.1 Pila Tecnológica

| Capa | Herramienta | Motivo |
|------|-------------|--------|
| Lenguaje | Python 3.11 | Ampliamente usado |
| Simulación | SimPy | Motor de eventos discretos fácil de usar |
| Persistencia | SQLite | Ligero y portable |
| Back-end API | Fastapi + Pydantic | Implementación de la API REST |
| Interfaz | Streamlit | Construcción rápida |
| Gráficas | Vega-Altair | Integración directa en Streamlit |
| Control de versiones | Git + GitHub | Flujo estándar de desarrollo |

### 8.2 Estructuras de Datos en Python
```python
from typing import Literal, Optional, Dict, List
from pydantic import BaseModel

# Productos
class Product(BaseModel):
    id: int
    name: str
    type: Literal["raw", "finished"]  # Tipo de producto

# Composición de productos (Bill of Materials)
class BOM(BaseModel):
    finished_product_id: int
    material_id: int
    quantity: int

# Proveedores
class Supplier(BaseModel):
    id: int
    name: str
    product_id: int  # Producto que provee
    unit_cost: float
    lead_time_days: int  # Tiempo de entrega en días

# Inventario actual
class StockCurrent(BaseModel):
    product_id: int
    quantity: int

# Pedidos de fabricación
class ManufacturingOrder(BaseModel):
    id: int
    creation_date: str  # ISO 8601 o formato consistente
    product_id: int
    quantity: int
    status: str

# Órdenes de compra
class PurchaseOrder(BaseModel):
    id: int
    supplier_id: int
    product_id: int
    quantity: int
    issue_date: str
    estimated_delivery_date: str
    status: str

# Eventos
class Event(BaseModel):
    id: int
    type: str
    event_date: str
    details: str
```

## 9. Flujo de Simulación

### 9.1 Ciclo Diario
1. **Avanzar día** → SimPy ejecuta simulación de 24 horas.
2. Se generan nuevos pedidos según parámetros configurados.
3. El tablero se actualiza y el usuario toma decisiones:
   - Liberar pedidos a producción.
   - Emitir órdenes de compra.
4. SimPy procesa las actividades de compras y producción.
5. Fin del día: se registran todos los eventos en la tabla `Evento`.

### 9.2 Escenario de Ejemplo
- **Día 1:** 
  - Stock inicial = 30 kits de piezas
  - Capacidad = 10 impresoras/día
  - Generación de pedidos: 8 y 6 unidades
  - Usuario libera pedido de 8 unidades
  - Sistema verifica stock (8 kits), quedan 22 en inventario

- **Día 2:**
  - Generación de nuevos pedidos: 5 y 7 unidades
  - Stock disminuye
  - Usuario decide comprar 20 kits al proveedor A (90€/kit, lead time 3 días)

## 10. Entregables

### 10.1 Repositorio Git
- Código fuente completo con README.
- Instrucciones detalladas de instalación y uso.

### 10.2 Informe Técnico (PDF)
- Diseño de datos y decisiones técnicas tomadas.
- Capturas de la interfaz de usuario.
- Análisis de escenarios de prueba.

### 10.3 Presentación
- Máximo 10 diapositivas para exposición del proyecto.

## 11. Hitos del Proyecto

1. **Diseño e implementación del modelo de datos** (Semana 1)
2. **Implementación de la simulación básica con SimPy** (Semana 2)
3. **Integración con Streamlit y tablero mínimo** (Semana 3)
4. **Implementación de lógica de BOM y compras** (Semana 4)
5. **Mejora de interfaz y gráficas** (Semana 5)
6. **Pruebas con escenarios y documentación** (Semana 6)

## 12. Consideraciones Adicionales

- Uso de Vibe Coding para generar documentos técnicos.
- Posibilidad de compartir archivos de inicialización, importación/exportación JSON y partes de código con otros equipos (máximo 20% del código).
- Documentación de la API debe ser clara y completa para facilitar el uso por parte de terceros.
- Los hitos deben ser marcados en GitHub Issues y cada commit relacionado debe hacer referencia al número de issue correspondiente.