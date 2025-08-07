"""
Punto de entrada para servidor WSGI en producción
Optimizado para Render.com y otros servicios de hosting
"""
import os
import logging
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

def setup_logging():
    """Configura el sistema de logging para la aplicación."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("wsgi")

# Inicializar logging
logger = setup_logging()
logger.info("Inicializando aplicación WSGI para producción")

try:
    from app import create_app
    
    # Crear aplicación con configuración de producción
    environment = os.getenv('FLASK_ENV', 'production')
    app = create_app(environment)
    application = app  # Para servidores WSGI como Gunicorn
    
    logger.info(f"Aplicación creada exitosamente - env: {environment}")
    
except Exception as e:
    logger.error(f"Error al crear la aplicación: {str(e)}")
    raise

if __name__ == "__main__":
    # Para desarrollo local
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
