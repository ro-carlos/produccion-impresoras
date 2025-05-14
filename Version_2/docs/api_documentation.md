# Documentación de la API REST
## Simulador de Producción de Impresoras 3D

Esta documentación describe la API REST del Simulador de Producción de Impresoras 3D, que permite acceder a todas las funcionalidades del sistema de manera programática.

## Información General

- **Base URL**: `http://localhost:8000/api/v1`
- **Formato**: Todas las respuestas son en formato JSON
- **Autenticación**: No se requiere autenticación para esta versión

## Endpoints

### Simulación

#### Avanzar Día

```
POST /simulation/advance-day
```

Avanza la simulación un día completo, generando nuevos pedidos y actualizando todos los estados.

**Respuesta**:
```json
{
  "status": "success",
  "current_day": 5,
  "new_orders": [
    {
      "id": 34,
      "product_id": 1,
      "quantity": 8,
      "creation_date": "2025-05-14",
      "status": "pending"
    },
    {
      "id": 35,
      "product_id": 2,
      "quantity": 4,
      "creation_date": "2025-05-14",
      "status": "pending"
    }
  ]
}
```

#### Obtener Día Actual

```
GET /simulation/current-day
```

Devuelve el día actual de la simulación.

**Respuesta**:
```json
{
  "current_day": 5
}
```

#### Reiniciar Simulación

```
POST /simulation/reset
```

Reinicia la simulación al día 1 con los valores iniciales.

**Respuesta**:
```json
{
  "status": "success",
  "message": "Simulation reset to day 1"
}
```

### Productos

#### Listar Productos

```
GET /products
```

Devuelve la lista de todos los productos en el sistema.

**Parámetros de consulta**:
- `type` (opcional): Filtrar por tipo de producto ("raw" o "finished")

**Respuesta**:
```json
[
  {
    "id": 1,
    "name": "P3D-Classic",
    "type": "finished"
  },
  {
    "id": 2,
    "name": "P3D-Pro",
    "type": "finished"
  },
  {
    "id": 3,
    "name": "kit_piezas",
    "type": "raw"
  },
  {
    "id": 4,
    "name": "pcb",
    "type": "raw"
  }
]
```

#### Obtener Producto

```
GET /products/{product_id}
```

Devuelve la información de un producto específico.

**Respuesta**:
```json
{
  "id": 1,
  "name": "P3D-Classic",
  "type": "finished"
}
```

#### Obtener BOM de Producto

```
GET /products/{product_id}/bom
```

Devuelve la lista de materiales (BOM) para un producto terminado.

**Respuesta**:
```json
{
  "product_id": 1,
  "product_name": "P3D-Classic",
  "materials": [
    {
      "material_id": 3,
      "material_name": "kit_piezas",
      "quantity": 1
    },
    {
      "material_id": 4,
      "material_name": "pcb",
      "quantity": 1
    },
    {
      "material_id": 5,
      "material_name": "extrusor",
      "quantity": 1
    },
    {
      "material_id": 6,
      "material_name": "cables_conexion",
      "quantity": 2
    },
    {
      "material_id": 7,
      "material_name": "transformador_24v",
      "quantity": 1
    },
    {
      "material_id": 8,
      "material_name": "enchufe_schuko",
      "quantity": 1
    }
  ]
}
```

### Inventario

#### Obtener Inventario Actual

```
GET /inventory
```

Devuelve el estado actual del inventario.

**Parámetros de consulta**:
- `type` (opcional): Filtrar por tipo de producto ("raw" o "finished")

**Respuesta**:
```json
[
  {
    "product_id": 3,
    "product_name": "kit_piezas",
    "quantity": 25,
    "type": "raw"
  },
  {
    "product_id": 4,
    "product_name": "pcb",
    "quantity": 18,
    "type": "raw"
  }
]
```

#### Verificar Disponibilidad

```
GET /inventory/check-availability
```

Verifica si hay suficiente inventario para producir una cantidad de un producto.

**Parámetros de consulta**:
- `product_id` (requerido): ID del producto
- `quantity` (requerido): Cantidad deseada

**Respuesta**:
```json
{
  "available": true,
  "missing_materials": []
}
```

o

```json
{
  "available": false,
  "missing_materials": [
    {
      "material_id": 4,
      "material_name": "pcb",
      "required": 10,
      "available": 8,
      "missing": 2
    }
  ]
}
```

### Pedidos de Fabricación

#### Listar Pedidos

```
GET /manufacturing-orders
```

Devuelve la lista de pedidos de fabricación.

**Parámetros de consulta**:
- `status` (opcional): Filtrar por estado ("pending", "in_progress", "completed", "cancelled")
- `date_from` (opcional): Filtrar desde una fecha (YYYY-MM-DD)
- `date_to` (opcional): Filtrar hasta una fecha (YYYY-MM-DD)

**Respuesta**:
```json
[
  {
    "id": 1,
    "product_id": 1,
    "product_name": "P3D-Classic",
    "quantity": 5,
    "creation_date": "2025-05-10",
    "status": "completed"
  },
  {
    "id": 2,
    "product_id": 2,
    "product_name": "P3D-Pro",
    "quantity": 3,
    "creation_date": "2025-05-10",
    "status": "in_progress"
  }
]
```

