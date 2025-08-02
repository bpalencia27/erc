"""
Punto de entrada para servidor WSGI en producción
"""
from app import create_app

app = create_app('config.ProductionConfig')

if __name__ == "__main__":
    app.run()
