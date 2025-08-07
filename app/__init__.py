<<<<<<< HEAD
from flask import Flask
from flask_cors import CORS
from config import config
import os
from logging.handlers import RotatingFileHandler
import logging
from app.extensions import db, migrate

def create_app(config_name='default'):
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)
    
    # Cargar configuración
    if isinstance(config_name, str):
        app.config.from_object(config[config_name])
    else:
        app.config.from_object(config_name)
        
    # Inicializar la configuración
    try:
        from app.report import bp as report_bp
        app.register_blueprint(report_bp, url_prefix='/report')
        # logger se define más abajo
        pass
    except ImportError as e:
        pass
    
    try:
        from app.upload import bp as upload_bp
        app.register_blueprint(upload_bp, url_prefix='/upload')
        pass
    except ImportError as e:
        pass
    
    # Manejadores de error
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        import logging
        logging.error(f"Error interno del servidor: {error}")
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        from werkzeug.exceptions import HTTPException
        if isinstance(e, HTTPException):
            return e
        import logging
        from flask import render_template
        logging.error(f"Error no controlado: {e}", exc_info=True)
        return render_template('errors/500.html'), 500
    
    # Contexto de template global
    @app.context_processor
    def inject_debug():
        return dict(debug=app.debug)
    
    # Ruta de salud
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'version': '2.0.0'}, 200
    
    import logging
    logging.info(f"Aplicación Flask creada exitosamente - config: {config_name}, debug: {app.debug}")
    
    return app

