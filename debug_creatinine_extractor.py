"""
Script de debugging específico para validar la extracción de creatinina
PROBLEMA CRÍTICO: Creatinina de orina siendo tomada como sérica
"""
import sys
import os
from datetime import datetime

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.parsers.lab_parser import AdvancedLabParser, parse_lab_results
import logging

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_creatinine_cases():
    """Prueba casos específicos de creatinina"""
    
    parser = AdvancedLabParser()
    
    # Casos de prueba críticos
    test_cases = [
        {
            'name': 'CASO 1: Solo creatinina sérica',
            'text': '''
            LABORATORIO CLÍNICO
            BIOQUÍMICA SANGUÍNEA
            Creatinina sérica: 1.2 mg/dL
            Urea: 45 mg/dL
            ''',
            'expected_serica': 1.2,
            'should_detect': True
        },
        {
            'name': 'CASO 2: Solo creatinina de orina (NO debe detectar)',
            'text': '''
            EXAMEN DE ORINA
            Creatinina: 120 mg/dL
            Volumen: 50 mL
            ''',
            'expected_serica': None,
            'should_detect': False
        },
        {
            'name': 'CASO 3: Ambas presentes - solo tomar sérica',
            'text': '''
            QUÍMICA SANGUÍNEA
            Creatinina sérica: 1.5 mg/dL
            Urea: 55 mg/dL
            
            EXAMEN DE ORINA
            Creatinina: 85 mg/dL
            Proteínas: trazas
            ''',
            'expected_serica': 1.5,
            'should_detect': True
        },
        {
            'name': 'CASO 4: Creatinina en contexto de RAC',
            'text': '''
            MICROALBUMINURIA
            Albúmina: 45 mg/L
            Creatinina orina: 120 mg/dL
            RAC: 30 mg/g
            ''',
            'expected_serica': None,
            'should_detect': False
        },
        {
            'name': 'CASO 5: Clearance de creatinina (NO debe detectar)',
            'text': '''
            FUNCIÓN RENAL
            Clearance de creatinina: 85 mL/min
            Creatinina orina: 95 mg/dL
            Volumen urinario: 1200 mL
            ''',
            'expected_serica': None,
            'should_detect': False
        },
        {
            'name': 'CASO 6: Formato estándar de laboratorio',
            'text': '''
            PACIENTE: Juan Pérez
            EDAD: 65 años
            
            BIOQUÍMICA CLÍNICA
            Glucosa: 110 mg/dL
            Creatinina: 1.8 mg/dL
            BUN: 25 mg/dL
            
            ORINA ESPONTÁNEA
            Densidad: 1.020
            Proteínas: ++
            ''',
            'expected_serica': 1.8,
            'should_detect': True
        },
        {
            'name': 'CASO 7: Valor muy alto (típico de orina)',
            'text': '''
            LABORATORIO
            Creatinina: 150 mg/dL
            ''',
            'expected_serica': None,
            'should_detect': False
        },
        {
            'name': 'CASO 8: Creatinina en plasma',
            'text': '''
            PERFIL RENAL
            Creatinina plasma: 0.9 mg/dL
            Urea plasma: 35 mg/dL
            ''',
            'expected_serica': 0.9,
            'should_detect': True
        }
    ]
    
    print("🔍 DEBUGGING DE EXTRACCIÓN DE CREATININA")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 {case['name']}")
        print(f"📄 Texto de entrada:")
        print(case['text'].strip())
        print(f"\n🎯 Expectativa: {'SÍ detectar' if case['should_detect'] else 'NO detectar'} creatinina sérica")
        if case['expected_serica']:
            print(f"   Valor esperado: {case['expected_serica']} mg/dL")
        
        # Parsear
        result = parser.parse(case['text'])
        
        # Verificar resultado
        has_creatinina = 'creatinina_serica' in result.get('lab_results', {})
        detected_value = result.get('lab_results', {}).get('creatinina_serica')
        
        print(f"\n📊 Resultado:")
        print(f"   ✓ Parse exitoso: {result.get('success', False)}")
        print(f"   ✓ Creatinina detectada: {has_creatinina}")
        if has_creatinina:
            print(f"   ✓ Valor detectado: {detected_value} mg/dL")
        
        # Mostrar warnings si existen
        warnings = result.get('metadata', {}).get('warnings', [])
        if warnings:
            print(f"   ⚠️  Warnings: {warnings}")
        
        # Evaluación
        success = False
        if case['should_detect']:
            if has_creatinina and detected_value is not None:
                if case['expected_serica'] is None or abs(detected_value - case['expected_serica']) < 0.1:
                    success = True
                    print(f"   ✅ CORRECTO: Creatinina sérica detectada correctamente")
                else:
                    print(f"   ❌ ERROR: Valor incorrecto. Esperado: {case['expected_serica']}, Obtenido: {detected_value}")
            else:
                print(f"   ❌ ERROR: Debería haber detectado creatinina sérica pero no lo hizo")
        else:
            if not has_creatinina:
                success = True
                print(f"   ✅ CORRECTO: No detectó creatinina sérica (como esperado)")
            else:
                print(f"   ❌ ERROR CRÍTICO: Detectó creatinina sérica cuando NO debería ({detected_value} mg/dL)")
        
        if success:
            passed += 1
        else:
            failed += 1
        
        print("-" * 60)
    
    # Resumen
    print(f"\n📈 RESUMEN DE RESULTADOS")
    print(f"✅ Casos exitosos: {passed}/{len(test_cases)}")
    print(f"❌ Casos fallidos: {failed}/{len(test_cases)}")
    print(f"📊 Tasa de éxito: {(passed/len(test_cases)*100):.1f}%")
    
    if failed > 0:
        print(f"\n🚨 ATENCIÓN: {failed} casos fallaron. Revisar lógica de extracción.")
        return False
    else:
        print(f"\n🎉 ÉXITO: Todos los casos pasaron correctamente.")
        return True

