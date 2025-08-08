#!/usr/bin/env python3
"""
Script principal para ejecutar ERC Insight
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv no instalado. Usando variables de entorno del sistema.")

def main():
    """Función principal para ejecutar la aplicación."""
    try:
        from app import create_app
        
        # Determinar entorno
        env = os.environ.get('FLASK_ENV', 'development')
        
        # Crear aplicación
        app = create_app(env)
        
        # Configurar puerto
        port = int(os.environ.get('PORT', 5000))
        
        # Ejecutar servidor
        if env == 'development':
            app.run(
                host='0.0.0.0',
                port=port,
                debug=True,
                use_reloader=True
            )
        else:
            # En producción, usar gunicorn
            print(f"✅ Aplicación lista en modo {env}")
            print(f"   Usar: gunicorn -w 4 -b 0.0.0.0:{port} wsgi:app")
            
    except ImportError as e:
        print(f"❌ Error al importar módulos: {e}")
        print("   Ejecute: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