#### Obtener Pedido

```
GET /manufacturing-orders/{order_id}
```

Devuelve la información de un pedido específico.

**Respuesta**:
```json
{
  "id": 1,
  "product_id": 1,
  "product_name": "P3D-Classic",
  "quantity": 5,
  "creation_date": "2025-05-10",
  "status": "completed"
}
```

#### Crear Pedido

```
POST /manufacturing-orders
```

Crea un nuevo pedido de fabricación.

**Cuerpo de la solicitud**:
```json
{
  "product_id": 1,
  "quantity": 5
}
```

**Respuesta**:
```json
{
  "id": 36,
  "product_id": 1,
  "product_name": "P3D-Classic",
  "quantity": 5,
  "creation_date": "2025-05-14",
  "status": "pending"
}
```

#### Liberar Pedido a Producción

```
POST /manufacturing-orders/{order_id}/release
```

Libera un pedido a producción, verificando disponibilidad de materiales y capacidad.

**Respuesta**:
```json
{
  "status": "success",
  "message": "Order released to production",
  "order_id": 36,
  "materials_consumed": [
    {
      "material_id": 3,
      "material_name": "kit_piezas",
      "quantity": 5
    },
    {
      "material_id": 4,
      "material_name": "pcb",
      "quantity": 5
    }
  ]
}
```

o

```json
{
  "status": "error",
  "message": "Insufficient materials",
  "missing_materials": [
    {
      "material_id": 4,
      "material_name": "pcb",
      "required": 5,
      "available": 3,
      "missing": 2
    }
  ]
}
```

#### Cancelar Pedido

```
POST /manufacturing-orders/{order_id}/cancel
```

Cancela un pedido pendiente.

**Respuesta**:
```json
{
  "status": "success",
  "message": "Order cancelled",
  "order_id": 36
}
```

### Proveedores

#### Listar Proveedores

```
GET /suppliers
```

Devuelve la lista de proveedores disponibles.

**Parámetros de consulta**:
- `product_id` (opcional): Filtrar por producto

**Respuesta**:
```json
[
  {
    "id": 1,
    "name": "Proveedor A",
    "product_id": 3,
    "product_name": "kit_piezas",
    "unit_cost": 90.0,
    "lead_time_days": 3
  },
  {
    "id": 2,
    "name": "Proveedor B",
    "product_id": 3,
    "product_name": "kit_piezas",
    "unit_cost": 85.0,
    "lead_time_days": 5
  }
]
```

#### Obtener Proveedor

```
GET /suppliers/{supplier_id}
```

Devuelve la información de un proveedor específico.

**Respuesta**:
```json
{
  "id": 1,
  "name": "Proveedor A",
  "product_id": 3,
  "product_name": "kit_piezas",
  "unit_cost": 90.0,
  "lead_time_days": 3
}
```

### Órdenes de Compra

#### Listar Órdenes de Compra

```
GET /purchase-orders
```

Devuelve la lista de órdenes de compra.

**Parámetros de consulta**:
- `status` (opcional): Filtrar por estado ("pending", "received", "cancelled")
- `date_from` (opcional): Filtrar desde una fecha (YYYY-MM-DD)
- `date_to` (opcional): Filtrar hasta una fecha (YYYY-MM-DD)

**Respuesta**:
```json
[
  {
    "id": 1,
    "supplier_id": 1,
    "supplier_name": "Proveedor A",
    "product_id": 3,
    "product_name": "kit_piezas",
    "quantity": 20,
    "unit_cost": 90.0,
    "total_cost": 1800.0,
    "issue_date": "2025-05-12",
    "estimated_delivery_date": "2025-05-15",
    "status": "pending"
  }
]
```

#### Obtener Orden de Compra

```
GET /purchase-orders/{order_id}
```

Devuelve la información de una orden de compra específica.

**Respuesta**:
```json
{
  "id": 1,
  "supplier_id": 1,
  "supplier_name": "Proveedor A",
  "product_id": 3,
  "product_name": "kit_piezas",
  "quantity": 20,
  "unit_cost": 90.0,
  "total_cost": 1800.0,
  "issue_date": "2025-05-12",
  "estimated_delivery_date": "2025-05-15",
  "status": "pending"
}
```

#### Crear Orden de Compra

```
POST /purchase-orders
```

Crea una nueva orden de compra.

**Cuerpo de la solicitud**:
```json
{
  "supplier_id": 1,
  "product_id": 3,
  "quantity": 20
}
```

**Respuesta**:
```json
{
  "id": 5,
  "supplier_id": 1,
  "supplier_name": "Proveedor A",
  "product_id": 3,
  "product_name": "kit_piezas",
  "quantity": 20,
  "unit_cost": 90.0,
  "total_cost": 1800.0,
  "issue_date": "2025-05-14",
  "estimated_delivery_date": "2025-05-17",
  "status": "pending"
}
```

