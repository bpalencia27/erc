import unittest
from app.api.gemini_client import GeminiClient

class TestGeminiClientSimulado(unittest.TestCase):
    def setUp(self):
        self.client = GeminiClient()
        # Fuerza modo simulado si no hay claves
        if not self.client.api_key:
            self.client.use_simulation = True

    def test_extract_lab_results_structure(self):
        data = self.client.extract_lab_results("Paciente creatinina 1.2 mg/dL y glucosa 105 mg/dL")
        self.assertIn("results", data)
        self.assertIn("creatinina", data["results"])  # en modo simulado fijo

    def test_generate_patient_report_returns_html(self):
        html = self.client.generate_patient_report({"nombre": "Juan", "edad": 55, "sexo": "m"})
        self.assertTrue(html.strip().startswith("<"))

    def test_process_advanced_evaluation_sim(self):
        payload = {"evaluacion_diagnosticos": {"erc_estadio": "g3a", "riesgo_cardiovascular": "alto"}}
        report = self.client.process_advanced_evaluation(payload)
        self.assertIn("Informe", report)

if __name__ == '__main__':
    unittest.main()
