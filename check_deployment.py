<<<<<<< HEAD
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
=======
#!/usr/bin/env python3
"""
Script de verificación completa para despliegue de ERC Insight
Versión mejorada con análisis exhaustivo
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import pkg_resources
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class DeploymentChecker:
    """Clase para verificar el estado del despliegue"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.passed_checks = []
        
    def run_all_checks(self) -> bool:
        """Ejecuta todas las verificaciones"""
        print("🔍 VERIFICACIÓN COMPLETA DE DESPLIEGUE - ERC INSIGHT")
        print("=" * 60)
        
        checks = [
            ("📁 Estructura de archivos", self.check_file_structure),
            ("📦 Dependencias", self.check_dependencies),
            ("⚙️ Configuración", self.check_configuration),
            ("🔧 Variables de entorno", self.check_environment),
            ("🐍 Código Python", self.check_python_syntax),
            ("🌐 Frontend", self.check_frontend_assets),
            ("📋 Archivos de despliegue", self.check_deployment_files),
            ("🧪 Tests básicos", self.check_basic_tests),
            ("🔐 Seguridad", self.check_security)
        ]
        
        for name, check_func in checks:
            try:
                print(f"\n{name}...")
                check_func()
            except Exception as e:
                self.errors.append(f"{name}: {str(e)}")
                print(f"❌ Error en {name}: {e}")
        
        return self.print_summary()
    
    def check_file_structure(self):
        """Verificar estructura de archivos críticos"""
        required_files = [
            'wsgi.py', 'run.py', 'config.py', 'requirements.txt',
            'render.yaml', 'runtime.txt', '.env.example',
            'app/__init__.py', 'app/main/__init__.py', 'app/api/__init__.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.errors.append(f"Archivos faltantes: {', '.join(missing_files)}")
        else:
            self.passed_checks.append("Estructura de archivos completa")
            
        # Verificar archivos no deseados
        unwanted_patterns = ['*.pyc', '__pycache__', 'venv', '.env']
        found_unwanted = []
        
        for pattern in unwanted_patterns:
            if pattern == 'venv' and (self.project_root / 'venv').exists():
                found_unwanted.append('venv/')
            elif pattern == '.env' and (self.project_root / '.env').exists():
                self.warnings.append("Archivo .env encontrado - asegúrate de no subirlo a git")
        
        if found_unwanted:
            self.warnings.append(f"Archivos/directorios que no deberían estar en git: {', '.join(found_unwanted)}")

    def check_dependencies(self):
        """Verificar dependencias instaladas"""
        req_file = self.project_root / "requirements.txt"
        if not req_file.exists():
            self.errors.append("requirements.txt no encontrado")
            return
            
        try:
            with open(req_file) as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            
            missing = []
            outdated = []
            
            for requirement in requirements:
                try:
                    pkg_name = requirement.split("==")[0].split(">=")[0].strip()
                    installed = pkg_resources.get_distribution(pkg_name)
                    
                    # Verificar versión si está especificada
                    if "==" in requirement:
                        required_version = requirement.split("==")[1].strip()
                        if installed.version != required_version:
                            outdated.append(f"{pkg_name}: {installed.version} -> {required_version}")
                            
                except pkg_resources.DistributionNotFound:
                    missing.append(requirement)
                except Exception as e:
                    self.warnings.append(f"Error verificando {requirement}: {e}")
            
            if missing:
                self.errors.append(f"Dependencias faltantes: {', '.join(missing)}")
            else:
                self.passed_checks.append(f"{len(requirements)} dependencias verificadas")
                
            if outdated:
                self.warnings.append(f"Versiones desactualizadas: {', '.join(outdated)}")
                
        except Exception as e:
            self.errors.append(f"Error leyendo requirements.txt: {e}")

    def check_configuration(self):
        """Verificar archivos de configuración"""
        try:
            # Verificar config.py
            sys.path.insert(0, str(self.project_root))
            from config import get_config
            
            # Probar configuraciones
            environments = ['development', 'production', 'testing']
            for env in environments:
                try:
                    config = get_config(env)
                    if not hasattr(config, 'SECRET_KEY'):
                        self.errors.append(f"Configuración {env} sin SECRET_KEY")
                except Exception as e:
                    self.errors.append(f"Error en configuración {env}: {e}")
            
            self.passed_checks.append("Configuraciones válidas")
            
        except ImportError as e:
            self.errors.append(f"Error importando config.py: {e}")
        except Exception as e:
            self.errors.append(f"Error verificando configuración: {e}")

    def check_environment(self):
        """Verificar variables de entorno"""
        env_example = self.project_root / ".env.example"
        if not env_example.exists():
            self.errors.append(".env.example no encontrado")
            return
            
        try:
            with open(env_example) as f:
                lines = [line.strip() for line in f if '=' in line and not line.startswith('#')]
            
            required_vars = []
            for line in lines:
                var_name = line.split('=')[0].strip()
                if var_name:
                    required_vars.append(var_name)
            
            critical_vars = ['SECRET_KEY', 'GEMINI_API_KEY', 'DATABASE_URL']
            missing_critical = [var for var in critical_vars if var not in required_vars]
            
            if missing_critical:
                self.errors.append(f"Variables críticas faltantes en .env.example: {', '.join(missing_critical)}")
            else:
                self.passed_checks.append("Variables de entorno documentadas")
                
        except Exception as e:
            self.errors.append(f"Error verificando .env.example: {e}")

    def check_python_syntax(self):
        """Verificar sintaxis de archivos Python críticos"""
        python_files = [
            'wsgi.py', 'run.py', 'config.py',
            'app/__init__.py', 'app/main/routes.py', 'app/api/routes.py'
        ]
        
        syntax_errors = []
        for file_path in python_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        source = f.read()
                    compile(source, str(full_path), 'exec')
                except SyntaxError as e:
                    syntax_errors.append(f"{file_path}: {e}")
                except Exception as e:
                    self.warnings.append(f"Error verificando {file_path}: {e}")
        
        if syntax_errors:
            self.errors.append(f"Errores de sintaxis: {'; '.join(syntax_errors)}")
        else:
            self.passed_checks.append("Sintaxis Python válida")

    def check_frontend_assets(self):
        """Verificar recursos frontend"""
        css_files = list((self.project_root / "app/static/css").glob("*.css")) if (self.project_root / "app/static/css").exists() else []
        js_files = list((self.project_root / "app/static/js").glob("*.js")) if (self.project_root / "app/static/js").exists() else []
        
        if not css_files and not js_files:
            self.warnings.append("No se encontraron archivos CSS/JS")
        else:
            self.passed_checks.append(f"Frontend: {len(css_files)} CSS, {len(js_files)} JS")
        
        # Verificar templates
        templates_dir = self.project_root / "app/templates"
        if templates_dir.exists():
            templates = list(templates_dir.glob("*.html"))
            if templates:
                self.passed_checks.append(f"{len(templates)} templates encontrados")
            else:
                self.warnings.append("No se encontraron templates HTML")

    def check_deployment_files(self):
        """Verificar archivos específicos de despliegue"""
        render_yaml = self.project_root / "render.yaml"
        runtime_txt = self.project_root / "runtime.txt"
        procfile = self.project_root / "Procfile"
        
        if not render_yaml.exists():
            self.errors.append("render.yaml no encontrado")
        else:
            try:
                import yaml
                with open(render_yaml) as f:
                    yaml.safe_load(f)
                self.passed_checks.append("render.yaml válido")
            except ImportError:
                self.warnings.append("PyYAML no instalado, no se puede verificar render.yaml")
            except Exception as e:
                self.errors.append(f"Error en render.yaml: {e}")
        
        if not runtime_txt.exists():
            self.errors.append("runtime.txt no encontrado")
        else:
            with open(runtime_txt) as f:
                runtime = f.read().strip()
                if not runtime.startswith('python-'):
                    self.errors.append("runtime.txt debe especificar versión de Python")
                else:
                    self.passed_checks.append(f"Runtime: {runtime}")

    def check_basic_tests(self):
        """Ejecutar tests básicos"""
        try:
            # Verificar que la aplicación se puede importar
            sys.path.insert(0, str(self.project_root))
            from app import create_app
            
            app = create_app('testing')
            if app:
                self.passed_checks.append("Aplicación se puede crear")
            else:
                self.errors.append("No se puede crear la aplicación")
                
        except Exception as e:
            self.errors.append(f"Error creando aplicación de prueba: {e}")

    def check_security(self):
        """Verificar aspectos de seguridad"""
        security_issues = []
        
        # Verificar que no hay .env en git
        if (self.project_root / ".env").exists():
            security_issues.append("Archivo .env presente (no debe estar en git)")
        
        # Verificar .gitignore
        gitignore = self.project_root / ".gitignore"
        if gitignore.exists():
            with open(gitignore) as f:
                gitignore_content = f.read()
                if '.env' not in gitignore_content:
                    security_issues.append(".env no está en .gitignore")
                if 'venv/' not in gitignore_content:
                    security_issues.append("venv/ no está en .gitignore")
        else:
            security_issues.append(".gitignore no encontrado")
        
        if security_issues:
            self.warnings.extend(security_issues)
        else:
            self.passed_checks.append("Configuración de seguridad básica OK")

    def print_summary(self) -> bool:
        """Imprimir resumen final"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE VERIFICACIÓN")
        print("=" * 60)
        
        if self.passed_checks:
            print(f"\n✅ VERIFICACIONES EXITOSAS ({len(self.passed_checks)}):")
            for check in self.passed_checks:
                print(f"   ✓ {check}")
        
        if self.warnings:
            print(f"\n⚠️  ADVERTENCIAS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   ⚠ {warning}")
        
        if self.errors:
            print(f"\n❌ ERRORES CRÍTICOS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   ✗ {error}")
            print(f"\n🚨 RESULTADO: FALLÓ - Corrige {len(self.errors)} errores antes del despliegue")
            return False
        else:
            print(f"\n🎉 RESULTADO: LISTO PARA DESPLIEGUE")
            print("✨ Tu aplicación está lista para subir a Render.com")
            return True

def main():
    """Función principal"""
    print("🚀 ERC Insight - Verificador de Despliegue v2.0")
    checker = DeploymentChecker()
    success = checker.run_all_checks()
    
    if success:
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. git add .")
        print("2. git commit -m 'Preparación para despliegue'")
        print("3. git push origin main")
        print("4. Configurar en Render.com usando render.yaml")
        print("5. Agregar GEMINI_API_KEY en variables de entorno")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
>>>>>>> 1a009ef5 ( Preparación completa para despliegue en Render.com)
