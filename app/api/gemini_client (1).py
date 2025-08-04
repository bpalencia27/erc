"""
Cliente para interactuar con la API de Google Gemini
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from app.utils.caching import cached_result
import google.generativeai as genai
from flask import current_app

# Cargar variables de entorno
load_dotenv()

class GeminiClient:
    """Cliente para interactuar con la API de Google Gemini."""
    
    def __init__(self):
        """Inicializa el cliente con la API key de Gemini."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_simulation = not self.api_key
        
        if self.use_simulation:
            logging.warning("API key de Google Gemini no configurada, usando modo simulado")
        else:
            # Configurar la API de Gemini con la clave
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
    
    def extract_lab_results(self, text):
        """Extrae resultados de laboratorio desde un texto utilizando IA."""
        if self.use_simulation:
            # Modo simulado cuando no hay API key
            return {
                "results": {
                    "creatinina": {"value": "1.2", "unit": "mg/dL"},
                    "glucosa": {"value": "105", "unit": "mg/dL"},
                    "ldl": {"value": "110", "unit": "mg/dL"}
                }
            }
            
        prompt = f"""
        Analiza el siguiente texto de un reporte médico y extrae los valores de laboratorio.
        Por favor, extrae con precisión los siguientes datos:
        
        1. Datos del paciente (nombre, edad, sexo, fecha del informe)
        2. Valores de laboratorio, prestando especial atención a:
           - Creatinina (mg/dL)
           - Glucosa (mg/dL)
           - Colesterol total, LDL, HDL (mg/dL)
           - Triglicéridos (mg/dL)
           - Potasio, Sodio (mEq/L)
           - Calcio, Fósforo (mg/dL)
           - Hemoglobina (g/dL)
           - PTH (pg/mL)
           - Albúmina (g/dL)
           - HbA1c (%)
           - Ácido úrico (mg/dL)
           - Urea o BUN (mg/dL)
        
        Devuelve un objeto JSON con este formato exacto:
        {{
            "patient_data": {{
                "nombre": "Nombre del paciente",
                "edad": "65",
                "sexo": "m/f",
                "fecha_informe": "YYYY-MM-DD"
            }},
            "results": {{
                "creatinina": {{ "value": "1.2", "unit": "mg/dL" }},
                "glucosa": {{ "value": "110", "unit": "mg/dL" }},
                ...
            }}
        }}
        
        Texto a analizar:
        {text}
        """
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            # Extraer solo el JSON (eliminar cualquier texto adicional)
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                return json.loads(json_str)
            else:
                # Si no se encuentra un JSON válido, devolver vacío
                logging.warning(f"No se pudo extraer JSON de la respuesta: {result_text}")
                return {}
                
        except Exception as e:
            logging.error(f"Error al extraer resultados con IA: {str(e)}")
            logging.error(f"Respuesta original: {response.text if 'response' in locals() else 'N/A'}")
            return {}
        
    def generate_patient_report(self, patient_data):
        """Genera un informe clínico completo basado en los datos del paciente."""
        if self.use_simulation:
            # Modo simulado cuando no hay API key
            return """
            <h3>Evaluación Médica del Paciente</h3>
            <p>Este es un informe simulado ya que no se ha configurado la API key de Google Gemini.</p>
            <p>Por favor, configure la variable de entorno GEMINI_API_KEY para obtener informes reales.</p>
            """
            
        # Preparar datos para el prompt
        nombre = patient_data.get('nombre', 'Paciente')
        edad = patient_data.get('edad', '')
        sexo = 'Masculino' if patient_data.get('sexo') == 'm' else 'Femenino'
        diagnosticos = ', '.join(patient_data.get('diagnosticos', [])) or 'Ninguno'
        
        # Datos de laboratorio
        lab_results = patient_data.get('labResults', {})
        lab_text = ""
        for key, value in lab_results.items():
            if isinstance(value, dict):
                lab_text += f"- {key.capitalize()}: {value.get('value')} {value.get('unit', '')}\n"
        
        # Medicamentos
        medicamentos = patient_data.get('medicamentos', [])
        med_text = ""
        for med in medicamentos:
            med_text += f"- {med.get('nombre', '')} {med.get('dosis', '')} {med.get('frecuencia', '')}\n"
        
        # Crear prompt
        prompt = f"""
        Genera un informe clínico detallado en formato HTML para el siguiente paciente:
        
        DATOS BÁSICOS:
        - Nombre: {nombre}
        - Edad: {edad} años
        - Sexo: {sexo}
        - IMC: {patient_data.get('imc', 'No disponible')}
        - TFG: {patient_data.get('tfg', 'No disponible')}
        - Riesgo Cardiovascular: {patient_data.get('riesgoCardiovascular', 'No calculado')}
        
        DIAGNÓSTICOS:
        {diagnosticos}
        
        RESULTADOS DE LABORATORIO:
        {lab_text if lab_text else "No disponibles"}
        
        MEDICAMENTOS ACTUALES:
        {med_text if med_text else "No hay medicamentos registrados"}
        
        PRESIÓN ARTERIAL:
        {self._format_blood_pressure(patient_data.get('presionArterial', []))}
        
        NOTAS ADICIONALES:
        - Condición de fragilidad: {"Sí" if patient_data.get('fragil') else "No"}
        - Adherencia al tratamiento: {patient_data.get('adherencia', 'No especificada')}
        - Barreras de acceso: {"Sí" if patient_data.get('barrerasAcceso') else "No"}
        
        Por favor, genera un informe clínico completo que incluya:
        1. Una evaluación general del paciente.
        2. Análisis de riesgo cardiovascular.
        3. Interpretación de los resultados de laboratorio.
        4. Recomendaciones de tratamiento y ajustes de medicación si fuera necesario.
        5. Plan de seguimiento.
        
        El informe debe estar en formato HTML con secciones claramente definidas. Usa tags como <h3> para títulos de sección, <p> para párrafos, <ul> y <li> para listas, y <strong> para énfasis. Evita usar clases CSS o estilos complejos.
        """
        
        try:
            response = self.model.generate_content(prompt)
            html_content = response.text
            
            # Limpiar el HTML si es necesario
            if "```html" in html_content:
                html_content = html_content.split("```html")[1].split("```")[0].strip()
            elif "```" in html_content:
                html_content = html_content.split("```")[1].split("```")[0].strip()
            
            return html_content
            
        except Exception as e:
            logging.error(f"Error al generar informe con IA: {str(e)}")
            return f"<p>Error al generar informe: {str(e)}</p>"
    
    def _format_blood_pressure(self, blood_pressure_data):
        """Formatea los datos de presión arterial para el prompt."""
        if not blood_pressure_data:
            return "No hay registros de presión arterial"
            
        result = ""
        for bp in blood_pressure_data:
            result += f"- {bp.get('sistolica', '')}/{bp.get('diastolica', '')} mmHg (Fecha: {bp.get('fecha', 'No registrada')})\n"
            
        return result
    
    def generate_medical_report(self, patient_data, report_type="complete"):
        """
        Genera un informe médico basado en los datos del paciente.
        
        Args:
            patient_data (dict): Datos completos del paciente
            report_type (str): Tipo de informe ('complete', 'summary', 'follow_up')
            
        Returns:
            str: Texto del informe generado
        """
        # Verificar modo de simulación
        if self.use_simulation:
            return self._generate_simulated_report(patient_data, report_type)
            
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
                
            # Llamar a la API de Gemini
            response = self.model.generate_content(prompt)
            return self._process_ai_response(response)
            
        except Exception as e:
            logging.error(f"Error al generar informe con Gemini: {str(e)}")
            # Devolver un informe de respaldo
            return self._generate_fallback_report(patient_data)
    
    @cached_result(expiration_seconds=3600)  # Cachear por 1 hora
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
