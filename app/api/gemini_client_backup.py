"""
Cliente para interactuar con la API de Google Gemini
"""
import os
import json
import logging
from typing import Dict, Any, Optional
import requests
from datetime import datetime

class GeminiClient:
    """Cliente para interactuar con la API de Google Gemini."""
    
    def __init__(self):
        """Inicializa el cliente con la API key y configura el modelo."""
        self.api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not self.api_key:
            logging.warning("API key de Google Gemini no configurada, usando modo simulado")
        
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
        self.headers = {"Content-Type": "application/json"}
        
    def generate_content(self, prompt: str) -> str:
        """
        Genera contenido utilizando la API de Gemini.
        
        Args:
            prompt (str): El prompt para enviar a la API
            
        Returns:
            str: El texto generado por el modelo
        """
        if not self.api_key:
            return self._simulate_response(prompt)
            
        try:
            url = f"{self.api_url}?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.4,
                    "topP": 0.95,
                    "topK": 40,
                    "maxOutputTokens": 8192
                }
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
            
        except Exception as e:
            logging.error(f"Error al generar contenido con Gemini: {str(e)}")
            return self._simulate_response(prompt)
            
    def _simulate_response(self, prompt: str) -> str:
        """
        Genera una respuesta simulada cuando la API no está disponible.
        Útil para desarrollo y pruebas.
        
        Args:
            prompt (str): El prompt original
            
        Returns:
            str: Una respuesta simulada
        """
        logging.warning("Utilizando respuesta simulada de Gemini (API no disponible)")
        
        # Extraer información básica para la simulación
        patient_info = "paciente"
        if "json" in prompt.lower():
            try:
                # Intenta extraer datos básicos del JSON en el prompt
                json_start = prompt.find("{")
                json_end = prompt.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    patient_data = json.loads(prompt[json_start:json_end])
                    patient_info = f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}"
            except:
                pass
                
        return f"""# Informe Médico (SIMULADO)

## Resumen Clínico
Este es un informe simulado para el {patient_info}. La API de Gemini no está disponible en este momento.

## Clasificación de Riesgo y Estadio
**Riesgo Cardiovascular:** MODERADO
**Estadio ERC (KDIGO):** G3a A2

## Evaluación de Metas Terapéuticas
* PA: Meta <130/80 mmHg - FUERA DE META
* LDL: Meta <70 mg/dL - EN META
* HbA1c: Meta <7.0% - EN META

## Análisis y Plan Farmacológico
Se recomienda el siguiente plan basado en los 4 pilares:
1. IECA/ARA II: Enalapril 10 mg cada 12 horas
2. iSGLT2: Empagliflozina 10 mg cada día
3. Estatinas: Atorvastatina 40 mg en la noche
4. Antiagregación: ASA 100 mg al día

## Plan de Seguimiento
Se recomienda control médico en 3 meses con nuevos laboratorios.
"""
            
        Returns:
            str: Texto del informe generado
        """
        try:
            # Construir el prompt según el tipo de informe
            if report_type == "complete":
                prompt = self._build_complete_report_prompt(patient_data)
            elif report_type == "summary":
                prompt = self._build_summary_prompt(patient_data)
            elif report_type == "follow_up":
                prompt = self._build_follow_up_prompt(patient_data)
            else:
                prompt = self._build_complete_report_prompt(patient_data)
            
            # Si no hay API key, usar modo simulado
            if not self.api_key:
                return self._generate_simulated_report(patient_data, report_type)
            
            # En una implementación real, aquí se enviaría el prompt a la API de Gemini
            # Por ahora, usamos un informe simulado
            return self._generate_simulated_report(patient_data, report_type)
            
        except Exception as e:
            logging.error(f"Error al generar informe con Gemini: {str(e)}")
            # Devolver un informe de respaldo
            return self._generate_fallback_report(patient_data)
    
    def process_advanced_evaluation(self, payload: Dict[str, Any]) -> str:
        """
        Procesa una evaluación avanzada y genera un informe detallado.
        Este método usa el nuevo formato de payload según los requisitos.
        
        Args:
            payload: Payload JSON con la estructura requerida para la API de Gemini
            
        Returns:
            str: Informe médico generado
        """
        if not self.api_key:
            logging.warning("Usando respuesta simulada porque no hay clave API configurada")
            return self._generate_advanced_report(payload)
        
        try:
            # Construir el prompt para Gemini según las instrucciones específicas
            prompt = """
Eres un médico experto en Medicina Interna y Nefrología. Tienes total autonomía para redactar un informe clínico coherente y profesional, utilizando los datos estructurados que se te proporcionan en este JSON. Sin embargo, debes adherirte estrictamente a las siguientes directivas:

