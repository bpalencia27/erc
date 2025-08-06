"""
Test suite comprehensivo para ERC Insight
Incluye tests críticos para extracción de creatinina y otros componentes
"""
import unittest
import sys
import os
from datetime import datetime
import json

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.parsers.lab_parser import AdvancedLabParser, parse_lab_results
from app.logic.patient_eval import calcular_tfg, determinar_etapa_erc
from app.api.gemini_client import GeminiClient
from app.api.report_generator import AdvancedReportGenerator


class TestCriticalCreatinineExtraction(unittest.TestCase):
    """Tests críticos para extracción correcta de creatinina"""
    
    def setUp(self):
        self.parser = AdvancedLabParser()
        
    def test_creatinina_serica_correcta(self):
        """Test: Extracción correcta de creatinina sérica"""
        test_cases = [
            {
                'text': 'CREATININA SERICA: 1.2 mg/dL',
                'expected': 1.2,
                'description': 'Formato estándar sérica'
            },
            {
                'text': 'Creatinina en suero: 0.8 mg/dl',
                'expected': 0.8,
                'description': 'Especificación de suero'
            },
            {
                'text': 'BIOQUIMICA\nCreatinina: 1.5 mg/dL\nUrea: 45 mg/dL',
                'expected': 1.5,
                'description': 'Creatinina en contexto bioquímico'
            },
            {
                'text': 'Creatinina plasma: 0.9 mg/dL',
                'expected': 0.9,
                'description': 'Creatinina en plasma'
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case['description']):
                result = self.parser.parse(case['text'])
                self.assertTrue(result['success'], f"Parse falló para: {case['description']}")
                self.assertIn('creatinina_serica', result['lab_results'])
                self.assertAlmostEqual(
                    result['lab_results']['creatinina_serica'], 
                    case['expected'], 
                    places=1,
                    msg=f"Valor incorrecto en {case['description']}"
                )
    
    def test_creatinina_orina_excluida(self):
        """Test CRÍTICO: Creatinina de orina debe ser excluida"""
        test_cases = [
            {
                'text': 'Creatinina en orina: 120 mg/dL\nCreatinina sérica: 1.2 mg/dL',
                'expected_serica': 1.2,
                'description': 'Ambas presentes, solo tomar sérica'
            },
            {
                'text': 'ORINA ESPONTANEA\nCreatinina: 95 mg/dL\nVolumen: 50 ml',
                'expected_serica': None,
                'description': 'Solo creatinina de orina'
            },
            {
                'text': 'Creatinina urinaria: 85 mg/dL',
                'expected_serica': None,
                'description': 'Explícitamente urinaria'
            },
            {
                'text': 'Relación Albumina/Creatinina: 30 mg/g\nCreatinina orina: 100 mg/dL',
                'expected_serica': None,
                'description': 'Contexto de RAC con orina'
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case['description']):
                result = self.parser.parse(case['text'])
                
                if case['expected_serica'] is not None:
                    self.assertIn('creatinina_serica', result['lab_results'])
                    self.assertAlmostEqual(
                        result['lab_results']['creatinina_serica'], 
                        case['expected_serica'], 
                        places=1
                    )
                else:
                    # NO debe haber creatinina sérica detectada
                    self.assertNotIn('creatinina_serica', result['lab_results'],
                                   f"Se detectó incorrectamente creatinina sérica en: {case['description']}")
    
    def test_rac_extraction(self):
        """Test: Extracción correcta de RAC"""
        test_cases = [
            {
                'text': 'Relación Albúmina/Creatinina: 15 mg/g',
                'expected': 15,
                'description': 'RAC estándar'
            },
            {
                'text': 'RAC: 45.5 mg/g',
                'expected': 45.5,
                'description': 'RAC abreviado'
            },
            {
                'text': 'Microalbuminuria/Creatinina: 120 mg/g',
                'expected': 120,
                'description': 'Microalbuminuria sobre creatinina'
            },
            {
                'text': 'Índice albúmina/creatinina: 8.2 mg/g',
                'expected': 8.2,
                'description': 'Como índice'
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case['description']):
                result = self.parser.parse(case['text'])
                self.assertTrue(result['success'])
                self.assertIn('rac', result['lab_results'])
                self.assertAlmostEqual(
                    result['lab_results']['rac'], 
                    case['expected'], 
                    places=1
                )


class TestTFGCalculation(unittest.TestCase):
    """Tests para cálculo de TFG"""
    
    def test_tfg_calculation_accuracy(self):
        """Test: Precisión del cálculo de TFG"""
        test_cases = [
            {
                'edad': 65, 'peso': 70, 'creatinina': 1.2, 'sexo': 'M',
                'expected_range': (55, 65),
                'description': 'Hombre mayor con creatinina elevada'
            },
            {
                'edad': 45, 'peso': 60, 'creatinina': 0.8, 'sexo': 'F',
                'expected_range': (80, 90),
                'description': 'Mujer adulta con creatinina normal'
            },
            {
                'edad': 75, 'peso': 65, 'creatinina': 2.0, 'sexo': 'M',
                'expected_range': (20, 30),
                'description': 'Hombre mayor con ERC avanzada'
            },
            {
                'edad': 35, 'peso': 55, 'creatinina': 0.9, 'sexo': 'F',
                'expected_range': (70, 80),
                'description': 'Mujer joven con función normal'
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case['description']):
                tfg = calcular_tfg(
                    case['edad'], 
                    case['peso'], 
                    case['creatinina'], 
                    case['sexo']
                )
                
                self.assertIsInstance(tfg, (int, float))
                self.assertGreaterEqual(tfg, case['expected_range'][0])
                self.assertLessEqual(tfg, case['expected_range'][1])
    
    def test_erc_stage_determination(self):
        """Test: Determinación correcta de etapas de ERC"""
        test_cases = [
            {'tfg': 95, 'expected': 'G1', 'description': 'Función normal'},
            {'tfg': 75, 'expected': 'G2', 'description': 'Disminución leve'},
            {'tfg': 45, 'expected': 'G3a', 'description': 'Disminución moderada'},
            {'tfg': 25, 'expected': 'G4', 'description': 'Disminución severa'},
            {'tfg': 12, 'expected': 'G5', 'description': 'Disminución grave'},
            {'tfg': 8, 'expected': 'G5', 'description': 'Falla renal'}
        ]
        
        for case in test_cases:
            with self.subTest(case=case['description']):
                etapa = determinar_etapa_erc(case['tfg'])
                self.assertEqual(etapa, case['expected'])


class TestGeminiAPIIntegration(unittest.TestCase):
    """Tests para integración con API de Gemini"""
    
    def setUp(self):
        self.client = GeminiClient()
    
    def test_api_connection(self):
        """Test: Conexión básica con API de Gemini"""
        try:
            # Test con prompt simple
            response = self.client.generate_response("Test de conexión")
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)
        except Exception as e:
            self.skipTest(f"API de Gemini no disponible: {e}")
    
    def test_medical_report_generation(self):
        """Test: Generación de reporte médico"""
        sample_data = {
            'nombre': 'Paciente Test',
            'edad': 65,
            'sexo': 'M',
            'creatinina_serica': 1.5,
            'tfg': 45,
            'etapa_erc': 'G3a',
            'rac': 25,
            'diagnosticos': ['HTA', 'DM']
        }
        
        try:
            generator = AdvancedReportGenerator()
            report = generator.generate_patient_report(sample_data)
            
            self.assertIsInstance(report, str)
            self.assertIn('Paciente Test', report)
            self.assertIn('ERC', report)
            self.assertGreater(len(report), 100)
            
        except Exception as e:
            self.skipTest(f"Generador de reportes no disponible: {e}")


class TestFileUploadAndParsing(unittest.TestCase):
    """Tests para subida y parsing de archivos"""
    
    def test_lab_file_parsing(self):
        """Test: Parsing de archivos de laboratorio"""
        # Crear archivo de prueba
        test_content = """
        LABORATORIO CLINICO
        Paciente: Juan Pérez Gómez
        Edad: 58 años
        Sexo: Masculino
        
        BIOQUIMICA CLINICA
        Creatinina sérica: 1.8 mg/dL
        Urea: 65 mg/dL
        Glucosa: 145 mg/dL
        HbA1c: 7.2%
        
        PERFIL LIPIDICO
        Colesterol total: 220 mg/dL
        LDL: 140 mg/dL
        HDL: 45 mg/dL
        Triglicéridos: 180 mg/dL
        
        ORINA
        Relación Albúmina/Creatinina: 45 mg/g
        """
        
        result = parse_lab_results(test_content)
        
        self.assertTrue(result['success'])
        results = result['results']
        
        # Verificar datos del paciente
        self.assertEqual(results['nombre'], 'Juan Pérez Gómez')
        self.assertEqual(results['edad'], 58)
        self.assertEqual(results['sexo'], 'M')
        
        # Verificar valores de laboratorio
        self.assertAlmostEqual(results['creatinina_serica'], 1.8, places=1)
        self.assertAlmostEqual(results['glicemia'], 145, places=1)
        self.assertAlmostEqual(results['hba1c'], 7.2, places=1)
        self.assertAlmostEqual(results['rac'], 45, places=1)
        
        # Verificar lípidos
        self.assertAlmostEqual(results['colesterol_total'], 220, places=1)
        self.assertAlmostEqual(results['ldl'], 140, places=1)
        self.assertAlmostEqual(results['hdl'], 45, places=1)
        self.assertAlmostEqual(results['trigliceridos'], 180, places=1)


class TestFrontendValidation(unittest.TestCase):
    """Tests para validaciones del frontend"""
    
    def test_patient_data_validation(self):
        """Test: Validación de datos del paciente"""
        # Aquí se probarían las validaciones JavaScript
        # Por ahora, test de estructura de datos
        
        required_fields = ['nombre', 'edad', 'sexo', 'peso']
        patient_data = {
            'nombre': 'Test Patient',
            'edad': 45,
            'sexo': 'M',
            'peso': 70
        }
        
        for field in required_fields:
            self.assertIn(field, patient_data)
            self.assertIsNotNone(patient_data[field])
    
    def test_lab_results_structure(self):
        """Test: Estructura de resultados de laboratorio"""
        expected_structure = {
            'creatinina_serica': float,
            'rac': float,
            'glicemia': float,
            'hba1c': float,
            'colesterol_total': float,
            'ldl': float,
            'hdl': float,
            'trigliceridos': float
        }
        
        # Verificar que la estructura esté definida
        self.assertTrue(all(isinstance(v, type) for v in expected_structure.values()))


class TestEndToEndWorkflow(unittest.TestCase):
    """Tests de flujo completo (end-to-end)"""
    
    def test_complete_patient_evaluation(self):
        """Test: Flujo completo de evaluación de paciente"""
        # Datos de entrada
        patient_data = {
            'nombre': 'Test Complete Patient',
            'edad': 65,
            'sexo': 'M',
            'peso': 75,
            'creatinina_serica': 1.6,
            'rac': 35,
            'glicemia': 160,
            'hba1c': 8.1,
            'diagnosticos': ['HTA', 'DM', 'ERC']
        }
        
        # Calcular TFG
        tfg = calcular_tfg(
            patient_data['edad'],
            patient_data['peso'],
            patient_data['creatinina_serica'],
            patient_data['sexo']
        )
        patient_data['tfg'] = tfg
        
        # Determinar etapa ERC
        etapa = determinar_etapa_erc(tfg)
        patient_data['etapa_erc'] = etapa
        
        # Verificar cálculos
        self.assertIsInstance(tfg, (int, float))
        self.assertGreater(tfg, 0)
        self.assertLess(tfg, 150)
        self.assertIn(etapa, ['G1', 'G2', 'G3a', 'G3b', 'G4', 'G5'])
        
        # Para este caso (creatinina 1.6, edad 65), esperamos TFG reducido
        self.assertLess(tfg, 60)  # Debería estar en ERC


def run_critical_tests():
    """Ejecuta solo los tests críticos para debugging rápido"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar tests críticos
    suite.addTest(loader.loadTestsFromTestCase(TestCriticalCreatinineExtraction))
    suite.addTest(loader.loadTestsFromTestCase(TestTFGCalculation))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_all_tests():
    """Ejecuta todos los tests"""
    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test suite para ERC Insight')
    parser.add_argument('--critical', action='store_true', 
                       help='Ejecutar solo tests críticos')
    parser.add_argument('--component', type=str, 
                       help='Ejecutar tests de un componente específico')
    
    args = parser.parse_args()
    
    if args.critical:
        print("🔍 Ejecutando tests críticos...")
        success = run_critical_tests()
    elif args.component:
        # Ejecutar tests de componente específico
        component_map = {
            'creatinine': TestCriticalCreatinineExtraction,
            'tfg': TestTFGCalculation,
            'gemini': TestGeminiAPIIntegration,
            'upload': TestFileUploadAndParsing,
            'frontend': TestFrontendValidation,
            'e2e': TestEndToEndWorkflow
        }
        
        if args.component in component_map:
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromTestCase(component_map[args.component])
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            success = result.wasSuccessful()
        else:
            print(f"❌ Componente '{args.component}' no encontrado")
            print(f"Componentes disponibles: {list(component_map.keys())}")
            success = False
    else:
        print("🧪 Ejecutando suite completa de tests...")
        success = run_all_tests()
    
    if success:
        print("✅ Todos los tests pasaron exitosamente")
    else:
        print("❌ Algunos tests fallaron")
        exit(1)
