"""
Configuración para entorno de pruebas
"""

import os

# Configuración base
class Config:
    # Configuración de seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-por-defecto'
    
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Carpeta de subida de archivos
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'static', 'uploads')
    
    # Configuración de logging
    LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'erc_insight.log')
    LOG_LEVEL = 'INFO'
    
    # API Keys
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or 'dummy-api-key-for-testing'
    
    # Límites de archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

# Configuración para desarrollo
class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

# Configuración para pruebas
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = 'DEBUG'

# Configuración para producción
class ProductionConfig(Config):
    DEBUG = False
    # En producción, usar una clave secreta real
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-produccion'
    # En producción, usar una base de datos PostgreSQL o similar
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'

# Diccionario para seleccionar la configuración
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