Contenido Obligatorio e Inflexible: La siguiente información del JSON debe ser incluida en tu redacción de forma explícita y sin alteraciones:
- La Clasificación del Riesgo Cardiovascular y su justificación.
- La tabla o lista detallada del Cumplimiento de Metas Terapéuticas, incluyendo parámetros, valores, metas, puntajes y el estado final.
- El Plan de Seguimiento, mostrando las fechas exactas (DD/MM/AAAA) para los próximos laboratorios y la cita de control médico.

Recomendaciones Dinámicas: Genera recomendaciones no farmacológicas personalizadas (dieta, ejercicio) que sean relevantes para la condición específica del paciente descrita en los datos.

Remisiones Estándar Obligatorias: En todos los informes, independientemente del paciente, debes incluir la siguiente nota de remisión:
'Se remite a Enfermería para la gestión de citas con Odontología, Nutrición y Psicología. Adicionalmente, se remite al servicio de Vacunación para completar o verificar el esquema según la edad y las condiciones de riesgo del paciente.'
"""
            
            # En una implementación real, aquí se enviaría el prompt y el payload a la API de Gemini
            # Por ahora, usamos un informe simulado
            return self._generate_advanced_report(payload)
            
        except Exception as e:
            logging.error(f"Error al generar informe avanzado con Gemini: {str(e)}")
            return "Error al generar el informe médico. Por favor, inténtelo de nuevo."
    
    def _build_complete_report_prompt(self, patient_data):
        """Construye el prompt para un informe completo."""
        # Extraer datos relevantes del paciente
        name = patient_data.get('paciente', {}).get('nombre', 'Paciente')
        age = patient_data.get('paciente', {}).get('edad', 'N/A')
        gender = 'masculino' if patient_data.get('paciente', {}).get('sexo') == 'm' else 'femenino'
        
        # Construir prompt
        prompt = f"""
        Eres un especialista en nefrología y medicina interna con 20 años de experiencia.
        Genera un informe médico completo para el siguiente paciente:
        
        DATOS DEL PACIENTE:
        - Nombre: {name}
        - Edad: {age} años
        - Sexo: {gender}
        
        VALORACIÓN RENAL:
        - TFG calculada: {patient_data.get('valores', {}).get('tfg', 'N/A')} ml/min
        - Etapa ERC: {patient_data.get('valores', {}).get('etapa_erc', 'N/A').upper()}
        
        Genera un informe médico estructurado con los siguientes apartados:
        1. Evaluación clínica
        2. Análisis de función renal
        3. Plan terapéutico
        4. Recomendaciones
        5. Plan de seguimiento
        
        El informe debe ser claro, profesional y usar terminología médica apropiada.
        """
        
        return prompt
        """Genera un informe simulado cuando no se puede usar la API."""
        name = patient_data.get('paciente', {}).get('nombre', 'Paciente')
        age = patient_data.get('paciente', {}).get('edad', 'N/A')
        gender = 'masculino' if patient_data.get('paciente', {}).get('sexo') == 'm' else 'femenino'
        tfg = patient_data.get('valores', {}).get('tfg', 'N/A')
        etapa_erc = patient_data.get('valores', {}).get('etapa_erc', 'N/A').upper()
        
        # Informe simulado basado en plantilla
        return f"""
        # INFORME MÉDICO
        
        ## 1. EVALUACIÓN CLÍNICA
        
        Paciente {name} de {age} años de edad, {gender}, quien acude a valoración nefrológica. 
        
        ## 2. ANÁLISIS DE FUNCIÓN RENAL
        
        Se calcula una Tasa de Filtración Glomerular (TFG) de {tfg} ml/min, 
        compatible con Enfermedad Renal Crónica estadio {etapa_erc}.
        
        ## 3. PLAN TERAPÉUTICO
        
        Se recomienda:
        - Control estricto de presión arterial
        - Dieta baja en sodio
        - Evitar nefrotóxicos
        
        ## 4. RECOMENDACIONES
        
        - Vigilar signos de alarma: edema, oliguria, hematuria
        - Control estricto de factores de riesgo cardiovascular
        
        ## 5. PLAN DE SEGUIMIENTO
        
        Se programa control en 3 meses con laboratorios previos.
        
        Fecha del informe: {datetime.now().strftime("%d/%m/%Y")}
        """
    
    def _generate_fallback_report(self, patient_data):
        """Genera un informe de respaldo cuando hay errores."""
        return "No se pudo generar el informe. Por favor, inténtelo de nuevo más tarde."
