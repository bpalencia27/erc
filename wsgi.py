"""
Punto de entrada para servidor WSGI en producción
"""

import os
import sys
from dotenv import load_dotenv

# No necesitas modificar sys.path en Render

# Cargar variables de entorno desde .env
load_dotenv()

from config import ProductionConfig
from app import create_app

app = create_app(ProductionConfig)
application = app  # Para servidores WSGI como Gunicorn o uWSGI
