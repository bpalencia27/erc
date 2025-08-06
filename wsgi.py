"""
Punto de entrada para servidor WSGI en producción
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

from config import config
from app import create_app

app = create_app('production')
application = app  # Para servidores WSGI como Gunicorn o uWSGI

# wsgi.py - Configuración WSGI optimizada para PythonAnywhere
import sys
import os
import logging
from pathlib import Path

# Función para crear directorio de logs si no existe
def setup_logging():
    """Configura el sistema de logging para la aplicación."""
    # Determinar la ruta base (directorio actual o HOME en PythonAnywhere)
    base_path = os.path.dirname(os.path.abspath(__file__))
    logs_path = os.path.join(base_path, "logs")

    # Crear directorio de logs si no existe
    try:
        os.makedirs(logs_path, exist_ok=True)
        log_file = os.path.join(logs_path, "wsgi_app.log")
    except Exception as e:
        # Si no se puede crear el directorio, usar un archivo en el directorio temporal
        import tempfile
        logs_path = tempfile.gettempdir()
        log_file = os.path.join(logs_path, "wsgi_app.log")
        print(f"No se pudo crear directorio de logs: {str(e)}. Usando {log_file}")

    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger("wsgi")

# Inicializar logging
logger = setup_logging()
logger.info("Inicializando aplicación WSGI")

# Añadir el directorio del proyecto al path
path = '/home/bpalencia27/erc_insight'
if path not in sys.path:
    sys.path.append(path)
    logger.info(f"Añadido {path} al path")

# Configurar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    dotenv_path = os.path.join(path, '.env')
    load_dotenv(dotenv_path)
    logger.info(f"Variables de entorno cargadas desde {dotenv_path}")
except ImportError:
    logger.warning("No se pudo importar dotenv. Las variables de entorno no se cargarán desde .env")

try:
    from run import app as application
    logger.info("Aplicación cargada correctamente desde run.py")
except ImportError as e:
    import traceback
    error_msg = f"Error importando aplicación desde run.py: {e}"
    logger.error(error_msg)
    logger.error(traceback.format_exc())

    # Aplicación de emergencia
    from flask import Flask, jsonify
    application = Flask(__name__)

    @application.route('/')
    def home():
        return jsonify({"status": "error", "message": "No se pudo cargar la aplicación"})

    @application.route('/test')
    def test():
        return jsonify({"status": "error", "message": "Aplicación de emergencia", "sys_path": sys.path})

    logger.error("Se ha creado una aplicación de emergencia debido a que no se encontró la aplicación principal")

# Configuración para PythonAnywhere
import sys
sys.path.insert(0, '/home/bpalencia27/erc_insight')
from wsgi import app as application
