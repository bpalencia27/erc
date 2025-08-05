from flask import render_template, current_app
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    """Renderiza la página principal de la aplicación."""
    return render_template('index.html', title='ERC Insight - Análisis Clínico Inteligente')

@bp.route('/about')
def about():
    """Renderiza la página de información sobre la aplicación."""
    return render_template('about.html', title='Acerca de ERC Insight')
