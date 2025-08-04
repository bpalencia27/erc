import unittest
from app.api.report_generator import AdvancedReportGenerator
from app.logic.advanced_patient_eval import PUNTAJE_METAS, METAS_TERAPEUTICAS

class TestTherapeuticGoals(unittest.TestCase):
    
    def setUp(self):
        self.generator = AdvancedReportGenerator()
    
    def test_total_puntos_erc4_nodm2(self):
        """Verifica que la suma total de puntos para ERC G4 sin DM sea 100."""
        perfil = "erc4_nodm2"
        total = sum(PUNTAJE_METAS[meta][perfil] for meta in PUNTAJE_METAS)
        self.assertEqual(100, total, 
                         f"La suma de puntos para {perfil} debe ser 100, pero es {total}")
    
    def test_rac_erc4_nodm2_value(self):
        """Verifica que el valor de RAC para ERC G4 sin DM sea 10 puntos."""
        self.assertEqual(10, PUNTAJE_METAS["rac"]["erc4_nodm2"],
                         "RAC debe valer 10 puntos para ERC G4 sin DM")
    
    def test_build_therapeutic_goals_erc4_nodm2(self):
        """Prueba la generación de metas terapéuticas para ERC G4 sin DM."""
        # Datos de prueba
        patient_data = {
            "sexo": "m",
            "edad": 65,
            "peso": 70,
            "tiene_dm2": False
        }
        labs_data = {
            "creatinina": 2.5,  # Valor elevado para simular ERC G4
            "rac": 25,          # Cumple meta RAC < 30 mg/g
            "glicemia": 95,      # Cumple meta
            "hdl": 45           # Cumple meta
        }
        tfg = 25  # TFG en rango de G4
        riesgo_cv = "alto"
        
        # Ejecución
        metas = self.generator._build_therapeutic_goals(patient_data, labs_data, tfg, riesgo_cv)
        
        # Verificación
        self.assertTrue(any(meta["parametro"] == "RAC" for meta in metas),
                       "Debe existir meta para RAC")
        
        # Verificar que RAC tenga asignado el puntaje correcto (10 puntos)
        rac_meta = next(meta for meta in metas if meta["parametro"] == "RAC")
        self.assertEqual(10, rac_meta["puntaje"],
                        "RAC debe valer 10 puntos para ERC G4 sin DM")