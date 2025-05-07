import os
from pathlib import Path
from typing import Dict, Any
import json
from datetime import date

# Rutas base
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Crear directorio de datos si no existe
os.makedirs(DATA_DIR, exist_ok=True)

# Archivo de base de datos
DB_FILE = DATA_DIR / "simulator.db"

# Archivo de configuración de la simulación
CONFIG_FILE = DATA_DIR / "config.json"

# Configuración por defecto de la simulación
DEFAULT_CONFIG = {
    "initial_day": date.today().isoformat(),
    "demand_mean": 5.0,
    "demand_std_dev": 2.0,
    "production_capacity_per_day": 10,
    "warehouse_capacity": 1000
}

# Datos iniciales para la simulación
DEFAULT_PRODUCTS = [
    {"id": 1, "name": "P3D-Classic", "type": "finished"},
    {"id": 2, "name": "P3D-Pro", "type": "finished"},
    {"id": 3, "name": "kit_piezas", "type": "raw"},
    {"id": 4, "name": "pcb_CTRL-V2", "type": "raw"},
    {"id": 5, "name": "pcb_CTRL-V3", "type": "raw"},
    {"id": 6, "name": "extrusor", "type": "raw"},
    {"id": 7, "name": "sensor_autonivel", "type": "raw"},
    {"id": 8, "name": "cables_conexion", "type": "raw"},
    {"id": 9, "name": "transformador_24v", "type": "raw"},
    {"id": 10, "name": "enchufe_schuko", "type": "raw"}
]

DEFAULT_BOM = [
    # P3D-Classic (id: 1)
    {"finished_product_id": 1, "material_id": 3, "quantity": 1},  # kit_piezas
    {"finished_product_id": 1, "material_id": 4, "quantity": 1},  # pcb_CTRL-V2
    {"finished_product_id": 1, "material_id": 6, "quantity": 1},  # extrusor
    {"finished_product_id": 1, "material_id": 8, "quantity": 2},  # cables_conexion
    {"finished_product_id": 1, "material_id": 9, "quantity": 1},  # transformador_24v
    {"finished_product_id": 1, "material_id": 10, "quantity": 1}, # enchufe_schuko
    
    # P3D-Pro (id: 2)
    {"finished_product_id": 2, "material_id": 3, "quantity": 1},  # kit_piezas
    {"finished_product_id": 2, "material_id": 5, "quantity": 1},  # pcb_CTRL-V3
    {"finished_product_id": 2, "material_id": 6, "quantity": 1},  # extrusor
    {"finished_product_id": 2, "material_id": 7, "quantity": 1},  # sensor_autonivel
    {"finished_product_id": 2, "material_id": 8, "quantity": 3},  # cables_conexion
    {"finished_product_id": 2, "material_id": 9, "quantity": 1},  # transformador_24v
    {"finished_product_id": 2, "material_id": 10, "quantity": 1}  # enchufe_schuko
]

DEFAULT_SUPPLIERS = [
    {"id": 1, "name": "ElectroPlastic S.A.", "product_id": 3, "unit_cost": 90.0, "lead_time_days": 3},
    {"id": 2, "name": "PCB Factory", "product_id": 4, "unit_cost": 45.0, "lead_time_days": 5},
    {"id": 3, "name": "PCB Factory", "product_id": 5, "unit_cost": 65.0, "lead_time_days": 5},
    {"id": 4, "name": "ExtruTech", "product_id": 6, "unit_cost": 35.0, "lead_time_days": 2},
    {"id": 5, "name": "SensorTech", "product_id": 7, "unit_cost": 25.0, "lead_time_days": 4},
    {"id": 6, "name": "CableMaker", "product_id": 8, "unit_cost": 3.0, "lead_time_days": 1},
    {"id": 7, "name": "PowerSupply Inc", "product_id": 9, "unit_cost": 18.0, "lead_time_days": 3},
    {"id": 8, "name": "ConnectAll", "product_id": 10, "unit_cost": 2.0, "lead_time_days": 2},
    {"id": 9, "name": "Global Plastics", "product_id": 3, "unit_cost": 105.0, "lead_time_days": 2}
]

DEFAULT_STOCK = [
    {"product_id": 3, "quantity": 30},  # kit_piezas
    {"product_id": 4, "quantity": 25},  # pcb_CTRL-V2
    {"product_id": 5, "quantity": 15},  # pcb_CTRL-V3
    {"product_id": 6, "quantity": 40},  # extrusor
    {"product_id": 7, "quantity": 20},  # sensor_autonivel
    {"product_id": 8, "quantity": 100}, # cables_conexion
    {"product_id": 9, "quantity": 30},  # transformador_24v
    {"product_id": 10, "quantity": 50}  # enchufe_schuko
]

# Configuración de API y Streamlit
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))

# Guardar configuración
def save_config(config: Dict[str, Any]) -> None:
    """Guarda la configuración en un archivo JSON."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# Cargar configuración
def load_config() -> Dict[str, Any]:
    """Carga la configuración desde un archivo JSON."""
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)
