"""
Módulo de integración con la API de Gemini para generar informes avanzados
"""
import os
import logging
import json
from datetime import datetime
from app.api.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class AdvancedReportGenerator:
    """
    Clase para generar informes médicos avanzados utilizando 
    el motor de lógica de negocio y la API de Gemini.
    """
    
    def __init__(self):
        """Inicializa el generador de informes."""
        self.gemini_client = GeminiClient()
    
    def process_patient_data(self, patient_data, labs_data):
        """
        Procesa los datos del paciente y genera un informe médico avanzado.
        
        Args:
            patient_data (dict): Datos del paciente
            labs_data (dict): Resultados de laboratorio
            
        Returns:
            dict: Resultado con el informe y metadatos
        """
        from app.logic.advanced_patient_eval import generar_payload_gemini
        
        try:
            # Generar el payload usando la lógica de negocio avanzada
            payload = generar_payload_gemini(patient_data, labs_data)
            
            # Generar el informe usando la API de Gemini
            report_text = self.gemini_client.process_advanced_evaluation(payload)
            
            # Guardar metadatos relevantes
            result = {
                "report": report_text,
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "report_type": "advanced_erc",
                    "tfg": payload["evaluacion_diagnosticos"]["tfg_valor"],
                    "erc_stage": payload["evaluacion_diagnosticos"]["erc_estadio"],
                    "cv_risk": payload["evaluacion_diagnosticos"]["riesgo_cardiovascular"]
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error al generar informe avanzado: {str(e)}")
            return {
                "report": "Error al generar el informe. Por favor, inténtelo de nuevo.",
                "error": str(e)
            }
    
    def generate_pdf(self, report_data):
        """
        Genera un archivo PDF a partir del informe.
        
        Args:
            report_data (dict): Datos del informe
            
        Returns:
            str: Ruta al archivo PDF generado
        """
        # Esta función se implementaría para convertir el informe a PDF
        # Por ahora devolvemos solo un mensaje
        return "PDF generation not implemented yet"
