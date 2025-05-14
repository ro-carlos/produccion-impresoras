# Guía para Desarrolladores
## Simulador de Producción de Impresoras 3D

Esta guía proporciona la información necesaria para desarrolladores que deseen entender, ampliar o modificar el Simulador de Producción de Impresoras 3D. Se abordan aspectos técnicos, estructura del proyecto, convenciones de código y procedimientos para añadir nuevas funcionalidades.

## Índice

1. [Configuración del Entorno de Desarrollo](#1-configuración-del-entorno-de-desarrollo)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Convenciones de Código](#3-convenciones-de-código)
4. [Flujos de Trabajo del Desarrollo](#4-flujos-de-trabajo-del-desarrollo)
5. [Pruebas](#5-pruebas)
6. [Despliegue](#6-despliegue)
7. [Extensiones Comunes](#7-extensiones-comunes)
8. [Referencias](#8-referencias)

## 1. Configuración del Entorno de Desarrollo

### 1.1 Requisitos Previos

- **Python**: versión 3.11 o superior
- **Git**: para control de versiones
- **SQLite**: para la base de datos local
- **Docker** y **Docker Compose**: para desarrollo en contenedores (opcional)
- **Editor recomendado**: Visual Studio Code con extensiones para Python

### 1.2 Instalación del Entorno

#### 1.2.1 Configuración Local

1. Clone el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/mrp-dgsi.git
   cd mrp-dgsi
   ```

2. Cree y active un entorno virtual:
   ```bash
   python -m venv venv
   # En Windows
   venv\Scripts\activate
   # En macOS/Linux
   source venv/bin/activate
   ```

3. Instale las dependencias:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Dependencias de desarrollo
   ```

4. Inicialice la base de datos:
   ```bash
   python scripts/init_db.py
   ```

#### 1.2.2 Configuración con Docker

1. Clone el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/mrp-dgsi.git
   cd mrp-dgsi
   ```

2. Construya y ejecute los contenedores:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

3. Para acceder al contenedor de desarrollo:
   ```bash
   docker exec -it mrp-dgsi-dev bash
   ```

### 1.3 Configuración del IDE

Se recomienda configurar Visual Studio Code con las siguientes extensiones:
- Python (Microsoft)
- Pylance
- Python Test Explorer
- SQLite Viewer
- Docker
- Git Lens

#### settings.json recomendado:
```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.nosetestsEnabled": false,
    "python.testing.pytestArgs": [
        "tests"
    ]
}
```

## 2. Arquitectura del Sistema

### 2.1 Visión General

El sistema sigue una arquitectura hexagonal (también conocida como Ports & Adapters o Clean Architecture), que separa claramente el núcleo de la aplicación de sus interfaces externas.

![Diagrama de Arquitectura](https://via.placeholder.com/800x400)

### 2.2 Estructura de Carpetas

```
mrp-dgsi/
├── application/              # Capa de aplicación (casos de uso)
│   ├── __init__.py
│   ├── services.py           # Servicios de aplicación
│   └── simulation.py         # Lógica de simulación
├── config/                   # Configuración
│   ├── __init__.py
│   ├── di_container.py       # Contenedor de inyección de dependencias
│   └── settings.py           # Configuración del sistema
├── data/                     # Datos y configuración
│   ├── config.json           # Configuración en formato JSON
│   └── simulator.db          # Base de datos SQLite
├── domain/                   # Capa de dominio (entidades y reglas de negocio)
│   ├── __init__.py
│   ├── models.py             # Modelos y entidades de dominio
│   ├── repositories.py       # Interfaces de repositorio
│   └── services.py           # Servicios de dominio
├── docs/                     # Documentación
│   ├── api_documentation.md  # Documentación de la API
│   ├── architecture.md       # Documentación de la arquitectura
│   ├── database_schema.md    # Esquema de la base de datos
│   └── ...
├── infrastructure/           # Capa de infraestructura
│   ├── __init__.py
│   ├── data_export.py        # Exportación/importación de datos
│   ├── database.py           # Gestión de la base de datos
│   └── repositories.py       # Implementaciones concretas de repositorios
├── presentation/             # Capa de presentación
│   ├── __init__.py
│   ├── api.py                # API REST con FastAPI
│   └── streamlit_app.py      # Interfaz de usuario con Streamlit
├── scripts/                  # Scripts utilitarios
│   ├── export_import.py      # Script para exportar/importar datos
│   └── init_db.py            # Script para inicializar la base de datos
├── tests/                    # Tests automatizados
│   ├── __init__.py
│   ├── conftest.py           # Configuración de pytest
│   ├── unit/                 # Tests unitarios
│   └── integration/          # Tests de integración
├── .gitignore                # Archivos ignorados por Git
├── docker-compose.yml        # Configuración de Docker Compose para producción
├── docker-compose.dev.yml    # Configuración de Docker Compose para desarrollo
├── Dockerfile                # Definición de la imagen Docker
├── LICENSE                   # Licencia del proyecto
├── main.py                   # Punto de entrada principal
├── README.md                 # Descripción general del proyecto
└── requirements.txt          # Dependencias de Python
```

### 2.3 Capas de la Arquitectura

#### 2.3.1 Capa de Dominio

Es el núcleo de la aplicación y contiene:

- **Modelos**: Entidades de negocio como `Product`, `Supplier`, `ManufacturingOrder`, etc.
- **Repositorios**: Interfaces que definen cómo se accederá a los datos.
- **Servicios de Dominio**: Lógica de negocio que opera con las entidades.

```python
# Ejemplo de entidad en domain/models.py
from pydantic import BaseModel
from typing import Literal, Optional

class Product(BaseModel):
    id: Optional[int] = None
    name: str
    type: Literal["raw", "finished"]
```

#### 2.3.2 Capa de Aplicación

Coordina el flujo de datos entre el dominio y las interfaces externas:

- **Servicios de Aplicación**: Implementan los casos de uso.
- **Simulación**: Lógica específica de la simulación.

```python
# Ejemplo de servicio de aplicación en application/services.py
class InventoryService:
    def __init__(self, product_repository, stock_repository):
        self.product_repository = product_repository
        self.stock_repository = stock_repository
    
    def get_current_stock(self, product_type=None):
        """Obtiene el inventario actual, opcionalmente filtrado por tipo."""
        products = self.product_repository.get_all(product_type=product_type)
        stock_items = self.stock_repository.get_all()
        
        # Combina productos con su inventario
        result = []
        for product in products:
            stock_item = next((s for s in stock_items if s.product_id == product.id), None)
            quantity = stock_item.quantity if stock_item else 0
            result.append({
                "product_id": product.id,
                "product_name": product.name,
                "quantity": quantity,
                "type": product.type
            })
        
        return result
```

#### 2.3.3 Capa de Infraestructura

Proporciona implementaciones concretas para las interfaces definidas en el dominio:

- **Base de Datos**: Gestión de la conexión y operaciones con SQLite.
- **Repositorios**: Implementaciones concretas que utilizan SQLite.
- **Exportación/Importación**: Funcionalidades para guardar y cargar datos.

```python
# Ejemplo de implementación de repositorio en infrastructure/repositories.py
class SQLiteProductRepository(ProductRepository):
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def get_by_id(self, product_id):
        cursor = self.db_connection.cursor()
        cursor.execute(
            "SELECT id, name, type FROM products WHERE id = ?",
            (product_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        
        return Product(
            id=row[0],
            name=row[1],
            type=row[2]
        )
```

#### 2.3.4 Capa de Presentación

Proporciona interfaces para interactuar con el sistema:

- **API REST**: Implementada con FastAPI.
- **Interfaz de Usuario**: Implementada con Streamlit.

```python
# Ejemplo de endpoint en presentation/api.py
@app.get("/api/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    product_service = container.get_product_service()
    product = product_service.get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product
```

### 2.4 Flujo de Dependencias

El flujo de dependencias va desde las capas externas hacia el núcleo, no al revés:

```
Presentation → Application → Domain ← Infrastructure
```

La inversión de dependencias se logra mediante:
1. Interfaces definidas en la capa de dominio
2. Implementaciones en la capa de infraestructura
3. Inyección de dependencias gestionada por el contenedor DI

```python
# Ejemplo de inyección de dependencias en config/di_container.py
class DIContainer:
    def __init__(self):
        self.db_connection = None
        self.repositories = {}
        self.services = {}
    
    def initialize(self):
        # Configurar conexión a BD
        self.db_connection = create_db_connection()
        
        # Crear repositorios
        self.repositories["product"] = SQLiteProductRepository(self.db_connection)
        
        # Crear servicios
        self.services["inventory"] = InventoryService(
            self.repositories["product"],
            self.repositories["stock"]
        )
```

## 3. Convenciones de Código

### 3.1 Estilo de Código

El proyecto sigue PEP 8 y utiliza las siguientes herramientas para mantener la calidad del código:

- **Black**: Para formateo automático
- **Flake8**: Para linting
- **MyPy**: Para verificación de tipos
- **isort**: Para ordenar las importaciones

Configuración en `setup.cfg`:

```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,build,dist,venv

[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True

[isort]
profile = black
```

### 3.2 Documentación del Código

- Todas las clases, métodos y funciones deben tener docstrings en formato Google.
- Los módulos deben tener un docstring que explique su propósito.

```python
def check_availability(product_id: int, quantity: int) -> List[Dict]:
    """
    Verifica si hay suficientes materiales para producir una cantidad de un producto.
    
    Args:
        product_id: ID del producto a fabricar
        quantity: Cantidad a fabricar
        
    Returns:
        Lista de materiales faltantes, vacía si hay suficientes materiales
    """
    # Implementación...
```

### 3.3 Convenciones de Nombres

- **Clases**: CamelCase (ej. `ProductRepository`)
- **Funciones y métodos**: snake_case (ej. `get_by_id`)
- **Variables**: snake_case (ej. `product_id`)
- **Constantes**: UPPER_CASE (ej. `DEFAULT_CAPACITY`)
- **Módulos**: snake_case (ej. `data_export.py`)

### 3.4 Estructura de Commits

Los mensajes de commit deben seguir este formato:

```
<tipo>(<ámbito>): <descripción corta>

<cuerpo opcional>

<pie opcional>
```

Donde `<tipo>` puede ser:
- **feat**: Nueva funcionalidad
- **fix**: Corrección de bug
- **docs**: Cambios en documentación
- **style**: Cambios que no afectan al código (formato, espacios en blanco, etc.)
- **refactor**: Refactorización de código
- **test**: Adición o corrección de tests
- **chore**: Tareas rutinarias, cambios de configuración, etc.

Ejemplo:
```
feat(inventory): implementar verificación de disponibilidad

Añade función para verificar si hay suficientes materiales en inventario
para fabricar una cantidad específica de un producto.

Closes #42
```

## 4. Flujos de Trabajo del Desarrollo

### 4.1 Flujo de Trabajo de Git

El proyecto utiliza GitFlow como metodología:

- **main**: Rama principal, contiene código de producción
- **develop**: Rama de desarrollo, contiene código estable para la próxima versión
- **feature/<nombre>**: Ramas para nuevas funcionalidades
- **bugfix/<nombre>**: Ramas para corrección de bugs
- **release/<versión>**: Ramas para preparar una versión para producción
- **hotfix/<nombre>**: Ramas para correcciones urgentes en producción

#### 4.1.1 Desarrollo de Nueva Funcionalidad

1. Crear una rama desde `develop`:
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/nueva-funcionalidad
   ```

2. Desarrollar la funcionalidad con commits regulares.

3. Asegurarse de que los tests pasan:
   ```bash
   pytest
   ```

4. Enviar la rama al repositorio remoto:
   ```bash
   git push -u origin feature/nueva-funcionalidad
   ```

5. Crear un Pull Request a `develop`.

6. Después de la revisión y aprobación, hacer merge del PR.

### 4.2 Implementación de Nuevas Funcionalidades

Para añadir una nueva funcionalidad, siga estos pasos:

1. **Definir en el dominio**:
   - Añadir nuevos modelos o modificar existentes en `domain/models.py`
   - Si es necesario, añadir interfaces de repositorio en `domain/repositories.py`
   - Implementar lógica de dominio en `domain/services.py`

2. **Implementar en infraestructura**:
   - Añadir las tablas necesarias en la base de datos
   - Implementar los repositorios en `infrastructure/repositories.py`

3. **Añadir casos de uso**:
   - Implementar servicios en `application/services.py`
   - Integrar con la simulación en `application/simulation.py` si es necesario

4. **Exponer a través de interfaces**:
   - Añadir endpoints en la API (`presentation/api.py`)
   - Añadir componentes a la interfaz de usuario (`presentation/streamlit_app.py`)

5. **Actualizar la configuración**:
   - Registrar nuevos componentes en el contenedor DI (`config/di_container.py`)
   - Actualizar configuración si es necesario (`config/settings.py`)

6. **Añadir tests**:
   - Tests unitarios para la lógica de dominio y aplicación
   - Tests de integración para repositorios y API

### 4.3 Gestión de Dependencias

Para añadir nuevas dependencias:

1. Añadir a `requirements.txt` o `requirements-dev.txt` según corresponda
2. Actualizar el entorno virtual:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
3. Actualizar el Dockerfile si es necesario
4. Actualizar la documentación si la dependencia afecta a la configuración

### 4.4 Versionado

El proyecto sigue Semantic Versioning (SemVer):
- **MAJOR**: Cambios incompatibles con versiones anteriores
- **MINOR**: Nuevas funcionalidades compatibles con versiones anteriores
- **PATCH**: Correcciones de bugs compatibles con versiones anteriores

## 5. Pruebas

### 5.1 Estructura de Pruebas

El proyecto utiliza pytest como framework de testing:

```
tests/
├── conftest.py             # Configuración y fixtures compartidos
├── unit/                   # Tests unitarios
│   ├── domain/             # Tests de la capa de dominio
│   ├── application/        # Tests de la capa de aplicación
│   └── infrastructure/     # Tests de la capa de infraestructura
└── integration/            # Tests de integración
    ├── repositories/       # Tests de repositorios con BD real
    └── api/                # Tests de API
```

### 5.2 Tipos de Pruebas

#### 5.2.1 Pruebas Unitarias

Prueban componentes individuales de forma aislada, utilizando mocks o stubs para las dependencias:

```python
def test_check_availability():
    # Configurar mocks
    product_repo_mock = MagicMock()
    bom_repo_mock = MagicMock()
    stock_repo_mock = MagicMock()
    
    # Configurar valores de retorno para los mocks
    bom_repo_mock.get_bom_for_product.return_value = [
        BOM(finished_id=1, material_id=3, quantity=1),
        BOM(finished_id=1, material_id=4, quantity=1)
    ]
    stock_repo_mock.get_by_product_id.side_effect = [
        Stock(product_id=3, quantity=5),  # Suficiente stock
        Stock(product_id=4, quantity=0)   # Sin stock
    ]
    
    # Crear servicio con mocks
    service = InventoryService(product_repo_mock, bom_repo_mock, stock_repo_mock)
    
    # Ejecutar función a probar
    result = service.check_availability(1, 2)
    
    # Verificar resultado
    assert len(result) == 1
    assert result[0]["material_id"] == 4
    assert result[0]["missing"] == 2
```

#### 5.2.2 Pruebas de Integración

Prueban la interacción entre componentes, utilizando una base de datos de prueba:

```python
def test_product_repository_integration(test_db):
    # Crear repositorio con BD de prueba
    repo = SQLiteProductRepository(test_db)
    
    # Insertar datos de prueba
    test_db.execute(
        "INSERT INTO products (id, name, type) VALUES (1, 'Test Product', 'raw')"
    )
    test_db.commit()
    
    # Ejecutar función a probar
    product = repo.get_by_id(1)
    
    # Verificar resultado
    assert product is not None
    assert product.id == 1
    assert product.name == "Test Product"
    assert product.type == "raw"
```

#### 5.2.3 Pruebas de API

Prueban los endpoints de la API utilizando TestClient de FastAPI:

```python
def test_get_product_api(test_client):
    # Configurar datos de prueba
    # ...
    
    # Ejecutar solicitud
    response = test_client.get("/api/products/1")
    
    # Verificar respuesta
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Test Product"
```

### 5.3 Ejecución de Pruebas

Para ejecutar todas las pruebas:
```bash
pytest
```

Para ejecutar pruebas específicas:
```bash
pytest tests/unit/domain/  # Solo pruebas unitarias de dominio
pytest tests/integration/  # Solo pruebas de integración
pytest -k "inventory"      # Solo pruebas que contengan "inventory" en su nombre
```

Para generar un informe de cobertura:
```bash
pytest --cov=. --cov-report=html
```

## 6. Despliegue

### 6.1 Entornos

El proyecto está diseñado para funcionar en tres entornos:

- **Desarrollo**: Para trabajo local de los desarrolladores
- **Pruebas**: Para pruebas de QA y aceptación
- **Producción**: Para usuarios finales

### 6.2 Despliegue con Docker

#### 6.2.1 Construcción de la Imagen

```bash
docker build -t mrp-dgsi:latest .
```

#### 6.2.2 Despliegue con Docker Compose

```bash
docker-compose up -d
```

El archivo `docker-compose.yml` define los siguientes servicios:
- **app**: Servicio principal que ejecuta la aplicación
- **api**: Servicio que expone la API REST

### 6.3 Variables de Entorno

El sistema utiliza las siguientes variables de entorno para configuración:

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `DB_PATH` | Ruta a la base de datos SQLite | `./data/simulator.db` |
| `API_HOST` | Host para la API REST | `0.0.0.0` |
| `API_PORT` | Puerto para la API REST | `8000` |
| `UI_PORT` | Puerto para la interfaz de usuario | `8501` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |

Estas variables pueden ser definidas en un archivo `.env` o pasadas directamente al contenedor.

## 7. Extensiones Comunes

### 7.1 Añadir un Nuevo Tipo de Producto

1. No se requieren cambios en la estructura de la base de datos, solo insertar nuevos registros:
   ```sql
   INSERT INTO products (name, type) VALUES ('P3D-Ultimate', 'finished');
   ```

2. Definir la lista de materiales (BOM):
   ```sql
   INSERT INTO bom (finished_id, material_id, quantity) VALUES
   (3, 3, 1),  -- 1 kit_piezas
   (3, 5, 1),  -- 1 pcb_v3
   (3, 6, 2),  -- 2 extrusores (para impresión dual)
   (3, 7, 1),  -- 1 sensor_autonivel
   (3, 8, 4),  -- 4 cables_conexion
   (3, 9, 1),  -- 1 transformador_24v
   (3, 10, 1); -- 1 enchufe_schuko
   ```

3. Actualizar la interfaz de usuario si es necesario, pero el resto del sistema debería funcionar automáticamente.

### 7.2 Añadir un Nuevo Tipo de Evento

1. Identificar dónde se genera el evento en el código (usualmente en `application/services.py` o `application/simulation.py`)

2. Añadir la generación del evento:
   ```python
   def process_some_action(self, params):
       # Lógica de negocio...
       
       # Registrar evento
       event_details = {
           "action_id": action_id,
           "some_parameter": some_value,
           # Otros detalles relevantes
       }
       self.event_repository.create(
           type="new_action_type",
           event_date=current_date,
           details=json.dumps(event_details)
       )
   ```

3. Si es necesario, actualizar la interfaz para mostrar el nuevo tipo de evento.

### 7.3 Añadir una Nueva Métrica o Gráfica

1. Implementar la lógica para calcular la métrica en `application/services.py`:
   ```python
   def calculate_new_metric(self, date_from=None, date_to=None):
       # Lógica para calcular la métrica
       return metric_data
   ```

2. Añadir el endpoint en la API para acceder a la métrica:
   ```python
   @app.get("/api/metrics/new-metric")
   def get_new_metric(date_from: Optional[str] = None, date_to: Optional[str] = None):
       metric_service = container.get_metric_service()
       return metric_service.calculate_new_metric(date_from, date_to)
   ```

3. Añadir la visualización en la interfaz de usuario:
   ```python
   def show_new_metric_chart():
       st.header("Nueva Métrica")
       
       # Obtener datos
       response = requests.get(f"{API_URL}/metrics/new-metric")
       data = response.json()
       
       # Crear gráfico
       chart = alt.Chart(pd.DataFrame(data)).mark_line().encode(
           x='date:T',
           y='value:Q',
           tooltip=['date', 'value']
       ).properties(
           width=700,
           height=300,
           title="Evolución de la Nueva Métrica"
       )
       
       st.altair_chart(chart, use_container_width=True)
   ```

## 8. Referencias

### 8.1 Tecnologías Principales

- [Python 3.11](https://docs.python.org/3.11/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://docs.streamlit.io/)
- [SQLite](https://www.sqlite.org/docs.html)
- [SimPy](https://simpy.readthedocs.io/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Vega-Altair](https://altair-viz.github.io/)

### 8.2 Patrones de Diseño

- [Arquitectura Hexagonal](https://alistair.cockburn.us/hexagonal-architecture/)
- [Inyección de Dependencias](https://martinfowler.com/articles/injection.html)
- [Patrón Repositorio](https://martinfowler.com/eaaCatalog/repository.html)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)

### 8.3 Recursos Internos

- [PRD.md](../docs/PRD.md): Product Requirements Document
- [architecture.md](../docs/architecture.md): Documentación detallada de la arquitectura
- [api_documentation.md](../docs/api_documentation.md): Documentación de la API REST
- [database_schema.md](../docs/database_schema.md): Esquema de la base de datos

---

## Apéndice: Lista de Verificación para Pull Requests

- [ ] El código sigue las convenciones de estilo
- [ ] Se han añadido tests para las nuevas funcionalidades
- [ ] Todos los tests existentes pasan
- [ ] La documentación ha sido actualizada
- [ ] El código ha sido revisado por al menos un desarrollador
- [ ] Los cambios han sido probados en un entorno similar a producción