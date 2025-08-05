"""
Cliente mejorado para Google Gemini API
Implementa mejores prácticas de prompt engineering y manejo de errores
"""
import google.generativeai as genai
from typing import Dict, List, Optional, Any
import structlog
import asyncio
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel, Field
import os

logger = structlog.get_logger()

class MedicalReport(BaseModel):
    """Modelo para validar informes médicos generados"""
    patient_id: str
    summary: str
    risk_assessment: str
    recommendations: List[str]
    lab_interpretation: Dict[str, Any]
    follow_up: str
    generated_at: str

class GeminiClient:
    """Cliente avanzado para Google Gemini API con mejores prácticas 2025"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("API key de Gemini no configurada")
        
        genai.configure(api_key=self.api_key)
        
        # Configurar modelo con parámetros optimizados
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
        ]
        
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_medical_report(self, patient_data: Dict) -> MedicalReport:
        """
        Genera un informe médico usando Chain-of-Thought prompting
        """
        # Prompt mejorado con técnicas de 2025
        prompt = self._create_medical_prompt(patient_data)
        
        try:
            # Generar respuesta
            response = await self._async_generate(prompt)
            
            # Parsear y validar respuesta
            report_data = self._parse_response(response.text)
            
            # Validar con Pydantic
            report = MedicalReport(**report_data)
            
            logger.info("Informe médico generado exitosamente",
                       patient_id=patient_data.get('id'))
            
            return report
            
        except Exception as e:
            logger.error("Error generando informe médico",
                        error=str(e),
                        patient_id=patient_data.get('id'))
            raise
    
    def _create_medical_prompt(self, patient_data: Dict) -> str:
        """
        Crea un prompt optimizado usando mejores prácticas de prompt engineering
        """
        # Few-shot examples para mejorar la calidad
        few_shot_examples = """
        Ejemplo de análisis:
        Paciente: Hombre, 65 años
        Creatinina: 2.1 mg/dL (elevada)
        TFG: 35 mL/min/1.73m² (reducida)
        Diagnóstico: ERC estadio 3b
        Riesgo CV: Alto (diabetes + hipertensión)
        Recomendaciones: Control trimestral, ajuste medicación, dieta renal
        """
        
        # Chain-of-thought prompting
        prompt = f"""
        Actúa como un nefrólogo experto analizando datos de un paciente con enfermedad renal crónica.
        
        {few_shot_examples}
        
        Analiza paso a paso los siguientes datos del paciente:
        
        DATOS DEL PACIENTE:
        {json.dumps(patient_data, indent=2, ensure_ascii=False)}
        
        INSTRUCCIONES - Realiza el análisis siguiendo estos pasos:
        
        1. EVALUACIÓN DE FUNCIÓN RENAL:
           - Calcula y clasifica la TFG según CKD-EPI 2021
           - Determina el estadio de ERC (G1-G5)
           - Evalúa la albuminuria (A1-A3)
        
        2. ESTRATIFICACIÓN DE RIESGO CARDIOVASCULAR:
           - Identifica factores de riesgo presentes
           - Calcula el riesgo según guías ESC/ESH 2025
           - Determina el nivel de riesgo (bajo/moderado/alto/muy alto)
        
        3. EVALUACIÓN DE COMORBILIDADES:
           - Diabetes: control glucémico (HbA1c objetivo)
           - Hipertensión: control de PA (objetivo según edad/fragilidad)
           - Dislipidemia: objetivos LDL según riesgo CV
           - Anemia: evaluar hemoglobina
        
        4. RECOMENDACIONES TERAPÉUTICAS:
           - Medicación: IECA/ARA2, estatinas, antidiabéticos
           - Dieta: restricción proteica, sodio, potasio según estadio
           - Estilo de vida: ejercicio, cesación tabáquica
           - Vacunación: influenza, neumococo, COVID-19, hepatitis B
        
        5. PLAN DE SEGUIMIENTO:
           - Frecuencia de controles según estadio
           - Laboratorios a solicitar
           - Interconsultas necesarias
           - Criterios de derivación a nefrología/diálisis
        
        FORMATO DE RESPUESTA - Estructura tu respuesta como JSON:
        {{
            "patient_id": "identificador",
            "summary": "resumen ejecutivo del caso",
            "risk_assessment": "evaluación detallada del riesgo",
            "recommendations": ["lista de recomendaciones específicas"],
            "lab_interpretation": {{
                "parametro": "interpretación y significado clínico"
            }},
            "follow_up": "plan de seguimiento detallado",
            "generated_at": "timestamp ISO"
        }}
        
        Sé preciso, basado en evidencia y considera las guías clínicas más recientes (2025).
        """
        
        return prompt
    
    async def _async_generate(self, prompt: str):
        """Genera respuesta de forma asíncrona"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.model.generate_content,
            prompt
        )
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parsea y limpia la respuesta de Gemini"""
        try:
            # Intentar extraer JSON de la respuesta
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                # Si no hay JSON, estructurar la respuesta
                return self._structure_text_response(response_text)
                
        except json.JSONDecodeError as e:
            logger.error("Error parseando respuesta JSON", error=str(e))
            return self._structure_text_response(response_text)
    
    def _structure_text_response(self, text: str) -> Dict:
        """Estructura una respuesta de texto en el formato esperado"""
        from datetime import datetime
        
        return {
            "patient_id": "unknown",
            "summary": text[:500] if len(text) > 500 else text,
            "risk_assessment": "Evaluación pendiente de revisión manual",
            "recommendations": text.split('\n')[:5],
            "lab_interpretation": {"general": text},
            "follow_up": "Seguimiento según criterio médico",
            "generated_at": datetime.now().isoformat()
        }
    
    async def analyze_lab_document(self, document_text: str) -> Dict:
        """
        Analiza un documento de laboratorio y extrae información estructurada
        """
        prompt = f"""
        Analiza el siguiente documento de laboratorio y extrae la información en formato estructurado:
        
        DOCUMENTO:
        {document_text}
        
        Extrae y estructura:
        1. Datos del paciente (nombre, edad, sexo)
        2. Fecha del estudio
        3. Todos los parámetros de laboratorio con sus valores y unidades
        4. Valores fuera de rango normal
        5. Interpretación clínica básica
        
        Responde en formato JSON.
        """
        
        try:
            response = await self._async_generate(prompt)
            return self._parse_response(response.text)
        except Exception as e:
            logger.error("Error analizando documento", error=str(e))
            raise
