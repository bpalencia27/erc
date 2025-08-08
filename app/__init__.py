"""
Aplicación Flask para ERC Insight
"""
import os
import logging
from pathlib import Path
from datetime import timedelta
from flask import Flask, render_template
from flask_cors import CORS
from flask_caching import Cache
from werkzeug.exceptions import HTTPException
from logging.handlers import RotatingFileHandler

# Importar extensiones si existen
try:
    from app.extensions import db, migrate, csrf
    HAS_DB = True
except ImportError:
    HAS_DB = False

def create_app(config_name='development'):
    """Crea y configura la aplicación Flask.

    Acepta ya sea un nombre de configuración (str) o una clase/objeto
    con atributos de configuración (por ejemplo, usado en tests).
    """
    app = Flask(__name__)

    # Cargar configuración
    if isinstance(config_name, str):
        from config import config as CONFIG_MAP
        cfg = CONFIG_MAP.get(config_name, CONFIG_MAP.get('default'))
        app.config.from_object(cfg)
        # Inicializar la configuración si el objeto tiene init_app
        if hasattr(cfg, 'init_app'):
            cfg.init_app(app)
    else:
        # Se asume que es una clase u objeto de configuración (tests)
        app.config.from_object(config_name)
        if hasattr(config_name, 'init_app'):
            config_name.init_app(app)
    
    # Configurar seguridad de cookies
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    
    # Inicializar CORS con configuración más segura
    CORS(app, resources={
        r"/*": {
            "origins": app.config.get('ALLOWED_ORIGINS', ["http://localhost:5000"]),
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Range", "X-Content-Range"],
            "supports_credentials": True
        }
    })
    
    # Inicializar Cache
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})
    
    # Inicializar CSRF protection
    csrf.init_app(app)
    
    # Inicializar base de datos si está disponible
    if HAS_DB:
        # Solo inicializar DB si hay URI definida o si no estamos en testing sin configuración
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        if db_uri:
            db.init_app(app)
            migrate.init_app(app, db)
        else:
            app.logger.debug('Omitiendo inicialización de DB: falta SQLALCHEMY_DATABASE_URI')
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Registrar manejadores de error
    register_error_handlers(app)
    
    # Configurar logging
    if not app.debug and not app.testing:
        configure_logging(app)
    
    return app

def register_blueprints(app):
    """Registra todos los blueprints de la aplicación."""
    blueprints = [
        ('app.main', 'main', '/'),
        ('app.api', 'api', '/api'),
        ('app.report', 'report', '/report'),
        ('app.upload', 'upload', '/upload'),
        ('app.patient', 'patient', '/patient')
    ]
    
    for module_name, bp_name, url_prefix in blueprints:
        try:
            module = __import__(module_name, fromlist=['bp'])
            app.register_blueprint(module.bp, url_prefix=url_prefix)
        except ImportError as e:
            app.logger.warning(f"No se pudo cargar {module_name}: {e}")

def register_error_handlers(app):
    """Registra manejadores de errores personalizados."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Error interno: {error}")
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e
        app.logger.error(f"Error no controlado: {e}", exc_info=True)
        return render_template('errors/500.html'), 500

def configure_logging(app):
    """Configura el sistema de logging."""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/erc_insight.log',
        maxBytes=10240000,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('ERC Insight startup')

