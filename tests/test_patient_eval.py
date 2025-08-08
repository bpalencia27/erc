import unittest
from app.logic.patient_eval import calcular_tfg, determinar_etapa_erc

class TestPatientEval(unittest.TestCase):
    def test_calcular_tfg(self):
        """Test TFG calculation for different scenarios according to RCV-CO v1.2."""
        # Caso base: hombre adulto
        self.assertAlmostEqual(
            calcular_tfg(creatinina=1.2, edad=50, sexo='M', peso=70), 
            78.3, 
            delta=0.1,
            msg="TFG calculation failed for basic male case"
        )
        
        # Caso base: mujer adulta (con factor 0.85)
        self.assertAlmostEqual(
            calcular_tfg(creatinina=0.9, edad=65, sexo='F', peso=60), 
            63.38, 
            delta=0.1,
            msg="TFG calculation failed for basic female case"
        )
        
        # Casos límite
        # Edad mínima (18 años)
        self.assertAlmostEqual(
            calcular_tfg(creatinina=1.0, edad=18, sexo='M', peso=65),
            118.27,
            delta=0.1,
            msg="TFG calculation failed for minimum age"
        )
        
        # Edad avanzada (90 años)
        self.assertAlmostEqual(
            calcular_tfg(creatinina=1.1, edad=90, sexo='F', peso=55),
            31.69,
            delta=0.1,
            msg="TFG calculation failed for elderly case"
        )
        
        # Creatinina alta
        self.assertAlmostEqual(
            calcular_tfg(creatinina=3.0, edad=60, sexo='M', peso=80),
            31.0,
            delta=0.1,
            msg="TFG calculation failed for high creatinine"
        )
        
        # Test error cases
        with self.assertRaises(ValueError):
            calcular_tfg(creatinina=0, edad=50, sexo='M', peso=70)
        with self.assertRaises(ValueError):
            calcular_tfg(creatinina=1.0, edad=17, sexo='M', peso=70)
        with self.assertRaises(ValueError):
            calcular_tfg(creatinina=1.0, edad=50, sexo='X', peso=70)
    
    def test_determinar_etapa_erc(self):
        """Test ERC stage determination according to RCV-CO v1.2R standards."""
        # Test Stage 1 (TFG ≥ 90)
        self.assertEqual(determinar_etapa_erc(90), 1, "Failed at Stage 1 lower boundary")
        self.assertEqual(determinar_etapa_erc(95), 1, "Failed at Stage 1 middle range")
        self.assertEqual(determinar_etapa_erc(120), 1, "Failed at Stage 1 upper range")
        
        # Test Stage 2 (TFG 60-89)
        self.assertEqual(determinar_etapa_erc(89), 2, "Failed at Stage 2 upper boundary")
        self.assertEqual(determinar_etapa_erc(75), 2, "Failed at Stage 2 middle range")
        self.assertEqual(determinar_etapa_erc(60), 2, "Failed at Stage 2 lower boundary")
        
        # Test Stage 3a (TFG 45-59)
        self.assertEqual(determinar_etapa_erc(59), "3a", "Failed at Stage 3a upper boundary")
        self.assertEqual(determinar_etapa_erc(50), "3a", "Failed at Stage 3a middle range")
        self.assertEqual(determinar_etapa_erc(45), "3a", "Failed at Stage 3a lower boundary")
        
        # Test Stage 3b (TFG 30-44)
        self.assertEqual(determinar_etapa_erc(44), "3b", "Failed at Stage 3b upper boundary")
        self.assertEqual(determinar_etapa_erc(35), "3b", "Failed at Stage 3b middle range")
        self.assertEqual(determinar_etapa_erc(30), "3b", "Failed at Stage 3b lower boundary")
        
        # Test Stage 4 (TFG 15-29)
        self.assertEqual(determinar_etapa_erc(29), 4, "Failed at Stage 4 upper boundary")
        self.assertEqual(determinar_etapa_erc(25), 4, "Failed at Stage 4 middle range")
        self.assertEqual(determinar_etapa_erc(15), 4, "Failed at Stage 4 lower boundary")
        
        # Test Stage 5 (TFG < 15)
        self.assertEqual(determinar_etapa_erc(14), 5, "Failed at Stage 5 upper range")
        self.assertEqual(determinar_etapa_erc(10), 5, "Failed at Stage 5 middle range")
        self.assertEqual(determinar_etapa_erc(5), 5, "Failed at Stage 5 lower range")
        
        # Test error cases
        with self.assertRaises(ValueError):
            determinar_etapa_erc(-1)
        with self.assertRaises(ValueError):
            determinar_etapa_erc(0)


if __name__ == '__main__':
    unittest.main()
