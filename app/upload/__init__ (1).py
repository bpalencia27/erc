# app/upload/__init__.py

from flask import Blueprint

# Define el Blueprint UNA SOLA VEZ aquí
bp = Blueprint('upload', __name__)

# Importa las rutas para que se registren en este 'bp'
from app.upload import routes