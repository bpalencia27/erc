"""
Helper para obtener instancias del cliente Gemini mejorado
y adaptar la interfaz para compatibilidad con el código existente
"""
import os
from typing import Dict, Any, Optional, List
import structlog
from .gemini_client import GeminiClient, GeminiConfig, PromptStrategy

logger = structlog.get_logger()

_CLIENT_INSTANCE = None

def get_gemini_client() -> 'GeminiClientAdapter':
    """
    Obtiene una instancia singleton del cliente Gemini adaptado
    para mantener compatibilidad con el código existente
    """
    global _CLIENT_INSTANCE
    if _CLIENT_INSTANCE is None:
        # Inicializar el cliente
        _CLIENT_INSTANCE = GeminiClientAdapter()
    return _CLIENT_INSTANCE

class GeminiClientAdapter:
    """
    Adapter para la compatibilidad con el código existente
    Convierte las nuevas funciones asíncronas en sincrónicas y mantiene
    la interfaz anterior para una transición gradual
    """
    
    def __init__(self):
        """Inicializa el adaptador con el cliente Gemini mejorado"""
        self.client = GeminiClient()
        logger.info("GeminiClientAdapter initialized")
    
    def extract_lab_values(self, text: str) -> Dict[str, Any]:
        """Extrae valores de laboratorio - versión sincrónica"""
        import asyncio
        
        try:
            # Creamos un nuevo event loop para la llamada asíncrona
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Ejecutamos la función asíncrona y esperamos el resultado
            result = loop.run_until_complete(self.client.extract_lab_values(text))
            loop.close()
            
            # Adaptar formato de respuesta para compatibilidad
            if result.get('status') == 'success':
                return {
                    'success': True,
                    'values': result.get('lab_data', {}),
                    'source': result.get('provider', 'gemini')
                }
            else:
                return {
                    'success': False, 
                    'error': result.get('error', 'Unknown error'),
                    'values': {}
                }
                
        except Exception as e:
            logger.exception("Error extracting lab values", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'values': {}
            }
    
    def analyze_patient(self, patient_data: Dict[str, Any], strategy: Optional[PromptStrategy] = None) -> Dict[str, Any]:
        """Analiza datos del paciente - versión sincrónica"""
        try:
            # Convertir a formato compatible con nuevo cliente
            formatted_data = self._adapt_patient_data(patient_data)
            
            # Procesar datos con el cliente mejorado
            result = self.client.process_medical_data(formatted_data)
            
            # Adaptar respuesta al formato esperado
            return {
                'success': result.get('status') == 'success',
                'analysis': result.get('analysis', ''),
                'provider': result.get('provider', 'unknown'),
                'timestamp': result.get('timestamp')
            }
            
        except Exception as e:
            logger.exception("Error analyzing patient data", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'analysis': 'Error en el análisis de datos del paciente.'
            }
    
    def generate_therapeutic_goals(self, patient_data: Dict[str, Any], analysis_text: str) -> Dict[str, Any]:
        """Genera objetivos terapéuticos basados en análisis previo"""
        import asyncio
        
        try:
            # Crear un prompt específico para objetivos terapéuticos
            goals_prompt = f"""
A partir del siguiente análisis médico, extrae y enumera 3-5 objetivos terapéuticos específicos, 
medibles y alcanzables para este paciente con enfermedad renal crónica.

ANÁLISIS PREVIO:
{analysis_text}

Utiliza el siguiente formato para cada objetivo:
1. [Objetivo] - [Justificación] - [Indicador de éxito]
"""
            # Creamos un nuevo event loop para la llamada asíncrona
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Ejecutamos la función asíncrona y esperamos el resultado
            response = loop.run_until_complete(
                self.client.generate(
                    prompt=goals_prompt,
                    strategy=PromptStrategy.MEDICAL_EXPERT
                )
            )
            loop.close()
            
            if response.success:
                return {
                    'success': True,
                    'goals': response.content,
                    'provider': response.provider
                }
            else:
                return {
                    'success': False,
                    'error': response.error,
                    'goals': 'No se pudieron generar objetivos terapéuticos.'
                }
                
        except Exception as e:
            logger.exception("Error generating therapeutic goals", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'goals': 'Error generando objetivos terapéuticos.'
            }
    
    def validate_connection(self) -> Dict[str, Any]:
        """Valida la conexión con Gemini y servicios de fallback"""
        return {
            'connected': self.client.is_gemini_configured,
            'model': self.client.config.model_name,
            'fallback_available': self.client.is_fallback_configured,
            'fallback_provider': self.client.config.fallback_provider,
            'cache_enabled': self.client.config.cache_enabled
        }
    
    def _adapt_patient_data(self, legacy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapta el formato antiguo de datos al nuevo formato esperado"""
        # Convertir formato antiguo al nuevo formato
        new_format = {
            "demographics": {
                "age": legacy_data.get("age"),
                "gender": legacy_data.get("sex"),
                "weight": legacy_data.get("weight"),
                "height": legacy_data.get("height")
            },
            "lab_results": {},
            "comorbidities": legacy_data.get("medical_history", []),
            "medications": legacy_data.get("medications", [])
        }
        
        # Manejar creatinina si se proporciona como valor independiente
        if "creatinine" in legacy_data and legacy_data["creatinine"]:
            creatinine_val = legacy_data["creatinine"]
            if isinstance(creatinine_val, (int, float)):
                # Crear una entrada de laboratorio con fecha actual
                from datetime import datetime
                current_date = datetime.now().strftime("%Y-%m-%d")
                new_format["lab_results"][current_date] = {
                    "funcion_renal": {
                        "creatinina": {"valor": creatinine_val, "unidad": "mg/dL"}
                    }
                }
        
        # Manejar otros valores de laboratorio
        if "lab_values" in legacy_data and legacy_data["lab_values"]:
            lab_values = legacy_data["lab_values"]
            # Si no hay fecha, usar la actual
            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Adaptar formato
            if current_date not in new_format["lab_results"]:
                new_format["lab_results"][current_date] = {}
                
            # Recorrer categorías de lab_values
            for category, tests in lab_values.items():
                if category not in new_format["lab_results"][current_date]:
                    new_format["lab_results"][current_date][category] = {}
                    
                # Recorrer pruebas individuales
                for test_name, test_value in tests.items():
                    # Manejar diferentes formatos de valores
                    if isinstance(test_value, dict) and "valor" in test_value:
                        # Ya está en el formato correcto
                        new_format["lab_results"][current_date][category][test_name] = test_value
                    elif isinstance(test_value, (int, float)):
                        # Convertir a formato con unidad (asumiendo unidades comunes)
                        unit = self._get_default_unit(test_name, category)
                        new_format["lab_results"][current_date][category][test_name] = {
                            "valor": test_value,
                            "unidad": unit
                        }
                    elif isinstance(test_value, str):
                        # Intentar extraer valor numérico y unidad
                        try:
                            import re
                            match = re.match(r'(\d+\.?\d*)\s*([a-zA-Z/%]+)?', test_value)
                            if match:
                                value = float(match.group(1))
                                unit = match.group(2) or self._get_default_unit(test_name, category)
                                new_format["lab_results"][current_date][category][test_name] = {
                                    "valor": value,
                                    "unidad": unit
                                }
                            else:
                                # No se pudo parsear, guardar como texto
                                new_format["lab_results"][current_date][category][test_name] = test_value
                        except:
                            # Si falla, guardar como está
                            new_format["lab_results"][current_date][category][test_name] = test_value
        
        return new_format
    
    def _get_default_unit(self, test_name: str, category: str) -> str:
        """Devuelve unidad por defecto para pruebas comunes"""
        # Diccionario de unidades comunes
        unit_map = {
            "creatinina": "mg/dL",
            "urea": "mg/dL",
            "bun": "mg/dL",
            "acido_urico": "mg/dL",
            "glucosa": "mg/dL",
            "hemoglobina": "g/dL",
            "hematocrito": "%",
            "leucocitos": "x10³/μL",
            "plaquetas": "x10³/μL",
            "sodio": "mEq/L",
            "potasio": "mEq/L",
            "cloro": "mEq/L",
            "calcio": "mg/dL",
            "fosforo": "mg/dL",
            "colesterol_total": "mg/dL",
            "ldl": "mg/dL",
            "hdl": "mg/dL",
            "trigliceridos": "mg/dL",
            "hba1c": "%",
            "tfg": "ml/min/1.73m²",
            "ast": "U/L",
            "alt": "U/L",
            "ggt": "U/L",
            "bilirrubina": "mg/dL",
            "albumina": "g/dL",
            "proteinas_totales": "g/dL",
            "pth": "pg/mL"
        }
        
        # Normalizar nombre de prueba
        test_lower = test_name.lower().replace(" ", "_")
        
        # Buscar unidad
        if test_lower in unit_map:
            return unit_map[test_lower]
        
        # Unidades por categoría como fallback
        category_map = {
            "funcion_renal": "mg/dL",
            "hemograma": "g/dL",
            "electrolitos": "mEq/L",
            "perfil_lipidico": "mg/dL",
            "hepaticos": "U/L",
            "glucemia": "mg/dL"
        }
        
        return category_map.get(category.lower(), "")
