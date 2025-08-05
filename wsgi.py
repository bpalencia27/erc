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
"""
Punto de entrada para servidor WSGI en producción
"""
from app import create_app

# Por defecto, usamos la configuración de desarrollo
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> 2a25396d (Depuración automática: mejoras en modal-manager.js y correcciones generales)
