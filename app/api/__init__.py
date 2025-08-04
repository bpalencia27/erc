from flask import Blueprint, render_template

# Define el Blueprint para la API
bp = Blueprint('api', __name__)

# Importa las rutas para que se registren en este Blueprint
from app.api import routes

# En app/__init__.py
@bp.errorhandler(500)
def server_error(error):
    bp.logger.error(f'Error del servidor: {error}')
    return render_template('errors/500.html'), 500

@bp.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404
