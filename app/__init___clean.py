"""
Aplicación Flask para ERC Insight
"""
import os
import logging
from pathlib import Path
from flask import Flask, render_template, request
from flask_cors import CORS
from flask_caching import Cache
from werkzeug.exceptions import HTTPException

# Importar configuración
try:
    from config import config
except ImportError:
    # Fallback configuration si no existe config.py
    import tempfile
    import secrets
    
    class Config:
        SECRET_KEY = secrets.token_urlsafe(32)
        UPLOAD_FOLDER = tempfile.gettempdir()
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
        WTF_CSRF_ENABLED = True
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        CACHE_TYPE = "simple"
    
    config = {"development": Config(), "testing": Config(), "production": Config()}

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    """Factory de aplicación Flask"""
    
    app = Flask(__name__)
    
    # Configuración
    try:
        app.config.from_object(config.get(config_name, config['development']))
    except Exception as e:
        logger.warning(f"Error cargando configuración {config_name}: {e}")
        # Configuración básica de fallback
        app.config.update({
            'SECRET_KEY': os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production',
            'UPLOAD_FOLDER': os.path.join(app.root_path, 'static', 'uploads'),
            'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
            'WTF_CSRF_ENABLED': True,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        })
    
    # Configurar CORS
    CORS(app, 
         resources={r"/api/*": {"origins": "*"}},
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Configurar caché
    try:
        cache = Cache(app)
    except Exception as e:
        logger.warning(f"Error configurando caché: {e}")
        cache = None
    
    # Crear directorios necesarios
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
    
    # Registrar blueprints
    try:
        from app.main import bp as main_bp
        app.register_blueprint(main_bp)
        logger.info("Blueprint main registrado")
    except ImportError as e:
        logger.warning(f"No se pudo importar main blueprint: {e}")
    
    try:
        from app.api import bp as api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
        logger.info("Blueprint api registrado")
    except ImportError as e:
        logger.warning(f"No se pudo importar api blueprint: {e}")
    
    try:
        from app.patient import bp as patient_bp
        app.register_blueprint(patient_bp, url_prefix='/patient')
        logger.info("Blueprint patient registrado")
    except ImportError as e:
        logger.warning(f"No se pudo importar patient blueprint: {e}")
    
    try:
        from app.report import bp as report_bp
        app.register_blueprint(report_bp, url_prefix='/report')
        logger.info("Blueprint report registrado")
    except ImportError as e:
        logger.warning(f"No se pudo importar report blueprint: {e}")
    
    try:
        from app.upload import bp as upload_bp
        app.register_blueprint(upload_bp, url_prefix='/upload')
        logger.info("Blueprint upload registrado")
    except ImportError as e:
        logger.warning(f"No se pudo importar upload blueprint: {e}")
    
    # Manejadores de error
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Error interno del servidor: {error}")
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e
        logger.error(f"Error no controlado: {e}", exc_info=True)
        return render_template('errors/500.html'), 500
    
    # Contexto de template global
    @app.context_processor
    def inject_debug():
        return dict(debug=app.debug)
    
    # Ruta de salud
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'version': '2.0.0'}, 200
    
    logger.info(f"Aplicación Flask creada exitosamente - config: {config_name}, debug: {app.debug}")
    
    return app
