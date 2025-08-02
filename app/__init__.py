from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging
from logging.handlers import RotatingFileHandler

# Crear instancia de SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class='config.ProductionConfig'):
    """Inicializa y configura la aplicación Flask."""
    
    # Crear y configurar la app
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configurar CORS
    CORS(app)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configurar logging
    configure_logging(app)
    
    # Registrar blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.patient import bp as patient_bp
    app.register_blueprint(patient_bp, url_prefix='/patient')
    
    from app.report import bp as report_bp
    app.register_blueprint(report_bp, url_prefix='/report')
    
    from app.upload import bp as upload_bp
    app.register_blueprint(upload_bp, url_prefix='/upload')
    
    # Crear directorios necesarios
    create_directories(app)
    
    # Ruta de verificación de salud
    @app.route('/health')
    def health_check():
        return {"status": "ok", "version": "1.0.0"}
    
    return app

def configure_logging(app):
    """Configura el sistema de logging."""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/erc_insight.log', 
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

def create_directories(app):
    """Crea los directorios necesarios para la aplicación."""
    # Directorio para subida de archivos
    upload_dir = os.path.join(app.static_folder, 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # Directorio para informes generados
    reports_dir = os.path.join(app.static_folder, 'reports')
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
