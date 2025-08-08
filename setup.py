#!/usr/bin/env python3
"""
Script de instalación y configuración automática para ERC Insight
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Función principal de instalación"""
    print("🚀 Configurando ERC Insight...")
    
    # 1. Verificar Python
    if sys.version_info < (3, 9):
        print("❌ Se requiere Python 3.9 o superior")
        return False
    
    print(f"✅ Python {sys.version}")
    
    # 2. Crear entorno virtual si no existe
    venv_path = Path("venv")
    if not venv_path.exists():
        print("📦 Creando entorno virtual...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    else:
        print("✅ Entorno virtual ya existe")
    
    # 3. Activar entorno virtual y instalar dependencias
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    print("📦 Instalando dependencias...")
    subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
    
    # 4. Crear archivo .env si no existe
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creando archivo .env...")
        subprocess.run(["copy", ".env.example", ".env"], shell=True, check=True)
    
    # 5. Verificar instalación
    print("🔍 Verificando instalación...")
    try:
        result = subprocess.run([
            str(python_path), "-c", 
            "from app import create_app; app = create_app('development'); print('App creada correctamente')"
        ], capture_output=True, text=True, check=True)
        print("✅ Verificación exitosa")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en verificación: {e}")
        return False
    
    print("\n" + "="*60)
    print("🎉 ¡Instalación completada exitosamente!")
    print("\n📋 Próximos pasos:")
    print("1. Edita el archivo .env con tu API key de Gemini")
    print("2. Ejecuta: python run.py (para desarrollo)")
    print("3. O ejecuta: gunicorn wsgi:app (para producción)")
    print("="*60)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error durante la instalación: {e}")
        sys.exit(1)
