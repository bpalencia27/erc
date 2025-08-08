"""
Configuración de la aplicación
"""
import os
from dotenv import load_dotenv
import logging
import sys

# Cargar variables de entorno desde .env si existe
if os.path.exists('.env'):
    load_dotenv()

class Config:
    """Configuración base."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-por-defecto'
    
    # Gestionar correctamente la URL de la base de datos para Render.com
    DATABASE_URL = os.environ.get('DATABASE_URL', '')
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Usar rutas absolutas para los directorios de archivos
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    REPORT_FOLDER = os.environ.get('REPORT_FOLDER') or os.path.join(BASE_DIR, 'app', 'static', 'reports')
    
    # API Key para Gemini
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Limitación de tamaño para archivos subidos (15MB)
    MAX_CONTENT_LENGTH = 15 * 1024 * 1024
    
    @staticmethod
    def init_app(app):
        """Inicializar la aplicación con esta configuración."""
        # Asegurar que los directorios de carga y reportes existan
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.REPORT_FOLDER, exist_ok=True)

class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or os.environ.get('DATABASE_URL') or 'sqlite:///dev.db'
    
class TestingConfig(Config):
    """Configuración para pruebas."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Configuración de logging para producción
        # En entornos cloud como Render.com, es mejor loggear a stdout/stderr
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)
        
        # Configuración de seguridad para producción
        @app.after_request
        def add_security_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            return response

# Configuración según el entorno
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    
    'default': DevelopmentConfig
}
