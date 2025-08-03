"""
Configuración de la aplicación
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    """Configuración base."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-predeterminada'
    UPLOAD_FOLDER = 'app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # Configuración de Gemini API
    GEMINI_API_KEY = os.environ.get('GOOGLE_AI_API_KEY')
    
    # Configuración de logging
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Configuración para pruebas."""
    DEBUG = False
    TESTING = True

class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False
    TESTING = False

# Mapeo de configuraciones
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
