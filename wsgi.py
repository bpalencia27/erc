"""
Punto de entrada WSGI para producción
"""
import os
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Importar y crear aplicación
from app import create_app

# Detectar entorno
env = os.environ.get('FLASK_ENV', 'production')

# Crear aplicación
app = create_app(env)
application = app  # Para compatibilidad con algunos servidores WSGI

if __name__ == '__main__':
    # Solo para pruebas locales
    app.run(debug=False)
