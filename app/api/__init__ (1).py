from flask import Blueprint

# Define el Blueprint para la API
bp = Blueprint('api', __name__)

# Importa las rutas para que se registren en este Blueprint
from app.api import routes
