# Documento de Decisiones Arquitectónicas (ADR)
## Simulador de Producción de Impresoras 3D

Este documento registra las decisiones arquitectónicas significativas tomadas durante el desarrollo del Simulador de Producción de Impresoras 3D. Cada decisión se presenta en un formato estructurado, indicando el contexto, las alternativas consideradas, la decisión adoptada y sus consecuencias.

## Índice de Decisiones

1. [ADR-001: Adopción de Arquitectura Hexagonal](#adr-001-adopción-de-arquitectura-hexagonal)
2. [ADR-002: Selección de SimPy como Motor de Simulación](#adr-002-selección-de-simpy-como-motor-de-simulación)
3. [ADR-003: Uso de SQLite como Sistema de Almacenamiento](#adr-003-uso-de-sqlite-como-sistema-de-almacenamiento)
4. [ADR-004: Interfaz de Usuario con Streamlit](#adr-004-interfaz-de-usuario-con-streamlit)
5. [ADR-005: API REST con FastAPI](#adr-005-api-rest-con-fastapi)
6. [ADR-006: Modelo de Datos con Pydantic](#adr-006-modelo-de-datos-con-pydantic)
7. [ADR-007: Inyección de Dependencias](#adr-007-inyección-de-dependencias)
8. [ADR-008: Contenerización con Docker](#adr-008-contenerización-con-docker)
9. [ADR-009: Estrategia de Pruebas](#adr-009-estrategia-de-pruebas)
10. [ADR-010: Granularidad de Simulación](#adr-010-granularidad-de-simulación)

---

## ADR-001: Adopción de Arquitectura Hexagonal

### Fecha: 2024-01-15

### Estado: Aceptada

### Contexto

El Simulador de Producción de Impresoras 3D requiere una arquitectura que:
- Separe claramente la lógica de negocio de los detalles técnicos
- Facilite las pruebas automatizadas
- Permita cambiar implementaciones técnicas sin afectar el núcleo de la aplicación
- Sea mantenible y extensible a largo plazo

### Alternativas Consideradas

1. **Arquitectura en Capas Tradicional**: Separación en capas (presentación, negocio, datos) con dependencias directas entre ellas.
2. **Arquitectura Hexagonal (Ports & Adapters)**: Núcleo de la aplicación independiente, con puertos definidos para interactuar con el exterior y adaptadores para implementaciones concretas.
3. **Arquitectura Basada en Microservicios**: División en servicios independientes por responsabilidad.
4. **Arquitectura Monolítica Simple**: Sin separación explícita, todo integrado en un único bloque.

### Decisión

Adoptamos la **Arquitectura Hexagonal (Ports & Adapters)** por su capacidad para aislar la lógica de negocio y facilitar las pruebas unitarias.

### Justificación

La Arquitectura Hexagonal ofrece ventajas significativas para este proyecto:

1. **Separación clara de responsabilidades**: El dominio (núcleo de negocio) queda aislado de los detalles de presentación y persistencia.
2. **Testabilidad mejorada**: Al depender de abstracciones, es más fácil realizar pruebas unitarias con mocks o stubs.
3. **Flexibilidad para cambios técnicos**: Podemos cambiar la base de datos, la interfaz de usuario o la API sin afectar la lógica de negocio.
4. **Desarrollo independiente**: Diferentes equipos pueden trabajar en distintas capas sin interferir entre sí.
5. **Mantenibilidad a largo plazo**: La estructura clara facilita entender y modificar el código.

La arquitectura de microservicios se descartó por ser excesivamente compleja para el alcance actual, mientras que la arquitectura monolítica simple no ofrecía la separación necesaria para facilitar el mantenimiento y las pruebas.

### Consecuencias

**Positivas:**
- Mayor testabilidad de la lógica de dominio
- Capacidad para evolucionar técnicamente sin afectar el núcleo
- Código más mantenible y comprensible

**Negativas:**
- Mayor complejidad inicial y overhead de código
- Curva de aprendizaje para desarrolladores no familiarizados con el patrón
- Necesidad de crear y mantener interfaces adicionales

### Implementación

La arquitectura se implementa con las siguientes capas:

1. **Domain**: Contiene entidades, interfaces de repositorio y servicios de dominio.
2. **Application**: Coordina flujos de uso y orquesta servicios de dominio.
3. **Infrastructure**: Proporciona implementaciones concretas para los repositorios y servicios externos.
4. **Presentation**: Contiene la API REST y la interfaz de usuario.

---

## ADR-002: Selección de SimPy como Motor de Simulación

### Fecha: 2024-01-20

### Estado: Aceptada

### Contexto

El simulador requiere un motor de simulación de eventos discretos para modelar el proceso de producción, gestión de inventario y compras a lo largo del tiempo.

### Alternativas Consideradas

1. **SimPy**: Biblioteca de simulación de eventos discretos basada en procesos para Python.
2. **Implementación personalizada**: Desarrollo de un sistema propio de simulación de eventos.
3. **Salabim**: Alternativa a SimPy con enfoque en animación y visualización.
4. **AnyLogic**: Plataforma comercial de simulación multi-método.

### Decisión

Seleccionamos **SimPy** como motor de simulación para el proyecto.

### Justificación

SimPy ofrece varias ventajas que lo hacen adecuado para este proyecto:

1. **Biblioteca específica para Python**: Se integra naturalmente con el resto del stack tecnológico.
2. **Basado en generadores de Python**: Aprovecha características nativas del lenguaje para representar procesos.
3. **Maduro y bien documentado**: Existe desde 2002 y tiene documentación completa.
4. **Open source y activamente mantenido**: Bajo licencia MIT, con una comunidad activa.
5. **Ligero y sin dependencias externas**: Fácil de integrar y desplegar.
6. **Orientado a procesos**: Facilita modelar flujos de trabajo complejos.
7. **Soporte para recursos compartidos**: Ideal para modelar restricciones como la capacidad de producción.

Las alternativas se descartaron por las siguientes razones:
- La implementación personalizada requeriría un esfuerzo significativo sin ofrecer beneficios claros.
- Salabim está más orientado a visualización, cuando nuestro enfoque es el modelado de procesos.
- AnyLogic es una solución comercial compleja, excesiva para nuestras necesidades.

### Consecuencias

**Positivas:**
- Rápida implementación del motor de simulación
- Código más legible para representar procesos
- Facilidad para modelar restricciones de recursos

**Negativas:**
- Curva de aprendizaje para desarrolladores no familiarizados con SimPy
- Limitaciones en la paralelización real (SimPy simula paralelismo)
- Posibles limitaciones de rendimiento con simulaciones muy grandes

### Implementación

SimPy se integra en el sistema a través de la clase `ProductionSimulator` en el módulo `application/simulation.py`. Los procesos de producción, generación de pedidos y recepción de materiales se modelan como generadores de Python que interactúan con el entorno de simulación.

---

## ADR-003: Uso de SQLite como Sistema de Almacenamiento

### Fecha: 2024-01-25

### Estado: Aceptada

### Contexto

El simulador necesita persistir y recuperar datos como productos, pedidos, inventario y eventos. Se requiere un sistema de almacenamiento que sea:
- Fácil de configurar y usar
- Portable
- Adecuado para la escala esperada
- Compatible con despliegues en contenedores

### Alternativas Consideradas

1. **SQLite**: Base de datos relacional ligera basada en archivos.
2. **PostgreSQL**: Sistema de gestión de bases de datos relacional completo.
3. **MongoDB**: Base de datos NoSQL orientada a documentos.
4. **Almacenamiento en memoria con persistencia en archivos JSON**: Sin base de datos formal.

### Decisión

Seleccionamos **SQLite** como sistema de almacenamiento para el proyecto.

### Justificación

SQLite ofrece un equilibrio adecuado entre facilidad de uso y funcionalidad:

1. **Sin servidor separado**: Se ejecuta como parte de la aplicación, sin necesidad de un proceso separado.
2. **Cero configuración**: No requiere instalación ni configuración complejas.
3. **Portable**: Toda la base de datos está contenida en un único archivo.
4. **Transacciones ACID**: Garantiza la integridad de los datos.
5. **Rendimiento suficiente**: Para la escala esperada (cientos o miles de registros), SQLite ofrece un rendimiento adecuado.
6. **Soporte nativo en Python**: A través del módulo `sqlite3` de la biblioteca estándar.
7. **Facilita distribución**: Al ser un archivo, es fácil de compartir o respaldar.

Las alternativas se descartaron por las siguientes razones:
- PostgreSQL requiere un servidor separado, complicando el despliegue.
- MongoDB añade complejidad sin beneficios claros para este caso de uso.
- El almacenamiento en memoria con persistencia manual no garantizaría la integridad de datos y requeriría más desarrollo.

### Consecuencias

**Positivas:**
- Despliegue simple y sin dependencias externas
- Facilidad para hacer copias de seguridad (solo se copia un archivo)
- Cero configuración para los usuarios finales
- Transacciones que garantizan la integridad de datos

**Negativas:**
- Limitaciones de concurrencia (un solo escritor a la vez)
- No adecuado para múltiples instancias distribuidas
- Limitaciones de rendimiento para volúmenes de datos muy grandes
- Menos características avanzadas que sistemas como PostgreSQL

### Implementación

SQLite se implementa a través de la clase `DatabaseManager` en el módulo `infrastructure/database.py`. Los repositorios concretos en `infrastructure/repositories.py` utilizan esta clase para realizar operaciones CRUD.

---

## ADR-004: Interfaz de Usuario con Streamlit

### Fecha: 2024-02-01

### Estado: Aceptada

### Contexto

El simulador requiere una interfaz de usuario que:
- Sea intuitiva y fácil de usar
- Permita visualizar datos en tiempo real
- Facilite la interacción con la simulación
- Se pueda desarrollar rápidamente
- Sea accesible desde un navegador web

### Alternativas Consideradas

1. **Streamlit**: Framework de Python para crear aplicaciones web interactivas con mínimo código.
2. **Flask+Bootstrap+JavaScript**: Stack web tradicional.
3. **Django**: Framework web completo.
4. **React+FastAPI**: Frontend en React con backend en FastAPI.
5. **Dash**: Framework para aplicaciones analíticas web.

### Decisión

Seleccionamos **Streamlit** como framework para la interfaz de usuario.

### Justificación

Streamlit ofrece ventajas significativas para este proyecto:

1. **Desarrollo rápido**: Permite crear interfaces interactivas con pocas líneas de código Python.
2. **Sin necesidad de HTML/CSS/JavaScript**: No requiere conocimientos de desarrollo frontend tradicional.
3. **Integración nativa con bibliotecas de visualización**: Funciona bien con Pandas, Altair, Plotly, etc.
4. **Actualizaciones en tiempo real**: Facilita mostrar datos actualizados automáticamente.
5. **Componentes interactivos integrados**: Botones, selectores, formularios ya disponibles.
6. **Orientado a datos**: Perfecto para mostrar tablas, gráficos y métricas.
7. **Despliegue sencillo**: Se puede ejecutar como un servicio web simple.

Las alternativas se descartaron por las siguientes razones:
- Flask o Django requerirían más código y tiempo para lograr resultados similares.
- React+FastAPI introduciría la complejidad de mantener un stack dividido.
- Dash está más orientado a dashboards analíticos que a interfaces interactivas.

### Consecuencias

**Positivas:**
- Desarrollo mucho más rápido de la interfaz
- Cambios visuales fáciles de implementar
- Coherencia de lenguaje (todo en Python)
- Experiencia de usuario moderna e interactiva

**Negativas:**
- Menor flexibilidad para diseños muy personalizados
- Posible sobrecarga de rendimiento en el servidor
- Limitaciones para interfaces muy complejas
- Menos control sobre el ciclo de vida de la aplicación web

### Implementación

Streamlit se implementa en el módulo `presentation/streamlit_app.py`. La interfaz se organiza en secciones (pedidos, inventario, compras, producción) y utiliza Altair para visualizaciones gráficas.

---

## ADR-005: API REST con FastAPI

### Fecha: 2024-02-05

### Estado: Aceptada

### Contexto

El simulador debe exponer sus funcionalidades a través de una API REST para:
- Permitir integración con otros sistemas
- Facilitar el desarrollo de interfaces alternativas
- Separar la lógica de negocio de la presentación
- Proporcionar una interfaz programática completa

### Alternativas Consideradas

1. **FastAPI**: Framework web moderno, rápido y orientado a APIs.
2. **Flask**: Microframework web ligero.
3. **Django REST Framework**: Extensión de Django para APIs.
4. **Falcon**: Framework minimalista para APIs.

### Decisión

Seleccionamos **FastAPI** como framework para la implementación de la API REST.

### Justificación

FastAPI ofrece características que lo hacen ideal para este proyecto:

1. **Validación automática de datos**: Mediante integración con Pydantic.
2. **Generación automática de documentación**: OpenAPI/Swagger y ReDoc.
3. **Rendimiento elevado**: Gracias a Starlette y Pydantic.
4. **Tipado estático**: Aprovecha las anotaciones de tipo de Python.
5. **Async/await nativo**: Soporte para operaciones asíncronas.
6. **Inyección de dependencias integrada**: Facilita la arquitectura limpia.
7. **Curva de aprendizaje suave**: API declarativa e intuitiva.

Las alternativas se descartaron por las siguientes razones:
- Flask requeriría bibliotecas adicionales para validación y documentación.
- Django REST Framework introduce demasiada complejidad para este proyecto.
- Falcon, aunque eficiente, carece de funcionalidades como validación integrada.

### Consecuencias

**Positivas:**
- Documentación interactiva automática (Swagger/ReDoc)
- Validación robusta de entradas y salidas
- Código más seguro gracias al tipado estático
- Mejor rendimiento frente a otras alternativas

**Negativas:**
- Requiere Python 3.6+ (no un problema real para este proyecto)
- Menor cantidad de extensiones/plugins que Flask o Django
- Posible sobrecarga para APIs muy simples

### Implementación

FastAPI se implementa en el módulo `presentation/api.py`. La API se organiza en rutas para productos, inventario, pedidos, proveedores, compras y simulación. Se integra con Pydantic para validación de datos y generación de documentación OpenAPI.

---

## ADR-006: Modelo de Datos con Pydantic

### Fecha: 2024-02-10

### Estado: Aceptada

### Contexto

El simulador necesita un sistema para:
- Definir modelos de datos con validación
- Convertir entre diferentes representaciones (DB, API, lógica interna)
- Documentar la estructura de datos
- Garantizar la integridad de los datos

### Alternativas Consideradas

1. **Pydantic**: Biblioteca para validación de datos con anotaciones de tipo.
2. **Dataclasses**: Integradas en Python 3.7+.
3. **SQLAlchemy ORM**: Mapeo objeto-relacional completo.
4. **Clases simples + validación manual**: Enfoque minimalista.

### Decisión

Seleccionamos **Pydantic** como base para nuestros modelos de datos.

### Justificación

Pydantic ofrece características importantes para el proyecto:

1. **Validación automática**: Aplicación automática de tipos y restricciones.
2. **Conversión de tipos**: Manejo inteligente de conversiones (str→int, etc.).
3. **Generación de schemas JSON**: Integración perfecta con OpenAPI/FastAPI.
4. **Serialización/deserialización**: Conversión fácil entre dict, JSON, etc.
5. **Extensible**: Permite validadores personalizados y campos computados.
6. **Rendimiento**: Implementación eficiente en Rust (con pydantic v2).
7. **Inmutabilidad opcional**: Soporte para modelos inmutables.

Las alternativas se descartaron por las siguientes razones:
- Dataclasses no ofrecen validación integrada.
- SQLAlchemy mezcla preocupaciones de persistencia con definición de modelos.
- La validación manual es propensa a errores y verbosa.

### Consecuencias

**Positivas:**
- Modelos más seguros y autodocumentados
- Menor código para validación y conversión
- Integración perfecta con FastAPI
- Representación clara de la estructura de datos

**Negativas:**
- Dependencia adicional en el proyecto
- Posible sobrecarga para modelos muy simples
- Separación de modelos de API y modelos de dominio

### Implementación

Los modelos Pydantic se definen en el módulo `domain/models.py`. Estos modelos se utilizan tanto en la capa de dominio para representar entidades de negocio como en la API para validación de entrada/salida.

---

## ADR-007: Inyección de Dependencias

### Fecha: 2024-02-15

### Estado: Aceptada

### Contexto

La arquitectura hexagonal requiere un mecanismo para:
- Conectar las implementaciones concretas con las interfaces
- Gestionar el ciclo de vida de los componentes
- Facilitar la prueba unitaria mediante la sustitución de dependencias
- Mantener la inversión de dependencias

### Alternativas Consideradas

1. **Contenedor DI personalizado**: Implementación propia de un contenedor simple.
2. **Dependency Injector**: Biblioteca completa de inyección de dependencias.
3. **FastAPI Depends**: Sistema de dependencias integrado en FastAPI.
4. **Construcción manual de objetos**: Sin contenedor centralizado.

### Decisión

Implementamos un **Contenedor DI personalizado** para gestionar las dependencias.

### Justificación

Un contenedor personalizado ofrece varias ventajas:

1. **Simplicidad**: Implementación sencilla adaptada a nuestras necesidades exactas.
2. **Control total**: Podemos definir exactamente cómo se crean y gestionan los componentes.
3. **Sin dependencias adicionales**: No requiere bibliotecas externas.
4. **Integración perfecta**: Se adapta exactamente a nuestra arquitectura.
5. **Fácil de entender**: Todo el equipo puede comprender cómo funciona.
6. **Testabilidad**: Facilita la sustitución de componentes en pruebas.

Las alternativas se descartaron por las siguientes razones:
- Dependency Injector añade complejidad innecesaria para nuestro caso.
- FastAPI Depends está limitado al contexto de peticiones HTTP.
- La construcción manual de objetos dificulta el testing y crea acoplamiento.

### Consecuencias

**Positivas:**
- Código más limpio y desacoplado
- Fácil sustitución de implementaciones
- Inicialización centralizada de componentes
- Mejor testabilidad

**Negativas:**
- Código adicional para mantener
- Posible complejidad para nuevos desarrolladores
- Falta de características avanzadas de bibliotecas especializadas

### Implementación

El contenedor DI se implementa en el módulo `config/di_container.py`. La clase `DIContainer` gestiona la creación y el acceso a repositorios y servicios, facilitando la inversión de dependencias requerida por la arquitectura hexagonal.

---

## ADR-008: Contenerización con Docker

### Fecha: 2024-02-20

### Estado: Aceptada

### Contexto

El simulador necesita ser fácilmente desplegable y ejecutable en diferentes entornos, requiriendo:
- Consistencia entre entornos de desarrollo y producción
- Facilidad de despliegue
- Gestión de dependencias
- Portabilidad

### Alternativas Consideradas

1. **Docker + Docker Compose**: Contenerización estándar.
2. **Entorno virtual de Python + Scripts**: Enfoque tradicional.
3. **Paquete Python instalable**: Distribución como paquete pip.
4. **Entorno de desarrollo integrado**: IDEs con entornos aislados.

### Decisión

Adoptamos **Docker + Docker Compose** para la contenerización de la aplicación.

### Justificación

Docker ofrece ventajas significativas para la distribución y ejecución:

1. **Aislamiento completo**: El entorno de ejecución es consistente y reproducible.
2. **Dependencias encapsuladas**: Todas las dependencias están incluidas en la imagen.
3. **Multi-servicio**: Docker Compose permite definir y orquestar múltiples contenedores.
4. **Portabilidad**: Funciona igual en cualquier plataforma que soporte Docker.
5. **Versionado de entorno**: Las imágenes pueden versionarse junto con el código.
6. **Fácil distribución**: Las imágenes pueden publicarse en registros como Docker Hub.
7. **Despliegue simplificado**: Única dependencia externa es Docker.

Las alternativas se descartaron por las siguientes razones:
- Los entornos virtuales no aíslan dependencias a nivel de sistema.
- Los paquetes pip requieren que el usuario configure correctamente su entorno.
- Los entornos integrados en IDEs son específicos de cada IDE.

### Consecuencias

**Positivas:**
- Mismo entorno en desarrollo y producción
- Facilidad para nuevos desarrolladores ("funciona en mi máquina")
- Despliegue rápido y consistente
- Gestión simplificada de múltiples servicios

**Negativas:**
- Curva de aprendizaje para Docker
- Overhead de recursos (mínimo en este caso)
- Posible complejidad para depuración

### Implementación

La contenerización se implementa mediante:
- `Dockerfile`: Define la imagen base del simulador
- `docker-compose.yml`: Orquesta servicios (app, api) y configuración
- `docker-compose.dev.yml`: Configuración específica para desarrollo

---

## ADR-009: Estrategia de Pruebas

### Fecha: 2024-02-25

### Estado: Aceptada

### Contexto

El simulador requiere una estrategia de pruebas para:
- Garantizar la calidad del código
- Facilitar el mantenimiento y refactoring
- Documentar el comportamiento esperado
- Detectar regresiones

### Alternativas Consideradas

1. **Pruebas por capas**: Unitarias, integración, API, UI.
2. **Pruebas end-to-end**: Enfoque en flujos completos.
3. **Testing basado en propiedades**: Generación aleatoria de casos de prueba.
4. **Testing manual**: Sin automatización.

### Decisión

Adoptamos la estrategia de **Pruebas por capas** utilizando pytest.

### Justificación

Las pruebas por capas ofrecen un enfoque completo y equilibrado:

1. **Pruebas unitarias**: Verifican componentes individuales aisladamente.
   - Dominio: Entidades, reglas de negocio
   - Aplicación: Servicios, coordinación
   - Infraestructura: Adaptadores a sistemas externos

2. **Pruebas de integración**: Verifican interacción entre componentes.
   - Repositorios con base de datos real
   - Servicios con sus dependencias

3. **Pruebas de API**: Verifican interfaces externas.
   - Endpoints REST
   - Formatos de entrada/salida

4. **Pruebas funcionales**: Verifican flujos completos.
   - Simulación de escenarios de negocio
   - Interacciones entre subsistemas

Esta estrategia proporciona:
- Feedback rápido (unitarias)
- Confianza en integraciones (integración)
- Verificación de interfaces (API)
- Validación de flujos de negocio (funcionales)

Las alternativas se descartaron por las siguientes razones:
- Las pruebas exclusivamente end-to-end son lentas y frágiles.
- El testing basado en propiedades requiere más esfuerzo inicial.
- El testing manual no es sostenible a largo plazo.

### Consecuencias

**Positivas:**
- Mayor confianza en el código
- Documentación viva del comportamiento
- Facilidad para refactoring
- Detección temprana de problemas

**Negativas:**
- Tiempo dedicado a escribir y mantener pruebas
- Posible duplicación entre niveles de prueba
- Necesidad de infraestructura para CI/CD

### Implementación

Las pruebas se organizan en el directorio `tests/`:
- `tests/unit/`: Pruebas unitarias por capa
- `tests/integration/`: Pruebas de integración
- `tests/api/`: Pruebas de la API REST
- `tests/functional/`: Pruebas de flujos completos

Se utiliza pytest como framework principal, con pytest-mock para mocks y pytest-cov para cobertura.

---

## ADR-010: Granularidad de Simulación

### Fecha: 2024-03-01

### Estado: Aceptada

### Contexto

La simulación de producción requiere decidir el nivel de detalle (granularidad) con el que se modelarán los procesos:
- Desde nivel de segundos/minutos hasta semanas/meses
- Afecta a la precisión, rendimiento y complejidad
- Impacta en la experiencia de usuario

### Alternativas Consideradas

1. **Granularidad diaria**: El día como unidad mínima de tiempo.
2. **Granularidad horaria**: La hora como unidad mínima.
3. **Granularidad por turnos**: Modelar turnos de trabajo (mañana, tarde, noche).
4. **Granularidad variable**: Diferentes unidades para diferentes procesos.

### Decisión

Adoptamos la **Granularidad diaria** como unidad básica de simulación.

### Justificación

La granularidad diaria ofrece el equilibrio más adecuado para nuestro caso:

1. **Adecuada para decisiones de planificación**: La planificación de producción y compras típicamente se realiza en base diaria.
2. **Suficiente precisión**: Captura los aspectos importantes del proceso sin detalles excesivos.
3. **Experiencia de usuario fluida**: El avance día a día es intuitivo para los usuarios.
4. **Complejidad manejable**: Simplifica el modelado y reduce los estados a mantener.
5. **Datos agregados significativos**: Los indicadores diarios son más útiles que los de grano más fino.
6. **Consistente con lead times de proveedores**: Los tiempos de entrega se expresan en días.

Las alternativas se descartaron por las siguientes razones:
- La granularidad horaria introduce complejidad innecesaria sin beneficios claros.
- La granularidad por turnos es más compleja y menos universal.
- La granularidad variable complicaría la interfaz y el modelo mental.

### Consecuencias

**Positivas:**
- Modelo mental simple para los usuarios
- Menor complejidad de implementación
- Mayor rendimiento de la simulación
- Interfaz más limpia

**Negativas:**
- No captura eventos intra-día
- Puede parecer simplista para algunos casos de uso
- Limitada para analizar eficiencia operativa detallada

### Implementación

La granularidad diaria se implementa:
- En el controlador de simulación (`application/simulation.py`)
- En la función "Avanzar día" de la interfaz
- En el manejo de fechas (formato YYYY-MM-DD)
- En los ciclos de producción y entregas

## Conclusión

Las decisiones arquitectónicas documentadas en este ADR han guiado el desarrollo del Simulador de Producción de Impresoras 3D, proporcionando una base sólida para un sistema mantenible, testeable y extensible. La combinación de arquitectura hexagonal, SimPy, SQLite, Streamlit, FastAPI y las demás decisiones ha permitido crear un simulador que cumple con los requisitos funcionales y no funcionales establecidos, a la vez que facilita futuras mejoras y adaptaciones.