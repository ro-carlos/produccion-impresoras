# Arquitectura del Sistema MRP-DGSI
## Simulador de Producción de Impresoras 3D

## 1. Visión General de la Arquitectura

El sistema MRP-DGSI está diseñado siguiendo los principios de la **Arquitectura Hexagonal** (también conocida como Arquitectura de Puertos y Adaptadores o Clean Architecture). Esta arquitectura permite separar claramente las preocupaciones de negocio de los detalles técnicos, facilitando el mantenimiento, la escalabilidad y el testing del sistema.

## 2. Capas de la Arquitectura

La aplicación está organizada en las siguientes capas:

```
                    +------------------+
                    |   Presentation   |
                    +------------------+
                            |
                            v
                    +------------------+
                    |   Application    |
                    +------------------+
                            |
                            v
                    +------------------+
                    |     Domain       |
                    +------------------+
                            |
                            v
                    +------------------+
                    | Infrastructure   |
                    +------------------+
```

### 2.1 Capa de Dominio (Domain)

La capa de dominio es el núcleo de la aplicación y contiene:

- **Modelos**: Entidades principales del negocio, como `Product`, `Supplier`, `ManufacturingOrder`, `PurchaseOrder`, etc.
- **Repositorios**: Interfaces que definen cómo se accede a los datos del dominio.
- **Servicios de Dominio**: Lógica de negocio compleja que opera sobre múltiples entidades.

Esta capa está completamente aislada de los detalles técnicos y no tiene dependencias externas, lo que la hace altamente testeable.

### 2.2 Capa de Aplicación (Application)

La capa de aplicación coordina el flujo de datos entre las interfaces externas y el dominio:

- **Servicios de Aplicación**: Orquestan los casos de uso implementando la lógica de la aplicación.
- **Simulación**: Contiene la lógica de simulación basada en SimPy que ejecuta el ciclo de producción.

Esta capa depende de la capa de dominio pero no conoce los detalles de implementación de las interfaces externas.

### 2.3 Capa de Infraestructura (Infrastructure)

La capa de infraestructura proporciona implementaciones concretas para las interfaces definidas en el dominio:

- **Base de Datos**: Implementación concreta de los repositorios utilizando SQLite.
- **Exportación/Importación de Datos**: Funcionalidades para importar y exportar datos del sistema.

### 2.4 Capa de Presentación (Presentation)

La capa de presentación contiene las interfaces de usuario y las APIs:

- **API REST**: Implementada con FastAPI para proporcionar acceso a todas las funcionalidades del sistema.
- **Interfaz de Usuario**: Implementada con Streamlit para proporcionar una interfaz gráfica intuitiva.

## 3. Flujo de Dependencias

La arquitectura sigue la **Regla de Dependencia**: las dependencias de código solo pueden apuntar hacia adentro. Una capa externa puede depender de una capa interna, pero nunca al revés.

```
Infrastructure → Application → Domain
Presentation → Application → Domain
```

## 4. Principios de Diseño

### 4.1 Inversión de Dependencias (DIP)

Las capas externas dependen de abstracciones (interfaces) definidas en las capas internas, no de implementaciones concretas. Esto se logra mediante:

- Definición de interfaces de repositorio en la capa de dominio
- Implementación de estas interfaces en la capa de infraestructura
- Inyección de dependencias con el contenedor DI en `config/di_container.py`

### 4.2 Principio de Responsabilidad Única (SRP)

Cada clase tiene una única responsabilidad y razón para cambiar. Por ejemplo:

- Los modelos de dominio solo contienen la estructura y comportamiento de las entidades
- Los repositorios solo se preocupan por el acceso a datos
- Los servicios de aplicación solo orquestan los casos de uso

### 4.3 Principio de Segregación de Interfaces (ISP)

Las interfaces son específicas para cada tipo de cliente, evitando que los clientes dependan de métodos que no utilizan.

## 5. Comunicación entre Capas

### 5.1 Dominio → Aplicación → Presentación

- La capa de aplicación utiliza repositorios y servicios del dominio para implementar casos de uso
- La capa de presentación utiliza servicios de la capa de aplicación para atender las solicitudes del usuario

### 5.2 Infraestructura → Dominio

- La infraestructura implementa las interfaces de repositorio definidas en el dominio
- La infraestructura proporciona implementaciones concretas para servicios abstractos definidos en el dominio

