import sqlite3
import os

# Ruta del archivo de base de datos
db_file = 'simulador_produccion.db'

# Verificar si la base de datos ya existe
db_exists = os.path.exists(db_file)

# Conectar a la base de datos (la crea si no existe)
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Leer el script SQL desde un archivo (si lo tienes guardado)
with open('./src/crear_tablas.sql', 'r') as sql_file:
    sql_script = sql_file.read()
    
# O usar el script directamente como string
# sql_script = """CREATE TABLE IF NOT EXISTS Producto...."""

# Ejecutar el script SQL
cursor.executescript(sql_script)

# Confirmar cambios
conn.commit()

# Si es primera vez, insertar datos iniciales
if not db_exists:
    # Insertar datos de configuración inicial
    cursor.execute('''
        INSERT INTO ConfiguracionSimulacion 
        (fecha_actual, media_demanda, varianza_demanda, capacidad_almacen, capacidad_produccion_diaria) 
        VALUES (date('now'), 5, 2, 1000, 10)
    ''')
    
    # Insertar línea de producción inicial
    cursor.execute('''
        INSERT INTO LineaProduccion (nombre, capacidad_diaria, estado)
        VALUES ('Línea Principal', 10, 'activa')
    ''')
    
    # Añadir más datos iniciales según sea necesario...
    
    # Confirmar cambios
    conn.commit()

# Cerrar la conexión
conn.close()

print(f"Base de datos {db_file} creada o actualizada correctamente.")
