#!/usr/bin/env python3
"""
Script de verificación rápida para el proyecto ERC
"""
import sys
import importlib

def test_imports():
    """Prueba las importaciones principales"""
    modules_to_test = [
        'flask',
        'flask_cors', 
        'flask_caching',
        'werkzeug.exceptions',
        'dotenv',
        'google.generativeai',
        'pydantic',
        'pydantic_settings',
        'tenacity',
        'structlog'
    ]
    
    failed = []
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed.append(module)
    
    if failed:
        print(f"\n⚠️  Faltaron {len(failed)} módulos")
        print("Ejecute: pip install " + " ".join(failed))
        return False
    else:
        print("\n🎉 ¡Todas las importaciones exitosas!")
        return True

def test_app_import():
    """Prueba importar la aplicación"""
    try:
        from app import create_app
        app = create_app('development')
        print("✅ Aplicación creada exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error creando aplicación: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verificando importaciones...")
    imports_ok = test_imports()
    
    print("\n🔍 Verificando aplicación...")
    app_ok = test_app_import()
    
    if imports_ok and app_ok:
        print("\n✅ ¡Todo funciona correctamente!")
        sys.exit(0)
    else:
        print("\n❌ Hay problemas que resolver")
        sys.exit(1)
