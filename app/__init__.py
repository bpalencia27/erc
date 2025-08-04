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
    config[config_name].init_app(app)
    
    # Inicializar extensiones
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configurar logging
    setup_logging(app, config_name)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Registrar comandos CLI
    from app.commands import register_commands
    register_commands(app)
    
    return app

def setup_logging(app, config_name):
    """Configura el sistema de logging para la aplicación."""
    # Crear directorio de logs con ruta absoluta
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configurar logging basado en el entorno
    if config_name == 'production':
        # En producción, la clase ProductionConfig ya configura el handler de stdout
        pass
    else:
        # En desarrollo, configurar logging a archivo
        file_handler = RotatingFileHandler(
            os.path.join(logs_dir, 'erc_insight.log'), 
            maxBytes=10240, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
    app.logger.setLevel(logging.INFO)
    app.logger.info('ERC Insight startup')

def register_blueprints(app):
    """Registra todos los blueprints de la aplicación."""
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from app.upload import bp as upload_bp
    app.register_blueprint(upload_bp, url_prefix='/upload')
    
    from app.patient import bp as patient_bp
    app.register_blueprint(patient_bp, url_prefix='/patient')
    
    from app.report import bp as report_bp
    app.register_blueprint(report_bp, url_prefix='/report')
    
    # Añadir otros blueprints según sea necesario
    try:
        from app.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
    except ImportError:
        app.logger.warning("Blueprint 'auth' no encontrado o no configurado correctamente.")

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(__file__), 'static', 'uploads'))
REPORT_FOLDER = os.environ.get('REPORT_FOLDER', os.path.join(os.path.dirname(__file__), 'static', 'reports'))

# Esta parte es redundante ya que lo manejamos en Config.init_app
# Las carpetas se crearán cuando se inicialice la aplicación
