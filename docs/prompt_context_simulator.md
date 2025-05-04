Estoy desarrollando una API con FastAPI para un sistema logístico y necesito agregar una capa de simulación. Quiero que me generes lo siguiente:

    Un archivo llamado simulator.py que contenga la lógica de simulación del sistema. Este debe incluir:

        Una clase o conjunto de funciones que representen el estado interno de una simulación logística.

        Una función avanzar_dia_simulacion() que actualice el estado de la simulación como si hubiese pasado un día. Por ahora, puede simular cambios simples (por ejemplo, un contador de días).

        Una función obtener_estado_simulacion() que retorne el estado actual de la simulación, como el número de días transcurridos y un resumen general.

        El estado puede mantenerse en memoria (por ejemplo, usando una variable global o singleton).

    Al final del archivo api.py, agrega los endpoints de FastAPI relacionados con esta simulación:

        POST /simulator/advance → llama a avanzar_dia_simulacion() y retorna una respuesta con el nuevo estado.

        GET /simulator/status → llama a obtener_estado_simulacion() y retorna el estado actual.

        Usa JSONResponse para las respuestas y maneja errores potenciales.

Consideraciones:

    El código debe estar bien estructurado, modular y listo para producción.

    Asegúrate de manejar el estado con cuidado (inicialización, concurrencia básica si aplica).

    Proporciona respuestas claras, como { "success": true, "estado": ... }.

    Utiliza typing y comentarios para mayor claridad.

    Todos los nombres de funciones, variables y endpoints deben estar en español, siguiendo la convención del resto del proyecto.