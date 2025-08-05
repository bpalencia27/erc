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
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("erc_insight")
cache = Cache()

def create_app(config_name='development'):
    """Factory pattern para crear la aplicación Flask"""
    
    # Inicializar Flask
    app = Flask(__name__)
    
    # Cargar configuración
    from config import get_config
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Inicializar Sentry para monitoreo en producción
    if config.SENTRY_DSN and config.FLASK_ENV == 'production':
        sentry_sdk.init(
            dsn=config.SENTRY_DSN,
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
        )
    
    # Inicializar extensiones
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    cache.init_app(app)
    
    # Crear directorios necesarios
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
    Path('logs').mkdir(exist_ok=True)
    
    # Configurar logging
    if not app.debug and not app.testing:
        file_handler = logging.handlers.RotatingFileHandler(
            'logs/erc_insight.log',
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('ERC Insight startup')
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    # Registrar filtros de template
    register_template_filters(app)
    
    logger.info(f"Aplicación Flask creada exitosamente - config: {config_name}, debug: {app.debug}")
    
    return app

def register_blueprints(app):
    """Registra todos los blueprints de la aplicación"""
    from app.main import bp as main_bp
    from app.api import bp as api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    logger.debug("Blueprints registrados correctamente")

def register_error_handlers(app):
    """Registra manejadores de errores personalizados"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"Página no encontrada: {request.path}")
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Error interno del servidor: {str(error)}")
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e
        logger.error(f"Error no manejado: {str(e)}", exc_info=True)
        return render_template('errors/500.html'), 500

def register_template_filters(app):
    """Registra filtros personalizados para Jinja2"""
    
    @app.template_filter('dateformat')
    def dateformat(value, format='%Y-%m-%d'):
        """Formatea una fecha"""
        if value is None:
            return ""
        return value.strftime(format)
    
    @app.template_filter('currency')
    def currency(value):
        """Formatea un valor como moneda"""
        return f"${value:,.2f}"