#### Cancelar Orden de Compra

```
POST /purchase-orders/{order_id}/cancel
```

Cancela una orden de compra pendiente.

**Respuesta**:
```json
{
  "status": "success",
  "message": "Purchase order cancelled",
  "order_id": 5
}
```

### Eventos

#### Listar Eventos

```
GET /events
```

Devuelve la lista de eventos registrados en el sistema.

**Parámetros de consulta**:
- `type` (opcional): Filtrar por tipo de evento ("order_created", "production_started", "production_completed", "purchase_order_created", "materials_received")
- `date_from` (opcional): Filtrar desde una fecha (YYYY-MM-DD)
- `date_to` (opcional): Filtrar hasta una fecha (YYYY-MM-DD)

**Respuesta**:
```json
[
  {
    "id": 1,
    "type": "order_created",
    "event_date": "2025-05-10",
    "details": "Order #1 created for 5 units of P3D-Classic"
  },
  {
    "id": 2,
    "type": "production_started",
    "event_date": "2025-05-10",
    "details": "Production started for Order #1"
  }
]
```

### Exportación e Importación

#### Exportar Datos

```
GET /export
```

Exporta todos los datos del sistema en formato JSON.

**Parámetros de consulta**:
- `include` (opcional): Lista separada por comas de entidades a incluir (por defecto, todas)

**Respuesta**:
```json
{
  "products": [...],
  "bom": [...],
  "suppliers": [...],
  "stock_current": [...],
  "manufacturing_orders": [...],
  "purchase_orders": [...],
  "events": [...]
}
```

#### Importar Datos

```
POST /import
```

Importa datos al sistema en formato JSON.

**Cuerpo de la solicitud**:
```json
{
  "products": [...],
  "bom": [...],
  "suppliers": [...],
  "stock_current": [...],
  "manufacturing_orders": [...],
  "purchase_orders": [...],
  "events": [...]
}
```

**Respuesta**:
```json
{
  "status": "success",
  "message": "Data imported successfully",
  "entities_imported": {
    "products": 10,
    "bom": 15,
    "suppliers": 5,
    "stock_current": 8,
    "manufacturing_orders": 20,
    "purchase_orders": 8,
    "events": 50
  }
}
```

## Códigos de Estado

- `200 OK`: La solicitud se ha completado correctamente
- `201 Created`: El recurso se ha creado correctamente
- `400 Bad Request`: La solicitud contiene errores de validación
- `404 Not Found`: El recurso solicitado no existe
- `422 Unprocessable Entity`: La solicitud no puede ser procesada (ej. inventario insuficiente)
- `500 Internal Server Error`: Error del servidor

## Modelos de Datos

### Product

```json
{
  "id": 1,
  "name": "P3D-Classic",
  "type": "finished"
}
```

### BOM (Bill of Materials)

```json
{
  "finished_product_id": 1,
  "material_id": 3,
  "quantity": 1
}
```

### Supplier

```json
{
  "id": 1,
  "name": "Proveedor A",
  "product_id": 3,
  "unit_cost": 90.0,
  "lead_time_days": 3
}
```

### StockCurrent

```json
{
  "product_id": 3,
  "quantity": 25
}
```

### ManufacturingOrder

```json
{
  "id": 1,
  "creation_date": "2025-05-10",
  "product_id": 1,
  "quantity": 5,
  "status": "completed"
}
```

### PurchaseOrder

```json
{
  "id": 1,
  "supplier_id": 1,
  "product_id": 3,
  "quantity": 20,
  "issue_date": "2025-05-12",
  "estimated_delivery_date": "2025-05-15",
  "status": "pending"
}
```

### Event

```json
{
  "id": 1,
  "type": "order_created",
  "event_date": "2025-05-10",
  "details": "Order #1 created for 5 units of P3D-Classic"
}
```

## Ejemplos de Uso

### Flujo Típico de Operación

1. Consultar el inventario actual:
   ```
   GET /inventory
   ```

2. Verificar pedidos pendientes:
   ```
   GET /manufacturing-orders?status=pending
   ```

3. Verificar disponibilidad para un pedido:
   ```
   GET /inventory/check-availability?product_id=1&quantity=5
   ```

4. Si hay suficientes materiales, liberar el pedido a producción:
   ```
   POST /manufacturing-orders/12/release
   ```

5. Si faltan materiales, consultar proveedores:
   ```
   GET /suppliers?product_id=3
   ```

6. Emitir una orden de compra:
   ```
   POST /purchase-orders
   {
     "supplier_id": 1,
     "product_id": 3,
     "quantity": 20
   }
   ```

7. Avanzar el día para que avance la simulación:
   ```
   POST /simulation/advance-day
   ```

8. Ver los eventos generados:
   ```
   GET /events?date_from=2025-05-14
   ```

## Notas Adicionales

- Todas las fechas están en formato ISO 8601 (YYYY-MM-DD)
- Los identificadores (IDs) son enteros positivos
- Los estados de los pedidos y las órdenes de compra son strings enumerados