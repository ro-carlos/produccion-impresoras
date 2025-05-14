# Resumen de Materiales Requeridos

## Descripción

La funcionalidad de "Resumen de Materiales Requeridos" permite a los usuarios visualizar la totalidad de materiales necesarios para satisfacer todos los pedidos de fabricación pendientes, comparándolos con las existencias actuales. Esta característica facilita la planificación de compras consolidadas al proporcionar una visión clara y rápida de las necesidades globales de materiales.

## Propósito

Esta funcionalidad fue diseñada para:

- Facilitar la planificación consolidada de compras
- Proporcionar una visión general de las necesidades de materiales
- Evitar realizar múltiples órdenes pequeñas para el mismo material
- Reducir el tiempo de análisis necesario para la toma de decisiones
- Minimizar los errores en el cálculo manual de materiales requeridos

## Características principales

### Tabla de resumen consolidado

La tabla muestra la siguiente información para cada material requerido:

1. **ID**: Identificador único del material
2. **Material**: Nombre del material
3. **Total Requerido**: Suma de las cantidades necesarias para todos los pedidos pendientes
4. **Existencia**: Cantidad actual disponible en inventario
5. **Comprar**: Diferencia entre lo requerido y lo disponible (cantidad sugerida para comprar)

### Indicadores visuales

- Las filas donde la cantidad a comprar es mayor que cero se resaltan en color rojo para facilitar la identificación de materiales con inventario insuficiente.
- La columna "Comprar" muestra claramente cuántas unidades faltan para satisfacer todos los pedidos.

### Selección rápida

- El botón "Seleccionar material para comprar" permite elegir automáticamente el primer material con inventario insuficiente.
- Esta selección se integra con el formulario de compra, pre-seleccionando el material y facilitando el proceso.

## Funcionamiento técnico

### Cálculo del resumen

1. Se recorren todos los pedidos pendientes en `st.session_state.pending_orders`.
2. Para cada pedido, se extraen los materiales necesarios de la lista `materials`.
3. Se acumulan las cantidades requeridas para cada material en un diccionario.
4. Se comparan las cantidades requeridas con las existencias actuales del inventario.
5. Se calculan las cantidades a comprar como `max(0, requerido - existencia)`.

### Integración con el formulario de compra

1. Cuando se presiona el botón "Seleccionar material para comprar", se guarda el ID del material en `st.session_state.selected_material_id`.
2. El selectbox de materiales utiliza este valor para pre-seleccionar el material correspondiente.
3. Esto permite un flujo de trabajo continuo desde la identificación de necesidades hasta la realización de la compra.

## Beneficios para el usuario

- **Ahorro de tiempo**: No es necesario revisar cada pedido individualmente para calcular las necesidades totales.
- **Reducción de errores**: El cálculo automático elimina posibles errores de suma manual.
- **Mejor planificación**: Facilita la compra de cantidades óptimas, evitando sobrecompras o faltantes.
- **Proceso simplificado**: La selección automática reduce el número de clics necesarios para realizar una compra.

## Ejemplos de uso

### Escenario 1: Múltiples pedidos con materiales comunes

Supongamos que hay tres pedidos pendientes:
- 5 unidades de P3D-Classic (requieren 5 kits de piezas)
- 3 unidades de P3D-Pro (requieren 3 kits de piezas)
- 2 unidades de P3D-Classic (requieren 2 kits de piezas)

El resumen mostrará que se necesitan 10 kits de piezas en total. Si el inventario actual es de 7 kits, la columna "Comprar" indicará que se deben adquirir 3 kits adicionales.

### Escenario 2: Identificación de cuellos de botella

Si hay varios materiales con inventario insuficiente, el resumen permitirá identificar rápidamente cuáles son los más críticos por cantidad o importancia. El botón "Seleccionar material para comprar" elegirá automáticamente el primero de la lista, facilitando la priorización.

## Consideraciones futuras

En futuras versiones, se podrían implementar mejoras como:

- Ordenar la tabla por diferentes criterios (mayor déficit, costo del material, etc.)
- Añadir un botón para generar automáticamente órdenes de compra para todos los materiales faltantes
- Incluir información sobre tiempos de entrega estimados para ayudar en la priorización
- Agregar gráficos visuales para representar las proporciones de materiales requeridos

## Conclusión

La funcionalidad de "Resumen de Materiales Requeridos" representa una mejora significativa en la experiencia del usuario del simulador, facilitando la toma de decisiones informadas y eficientes en la gestión de compras y permitiendo una mejor planificación de la producción.
