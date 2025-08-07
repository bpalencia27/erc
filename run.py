<<<<<<< HEAD
"""
Punto de entrada para ejecutar la aplicación en modo desarrollo
"""
from app import create_app
import os

app = create_app('development')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
=======
#!/usr/bin/env python3
"""
Script principal para ejecutar ERC Insight
Optimizado para desarrollo y producción
"""
import os
import sys
from pathlib import Path
import logging
from dotenv import load_dotenv

# Configurar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("erc_insight")

# Cargar variables de entorno
env_path = Path('.') / '.env'
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"Variables de entorno cargadas desde {env_path}")
else:
    logger.warning("Archivo .env no encontrado, usando configuración por defecto")

def main():
    """Función principal para ejecutar la aplicación"""
    try:
        from app import create_app
        
        # Obtener configuración del entorno
        config_name = os.getenv('FLASK_ENV', 'development')
        
        # Crear aplicación
        app = create_app(config_name)
        
        # Configuración para desarrollo
        if config_name == 'development':
            app.config.update(
                TEMPLATES_AUTO_RELOAD=True,
                SEND_FILE_MAX_AGE_DEFAULT=0
            )
        
        # Obtener puerto
        port = int(os.getenv('PORT', 5000))
        debug = config_name == 'development'
        
        logger.info(f"Iniciando ERC Insight en modo {config_name}")
        logger.info(f"Puerto: {port}, Debug: {debug}")
        
        print(f"""
        ╔══════════════════════════════════════════╗
        ║         ERC Insight - v2.0.0            ║
        ║     Sistema de Análisis Renal con IA    ║
        ╠══════════════════════════════════════════╣
        ║  Servidor: http://localhost:{port:<5}       ║
        ║  Entorno: {config_name:<15}           ║
        ║  Debug: {str(debug):<5}                    ║
        ╚══════════════════════════════════════════╝
        
        Presiona CTRL+C para detener el servidor
        """)
        
        # Ejecutar aplicación
        app.run(
            host='0.0.0.0' if config_name == 'production' else '127.0.0.1',
            port=port,
            debug=debug,
            use_reloader=debug
        )
        
    except ImportError as e:
        logger.error(f"Error al importar módulos: {str(e)}")
        print(f"❌ Error: {e}")
        print("Ejecuta: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error al ejecutar la aplicación: {str(e)}", exc_info=True)
        print(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
>>>>>>> 1a009ef5 ( Preparación completa para despliegue en Render.com)
