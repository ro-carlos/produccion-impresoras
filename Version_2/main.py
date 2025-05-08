import argparse
import uvicorn
import os
import subprocess
import sys
from pathlib import Path
import logging
import threading
import time

from config.settings import API_HOST, API_PORT, STREAMLIT_PORT, load_config
from config.di_container import DIContainer
from presentation.api import create_api

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('simulator.log')
    ]
)

logger = logging.getLogger("3d_printer_simulator")

def start_api(host: str = API_HOST, port: int = API_PORT) -> None:
    """
    Inicia el servidor de la API.
    
    Args:
        host: Host donde escuchará la API
        port: Puerto donde escuchará la API
    """
    # Cargar configuración
    config = load_config()
    
    # Inicializar contenedor de dependencias en este proceso
    container = DIContainer(config)
    container.initialize()
    container.seed_database()
    
    # Crear la aplicación FastAPI
    app = create_api(container.simulation_service)
    
    # Iniciar servidor uvicorn
    logger.info(f"Iniciando servidor API en http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)

def start_streamlit(streamlit_port: int = STREAMLIT_PORT, api_port: int = API_PORT) -> None:
    """
    Inicia la aplicación Streamlit.
    
    Args:
        streamlit_port: Puerto donde escuchará Streamlit
        api_port: Puerto donde está escuchando la API
    """
    # Construir la URL de la API
    api_host = os.environ.get("API_HOST", "localhost")
    api_url = f"http://{api_host}:{api_port}"
    
    # Obtener la ruta al archivo de la aplicación Streamlit
    streamlit_app_path = Path(__file__).resolve().parent / "presentation" / "streamlit_app.py"
    
    # Verificar si estamos en modo UI only (Docker probablemente)
    ui_only_mode = "--ui-only" in sys.argv
    
    # Construir comando para iniciar Streamlit
    cmd = [
        "streamlit", "run", str(streamlit_app_path),
        "--server.port", str(streamlit_port),
        "--server.address", "0.0.0.0",  # Escuchar en todas las interfaces
        "--", api_url
    ]
    
    logger.info(f"Iniciando aplicación Streamlit en http://localhost:{streamlit_port}")
    
    if ui_only_mode:
        # En modo UI only, ejecutamos directamente el comando
        # Esto mantiene vivo el proceso principal del contenedor Docker
        os.execvp(cmd[0], cmd)
    else:
        # En modo normal, iniciamos como proceso separado
        subprocess.Popen(cmd)

def main():
    """Función principal de la aplicación."""
    # Parsear argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Simulador de Producción de Impresoras 3D")
    
    parser.add_argument(
        "--api-only", action="store_true",
        help="Iniciar solo el servidor API (sin interfaz Streamlit)"
    )
    
    parser.add_argument(
        "--ui-only", action="store_true",
        help="Iniciar solo la interfaz Streamlit (requiere servidor API en ejecución)"
    )
    
    parser.add_argument(
        "--api-host", type=str, default=API_HOST,
        help=f"Host para el servidor API (predeterminado: {API_HOST})"
    )
    
    parser.add_argument(
        "--api-port", type=int, default=API_PORT,
        help=f"Puerto para el servidor API (predeterminado: {API_PORT})"
    )
    
    parser.add_argument(
        "--ui-port", type=int, default=STREAMLIT_PORT,
        help=f"Puerto para la interfaz Streamlit (predeterminado: {STREAMLIT_PORT})"
    )
    
    args = parser.parse_args()
    
    if not args.ui_only:
        # Iniciar servidor API
        logger.info("Iniciando servidor API...")
        if args.api_only:
            # Solo API, en el hilo principal
            start_api(args.api_host, args.api_port)
        else:
            # Iniciar API en un hilo separado en lugar de un proceso
            # Esto evita los problemas de pickle con la conexión SQLite
            api_thread = threading.Thread(
                target=start_api,
                args=(args.api_host, args.api_port),
                daemon=True
            )
            api_thread.start()
    
    if not args.api_only:
        # Iniciar interfaz Streamlit
        logger.info("Iniciando interfaz Streamlit...")
        start_streamlit(args.ui_port, args.api_port)
        
        # Si estamos ejecutando ambos servicios, mantener vivo el proceso principal
        if not args.ui_only:
            try:
                # Mantener vivo el proceso principal hasta Ctrl+C
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Deteniendo el simulador...")
                sys.exit(0)

if __name__ == "__main__":
    main()
