# Contexto del Prompt para Generación de la API REST

## Objetivo
Crear una API REST utilizando FastAPI para gestionar los datos de un sistema de producción de impresoras, específicamente enfocado en productos y órdenes de producción.

## Contexto Inicial
- El proyecto ya contaba con una base de datos SQLite (`simulador_produccion.db`)
- Existía un archivo `entities.py` con las definiciones de las entidades del sistema
- Se requería implementar servicios para crear y actualizar datos

## Entidades Principales
Las entidades principales definidas en `entities.py` incluyen:
- Product: Productos (materia prima o producto terminado)
- ProductionOrder: Órdenes de producción
- BOMItem: Lista de materiales
- Supplier: Proveedores
- InventoryItem: Items en inventario
- PurchaseOrder: Órdenes de compra
- Event: Eventos del sistema
- SimulationConfig: Configuración de simulación
- DailyPlan: Plan diario
- SimulationState: Estado de la simulación

## Requisitos de Implementación
1. Crear endpoints REST para:
   - Crear y actualizar productos
   - Crear y actualizar órdenes de producción
   - Obtener listados de productos y órdenes

2. Utilizar FastAPI como framework
3. Mantener la integridad de los datos con la base de datos SQLite existente
4. Implementar manejo de errores apropiado
5. Proporcionar documentación clara de la API

## Consideraciones Técnicas
- Uso de Pydantic para validación de datos
- Manejo de conexiones a la base de datos
- Implementación de transacciones
- Manejo de errores HTTP apropiados
- Documentación automática de la API

## Resultado
Se implementó una API REST con los siguientes endpoints:

### Productos
- POST /products/
- GET /products/
- PUT /products/{product_id}

### Órdenes de Producción
- POST /production-orders/
- GET /production-orders/
- PUT /production-orders/{order_id}

La implementación incluye:
- Validación de datos
- Manejo de errores
- Documentación automática
- Conexión segura a la base de datos
- Transacciones para mantener la integridad de los datos 