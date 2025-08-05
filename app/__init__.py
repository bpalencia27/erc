from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Instancias globales de extensiones
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=None):
    """Inicializa y configura la aplicación Flask."""
    if config_class is None:
        from config import ProductionConfig
        config_class = ProductionConfig

    app = Flask(__name__)
    app.config.from_object(config_class)
    # Configuración por defecto para tests si no está definida
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
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
    
    from app.upload import bp as upload_bp
    app.register_blueprint(upload_bp, url_prefix='/upload')
    
    from app.report import bp as report_bp
    app.register_blueprint(report_bp, url_prefix='/report')
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Crear directorios necesarios
    create_directories(app)
    
    # Ruta de verificación de salud
    @app.route('/health')
    def health_check():
        return {"status": "ok", "version": "1.0.0"}
    
    return app

# Función de logging básica
def configure_logging(app):
    import logging
    logging.basicConfig(level=logging.INFO)
    app.logger.info("Logging configurado correctamente.")

# Función para crear directorios necesarios
def create_directories(app):
    import os
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
