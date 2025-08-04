import unittest
from datetime import datetime, timedelta
from app.api.report_generator import AdvancedReportGenerator

class TestReportGenerator(unittest.TestCase):
    
    def setUp(self):
        self.generator = AdvancedReportGenerator()
    
    def test_build_follow_up_plan_g4(self):
        """Prueba el plan de seguimiento para ERC G4."""
        # Configuración
        etapa_erc = "g4"
        riesgo_cv = "alto"
        metas_evaluacion = {"porcentaje_cumplimiento": 70}
        
        # Ejecución
        plan = self.generator._build_follow_up_plan(etapa_erc, riesgo_cv, metas_evaluacion)
        
        # Verificación
        self.assertIn("laboratorios", plan)
        self.assertIn("consulta_control", plan)
        self.assertIn("laboratorios_detallados", plan)
        
        # La fecha de laboratorios debe ser 30 días desde hoy para G4
        fecha_lab = datetime.strptime(plan["laboratorios"], "%d/%m/%Y")
        hoy = datetime.now()
        dias_diferencia = (fecha_lab - hoy).days
        self.assertTrue(29 <= dias_diferencia <= 31)  # Permitimos un margen de error
    
    def test_build_follow_up_plan_g3_alto_riesgo(self):
        """Prueba el plan de seguimiento para ERC G3 con alto riesgo CV."""
        # Configuración
        etapa_erc = "g3a"
        riesgo_cv = "muy_alto"
        metas_evaluacion = {"porcentaje_cumplimiento": 60}
        
        # Ejecución
        plan = self.generator._build_follow_up_plan(etapa_erc, riesgo_cv, metas_evaluacion)
        
        # Verificación
        # Para G3 con riesgo muy alto, algunos laboratorios deben ser a los 60 días
        labs_detallados = plan["laboratorios_detallados"]
        
        # Debe haber al menos una fecha a aproximadamente 60 días
        tiene_fecha_60_dias = False
        for fecha_str in labs_detallados.keys():
            fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
            dias = (fecha - datetime.now()).days
            if 55 <= dias <= 65:  # Aproximadamente 60 días
                tiene_fecha_60_dias = True
                break
        
        self.assertTrue(tiene_fecha_60_dias)
    
    def test_build_follow_up_plan_mal_cumplimiento(self):
        """Prueba el plan de seguimiento con mal cumplimiento de metas."""
        # Configuración
        etapa_erc = "g2"
        riesgo_cv = "moderado"
        metas_evaluacion = {"porcentaje_cumplimiento": 30}  # Mal cumplimiento
        
        # Ejecución
        plan = self.generator._build_follow_up_plan(etapa_erc, riesgo_cv, metas_evaluacion)
        
        # Verificación
        # El plan debe incluir un mensaje sobre acortar tiempos por mal cumplimiento
        self.assertIn("deficiente", plan["recomendacion"].lower())
        self.assertIn("acorta tiempo", plan["recomendacion"].lower())
        
        # El nivel de cumplimiento debe ser "deficiente"
        self.assertEqual("deficiente", plan["nivel_cumplimiento"])
    
    def test_build_follow_up_plan_g1_g2(self):
        """Prueba el plan de seguimiento para ERC G1/G2 (leve)."""
        # Configuración
        etapa_erc = "g1"
        riesgo_cv = "bajo"
        metas_evaluacion = {"porcentaje_cumplimiento": 85}  # Buen cumplimiento
        
        # Ejecución
        plan = self.generator._build_follow_up_plan(etapa_erc, riesgo_cv, metas_evaluacion)
        
        # Verificación
        # Para G1 con buen cumplimiento, los laboratorios deben ser a los 180 días (6 meses)
        fecha_lab = datetime.strptime(plan["laboratorios"], "%d/%m/%Y")
        hoy = datetime.now()
        dias_diferencia = (fecha_lab - hoy).days
        
        # Permitimos un margen de error pequeño por la ejecución de la prueba
        self.assertTrue(175 <= dias_diferencia <= 185)
        
        # El nivel de cumplimiento debe ser "bueno"
        self.assertEqual("bueno", plan["nivel_cumplimiento"])
        
        # La recomendación debe incluir seguimiento semestral
        self.assertIn("semestral", plan["recomendacion"].lower())
    
    def test_build_follow_up_plan_estructura_completa(self):
        """Prueba que la estructura del plan de seguimiento sea completa."""
        # Configuración
        etapa_erc = "g3b"
        riesgo_cv = "alto"
        metas_evaluacion = {"porcentaje_cumplimiento": 60}  # Cumplimiento regular
        
        # Ejecución
        plan = self.generator._build_follow_up_plan(etapa_erc, riesgo_cv, metas_evaluacion)
        
        # Verificación de la estructura completa
        self.assertIn("laboratorios", plan)
        self.assertIn("consulta_control", plan)
        self.assertIn("laboratorios_detallados", plan)
        self.assertIn("recomendacion", plan)
        self.assertIn("nivel_cumplimiento", plan)
        
        # Verificar que laboratorios_detallados contenga al menos una fecha
        self.assertTrue(len(plan["laboratorios_detallados"]) > 0)
        
        # Verificar que la fecha de consulta sea posterior a la de laboratorios
        fecha_lab = datetime.strptime(plan["laboratorios"], "%d/%m/%Y")
        fecha_consulta = datetime.strptime(plan["consulta_control"], "%d/%m/%Y")
        self.assertTrue(fecha_consulta >= fecha_lab)
        
        # Verificar que el nivel de cumplimiento sea "regular"
        self.assertEqual("regular", plan["nivel_cumplimiento"])
    
    def test_build_follow_up_plan_sin_metas_evaluacion(self):
        """Prueba el plan de seguimiento cuando no se proporciona evaluación de metas."""
        # Configuración
        etapa_erc = "g3a"
        riesgo_cv = "moderado"
        metas_evaluacion = None  # Sin evaluación de metas
        
        # Ejecución
        plan = self.generator._build_follow_up_plan(etapa_erc, riesgo_cv, metas_evaluacion)
        
        # Verificación
        # El nivel de cumplimiento por defecto debe ser "regular"
        self.assertEqual("regular", plan["nivel_cumplimiento"])
        
        # La estructura del plan debe seguir siendo completa
        self.assertIn("laboratorios", plan)
        self.assertIn("consulta_control", plan)
        self.assertIn("laboratorios_detallados", plan)
        self.assertIn("recomendacion", plan)