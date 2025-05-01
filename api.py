from fastapi import FastAPI, HTTPException
from entities import (
    Product, BOMItem, Supplier, InventoryItem, 
    ProductionOrder, PurchaseOrder, PurchaseOrderDetail
)
import sqlite3
from datetime import date, datetime
from typing import List

app = FastAPI(title="Sistema de Producción de Impresoras")

def get_db():
    conn = sqlite3.connect('simulador_produccion.db')
    conn.row_factory = sqlite3.Row
    return conn

# Endpoints para Productos
@app.post("/products/", response_model=Product)
async def create_product(product: Product):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO products (id, name, type) VALUES (?, ?, ?)",
            (product.id, product.name, product.type)
        )
        db.commit()
        return product
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Product ID already exists")
    finally:
        db.close()

@app.get("/products/", response_model=List[Product])
async def get_products():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        return [
            Product(
                id=row['id'],
                name=row['name'],
                type=row['type']
            ) for row in products
        ]
    finally:
        db.close()

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return Product(
            id=product['id'],
            name=product['name'],
            type=product['type']
        )
    finally:
        db.close()

@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, product: Product):
    if product_id != product.id:
        raise HTTPException(status_code=400, detail="Path ID does not match body ID")
    
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "UPDATE products SET name = ?, type = ? WHERE id = ?",
            (product.name, product.type, product_id)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        db.commit()
        return product
    finally:
        db.close()

# Endpoints para Órdenes de Producción
@app.post("/production-orders/", response_model=ProductionOrder)
async def create_production_order(order: ProductionOrder):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO production_orders 
            (id, created_date, product_id, quantity, status) 
            VALUES (?, ?, ?, ?, ?)
            """,
            (order.id, order.created_date, order.product_id, 
             order.quantity, order.status)
        )
        db.commit()
        return order
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Order ID already exists or invalid product ID")
    finally:
        db.close()

@app.get("/production-orders/", response_model=List[ProductionOrder])
async def get_production_orders():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM production_orders")
        orders = cursor.fetchall()
        return [
            ProductionOrder(
                id=row['id'],
                created_date=row['created_date'],
                product_id=row['product_id'],
                quantity=row['quantity'],
                status=row['status']
            ) for row in orders
        ]
    finally:
        db.close()

@app.get("/production-orders/{order_id}", response_model=ProductionOrder)
async def get_production_order(order_id: int):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM production_orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        if order is None:
            raise HTTPException(status_code=404, detail="Production order not found")
        return ProductionOrder(
            id=order['id'],
            created_date=order['created_date'],
            product_id=order['product_id'],
            quantity=order['quantity'],
            status=order['status']
        )
    finally:
        db.close()

@app.put("/production-orders/{order_id}", response_model=ProductionOrder)
async def update_production_order(order_id: int, order: ProductionOrder):
    if order_id != order.id:
        raise HTTPException(status_code=400, detail="Path ID does not match body ID")
    
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            UPDATE production_orders 
            SET created_date = ?, product_id = ?, quantity = ?, status = ?
            WHERE id = ?
            """,
            (order.created_date, order.product_id, order.quantity, 
             order.status, order_id)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Production order not found")
        db.commit()
        return order
    finally:
        db.close()

# Endpoints para Inventario
@app.get("/inventory/", response_model=List[InventoryItem])
async def get_inventory():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM inventory")
        items = cursor.fetchall()
        return [
            InventoryItem(
                product_id=row['product_id'],
                qty=row['qty']
            ) for row in items
        ]
    finally:
        db.close()

@app.get("/inventory/{product_id}", response_model=InventoryItem)
async def get_inventory_item(product_id: int):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM inventory WHERE product_id = ?", (product_id,))
        item = cursor.fetchone()
        if item is None:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        return InventoryItem(
            product_id=item['product_id'],
            qty=item['qty']
        )
    finally:
        db.close()

# Endpoints para Proveedores
@app.get("/suppliers/", response_model=List[Supplier])
async def get_suppliers():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM suppliers")
        suppliers = cursor.fetchall()
        return [
            Supplier(
                id=row['id'],
                product_id=row['product_id'],
                unit_cost=row['unit_cost'],
                lead_time=row['lead_time']
            ) for row in suppliers
        ]
    finally:
        db.close()

@app.get("/suppliers/{supplier_id}", response_model=Supplier)
async def get_supplier(supplier_id: int):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        supplier = cursor.fetchone()
        if supplier is None:
            raise HTTPException(status_code=404, detail="Supplier not found")
        return Supplier(
            id=supplier['id'],
            product_id=supplier['product_id'],
            unit_cost=supplier['unit_cost'],
            lead_time=supplier['lead_time']
        )
    finally:
        db.close() 