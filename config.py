"""
Configuración mejorada para ERC Insight - Agosto 2025
Implementa mejores prácticas de seguridad y configuración
"""
import os
import sys
import logging
import secrets
from pathlib import Path
from typing import Type, Dict, Any
from dotenv import load_dotenv
import structlog

# Configurar structlog para mejor debugging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Cargar variables de entorno con manejo robusto
env_path = Path('.env')
if env_path.exists() and 'PYTEST_CURRENT_TEST' not in os.environ:
    try:
        load_dotenv(env_path, encoding='utf-8')
    except Exception as e:
        logger.warning("Error loading .env file", error=str(e))
        # Intentar con encoding alternativo
        try:
            load_dotenv(env_path, encoding='latin-1')
        except Exception as e2:
            logger.error("Failed to load .env file", error=str(e2))

def get_database_url() -> str:
    """
    Obtiene y normaliza la URL de la base de datos.
    Compatible con Render.com y otros proveedores cloud.
    """
    url = os.environ.get('DATABASE_URL', '')
    
    # Fix para Render.com y Heroku que usan postgres://
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql+psycopg2://', 1)
    elif url.startswith('postgresql://'):
        url = url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    
    # Fallback a SQLite para desarrollo
    if not url:
        db_path = Path('instance') / 'dev.db'
        db_path.parent.mkdir(exist_ok=True)
        url = f'sqlite:///{db_path}'
    
    return url

def generate_secret_key() -> str:
    """Genera una clave secreta segura si no existe"""
    return secrets.token_urlsafe(32)

class Config:
    """Configuración base con valores seguros por defecto"""
    
    # Paths
    BASE_DIR = Path(__file__).resolve().parent
    INSTANCE_PATH = BASE_DIR / 'instance'
    
    # Flask Core
    SECRET_KEY = os.environ.get('SECRET_KEY') or generate_secret_key()
    
    # SQLAlchemy 2.0+ configuration
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'connect_timeout': 10,
        } if 'postgresql' in get_database_url() else {}
    }
    
    # File Upload Configuration
    UPLOAD_FOLDER = Path(os.environ.get('UPLOAD_FOLDER', BASE_DIR / 'app' / 'static' / 'uploads'))
    REPORT_FOLDER = Path(os.environ.get('REPORT_FOLDER', BASE_DIR / 'app' / 'static' / 'reports'))
    MAX_CONTENT_LENGTH = 15 * 1024 * 1024  # 15MB
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'csv', 'xlsx'}
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # API Keys
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')  # Backup AI
    
    # Caching
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Monitoring
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    
    @classmethod
    def init_app(cls, app):
        """Inicializar la aplicación con esta configuración"""
        # Crear directorios necesarios
        cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.REPORT_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.INSTANCE_PATH.mkdir(exist_ok=True)
        
        # Configurar Sentry si está disponible
        if cls.SENTRY_DSN:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            
            sentry_sdk.init(
                dsn=cls.SENTRY_DSN,
                integrations=[FlaskIntegration()],
                traces_sample_rate=0.1,
                profiles_sample_rate=0.1,
            )

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    
    # Desarrollo usa SQLite por defecto
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{Config.BASE_DIR / "instance" / "dev.db"}')
    
    # Desactivar seguridad de cookies para desarrollo local
    SESSION_COOKIE_SECURE = False
    
    # Hot reload
    TEMPLATES_AUTO_RELOAD = True
    
    @classmethod
    def init_app(cls, app):
        super().init_app(app)
        logger.info("Running in DEVELOPMENT mode")

class TestingConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    
    # Base de datos en memoria para tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Desactivar rate limiting en tests
    RATELIMIT_ENABLED = False

class ProductionConfig(Config):
    """Configuración para producción con máxima seguridad"""
    DEBUG = False
    TESTING = False
    
    # Forzar HTTPS
    PREFERRED_URL_SCHEME = 'https'
    
    # Headers de seguridad adicionales
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; font-src 'self'"
    }
    
    @classmethod
    def init_app(cls, app):
        super().init_app(app)
        
        # Configurar logging para producción
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        handler.setLevel(logging.INFO)
        
        if not any(isinstance(h, logging.StreamHandler) for h in app.logger.handlers):
            app.logger.addHandler(handler)
            app.logger.setLevel(logging.INFO)
        
        # Aplicar headers de seguridad
        @app.after_request
        def add_security_headers(response):
            for header, value in cls.SECURITY_HEADERS.items():
                response.headers[header] = value
            return response
        
        logger.info("Running in PRODUCTION mode with enhanced security")

# Configuración por entorno con tipo hints
config: Dict[str, Type[Config]] = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: str = None) -> Type[Config]:
    """Obtiene la configuración según el entorno"""
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    return config.get(config_name, DevelopmentConfig)