def test_rac_extraction():
    """Prueba específicamente la extracción de RAC"""
    
    parser = AdvancedLabParser()
    
    rac_cases = [
        {
            'text': 'Relación Albúmina/Creatinina: 15 mg/g',
            'expected': 15,
            'name': 'RAC estándar'
        },
        {
            'text': 'RAC: 45.5 mg/g',
            'expected': 45.5,
            'name': 'RAC abreviado'
        },
        {
            'text': 'Microalbuminuria/Creatinina: 120 mg/g',
            'expected': 120,
            'name': 'Microalbuminuria/Creatinina'
        },
        {
            'text': '''
            MICROALBUMINURIA
            Albúmina orina: 35 mg/L
            Creatinina orina: 115 mg/dL
            Relación A/C: 25.2 mg/g
            ''',
            'expected': 25.2,
            'name': 'RAC con contexto completo'
        }
    ]
    
    print("\n🔍 TESTING DE EXTRACCIÓN DE RAC")
    print("=" * 40)
    
    for case in rac_cases:
        print(f"\n📋 {case['name']}")
        result = parser.parse(case['text'])
        
        rac_value = result.get('lab_results', {}).get('rac')
        
        if rac_value is not None:
            if abs(rac_value - case['expected']) < 0.1:
                print(f"   ✅ RAC detectado correctamente: {rac_value} mg/g")
            else:
                print(f"   ❌ RAC incorrecto. Esperado: {case['expected']}, Obtenido: {rac_value}")
        else:
            print(f"   ❌ RAC no detectado")

def test_real_lab_samples():
    """Prueba con muestras de laboratorio reales"""
    
    real_samples = [
        {
            'name': 'Laboratorio Típico 1',
            'text': '''
            LABORATORIO CLÍNICO CENTRAL
            
            Paciente: María González
            Edad: 58 años
            Sexo: Femenino
            
            QUÍMICA SANGUÍNEA
            Glucosa: 145 mg/dL
            Creatinina: 1.4 mg/dL (ALTO)
            BUN: 28 mg/dL
            Ácido úrico: 6.2 mg/dL
            
            PERFIL LIPÍDICO
            Colesterol total: 195 mg/dL
            HDL: 42 mg/dL
            LDL: 125 mg/dL
            Triglicéridos: 140 mg/dL
            
            EXAMEN DE ORINA
            Color: amarillo
            Aspecto: turbio
            Densidad: 1.025
            Proteínas: ++ (100 mg/dL)
            Glucosa: negativo
            
            MICROALBUMINURIA
            Albúmina urinaria: 85 mg/L
            Creatinina orina: 120 mg/dL
            Relación A/C: 58.5 mg/g (ALTO)
            '''
        }
    ]
    
    print("\n🔍 TESTING CON MUESTRAS REALES")
    print("=" * 50)
    
    parser = AdvancedLabParser()
    
    for sample in real_samples:
        print(f"\n📋 {sample['name']}")
        result = parser.parse(sample['text'])
        
        print("📊 Resultados extraídos:")
        
        # Datos del paciente
        patient_data = result.get('patient_data', {})
        if patient_data:
            print("   👤 Datos del paciente:")
            for key, value in patient_data.items():
                print(f"      {key}: {value}")
        
        # Resultados de laboratorio
        lab_results = result.get('lab_results', {})
        if lab_results:
            print("   🧪 Resultados de laboratorio:")
            for key, value in lab_results.items():
                print(f"      {key}: {value}")
        
        # Warnings
        warnings = result.get('metadata', {}).get('warnings', [])
        if warnings:
            print("   ⚠️  Advertencias:")
            for warning in warnings:
                print(f"      - {warning}")
        
        # Verificaciones específicas
        print("\n🔍 Verificaciones críticas:")
        
        # Verificar que creatinina sérica fue detectada
        creat_serica = lab_results.get('creatinina_serica')
        if creat_serica:
            print(f"   ✅ Creatinina sérica: {creat_serica} mg/dL")
            if 1.3 <= creat_serica <= 1.5:
                print("      ✓ Valor en rango esperado para este caso")
            else:
                print("      ⚠️  Valor fuera del rango esperado")
        else:
            print("   ❌ Creatinina sérica NO detectada")
        
        # Verificar RAC
        rac = lab_results.get('rac')
        if rac:
            print(f"   ✅ RAC: {rac} mg/g")
            if 55 <= rac <= 60:
                print("      ✓ Valor en rango esperado para este caso")
        else:
            print("   ❌ RAC NO detectado")

if __name__ == '__main__':
    print("🚀 INICIANDO DEBUGGING DE EXTRACCIÓN DE LABORATORIOS")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Ejecutar todos los tests
    success = True
    
    success &= test_creatinine_cases()
    test_rac_extraction()
    test_real_lab_samples()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 DEBUGGING COMPLETADO EXITOSAMENTE")
        print("✅ El extractor de creatinina está funcionando correctamente")
    else:
        print("❌ DEBUGGING REVELÓ PROBLEMAS")
        print("🔧 Revisar y corregir la lógica de extracción")
        
    print("=" * 80)
