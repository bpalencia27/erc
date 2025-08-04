"""
Punto de entrada para servidor WSGI en producción
"""
from app import create_app

# Usamos explícitamente la configuración de producción
app = create_app('production')

if __name__ == '__main__':
    app.run(debug=False)
