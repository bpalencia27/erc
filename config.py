
"""
Configuración de la aplicación
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    """Configuración base adaptable a Render y desarrollo local."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-clave-secreta-muy-dificil-de-adivinar'
    UPLOAD_FOLDER = 'app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

    # Configuración de base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # Fix para Render: convertir postgres:// a postgresql://
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///erc_insight.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de Gemini API
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_AI_API_KEY')

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
