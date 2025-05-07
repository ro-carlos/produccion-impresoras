# Simulador de Producción de Impresoras 3D

Este proyecto implementa un simulador para modelar el ciclo completo de operación de una planta de fabricación de impresoras 3D, enfocándose en tres aspectos clave: gestión de inventarios, compras y planificación de la producción.

## Características

- Simulación día a día del proceso de producción
- Gestión de inventario de materias primas y productos terminados
- Gestión de órdenes de fabricación
- Compra de materiales a proveedores
- Interfaz gráfica intuitiva con Streamlit
- API REST completa para integración con otros sistemas
- Visualización de datos y análisis histórico

## Arquitectura

El sistema sigue una arquitectura de capas:

- **Dominio**: Modelos y lógica de negocio
- **Aplicación**: Coordinación de casos de uso y simulación
- **Infraestructura**: Persistencia de datos y servicios externos
- **Presentación**: API REST y interfaz de usuario

## Requisitos

- Python 3.11 o superior
- FastAPI y Uvicorn para la API REST
- Streamlit para la interfaz de usuario
- SimPy para el motor de simulación
- SQLite para la persistencia de datos
- Docker y Docker Compose (opcional, para despliegue)

## Instalación

### Instalación manual

1. Clone este repositorio:

   ```
   git clone <url-del-repositorio>
   cd 3d_printer_simulator
   ```

2. Cree un entorno virtual (opcional pero recomendado):

   ```
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instale las dependencias:
   ```
   pip install -r requirements.txt
   ```

### Instalación con Docker

1. Clone este repositorio:

   ```
   git clone <url-del-repositorio>
   cd 3d_printer_simulator
   ```

2. Construya y ejecute los contenedores:
   ```
   docker-compose up -d
   ```

## Uso

### Ejecución manual

Para iniciar la aplicación completa (API + Interfaz de usuario):

```
python main.py
```

Para iniciar solo el servidor API:

```
python main.py --api-only
```

Para iniciar solo la interfaz de usuario (requiere que el servidor API esté en ejecución):

```
python main.py --ui-only
```

### Acceso a la aplicación

- Interfaz de usuario: http://localhost:8501
- API REST: http://localhost:8000
- Documentación de la API: http://localhost:8000/docs

## Flujo de Simulación

1. El sistema comienza con un inventario inicial de materias primas.
2. Cada día, se generan nuevos pedidos de fabricación de manera aleatoria.
3. El usuario debe tomar decisiones sobre:
   - Qué pedidos liberar a producción, verificando disponibilidad de materiales.
   - Qué materiales comprar a los proveedores para mantener el inventario.
4. Al avanzar el día, se procesan las actividades en curso:
   - Se completan órdenes de fabricación iniciadas anteriormente.
   - Se reciben materiales de compras con fecha de entrega vencida.
   - Se generan nuevos pedidos para el siguiente día.

## Estructura del Proyecto

```
3d_printer_simulator/
├── application/        # Capa de aplicación
│   ├── services.py     # Servicios de aplicación
│   └── simulation.py   # Motor de simulación (SimPy)
├── config/             # Configuración
│   ├── di_container.py # Contenedor de inyección de dependencias
│   └── settings.py     # Configuración general
├── domain/             # Capa de dominio
│   ├── models.py       # Modelos de dominio
│   ├── repositories.py # Interfaces de repositorios
│   └── services.py     # Servicios de dominio
├── infrastructure/     # Capa de infraestructura
│   ├── database.py     # Acceso a base de datos SQLite
│   ├── data_export.py  # Importación/exportación de datos
│   └── repositories.py # Implementación de repositorios
├── presentation/       # Capa de presentación
│   ├── api.py          # API REST (FastAPI)
│   └── streamlit_app.py # Interfaz de usuario (Streamlit)
├── data/               # Datos persistentes
├── docker-compose.yml  # Configuración de Docker Compose
├── Dockerfile          # Definición de la imagen Docker
├── main.py             # Punto de entrada de la aplicación
└── requirements.txt    # Dependencias del proyecto
```

## Desarrollo

### Modelos de Impresoras 3D

El sistema simula la producción de dos modelos de impresoras:

1. **P3D-Classic**: Modelo base con componentes estándar.

   - 1 kit_piezas
   - 1 pcb (CTRL-V2)
   - 1 extrusor
   - 2 cables_conexion
   - 1 transformador_24v
   - 1 enchufe_schuko

2. **P3D-Pro**: Modelo avanzado con sensores adicionales.
   - 1 kit_piezas
   - 1 pcb (CTRL-V3)
   - 1 extrusor
   - 1 sensor_autonivel
   - 3 cables_conexion
   - 1 transformador_24v
   - 1 enchufe_schuko

### API REST

La API REST proporciona acceso completo a todas las funcionalidades del simulador:

- `GET /`: Información general del simulador
- `POST /simulation/advance-day`: Avanza un día en la simulación
- `GET /products`: Lista todos los productos
- `GET /products/{product_id}`: Obtiene detalles de un producto
- `GET /products/{product_id}/suppliers`: Obtiene proveedores para un producto
- `GET /inventory`: Obtiene el inventario actual
- `GET /orders/manufacturing`: Obtiene órdenes de fabricación
- `POST /orders/manufacturing/{order_id}/release`: Libera una orden a producción
- `POST /orders/purchase`: Crea una nueva orden de compra
- `GET /events`: Obtiene el historial de eventos

La documentación completa de la API está disponible en formato SWAGGER/OpenAPI en `http://localhost:8000/docs`.

## Licencia

[MIT License](LICENSE)