## 6. Patrones Utilizados

### 6.1 Patrón Repositorio

Proporciona una abstracción de la capa de persistencia, permitiendo que el dominio opere con objetos de dominio sin conocer los detalles de almacenamiento.

```python
# Interfaces en domain/repositories.py
class ProductRepository(ABC):
    @abstractmethod
    def get_by_id(self, product_id: int) -> Product:
        pass
    
    @abstractmethod
    def get_all(self) -> List[Product]:
        pass
    
    # ...

# Implementaciones en infrastructure/repositories.py
class SQLiteProductRepository(ProductRepository):
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def get_by_id(self, product_id: int) -> Product:
        # Implementación concreta usando SQLite
        pass
```

### 6.2 Patrón Inyección de Dependencias

Se utiliza un contenedor DI para inyectar las dependencias concretas en tiempo de ejecución:

```python
# En config/di_container.py
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
        self.services["inventory"] = InventoryService(self.repositories["product"])
```

### 6.3 Patrón Factory

Utilizado para la creación de objetos complejos, especialmente para instanciar componentes del sistema de simulación.

### 6.4 Patrón Observer

Utilizado en el sistema de simulación para notificar eventos a diferentes componentes.

## 7. Gestión de Eventos

El sistema utiliza un enfoque basado en eventos para la simulación:

1. Los eventos son generados por la simulación (creación de pedidos, finalización de producción, etc.)
2. Estos eventos son registrados en la tabla `Events`
3. Los componentes interesados pueden reaccionar a estos eventos para actualizar su estado

## 8. Diagramas de Arquitectura

### 8.1 Diagrama de Componentes

```
+---------------------+     +---------------------+
|    Presentation     |     |     Presentation    |
|                     |     |                     |
|  +---------------+  |     |  +---------------+  |
|  |   Streamlit   |  |     |  |    FastAPI    |  |
|  |      UI       |  |     |  |      API      |  |
|  +---------------+  |     |  +---------------+  |
+---------|-----------+     +---------|-----------+
          |                           |
          v                           v
+---------------------+     +---------------------+
|    Application      |     |    Application      |
|                     |     |                     |
|  +---------------+  |     |  +---------------+  |
|  |   Services    |  |     |  |  Simulation   |  |
|  +---------------+  |     |  +---------------+  |
+---------|-----------+     +---------|-----------+
          |                           |
          v                           v
+--------------------------------------------------+
|                     Domain                       |
|                                                  |
|  +---------------+    +---------------+          |
|  |    Models     |    |  Repositories |          |
|  +---------------+    +---------------+          |
|                                                  |
|  +---------------+    +---------------+          |
|  |   Services    |    |  Interfaces   |          |
|  +---------------+    +---------------+          |
+--------------------------------------------------+
                    |
                    v
+--------------------------------------------------+
|                 Infrastructure                    |
|                                                  |
|  +---------------+    +---------------+          |
|  |    SQLite     |    |  Data Export  |          |
|  |   Database    |    |  & Import     |          |
|  +---------------+    +---------------+          |
|                                                  |
|  +---------------+                               |
|  | Repository    |                               |
|  | Implementations|                              |
|  +---------------+                               |
+--------------------------------------------------+
```

## 9. Consideraciones de Extensibilidad

La arquitectura está diseñada para ser fácilmente extensible:

1. **Nuevos tipos de productos**: Solo requiere agregar nuevos registros en la base de datos.
2. **Nuevos proveedores**: Se pueden añadir sin cambiar el código existente.
3. **Algoritmos alternativos de simulación**: Pueden ser implementados como nuevos servicios en la capa de aplicación.
4. **Interfaces de usuario alternativas**: Pueden interactuar con el sistema a través de la capa de aplicación sin afectar la lógica de negocio.

## 10. Conclusiones

La arquitectura hexagonal implementada en el sistema MRP-DGSI proporciona:

- **Separación de preocupaciones**: Cada capa tiene responsabilidades claramente definidas.
- **Testabilidad**: Las capas internas pueden ser probadas de forma aislada.
- **Flexibilidad**: Las implementaciones concretas pueden ser reemplazadas sin afectar al núcleo de la aplicación.
- **Mantenibilidad**: El código es más fácil de entender y modificar.
- **Escalabilidad**: El sistema puede crecer y evolucionar sin comprometer su diseño general.