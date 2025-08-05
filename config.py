"""
Configuración centralizada para ERC Insight
Actualizado: Agosto 2025
"""
import os
import secrets
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional
import logging

logger = logging.getLogger("erc_insight")

# Configurar logger
class Settings(BaseSettings):
    """Configuración con validación usando Pydantic v2"""
    
    # Flask Config
    SECRET_KEY: str = secrets.token_urlsafe(32)
    FLASK_APP: str = "wsgi.py"
    FLASK_ENV: str = "development"
    DEBUG: bool = False
    TESTING: bool = False
    
    # Database
    DATABASE_URL: Optional[str] = None
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        "pool_size": 10,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
        "max_overflow": 20
    }
    
    # Google Gemini API
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-pro"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 8192
    
    # File Upload
    UPLOAD_FOLDER: Path = Path("uploads")
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS: set = {'.pdf', '.txt', '.png', '.jpg', '.jpeg'}
    
    # Security
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    WTF_CSRF_ENABLED: bool = True
    WTF_CSRF_TIME_LIMIT: Optional[int] = None
    
    # Caching
    CACHE_TYPE: str = "RedisCache"
    CACHE_REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_DEFAULT_TIMEOUT: int = 300
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_TO_STDOUT: bool = True
    SENTRY_DSN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Configuraciones por entorno
class DevelopmentConfig(Settings):
    DEBUG: bool = True
    FLASK_ENV: str = "development"
    LOG_LEVEL: str = "DEBUG"
    SESSION_COOKIE_SECURE: bool = False

class ProductionConfig(Settings):
    DEBUG: bool = False
    FLASK_ENV: str = "production"
    LOG_LEVEL: str = "WARNING"
    
class TestingConfig(Settings):
    TESTING: bool = True
    WTF_CSRF_ENABLED: bool = False
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"

# Factory pattern para obtener configuración
def get_config(env: str = None) -> Settings:
    """Obtiene la configuración según el entorno"""
    env = env or os.getenv('FLASK_ENV', 'development')
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    config_class = configs.get(env, DevelopmentConfig)
    return config_class()

# Exportar configuración por defecto
config = get_config()
