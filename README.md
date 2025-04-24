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

¡Listo! Ahora puedes empezar a trabajar en tu simulador 🚀


