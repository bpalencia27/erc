import unittest
from app.logic.patient_eval import calcular_tfg, determinar_etapa_erc

class TestPatientEval(unittest.TestCase):
    def test_calcular_tfg(self):
        # Caso de prueba para hombre de 50 años con creatinina 1.2
        self.assertAlmostEqual(
            calcular_tfg(1.2, 50, 'M', 'no_negro'), 
            67.77, 
            delta=0.1
        )
        
        # Caso de prueba para mujer de 65 años con creatinina 0.9
        self.assertAlmostEqual(
            calcular_tfg(0.9, 65, 'F', 'no_negro'), 
            66.67, 
            delta=0.1
        )
    
    def test_determinar_etapa_erc(self):
        # Etapa 1
        self.assertEqual(determinar_etapa_erc(95), 1)
        
        # Etapa 2
        self.assertEqual(determinar_etapa_erc(75), 2)
        
        # Etapa 3a
        self.assertEqual(determinar_etapa_erc(50), "3a")
        
        # Etapa 3b
        self.assertEqual(determinar_etapa_erc(35), "3b")
        
        # Etapa 4
        self.assertEqual(determinar_etapa_erc(25), 4)
        
        # Etapa 5
        self.assertEqual(determinar_etapa_erc(10), 5)


if __name__ == '__main__':
    unittest.main()
