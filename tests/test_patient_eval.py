import unittest
from app.logic.patient_eval import calcular_tfg, determinar_etapa_erc

class TestPatientEval(unittest.TestCase):
    def test_calcular_tfg(self):
        # Caso de prueba para hombre de 50 años con creatinina 1.2
        # Nota: Adaptado para usar la firma correcta de Cockcroft-Gault (edad, peso, creatinina, sexo)
        self.assertAlmostEqual(
            calcular_tfg(50, 70, 1.2, 'm'), 
            72.92, 
            delta=0.1
        )
        
        # Caso de prueba para mujer de 65 años con creatinina 0.9
        self.assertAlmostEqual(
            calcular_tfg(65, 60, 0.9, 'f'), 
            59.03, 
            delta=0.1
        )
    
    def test_determinar_etapa_erc(self):
        # Etapa 1 (g1)
        self.assertEqual(determinar_etapa_erc(95), "g1")
        
        # Etapa 2 (g2)
        self.assertEqual(determinar_etapa_erc(75), "g2")
        
        # Etapa 3a (g3a)
        self.assertEqual(determinar_etapa_erc(50), "g3a")
        
        # Etapa 3b (g3b)
        self.assertEqual(determinar_etapa_erc(35), "g3b")
        
        # Etapa 4 (g4)
        self.assertEqual(determinar_etapa_erc(25), "g4")
        
        # Etapa 5 (g5)
        self.assertEqual(determinar_etapa_erc(10), "g5")


if __name__ == '__main__':
    unittest.main()
