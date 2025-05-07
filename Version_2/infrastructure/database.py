import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import os
import json

class Database:
    """Clase para manejar conexiones a la base de datos SQLite."""
    
    def __init__(self, db_path: str = ":memory:"):
        """
        Inicializa la conexión a la base de datos.
        
        Args:
            db_path: Ruta al archivo de base de datos, por defecto usa una BD en memoria
        """
        self.db_path = db_path
        self.connection = None
        
    def connect(self) -> None:
        """Establece la conexión a la base de datos."""
        self.connection = sqlite3.connect(self.db_path)
        # Configurar para que las filas se devuelvan como diccionarios
        self.connection.row_factory = sqlite3.Row
    
    def disconnect(self) -> None:
        """Cierra la conexión a la base de datos."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        """
        Ejecuta una consulta SQL sin retornar resultados.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
            
        Returns:
            Cursor de SQLite
        """
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor
    
    def execute_and_fetchall(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SQL y retorna todos los resultados.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
            
        Returns:
            Lista de diccionarios con los resultados
        """
        cursor = self.execute(query, params)
        results = cursor.fetchall()
        # Convertir los objetos Row a diccionarios
        return [dict(row) for row in results]
    
    def execute_and_fetchone(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """
        Ejecuta una consulta SQL y retorna un resultado.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
            
        Returns:
            Diccionario con el resultado o None si no hay resultados
        """
        cursor = self.execute(query, params)
        result = cursor.fetchone()
        return dict(result) if result else None
    
    def initialize_db(self) -> None:
        """
        Inicializa la base de datos creando todas las tablas necesarias.
        """
        self.create_tables()
    
    def create_tables(self) -> None:
        """
        Crea todas las tablas necesarias para el simulador.
        """
        # Tabla de productos
        self.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('raw', 'finished'))
        )
        ''')
        
        # Tabla de Bill of Materials (BOM)
        self.execute('''
        CREATE TABLE IF NOT EXISTS bom (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            finished_product_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (finished_product_id) REFERENCES products (id),
            FOREIGN KEY (material_id) REFERENCES products (id)
        )
        ''')
        
        # Tabla de proveedores
        self.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            unit_cost REAL NOT NULL,
            lead_time_days INTEGER NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        # Tabla de inventario actual
        self.execute('''
        CREATE TABLE IF NOT EXISTS stock_current (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL UNIQUE,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        # Tabla de órdenes de fabricación
        self.execute('''
        CREATE TABLE IF NOT EXISTS manufacturing_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creation_date TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        # Tabla de órdenes de compra
        self.execute('''
        CREATE TABLE IF NOT EXISTS purchase_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            issue_date TEXT NOT NULL,
            estimated_delivery_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        # Tabla de eventos
        self.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            event_date TEXT NOT NULL,
            details TEXT NOT NULL
        )
        ''')
        
        # Tabla de configuración de simulación
        self.execute('''
        CREATE TABLE IF NOT EXISTS simulation_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            current_day TEXT NOT NULL,
            demand_mean REAL NOT NULL,
            demand_std_dev REAL NOT NULL,
            production_capacity_per_day INTEGER NOT NULL,
            warehouse_capacity INTEGER NOT NULL
        )
        ''')
