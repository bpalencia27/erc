"""
ERC Insight Application Factory
Implementa el patrón Application Factory con mejores prácticas 2025
"""
import os
import pathlib
from flask import Flask, render_template, request
from flask_cors import CORS
from flask_caching import Cache
import structlog
from werkzeug.middleware.proxy_fix import ProxyFix

from config import get_config
from app.extensions import db, migrate

logger = structlog.get_logger()

# Inicializar extensiones
cache = Cache()

def create_app(config_name: str = None) -> Flask:
    """
    Factory function para crear la aplicación Flask
    Args:
        config_name: Nombre de la configuración a usar (development, testing, production)
    Returns:
        Flask application instance
    """
    # Configura correctamente la ruta de las plantillas
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    app = Flask(__name__, template_folder=template_dir)
    
    # Cargar configuración
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Debug de plantillas
    print(f"Template folder: {app.template_folder}")
    print(f"Template folder exists: {os.path.exists(app.template_folder)}")
    error_template_path = os.path.join(app.template_folder, 'errors', '404.html')
    print(f"Error template path: {error_template_path}")
    print(f"Error template exists: {os.path.exists(error_template_path)}")
    
    # Inicializar la configuración específica del entorno
    config_class.init_app(app)
    
    # Configurar ProxyFix para entornos detrás de proxy (Render, etc)
    if app.config.get('ENV') == 'production':
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['*']))
    cache.init_app(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Registrar error handlers
    register_error_handlers(app)
    
    # Registrar comandos CLI
    register_cli_commands(app)
    
    # Health check endpoint
    @app.route('/health')
    @app.route('/healthz')
    def health_check():
        """Endpoint para health checks (Render.com, K8s, etc)"""
        try:
            # Verificar conexión a base de datos
            db.session.execute(db.text('SELECT 1'))
            db_status = 'healthy'
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            db_status = 'unhealthy'
        
        return {
            'status': 'healthy' if db_status == 'healthy' else 'degraded',
            'timestamp': os.environ.get('RENDER_GIT_COMMIT', 'local'),
            'database': db_status,
            'version': '1.0.0'
        }
    
    logger.info(f"Application created with config: {config_name}")
    return app

def register_blueprints(app: Flask) -> None:
    """Registra todos los blueprints de la aplicación"""
    # Importar blueprints
    from app.main import bp as main_bp
    from app.api import bp as api_bp
    from app.patient import bp as patient_bp
    from app.report import bp as report_bp
    from app.upload import bp as upload_bp
    
    # Registrar con prefijos URL
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(upload_bp, url_prefix='/upload')
    
    logger.info("Blueprints registered successfully")

def register_error_handlers(app: Flask) -> None:
    """Registra manejadores de errores globales"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        if 'api' in request.path:
            return {'error': 'Resource not found'}, 404
        
        try:
            # Intenta renderizar la plantilla
            return render_template('errors/404.html'), 404
        except Exception as e:
            logger.error("Error rendering 404 template", error=str(e))
            # Fallback a HTML en línea si la plantilla falla
            html = '''
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>404 - Página no encontrada</title>
                <!-- Referencias externas eliminadas por reglas internas -->
            </head>
            <body style="background-color:#f3f4f6;font-family:sans-serif;">
                <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;">
                    <div style="background:#fff;padding:2rem;border-radius:0.5rem;box-shadow:0 2px 8px #0001;max-width:400px;width:100%;text-align:center;">
                        <h1 style="font-size:5rem;font-weight:bold;color:#6366f1;">404</h1>
                        <h2 style="font-size:1.5rem;font-weight:600;margin-top:1rem;color:#1e293b;">Página no encontrada</h2>
                        <p style="margin-top:0.5rem;color:#64748b;">Lo sentimos, la página que buscas no existe o ha sido movida.</p>
                        <div style="margin-top:1.5rem;">
                            <a href="/" style="display:inline-block;padding:0.5rem 1rem;background:#6366f1;color:#fff;font-weight:500;border-radius:0.375rem;text-decoration:none;">Volver al inicio</a>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            '''
            return html, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        logger.error("Internal server error", error=str(error))
        if 'api' in request.path:
            return {'error': 'Internal server error'}, 500
        
        try:
            # Intenta renderizar la plantilla
            return render_template('errors/500.html'), 500
        except Exception as e:
            logger.error("Error rendering 500 template", error=str(e))
            # Fallback a HTML en línea si la plantilla falla
            html = '''
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>500 - Error del servidor</title>
                <!-- Referencias externas eliminadas por reglas internas -->
            </head>
            <body style="background-color:#f3f4f6;font-family:sans-serif;">
                <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;">
                    <div style="background:#fff;padding:2rem;border-radius:0.5rem;box-shadow:0 2px 8px #0001;max-width:400px;width:100%;text-align:center;">
                        <h1 style="font-size:5rem;font-weight:bold;color:#ef4444;">500</h1>
                        <h2 style="font-size:1.5rem;font-weight:600;margin-top:1rem;color:#1e293b;">Error del servidor</h2>
                        <p style="margin-top:0.5rem;color:#64748b;">Lo sentimos, ha ocurrido un error en el servidor. Nuestro equipo ha sido notificado.</p>
                        <div style="margin-top:1.5rem;">
                            <a href="/" style="display:inline-block;padding:0.5rem 1rem;background:#6366f1;color:#fff;font-weight:500;border-radius:0.375rem;text-decoration:none;">Volver al inicio</a>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            '''
            return html, 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return {'error': 'File too large. Maximum size is 15MB'}, 413

def register_cli_commands(app: Flask) -> None:
    """Registra comandos CLI personalizados"""
    
    @app.cli.command()
    def init_db():
        """Inicializa la base de datos"""
        db.create_all()
        logger.info("Database initialized")
    
    @app.cli.command()
    def seed_db():
        """Puebla la base de datos con datos de prueba"""
        # Implementar seeding si es necesario
        logger.info("Database seeded")
