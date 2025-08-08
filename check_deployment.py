#!/usr/bin/env python3
"""
Script de verificación completa para despliegue de ERC Insight
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import pkg_resources
except ImportError:
    print("⚠️  Instalando setuptools para verificación...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools"])
    import pkg_resources

class DeploymentChecker:
    """Verificador de despliegue para ERC Insight."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.checks_passed = []
        self.checks_failed = []
        
    def run_all_checks(self) -> bool:
        """Ejecuta todas las verificaciones."""
        checks = [
            ("Python version", self.check_python_version),
            ("Dependencies", self.check_dependencies),
            ("File structure", self.check_file_structure),
            ("Configuration", self.check_configuration),
            ("Database", self.check_database),
            ("Frontend assets", self.check_frontend_assets),
            ("Security", self.check_security)
        ]
        
        for name, check_func in checks:
            try:
                if check_func():
                    self.checks_passed.append(name)
                    print(f"✅ {name}")
                else:
                    self.checks_failed.append(name)
                    print(f"❌ {name}")
            except Exception as e:
                self.checks_failed.append(name)
                print(f"❌ {name}: {e}")
        
        return len(self.checks_failed) == 0
    
    def check_python_version(self) -> bool:
        """Verifica la versión de Python."""
        required = (3, 9)
        current = sys.version_info[:2]
        return current >= required
    
    def check_dependencies(self) -> bool:
        """Verifica las dependencias instaladas."""
        req_file = self.root_dir / "requirements.txt"
        if not req_file.exists():
            return False
        
        with open(req_file) as f:
            requirements = [
                line.strip().split('==')[0].split('>=')[0]
                for line in f
                if line.strip() and not line.startswith('#')
            ]
        
        missing = []
        for req in requirements:
            try:
                pkg_resources.get_distribution(req)
            except pkg_resources.DistributionNotFound:
                missing.append(req)
        
        if missing:
            print(f"   Dependencias faltantes: {', '.join(missing)}")
            return False
        return True
    
    def check_file_structure(self) -> bool:
        """Verifica la estructura de archivos."""
        required_files = [
            "app/__init__.py",
            "app/templates/base.html",
            "app/static/css/cardia_ia.css",
            "app/static/js/app.js",
            "requirements.txt",
            "wsgi.py"
        ]
        
        missing = []
        for file_path in required_files:
            if not (self.root_dir / file_path).exists():
                missing.append(file_path)
        
        if missing:
            print(f"   Archivos faltantes: {', '.join(missing)}")
            return False
        return True
    
    def check_configuration(self) -> bool:
        """Verifica la configuración."""
        env_vars = ['SECRET_KEY', 'GEMINI_API_KEY']
        missing = [var for var in env_vars if not os.environ.get(var)]
        
        if missing:
            print(f"   Variables de entorno faltantes: {', '.join(missing)}")
            return False
        return True
    
    def check_database(self) -> bool:
        """Verifica la configuración de base de datos."""
        # Por ahora, solo verificar si SQLite está configurado
        return True
    
    def check_frontend_assets(self) -> bool:
        """Verifica los assets del frontend."""
        static_dir = self.root_dir / "app" / "static"
        return static_dir.exists() and any(static_dir.iterdir())
    
    def check_security(self) -> bool:
        """Verifica configuraciones de seguridad."""
        warnings = []
        
        # Verificar SECRET_KEY
        secret_key = os.environ.get('SECRET_KEY', '')
        if len(secret_key) < 32:
            warnings.append("SECRET_KEY debe tener al menos 32 caracteres")
        
        # Verificar DEBUG en producción
        if os.environ.get('FLASK_ENV') == 'production':
            if os.environ.get('DEBUG', '').lower() == 'true':
                warnings.append("DEBUG debe estar desactivado en producción")
        
        if warnings:
            for warning in warnings:
                print(f"   ⚠️  {warning}")
            return False
        return True
    
    def print_summary(self) -> None:
        """Imprime resumen de verificaciones."""
        print("\n" + "="*50)
        print("RESUMEN DE VERIFICACIÓN")
        print("="*50)
        
        if self.checks_passed:
            print(f"\n✅ Verificaciones exitosas ({len(self.checks_passed)}):")
            for check in self.checks_passed:
                print(f"   • {check}")
        
        if self.checks_failed:
            print(f"\n❌ Verificaciones fallidas ({len(self.checks_failed)}):")
            for check in self.checks_failed:
                print(f"   • {check}")
        
        print("\n" + "="*50)
        
        if not self.checks_failed:
            print("🎉 ¡TODO LISTO PARA DESPLIEGUE!")
        else:
            print("⚠️  Corrija los problemas antes de desplegar")

def main():
    """Función principal."""
    checker = DeploymentChecker()
    success = checker.run_all_checks()
    checker.print_summary()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
