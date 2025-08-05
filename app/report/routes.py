from flask import render_template, jsonify
from app.report import bp

@bp.route('/', methods=['GET'])
def index():
    """Página principal del módulo de informes."""
    return render_template('index.html', title='Informes Médicos')

@bp.route('/test', methods=['GET'])
def test():
    """Ruta de prueba."""
    return jsonify({"status": "ok", "message": "Test route working"})
