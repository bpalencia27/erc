#!/usr/bin/env python
"""
Script de validación pre-despliegue para ERC Insight
"""
import os
import sys
import importlib.util
import subprocess
import pkg_resources

def check_python_version():
    """Verificar versión de Python"""
    required_version = (3, 9)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"⚠️ Versión de Python insuficiente: {current_version.major}.{current_version.minor}")
        print(f"   Se requiere Python {required_version[0]}.{required_version[1]} o superior")
        return False
    
    print(f"✅ Python {current_version.major}.{current_version.minor}.{current_version.micro}")
    return True

def check_dependencies():
    """Verificar dependencias instaladas"""
    try:
        with open("requirements.txt") as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        missing = []
        for requirement in requirements:
            try:
                pkg_name = requirement.split("==")[0].split(">=")[0].strip()
                pkg_resources.get_distribution(pkg_name)
            except pkg_resources.DistributionNotFound:
                missing.append(requirement)
        
        if missing:
            print("⚠️ Dependencias faltantes:")
            for req in missing:
                print(f"   - {req}")
            return False
        
        print(f"✅ {len(requirements)} dependencias verificadas")
        return True
    except Exception as e:
        print(f"⚠️ Error al verificar dependencias: {str(e)}")
        return False

def check_configuration_files():
    """Verificar archivos de configuración"""
    required_files = [
        "config.py",
        "wsgi.py",
        "runtime.txt",
        "requirements.txt",
        "render.yaml",
        ".env.example"
    ]
    
    missing = [file for file in required_files if not os.path.exists(file)]
    
    if missing:
        print("⚠️ Archivos de configuración faltantes:")
        for file in missing:
            print(f"   - {file}")
        return False
    
    print(f"✅ {len(required_files)} archivos de configuración verificados")
    return True

def run_basic_tests():
    """Ejecutar pruebas básicas"""
    try:
        result = subprocess.run(["pytest", "-xvs", "tests/test_basic.py"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"⚠️ Pruebas fallidas: {result.returncode}")
            print(result.stderr)
            return False
        
        print("✅ Pruebas básicas ejecutadas correctamente")
        return True
    except Exception as e:
        print(f"⚠️ Error al ejecutar pruebas: {str(e)}")
        return False

def check_database_config():
    """Verificar configuración de base de datos"""
    try:
        spec = importlib.util.spec_from_file_location("config", "config.py")
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        
        if not hasattr(config, 'Config') or not hasattr(config.Config, 'SQLALCHEMY_DATABASE_URI'):
            print("⚠️ Configuración de base de datos incorrecta")
            return False
        
        print("✅ Configuración de base de datos verificada")
        return True
    except Exception as e:
        print(f"⚠️ Error al verificar configuración de base de datos: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("ERC Insight - Validación Pre-Despliegue")
    print("="*50)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_configuration_files(),
        check_database_config()
    ]
    
    print("\nResumen:")
    if all(checks):
        print("✅ Todas las verificaciones pasaron correctamente")
        print("   La aplicación está lista para despliegue en Render.com")
        sys.exit(0)
    else:
        print("⚠️ Algunas verificaciones fallaron")
        print("   Corrija los problemas antes de desplegar")
        sys.exit(1)
