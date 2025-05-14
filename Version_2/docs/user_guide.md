# Manual de Usuario
## Simulador de Producción de Impresoras 3D

Este manual proporciona instrucciones detalladas sobre cómo utilizar el Simulador de Producción de Impresoras 3D, una aplicación diseñada para simular el ciclo completo de operación de una planta de fabricación de impresoras 3D.

## Índice

1. [Introducción](#1-introducción)
2. [Instalación y Ejecución](#2-instalación-y-ejecución)
3. [Interfaz de Usuario](#3-interfaz-de-usuario)
4. [Flujo de Trabajo Diario](#4-flujo-de-trabajo-diario)
5. [Escenarios Prácticos](#5-escenarios-prácticos)
6. [Guía de Referencia Rápida](#6-guía-de-referencia-rápida)
7. [Solución de Problemas](#7-solución-de-problemas)

## 1. Introducción

El Simulador de Producción de Impresoras 3D es una herramienta educativa que modela el proceso de producción de impresoras 3D, centrándose en tres aspectos clave:

- Gestión de inventarios
- Compras de materiales
- Planificación de la producción

Como usuario, asumirás el rol de planificador de producción, tomando decisiones sobre qué fabricar y qué comprar para satisfacer la demanda generada.

### 1.1 Modelos de Impresoras

El simulador incluye dos modelos de impresoras 3D:

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

### 1.2 Objetivos del Simulador

- Practicar y mejorar habilidades de planificación de producción.
- Aprender a optimizar la gestión de inventario.
- Entender la importancia del equilibrio entre demanda y capacidad.
- Experimentar con diferentes estrategias de compra.

## 2. Instalación y Ejecución

### 2.1 Requisitos Previos

- Python 3.11 o superior
- Docker y Docker Compose (opcional, para ejecución en contenedores)

### 2.2 Instalación con Python

1. Clone el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/mrp-dgsi.git
   cd mrp-dgsi
   ```

2. Instale las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Inicialice la base de datos:
   ```bash
   python scripts/init_db.py
   ```

4. Ejecute la aplicación:
   ```bash
   python main.py
   ```

### 2.3 Instalación con Docker

1. Clone el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/mrp-dgsi.git
   cd mrp-dgsi
   ```

2. Construya y ejecute los contenedores:
   ```bash
   docker-compose up -d
   ```

### 2.4 Acceso a la Aplicación

- **Interfaz Web**: Acceda a `http://localhost:8501` en su navegador.
- **API REST**: Disponible en `http://localhost:8000/api`.

## 3. Interfaz de Usuario

La interfaz de usuario está construida con Streamlit y se organiza en varias secciones principales.

### 3.1 Cabecera

![Cabecera](https://via.placeholder.com/800x100)

La cabecera muestra:
- **Día actual**: Indica el día de simulación en curso.
- **Botón "Avanzar día"**: Permite pasar al siguiente día de simulación.

### 3.2 Panel de Pedidos

![Panel de Pedidos](https://via.placeholder.com/800x300)

Este panel muestra:
- **Pedidos pendientes**: Lista de pedidos que aún no han sido procesados.
- **Detalles del pedido**: Incluye producto, cantidad y fecha de creación.
- **BOM requerido**: Cálculo automático de los materiales necesarios para cada pedido.
- **Botón "Liberar a producción"**: Permite enviar un pedido a producción si hay materiales disponibles.

### 3.3 Panel de Inventario

![Panel de Inventario](https://via.placeholder.com/800x300)

Muestra:
- **Inventario actual**: Nivel de stock de cada material y producto terminado.
- **Indicadores visuales**: Colores que indican niveles críticos (rojo), bajos (amarillo) o adecuados (verde).
- **Historial de inventario**: Gráfico que muestra la evolución del inventario a lo largo del tiempo.

### 3.4 Panel de Compras

![Panel de Compras](https://via.placeholder.com/800x300)

Permite:
- **Seleccionar proveedor**: Lista desplegable con proveedores disponibles.
- **Seleccionar producto**: Muestra automáticamente el producto asociado al proveedor.
- **Especificar cantidad**: Campo numérico para indicar cuánto comprar.
- **Ver detalles del proveedor**: Costo unitario y tiempo de entrega.
- **Botón "Emitir orden de compra"**: Crea una nueva orden de compra.
- **Órdenes pendientes**: Lista de órdenes de compra en camino.

### 3.5 Panel de Producción

![Panel de Producción](https://via.placeholder.com/800x300)

Presenta:
- **Capacidad diaria**: Número máximo de impresoras que se pueden fabricar por día.
- **Pedidos en cola**: Pedidos liberados a producción que esperan ser procesados.
- **Pedidos en proceso**: Pedidos que se están fabricando actualmente.
- **Historial de producción**: Gráfico que muestra la cantidad de pedidos completados por día.

### 3.6 Panel de Eventos

![Panel de Eventos](https://via.placeholder.com/800x200)

Muestra:
- **Registro cronológico**: Lista de todos los eventos ocurridos en la simulación.
- **Tipos de eventos**: Creación de pedidos, inicio de producción, recepción de materiales, etc.
- **Filtros**: Permiten mostrar solo ciertos tipos de eventos o rangos de fechas.

## 4. Flujo de Trabajo Diario

El simulador funciona en ciclos diarios. A continuación se describe el flujo de trabajo típico:

### 4.1 Inicio del Día

Al iniciar un nuevo día:
1. Se generan automáticamente nuevos pedidos de fabricación.
2. Se actualizan los estados de pedidos en producción.
3. Se reciben materiales de órdenes de compra que llegan ese día.

### 4.2 Análisis de la Situación

Como planificador, debes:
1. Revisar los pedidos pendientes.
2. Verificar el nivel de inventario actual.
3. Comprobar las órdenes de compra en camino.
4. Analizar la capacidad de producción disponible.

### 4.3 Toma de Decisiones

Basándote en tu análisis, debes decidir:

#### 4.3.1 Decisiones de Producción

1. **Liberar pedidos a producción**:
   - Selecciona un pedido pendiente.
   - Haz clic en "Liberar a producción".
   - El sistema verificará automáticamente si hay suficientes materiales.
   - Si hay suficientes materiales, el pedido pasa a estado "en proceso" y se consumen los materiales del inventario.
   - Si no hay suficientes materiales, recibirás una notificación indicando qué materiales faltan.

#### 4.3.2 Decisiones de Compra

1. **Emitir órdenes de compra**:
   - Selecciona un proveedor de la lista desplegable.
   - Verifica el producto, costo unitario y tiempo de entrega.
   - Indica la cantidad que deseas comprar.
   - Haz clic en "Emitir orden de compra".
   - La orden quedará registrada y los materiales llegarán después del tiempo de entrega especificado.

### 4.4 Avanzar al Siguiente Día

Una vez tomadas todas las decisiones:
1. Haz clic en "Avanzar día" en la cabecera.
2. El sistema procesará un día completo de simulación, actualizando todos los estados.
3. Se mostrarán los nuevos pedidos generados.

## 5. Escenarios Prácticos

### 5.1 Escenario 1: Gestión Básica de Producción

**Situación inicial**:
- Día 1
- Stock inicial: 30 kits de piezas, 20 pcb_v2, 25 extrusores, etc.
- Capacidad: 10 impresoras/día
- Nuevos pedidos: 8 P3D-Classic y 6 P3D-Pro

**Acciones recomendadas**:
1. Liberar el pedido de 8 P3D-Classic a producción.
2. Verificar el inventario restante.
3. Decidir si liberar también el pedido de P3D-Pro o esperar.
4. Avanzar al día 2.

**Resultado esperado**:
- Se consumirán 8 kits, 8 pcb_v2, 8 extrusores, 16 cables, etc.
- El pedido de P3D-Classic estará en proceso.
- Al día siguiente, el pedido estará completado y las impresoras estarán en inventario.

### 5.2 Escenario 2: Planificación de Compras

**Situación inicial**:
- Día 2
- Stock bajo en kits de piezas (22 unidades)
- Nuevos pedidos: 5 P3D-Classic y 7 P3D-Pro

**Acciones recomendadas**:
1. Analizar el stock actual y los pedidos pendientes.
2. Calcular las necesidades futuras.
3. Comparar proveedores para el kit de piezas:
   - Proveedor A: 90€/kit, lead time 3 días
   - Proveedor B: 85€/kit, lead time 5 días
4. Emitir una orden de compra por 20 kits al proveedor A.
5. Liberar el pedido de 5 P3D-Classic a producción.
6. Avanzar día.

**Resultado esperado**:
- La orden de compra quedará registrada con entrega estimada para el día 5.
- El stock de kits bajará a 17 unidades tras liberar el pedido.
- Habrá que gestionar cuidadosamente el stock hasta la llegada del nuevo material.

### 5.3 Escenario 3: Gestión de Escasez

**Situación inicial**:
- Día 3
- Stock crítico en pcb_v3 (2 unidades)
- Pedidos pendientes: 4 P3D-Pro (requieren 4 pcb_v3)

**Acciones recomendadas**:
1. Verificar la imposibilidad de liberar el pedido completo.
2. Emitir una orden de compra urgente por 10 pcb_v3 al Proveedor D.
3. Considerar liberar pedidos de P3D-Classic mientras tanto.
4. Avanzar día.

**Resultado esperado**:
- No se podrá liberar el pedido de P3D-Pro por falta de materiales.
- La orden de compra de pcb_v3 llegará en 2 días (día 5).
- Se podrán seguir fabricando P3D-Classic si hay pedidos.

## 6. Guía de Referencia Rápida

### 6.1 Atajos de Teclado

- `Alt+A`: Avanzar día
- `Alt+L`: Liberar pedido seleccionado
- `Alt+C`: Foco en panel de compras
- `Alt+I`: Foco en panel de inventario

### 6.2 Indicadores Visuales

- **Verde**: Nivel óptimo / Operación exitosa
- **Amarillo**: Nivel bajo / Precaución
- **Rojo**: Nivel crítico / Error

### 6.3 Estados de los Pedidos

- **Pendiente**: Pedido recién creado, esperando liberación.
- **En proceso**: Pedido en fabricación.
- **Completado**: Pedido fabricado correctamente.
- **Cancelado**: Pedido cancelado manualmente.

### 6.4 Estados de las Órdenes de Compra

- **Pendiente**: Orden emitida, materiales en camino.
- **Recibida**: Materiales recibidos e incorporados al inventario.
- **Cancelada**: Orden cancelada manualmente (solo posible si está pendiente).

## 7. Solución de Problemas

### 7.1 Errores Comunes

#### 7.1.1 "No se puede liberar el pedido"
- **Causa probable**: Falta de materiales en inventario.
- **Solución**: Verificar qué materiales faltan y emitir órdenes de compra.

#### 7.1.2 "Error al avanzar día"
- **Causa probable**: Problema de conexión con la base de datos.
- **Solución**: Reiniciar la aplicación. Si persiste, verificar el archivo `simulator.log`.

#### 7.1.3 "No se muestra el gráfico de inventario"
- **Causa probable**: No hay suficientes datos históricos.
- **Solución**: Avanzar algunos días más para generar datos históricos.

### 7.2 Preguntas Frecuentes

#### ¿Cómo puedo reiniciar la simulación?
Para reiniciar la simulación, haz clic en "Configuración" en el menú lateral y selecciona "Reiniciar simulación".

#### ¿Puedo cancelar una orden de compra?
Sí, puedes cancelar órdenes de compra pendientes desde el panel de compras, haciendo clic en el botón "Cancelar" junto a la orden.

#### ¿Cómo exporto los datos de la simulación?
Ve al menú lateral, selecciona "Exportar datos" y elige el formato deseado (JSON o CSV).

#### ¿Cuánta capacidad de almacén tengo?
El simulador considera que 1 unidad de cualquier material equivale a 1 unidad de almacenaje. No hay un límite explícito en el almacén.

#### ¿Puedo modificar los parámetros de simulación?
Sí, desde el menú "Configuración" puedes ajustar parámetros como la capacidad de producción diaria y la variabilidad de la demanda.

### 7.3 Contacto y Soporte

Si encuentras problemas no documentados o tienes sugerencias para mejorar el simulador, por favor:

- Crea un Issue en el repositorio GitHub
- Envía un correo a support@mrp-simulator.com
- Consulta la documentación actualizada en https://docs.mrp-simulator.com

## Conclusión

Este manual te ha proporcionado las herramientas necesarias para utilizar eficazmente el Simulador de Producción de Impresoras 3D. Recuerda que el objetivo principal es aprender sobre planificación de producción y gestión de inventarios en un entorno controlado.

¡Buena suerte con tus simulaciones!