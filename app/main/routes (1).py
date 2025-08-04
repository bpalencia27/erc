from flask import render_template, current_app
from app.main import bp

@bp.route('/')
def index():
    """Renderiza la página principal de la aplicación (Single Page App)."""
    return render_template('base.html', title='CardiaIA - Plataforma de Análisis Clínico Inteligente')

@bp.route('/partials/<partial_name>')
def get_partial(partial_name):
    """Sirve las plantillas parciales para la carga dinámica."""
    try:
        return render_template(f'partials/_{partial_name}.html')
    except Exception as e:
        current_app.logger.error(f"Error loading partial {partial_name}: {e}")
        return '', 404
