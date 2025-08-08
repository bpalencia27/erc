#!/usr/bin/env python3
"""
Script de inicio simplificado para ERC Insight
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
    print("⚠️  python-dotenv no está instalado")

def main():
    """Función principal"""
    try:
        # Importar la aplicación
        from app import create_app
        
        # Determinar entorno
        env = os.environ.get('FLASK_ENV', 'development')
        port = int(os.environ.get('PORT', 5000))
        
        # Crear aplicación
        app = create_app(env)
        
        print(f"🚀 Iniciando ERC Insight en modo {env}")
        print(f"📱 Servidor disponible en: http://localhost:{port}")
        print(f"⚡ Entorno virtual activo: {sys.prefix}")
        
        # Ejecutar aplicación
        app.run(
            host='0.0.0.0',
            port=port,
            debug=(env == 'development'),
            use_reloader=True
        )
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrese de que:")
        print("   1. El entorno virtual esté activado")
        print("   2. Las dependencias estén instaladas: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
