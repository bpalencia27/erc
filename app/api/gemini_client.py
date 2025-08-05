"""
Cliente mejorado de Google Gemini con fallback y prompt engineering avanzado
Implementa chain-of-thought, few-shot prompting y manejo robusto de errores
"""
import os
import time
import json
from typing import Dict, Any, Optional, List, Union, Callable
from functools import wraps
import google.generativeai as genai
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import structlog
from dataclasses import dataclass
from enum import Enum

logger = structlog.get_logger()

class PromptStrategy(Enum):
    """Estrategias de prompting disponibles"""
    CHAIN_OF_THOUGHT = "chain_of_thought"
    FEW_SHOT = "few_shot"
    ZERO_SHOT = "zero_shot"
    MEDICAL_EXPERT = "medical_expert"

@dataclass
class GeminiConfig:
    """Configuración para el cliente Gemini"""
    api_key: str
    model_name: str = "gemini-1.5-pro"
    temperature: float = 0.7
    max_output_tokens: int = 8192
    timeout: int = 30
    retry_attempts: int = 3
    fallback_enabled: bool = True
    fallback_provider: str = "anthropic"  # Proveedor alternativo si Gemini falla
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hora por defecto

class ModelResponse:
    """Clase para manejar respuestas de modelos de forma unificada"""
    
    def __init__(self, 
                 content: str, 
                 provider: str,
                 success: bool = True,
                 error: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.content = content
        self.provider = provider
        self.success = success
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la respuesta a diccionario"""
        return {
            "content": self.content,
            "provider": self.provider,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def error_response(cls, error_message: str, provider: str = "unknown"):
        """Crea una respuesta de error"""
        return cls(
            content="",
            provider=provider,
            success=False,
            error=error_message
        )

class ResponseCache:
    """Caché simple para respuestas de modelos"""
    
    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.ttl = ttl  # Tiempo de vida en segundos
    
    def get(self, key: str) -> Optional[ModelResponse]:
        """Obtiene una respuesta cacheada si existe y no ha expirado"""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry.timestamp < self.ttl:
                logger.info("Cache hit", key=key)
                return entry
            else:
                # Entrada expirada
                del self.cache[key]
        return None
    
    def set(self, key: str, response: ModelResponse) -> None:
        """Guarda una respuesta en caché"""
        if response.success:  # Solo cachear respuestas exitosas
            self.cache[key] = response
            logger.debug("Response cached", key=key)
    
    def clear(self) -> None:
        """Limpia toda la caché"""
        self.cache.clear()

class GeminiClient:
    """Cliente mejorado para Google Gemini con fallback y mejores prácticas"""
    
    def __init__(self, config: Optional[GeminiConfig] = None):
        self.config = config or self._load_config()
        self._initialize_clients()
        self.prompt_templates = self._load_prompt_templates()
        self.cache = ResponseCache(ttl=self.config.cache_ttl) if self.config.cache_enabled else None
        
    def _load_config(self) -> GeminiConfig:
        """Carga la configuración desde variables de entorno"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.warning("GEMINI_API_KEY not found, using fallback mode")
            
        return GeminiConfig(
            api_key=api_key or "dummy-key-for-fallback",
            model_name=os.getenv('GEMINI_MODEL', 'gemini-1.5-pro'),
            temperature=float(os.getenv('GEMINI_TEMPERATURE', '0.7')),
            max_output_tokens=int(os.getenv('GEMINI_MAX_TOKENS', '8192')),
            fallback_enabled=os.getenv('GEMINI_FALLBACK_ENABLED', 'true').lower() == 'true',
            fallback_provider=os.getenv('FALLBACK_PROVIDER', 'anthropic'),
            cache_enabled=os.getenv('GEMINI_CACHE_ENABLED', 'true').lower() == 'true',
            cache_ttl=int(os.getenv('GEMINI_CACHE_TTL', '3600'))
        )
    
    def _initialize_clients(self):
        """Inicializa el cliente principal y los de fallback"""
        # Inicializar Gemini
        self.is_gemini_configured = False
        if self.config.api_key and self.config.api_key != "dummy-key-for-fallback":
            try:
                genai.configure(api_key=self.config.api_key)
                self.gemini_model = genai.GenerativeModel(
                    self.config.model_name,
                    generation_config={
                        "temperature": self.config.temperature,
                        "max_output_tokens": self.config.max_output_tokens,
                        "top_p": 0.95,
                    }
                )
                self.is_gemini_configured = True
                logger.info(f"Gemini client initialized with model: {self.config.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
        
        # Inicializar cliente de fallback (Anthropic Claude)
        self.is_fallback_configured = False
        if self.config.fallback_enabled:
            fallback_api_key = os.getenv('ANTHROPIC_API_KEY')
            if fallback_api_key:
                try:
                    self.fallback_client = anthropic.Anthropic(api_key=fallback_api_key)
                    self.is_fallback_configured = True
                    logger.info("Fallback client (Anthropic) initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize fallback client: {e}")
            else:
                logger.warning("Fallback enabled but no API key found for provider")
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Carga plantillas de prompts optimizadas para casos médicos"""
        return {
            "erc_analysis": """
Actúa como un nefrólogo experto con 20 años de experiencia en enfermedad renal crónica.
Analiza los siguientes datos del paciente paso a paso:

DATOS DEL PACIENTE:
{patient_data}

INSTRUCCIONES:
1. Primero, evalúa la función renal calculando el TFG exacto
2. Clasifica la etapa de ERC según KDIGO 2024
3. Identifica factores de riesgo cardiovascular
4. Analiza tendencias en los valores de laboratorio
5. Proporciona recomendaciones específicas

Utiliza el siguiente formato de respuesta:
### EVALUACIÓN RENAL
- TFG calculado: [valor] ml/min/1.73m²
- Etapa ERC: [clasificación]
- Progresión: [análisis de tendencia]

### FACTORES DE RIESGO
- Cardiovasculares: [lista detallada]
- Metabólicos: [lista detallada]
- Otros: [lista detallada]

### RECOMENDACIONES
1. [Recomendación específica con justificación]
2. [Recomendación específica con justificación]
3. [Seguimiento sugerido]

### ALERTAS CLÍNICAS
- [Valores críticos o situaciones urgentes]
""",
            
            "lab_extraction": """
Extrae TODOS los valores de laboratorio del siguiente texto.
Sé extremadamente preciso con números y unidades.

TEXTO:
{text}

FORMATO DE SALIDA REQUERIDO (JSON):
{
    "hemograma": {
        "hemoglobina": {"valor": null, "unidad": "g/dL"},
        "hematocrito": {"valor": null, "unidad": "%"},
        "leucocitos": {"valor": null, "unidad": "x10³/μL"},
        "plaquetas": {"valor": null, "unidad": "x10³/μL"}
    },
    "funcion_renal": {
        "creatinina": {"valor": null, "unidad": "mg/dL"},
        "bun": {"valor": null, "unidad": "mg/dL"},
        "acido_urico": {"valor": null, "unidad": "mg/dL"},
        "tfg": {"valor": null, "unidad": "ml/min/1.73m²"}
    },
    "electrolitos": {
        "sodio": {"valor": null, "unidad": "mEq/L"},
        "potasio": {"valor": null, "unidad": "mEq/L"},
        "cloro": {"valor": null, "unidad": "mEq/L"},
        "calcio": {"valor": null, "unidad": "mg/dL"},
        "fosforo": {"valor": null, "unidad": "mg/dL"}
    },
    "perfil_lipidico": {
        "colesterol_total": {"valor": null, "unidad": "mg/dL"},
        "ldl": {"valor": null, "unidad": "mg/dL"},
        "hdl": {"valor": null, "unidad": "mg/dL"},
        "trigliceridos": {"valor": null, "unidad": "mg/dL"}
    },
    "hepaticos": {
        "ast": {"valor": null, "unidad": "U/L"},
        "alt": {"valor": null, "unidad": "U/L"},
        "bilirrubina_total": {"valor": null, "unidad": "mg/dL"}
    },
    "glucemia": {
        "glucosa": {"valor": null, "unidad": "mg/dL"},
        "hba1c": {"valor": null, "unidad": "%"}
    }
}
""",
            "medical_summary": """
Crea un resumen médico conciso de la siguiente información clínica.
Incluye solo los datos relevantes para la evaluación renal y cardiovascular.

INFORMACIÓN CLÍNICA:
{clinical_info}

FORMATO DE RESPUESTA:
### RESUMEN CLÍNICO
- Diagnósticos principales:
- Medicación actual:
- Factores de riesgo:
- Valores críticos:

### CONCLUSIONES
- [Evaluación concisa del estado renal y cardiovascular]
"""
        }
    
    def _generate_cache_key(self, prompt: str, strategy: Optional[PromptStrategy] = None) -> str:
        """Genera una clave única para caché basada en el prompt y estrategia"""
        # Simplificado - en producción se recomienda usar hash criptográfico
        strategy_str = strategy.value if strategy else "default"
        prompt_hash = hash(prompt) % 10000000  # Simplificado
        return f"{strategy_str}_{prompt_hash}"
    
    @retry(
        retry=retry_if_exception_type((genai.types.BlockedPromptException, TimeoutError, ConnectionError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _generate_with_gemini(self, prompt: str) -> ModelResponse:
        """Genera respuesta utilizando Gemini con manejo de errores"""
        try:
            response = await self.gemini_model.generate_content_async(prompt)
            return ModelResponse(
                content=response.text,
                provider="gemini",
                metadata={"model": self.config.model_name}
            )
        except genai.types.BlockedPromptException as e:
            logger.warning("Prompt blocked by Gemini safety settings", error=str(e))
            raise
        except Exception as e:
            logger.error("Error generating content with Gemini", error=str(e))
            return ModelResponse.error_response(str(e), provider="gemini")
    
    async def _generate_with_anthropic(self, prompt: str) -> ModelResponse:
        """Genera respuesta utilizando Anthropic Claude como fallback"""
        try:
            response = await self.fallback_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )
            return ModelResponse(
                content=response.content[0].text,
                provider="anthropic",
                metadata={"model": "claude-3-haiku"}
            )
        except Exception as e:
            logger.error("Error generating content with Anthropic fallback", error=str(e))
            return ModelResponse.error_response(str(e), provider="anthropic")
    
    async def _fallback_response(self, prompt: str) -> ModelResponse:
        """Genera una respuesta de fallback cuando todos los proveedores fallan"""
        # Respuesta offline básica
        if "lab_extraction" in prompt.lower():
            return ModelResponse(
                content=json.dumps({"error": "No se pudo procesar la solicitud"}),
                provider="offline_fallback",
                success=False,
                error="All providers failed"
            )
        else:
            return ModelResponse(
                content="Lo siento, no puedo generar una respuesta en este momento. Por favor, revise los datos manualmente o intente más tarde.",
                provider="offline_fallback",
                success=False,
                error="All providers failed"
            )
    
    async def generate(self, 
                     prompt: str, 
                     strategy: Optional[PromptStrategy] = None,
                     template_name: Optional[str] = None,
                     template_vars: Optional[Dict[str, Any]] = None) -> ModelResponse:
        """
        Genera contenido con el prompt especificado y estrategia
        
        Args:
            prompt: El prompt base para la generación
            strategy: Estrategia de prompting a utilizar
            template_name: Nombre de la plantilla a utilizar
            template_vars: Variables para la plantilla
            
        Returns:
            ModelResponse con el contenido generado
        """
        # Preparar el prompt final
        final_prompt = prompt
        
        # Si se especifica una plantilla, usarla
        if template_name and template_name in self.prompt_templates:
            template = self.prompt_templates[template_name]
            if template_vars:
                try:
                    final_prompt = template.format(**template_vars)
                except KeyError as e:
                    logger.error(f"Missing template variable: {e}")
                    return ModelResponse.error_response(f"Missing template variable: {e}")
        
        # Aplicar estrategia de prompting si se especifica
        if strategy:
            final_prompt = self._apply_prompt_strategy(final_prompt, strategy)
        
        # Verificar caché primero si está habilitada
        if self.cache:
            cache_key = self._generate_cache_key(final_prompt, strategy)
            cached_response = self.cache.get(cache_key)
            if cached_response:
                return cached_response
        
        # Intento con Gemini
        if self.is_gemini_configured:
            response = await self._generate_with_gemini(final_prompt)
            if response.success:
                if self.cache:
                    self.cache.set(self._generate_cache_key(final_prompt, strategy), response)
                return response
        
        # Si Gemini falla y el fallback está habilitado, intentar con el proveedor de fallback
        if self.config.fallback_enabled and self.is_fallback_configured:
            logger.info("Gemini failed or not configured, trying fallback provider")
            response = await self._generate_with_anthropic(final_prompt)
            if response.success:
                if self.cache:
                    self.cache.set(self._generate_cache_key(final_prompt, strategy), response)
                return response
        
        # Si todo falla, usar respuesta offline
        return await self._fallback_response(final_prompt)
    
    def _apply_prompt_strategy(self, prompt: str, strategy: PromptStrategy) -> str:
        """Aplica una estrategia de prompting al prompt base"""
        if strategy == PromptStrategy.CHAIN_OF_THOUGHT:
            return f"{prompt}\n\nResuelve este problema paso a paso, explicando tu razonamiento en cada etapa."
        
        elif strategy == PromptStrategy.FEW_SHOT:
            # Ejemplo simplificado - en producción, usar ejemplos más elaborados
            few_shot_examples = """
Ejemplo 1:
Paciente: Mujer, 65 años, creatinina 1.8 mg/dL, albuminuria 300 mg/g
Análisis: TFG = 29 mL/min/1.73m², ERC etapa G3b A3, alto riesgo cardiovascular
Recomendación: Control estricto de PA < 130/80, IECA/ARA2, estatinas, nefroprotección

Ejemplo 2:
Paciente: Hombre, 58 años, creatinina 2.5 mg/dL, albuminuria 150 mg/g
Análisis: TFG = 23 mL/min/1.73m², ERC etapa G4 A2, riesgo muy alto de progresión
Recomendación: Referir a nefrología, restricción proteica, control metabólico estricto

Ahora tu caso:
"""
            return f"{few_shot_examples}\n{prompt}"
        
        elif strategy == PromptStrategy.MEDICAL_EXPERT:
            medical_context = """
Eres un especialista en nefrología y medicina interna con experiencia en enfermedad renal crónica.
Utilizas las guías KDIGO 2024 para la evaluación y manejo de la ERC.
Tienes conocimiento actualizado sobre marcadores de función renal, factores de riesgo cardiovascular,
y evidencia reciente sobre nefroprotección y objetivos terapéuticos.

Analiza el siguiente caso clínico con un enfoque sistemático y científico:
"""
            return f"{medical_context}\n{prompt}"
        
        # Default - zero shot
        return prompt
    
    def process_medical_data(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa datos médicos completos utilizando el modelo
        
        Args:
            patient_data: Diccionario con los datos del paciente
            
        Returns:
            Diccionario con resultados del análisis
        """
        try:
            # Convertir datos del paciente a formato texto
            patient_text = self._format_patient_data(patient_data)
            
            # Generar análisis
            analysis_response = self.generate(
                prompt="",
                template_name="erc_analysis",
                template_vars={"patient_data": patient_text},
                strategy=PromptStrategy.MEDICAL_EXPERT
            )
            
            # Si la respuesta es exitosa, formatear el resultado
            if analysis_response.success:
                return {
                    "analysis": analysis_response.content,
                    "status": "success",
                    "provider": analysis_response.provider,
                    "timestamp": analysis_response.timestamp
                }
            else:
                return {
                    "analysis": "No se pudo generar el análisis. Por favor revise los datos manualmente.",
                    "status": "error",
                    "error": analysis_response.error,
                    "timestamp": time.time()
                }
                
        except Exception as e:
            logger.exception("Error processing medical data", error=str(e))
            return {
                "analysis": "Error en el procesamiento de datos médicos.",
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }
    
    def _format_patient_data(self, patient_data: Dict[str, Any]) -> str:
        """Formatea los datos del paciente para el prompt"""
        # Implementación simplificada
        sections = []
        
        # Datos demográficos
        if "demographics" in patient_data:
            demo = patient_data["demographics"]
            demo_text = f"Paciente de {demo.get('age', 'N/A')} años, {demo.get('gender', 'N/A')}"
            sections.append(f"DATOS DEMOGRÁFICOS:\n{demo_text}")
        
        # Laboratorios
        if "lab_results" in patient_data and patient_data["lab_results"]:
            lab_text = "RESULTADOS DE LABORATORIO:\n"
            for date, labs in patient_data["lab_results"].items():
                lab_text += f"Fecha: {date}\n"
                for category, values in labs.items():
                    lab_text += f"  {category.upper()}:\n"
                    for test, result in values.items():
                        if isinstance(result, dict) and "valor" in result and "unidad" in result:
                            lab_text += f"    - {test}: {result['valor']} {result['unidad']}\n"
                        else:
                            lab_text += f"    - {test}: {result}\n"
            sections.append(lab_text)
        
        # Comorbilidades
        if "comorbidities" in patient_data and patient_data["comorbidities"]:
            comorbid_text = "COMORBILIDADES:\n"
            for condition in patient_data["comorbidities"]:
                comorbid_text += f"- {condition}\n"
            sections.append(comorbid_text)
        
        # Medicamentos
        if "medications" in patient_data and patient_data["medications"]:
            med_text = "MEDICAMENTOS ACTUALES:\n"
            for med in patient_data["medications"]:
                med_text += f"- {med}\n"
            sections.append(med_text)
        
        # Unir todas las secciones
        return "\n\n".join(sections)
    
    async def extract_lab_values(self, text: str) -> Dict[str, Any]:
        """
        Extrae valores de laboratorio de texto no estructurado
        
        Args:
            text: Texto con resultados de laboratorio
            
        Returns:
            Diccionario con valores de laboratorio estructurados
        """
        try:
            response = await self.generate(
                prompt="",
                template_name="lab_extraction",
                template_vars={"text": text},
                strategy=PromptStrategy.ZERO_SHOT
            )
            
            if response.success:
                try:
                    # Intentar parsear como JSON
                    lab_data = json.loads(response.content)
                    return {
                        "lab_data": lab_data,
                        "status": "success",
                        "provider": response.provider
                    }
                except json.JSONDecodeError:
                    logger.error("Failed to parse lab extraction response as JSON")
                    return {
                        "lab_data": {},
                        "status": "error",
                        "error": "Invalid JSON response format"
                    }
            else:
                return {
                    "lab_data": {},
                    "status": "error",
                    "error": response.error
                }
                
        except Exception as e:
            logger.exception("Error extracting lab values", error=str(e))
            return {
                "lab_data": {},
                "status": "error", 
                "error": str(e)
            }
