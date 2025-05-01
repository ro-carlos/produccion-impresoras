# produccion-impresoras

# 🧪 Configuración del entorno y ejecución del simulador

Este proyecto utiliza **Python 3.11+**, `streamlit` para la interfaz, `simpy` para la simulación, y `fastapi` para exponer la API. Aquí te mostramos cómo configurar el entorno y ejecutar la aplicación.

---

## ⚙️ 1. Requisitos previos

- Tener instalado **Python 3.11** o superior.
  - Verifica tu versión con:
    ```bash
    python3 --version
    ```

- Si no tienes Python 3.11, puedes descargarlo desde:  
  👉 [https://www.python.org/downloads/release/python-3110/](https://www.python.org/downloads/release/python-3110/)

---

## 🧰 2. Crear y activar entorno virtual

Desde la raíz del proyecto:

```bash
python3 -m venv venv
```

### Activar el entorno:

#### En macOS / Linux:
```bash
source venv/bin/activate
```

#### En Windows (CMD):
```cmd
venv\Scripts\activate
```

#### En Windows (PowerShell):
```powershell
venv\Scripts\Activate.ps1
```

---

## 📦 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

##    4. Modelo de datos

El modelo de datos del simulador se encuentra documentado en detalle en el archivo [docs/modelo_datos.md](docs/modelo_datos.md). Este documento describe todas las entidades, sus atributos y las relaciones entre ellas.

## Configuración de la base de datos

El simulador utiliza SQLite3 como sistema de gestión de base de datos. La creación y configuración de la base de datos se realiza a través del script `src/models.py`.

### Creación de la base de datos

Para crear la base de datos:

1. Asegúrate de tener instalada la biblioteca sqlite3 de Python
2. Ejecuta el script models.py:

```bash
python src/models.py
```
---

## 🚀 5. Ejecutar la aplicación

Lanza la aplicación con:

```bash
streamlit run src/ui.py
```

Esto abrirá automáticamente tu navegador en:  
[http://localhost:8501](http://localhost:8501)

---

## 💡 6. Configuración opcional de desarrollo

Puedes crear un archivo de configuración para que Streamlit recargue automáticamente al guardar:

```ini
# .streamlit/config.toml
[server]
runOnSave = true
headless = true
```

---

## 🌐 7. Ejecución del Servicio REST

El proyecto incluye una API REST construida con FastAPI que permite gestionar productos y órdenes de producción. Para ejecutar el servicio:


Inicia el servidor:
```bash
uvicorn main:app --reload
```

El servidor estará disponible en:
- API: http://localhost:8000
- Documentación interactiva: http://localhost:8000/docs
- Documentación alternativa: http://localhost:8000/redoc

### Endpoints disponibles

#### Productos
- `POST /products/`: Crear un nuevo producto
- `GET /products/`: Obtener todos los productos
- `PUT /products/{product_id}`: Actualizar un producto existente

#### Órdenes de Producción
- `POST /production-orders/`: Crear una nueva orden de producción
- `GET /production-orders/`: Obtener todas las órdenes de producción
- `PUT /production-orders/{order_id}`: Actualizar una orden de producción existente

### Ejemplos de uso

1. Crear un producto:
```bash
curl -X POST "http://localhost:8000/products/" \
     -H "Content-Type: application/json" \
     -d '{"id": 1, "name": "Impresora 3D Básica", "type": "finished"}'
```

2. Crear una orden de producción:
```bash
curl -X POST "http://localhost:8000/production-orders/" \
     -H "Content-Type: application/json" \
     -d '{"id": 1, "created_date": "2024-03-20", "product_id": 1, "quantity": 10, "status": "pending"}'
```

3. Actualizar una orden:
```bash
curl -X PUT "http://localhost:8000/production-orders/1" \
     -H "Content-Type: application/json" \
     -d '{"id": 1, "created_date": "2024-03-20", "product_id": 1, "quantity": 10, "status": "in_production"}'
```

---

¡Listo! Ahora puedes empezar a trabajar en tu simulador 🚀


