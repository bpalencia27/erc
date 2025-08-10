"""Cliente LLM unificado para extracción y generación de informes.

Conecta con un adaptador (Gemini u OpenAI) vía `get_llm_adapter` y ofrece:
 - extract_lab_results(text)
 - generate_patient_report(patient_data)
 - process_advanced_evaluation(payload) (informes avanzados)

Incluye modo simulado cuando no hay credenciales configuradas.
"""
from __future__ import annotations

import os
import json
import logging
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from app.utils.caching import cached_result
from app.api.llm_adapters import get_llm_adapter

load_dotenv()


class GeminiClient:
    """Cliente unificado de LLM con fallback simulado."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.use_simulation = False
        try:
            self.model = get_llm_adapter()
        except Exception as e:  # noqa: BLE001
            logging.warning(f"No se pudo inicializar adaptador LLM, modo simulado: {e}")
            self.use_simulation = True

    def extract_lab_results(self, text: str) -> Dict[str, Any]:
        if self.use_simulation:
            return {
                "patient_data": {},
                "results": {
                    "creatinina": {"value": "1.2", "unit": "mg/dL"},
                    "glucosa": {"value": "105", "unit": "mg/dL"},
                    "ldl": {"value": "110", "unit": "mg/dL"},
                },
            }

        prompt = f"""
        Analiza el siguiente texto de un reporte médico y extrae los valores de laboratorio.
        Devuelve JSON con patient_data y results (diccionario de analito -> { '{"value":"","unit":""}' }).

        Texto:
        {text}
        """
        try:
            response = self.model.generate_content(prompt)
            result_text = getattr(response, 'text', str(response))
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(result_text[json_start:json_end])
            return {"results": {}}
        except Exception as e:  # noqa: BLE001
            logging.error(f"Error extracción IA: {e}")
            return {"results": {}}

    def generate_patient_report(self, patient_data: Dict[str, Any]) -> str:
        if self.use_simulation:
            return (
                "<h3>Informe Simulado</h3><p>Configura GEMINI_API_KEY u OPENAI_API_KEY para generar texto real."  # noqa: E501
                "</p>"
            )

        nombre = patient_data.get('nombre', 'Paciente')
        edad = patient_data.get('edad', 'N/D')
        sexo = patient_data.get('sexo', 'N/D')

        prompt = f"""
        Genera un informe clínico HTML estructurado (h3, p, ul/li) para el paciente:
        Nombre: {nombre}\nEdad: {edad}\nSexo: {sexo}
        Incluye: resumen, análisis de laboratorio si existe, recomendaciones, plan seguimiento.
        Devuelve SOLO HTML limpio.
        """
        try:
            response = self.model.generate_content(prompt)
            html_content = getattr(response, 'text', str(response))
            if "```" in html_content:
                parts = html_content.split("```")
                if len(parts) >= 2:
                    html_content = parts[1]
            return html_content.strip()
        except Exception as e:  # noqa: BLE001
            logging.error(f"Error informe IA: {e}")
            return f"<p>Error al generar informe: {e}</p>"

    def generate_medical_report(self, patient_data: Dict[str, Any], report_type: str = "complete") -> str:
        if self.use_simulation:
            return self._generate_simulated_report(patient_data, report_type)
        try:
            if report_type == "summary":
                prompt = "Resumen médico clínico conciso en HTML: " + json.dumps(patient_data)[:4000]
            elif report_type == "follow_up":
                prompt = "Plan de seguimiento estructurado en HTML: " + json.dumps(patient_data)[:4000]
            else:
                prompt = "Informe médico completo en HTML: " + json.dumps(patient_data)[:4000]
            response = self.model.generate_content(prompt)
            return getattr(response, 'text', str(response))
        except Exception as e:  # noqa: BLE001
            logging.error(f"Error generando informe clínico: {e}")
            return self._generate_fallback_report(patient_data)

    @cached_result(expiration_seconds=3600)
    def process_advanced_evaluation(self, payload: Dict[str, Any]) -> str:
        if self.use_simulation:
            return self._generate_advanced_report(payload)
        try:
            prompt = (
                "Eres un médico especialista. Genera informe avanzado estructurado (HTML) basado en este JSON. "
                "Incluye riesgo cardiovascular, estadio ERC, metas terapéuticas y plan de seguimiento."
            )
            response = self.model.generate_content(prompt + "\nJSON:\n" + json.dumps(payload)[:4000])
            return getattr(response, 'text', str(response)) or self._generate_advanced_report(payload)
        except Exception as e:  # noqa: BLE001
            logging.error(f"Error informe avanzado: {e}")
            return self._generate_advanced_report(payload)

    # -------------------- Métodos auxiliares / simulación --------------------
    def _generate_simulated_report(self, patient_data: Dict[str, Any], report_type: str) -> str:
        return f"<h3>Informe {report_type} simulado</h3><p>Sin credenciales LLM.</p>"

    def _generate_fallback_report(self, patient_data: Dict[str, Any]) -> str:
        return "<p>No se pudo generar informe. Intente más tarde.</p>"

    def _generate_advanced_report(self, payload: Dict[str, Any]) -> str:
        etapa = payload.get('evaluacion_diagnosticos', {}).get('erc_estadio', 'N/A')
        riesgo = payload.get('evaluacion_diagnosticos', {}).get('riesgo_cardiovascular', 'N/A')
        return (
            f"<h3>Informe Avanzado Simulado</h3><p>ERC estadio {etapa.upper()} - Riesgo CV {riesgo}</p>"
            "<p>Configura credenciales para activar generación real.</p>"
        )
