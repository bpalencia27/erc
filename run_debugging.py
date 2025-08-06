#!/usr/bin/env python3
"""
Script maestro de debugging y testing para ERC Insight
Ejecuta todos los tests críticos del sistema
"""
import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_header(title):
    """Imprime un encabezado formateado"""
    print("\n" + "="*80)
    print(f"🔍 {title}")
    print("="*80)

def print_section(title):
    """Imprime una sección"""
    print(f"\n📋 {title}")
    print("-"*60)

def run_command(command, description):
    """Ejecuta un comando y retorna el resultado"""
    print(f"🚀 Ejecutando: {description}")
    print(f"   Comando: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            print(f"   ✅ Éxito")
            if result.stdout.strip():
                print(f"   📤 Output: {result.stdout.strip()[:200]}...")
            return True, result.stdout
        else:
            print(f"   ❌ Error (código: {result.returncode})")
            if result.stderr.strip():
                print(f"   📤 Error: {result.stderr.strip()[:200]}...")
            return False, result.stderr
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
        return False, str(e)

def check_dependencies():
    """Verifica dependencias del proyecto"""
    print_section("Verificando Dependencias")
    
    # Verificar Python
    python_version = sys.version_info
    print(f"🐍 Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Verificar archivos críticos
    critical_files = [
        "app/__init__.py",
        "app/parsers/lab_parser.py",
        "app/api/gemini_client.py",
        "app/api/report_generator.py",
        "requirements.txt",
        "config.py"
    ]
    
    missing_files = []
    for file_path in critical_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (FALTANTE)")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def test_creatinine_extraction():
    """Test crítico de extracción de creatinina"""
    print_section("Test Crítico: Extracción de Creatinina")
    
    debug_script = project_root / "debug_creatinine_extractor.py"
    if not debug_script.exists():
        print("   ❌ Script de debugging no encontrado")
        return False
    
    success, output = run_command(
        f'python "{debug_script}"',
        "Debugging de extractor de creatinina"
    )
    
    # Analizar output para determinar éxito
    if success and "ÉXITO: Todos los casos pasaron correctamente" in output:
        print("   🎉 Extractor de creatinina funcionando correctamente")
        return True
    else:
        print("   🚨 Problemas detectados en extractor de creatinina")
        return False

def test_comprehensive_suite():
    """Ejecuta la suite comprehensiva de tests"""
    print_section("Suite Comprehensiva de Tests")
    
    test_script = project_root / "tests" / "test_comprehensive_suite.py"
    if not test_script.exists():
        print("   ❌ Suite de tests no encontrada")
        return False
    
    # Ejecutar tests críticos
    success, output = run_command(
        f'python "{test_script}" --critical',
        "Tests críticos del sistema"
    )
    
    return success

def test_api_endpoints():
    """Test de endpoints de API"""
    print_section("Test de Endpoints de API")
    
    # Verificar que Flask pueda importarse
    try:
        from app import create_app
        app = create_app('testing')
        print("   ✅ Aplicación Flask se puede crear")
        
        with app.test_client() as client:
            # Test de endpoint principal
            response = client.get('/')
            print(f"   📡 GET /: {response.status_code}")
            
            # Test de API de generación de reporte (mock)
            test_data = {
                'first_name': 'Test',
                'last_name': 'Patient',
                'edad': 65,
                'sexo': 'M',
                'peso': 70
            }
            
            response = client.post(
                '/api/generate_report',
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            print(f"   📡 POST /api/generate_report: {response.status_code}")
            
            return response.status_code in [200, 400]  # 400 es ok si falta API key
            
    except Exception as e:
        print(f"   ❌ Error al probar API: {e}")
        return False

def check_frontend_files():
    """Verifica archivos del frontend"""
    print_section("Verificación de Frontend")
    
    frontend_files = [
        "app/static/js/modal-manager.js",
        "app/static/js/cardia_ia.js",
        "app/static/js/api-bridge.js",
        "app/static/js/frontend-tests.js",
        "app/static/css/cardia_ia.css",
        "app/templates/base.html"
    ]
    
    missing_files = []
    for file_path in frontend_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (FALTANTE)")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def generate_report():
    """Genera reporte de debugging"""
    print_section("Generando Reporte de Debugging")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = project_root / f"debugging_report_{timestamp}.json"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "project_root": str(project_root),
        "tests_executed": [],
        "summary": {}
    }
    
    # Agregar información del sistema
    try:
        import platform
        report["system_info"] = {
            "platform": platform.platform(),
            "python_implementation": platform.python_implementation(),
            "architecture": platform.architecture()[0]
        }
    except Exception:
        pass
    
    # Guardar reporte
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"   📄 Reporte guardado en: {report_file}")
        return True
    except Exception as e:
        print(f"   ❌ Error al guardar reporte: {e}")
        return False

def main():
    """Función principal de debugging"""
    start_time = time.time()
    
    print_header("DEBUGGING COMPREHENSIVO DE ERC INSIGHT")
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Directorio: {project_root}")
    
    # Lista de tests a ejecutar
    tests = [
        ("Dependencias", check_dependencies),
        ("Archivos Frontend", check_frontend_files),
        ("Extracción de Creatinina", test_creatinine_extraction),
        ("Suite Comprehensiva", test_comprehensive_suite),
        ("Endpoints de API", test_api_endpoints),
    ]
    
    results = {}
    total_tests = len(tests)
    passed_tests = 0
    
    # Ejecutar cada test
    for test_name, test_function in tests:
        print(f"\n🔄 Ejecutando: {test_name}")
        try:
            result = test_function()
            results[test_name] = result
            if result:
                passed_tests += 1
                print(f"   ✅ {test_name}: EXITOSO")
            else:
                print(f"   ❌ {test_name}: FALLÓ")
        except Exception as e:
            print(f"   💥 {test_name}: EXCEPCIÓN - {e}")
            results[test_name] = False
    
    # Resumen final
    execution_time = time.time() - start_time
    
    print_header("RESUMEN DE DEBUGGING")
    print(f"📊 Tests ejecutados: {total_tests}")
    print(f"✅ Tests exitosos: {passed_tests}")
    print(f"❌ Tests fallidos: {total_tests - passed_tests}")
    print(f"📈 Porcentaje de éxito: {(passed_tests/total_tests*100):.1f}%")
    print(f"⏱️  Tiempo de ejecución: {execution_time:.2f} segundos")
    
    # Resultados detallados
    print("\n📋 Resultados detallados:")
    for test_name, result in results.items():
        status = "✅ EXITOSO" if result else "❌ FALLÓ"
        print(f"   {test_name}: {status}")
    
    # Recomendaciones
    print("\n💡 Recomendaciones:")
    
    if not results.get("Extracción de Creatinina", False):
        print("   🚨 CRÍTICO: Problemas en extracción de creatinina - revisar patrones de parsing")
    
    if not results.get("Suite Comprehensiva", False):
        print("   ⚠️  Algunos tests unitarios fallan - revisar lógica de negocio")
    
    if not results.get("Endpoints de API", False):
        print("   🌐 Problemas con API - verificar configuración y dependencias")
    
    if not results.get("Archivos Frontend", False):
        print("   🎨 Archivos de frontend faltantes - verificar estructura del proyecto")
    
    # Generar reporte
    generate_report()
    
    # Status de salida
    if passed_tests == total_tests:
        print("\n🎉 TODOS LOS TESTS PASARON - Sistema funcionando correctamente")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} TESTS FALLARON - Revisar problemas identificados")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
