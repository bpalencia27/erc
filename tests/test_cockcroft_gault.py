import unittest
from app.logic.advanced_patient_eval import calcular_tfg_cockcroft_gault

class TestCockcroftGault(unittest.TestCase):
    def test_calcular_tfg_cockcroft_gault(self):
        # Caso de prueba para hombre de 50 años con creatinina 1.2
        self.assertAlmostEqual(
            calcular_tfg_cockcroft_gault(1.2, 50, 'M', 70), 
            72.92, 
            delta=0.1
        )
        
        # Caso de prueba para mujer de 65 años con creatinina 0.9
        self.assertAlmostEqual(
            calcular_tfg_cockcroft_gault(0.9, 65, 'F', 60), 
            59.03, 
            delta=0.1
        )
        
        # Caso de creatinina con valor 0 (debe usar 1.0 como valor por defecto)
        self.assertAlmostEqual(
            calcular_tfg_cockcroft_gault(0, 50, 'M', 70),
            calcular_tfg_cockcroft_gault(1.0, 50, 'M', 70),
            delta=0.1
        )
        
        # Caso de edad con valor 0 (debe retornar 0)
        self.assertEqual(
            calcular_tfg_cockcroft_gault(1.2, 0, 'M', 70),
            0.0
        )
        
        # Caso de peso con valor 0 (debe retornar 0)
        self.assertEqual(
            calcular_tfg_cockcroft_gault(1.2, 50, 'M', 0),
            0.0
        )


if __name__ == '__main__':
    unittest.main()
