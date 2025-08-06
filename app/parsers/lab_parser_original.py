"""
Módulo para parsear resultados de laboratorio de diferentes fuentes
"""
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ImprovedLabParser:
    """Parser mejorado para resultados de laboratorio con validaciones"""
    
    def __init__(self):
        self.patterns = {
            # Información del paciente
            'patient_info': {
                'nombre': [
                    r'(?:nombre|paciente)[:\s]+([a-záéíóúñ\s]+?)(?=\n|documento|cc|edad|$)',
                    r'paciente[:\s]+([a-záéíóúñ\s]+?)(?=\n|$)'
                ],
                'sexo': [
                    r'(?:sexo|género)[:\s]+(masculino|femenino|m|f|hombre|mujer)',
                    r'(?:^|\n)\s*(masculino|femenino|m|f|hombre|mujer)\s*(?:\n|$)'
                ],
                'edad': [
                    r'edad[:\s]+(\d+)\s*(?:años?)?',
                    r'(\d+)\s*años?\s*(?:de\s*edad)?'
                ]
            },
            
            # Función renal - CRÍTICO
            'renal': {
                'creatinina_suero': [
                    r'creatinina\s+(?:en\s+)?(?:suero|sérica|plasma)[:\s]+(\d+\.?\d*)\s*mg/dl',
                    r'creatinina\s+sérica[:\s]+(\d+\.?\d*)',
                    r'creatinina[:\s]+(\d+\.?\d*)\s*mg/dl(?!\s*(?:en\s+)?orina)'
                ],
                'rac': [
                    r'(?:relaci[óo]n\s+)?(?:alb[úu]mina|microalb[úu]mina)[/\s]+creatinina[:\s]+(\d+\.?\d*)\s*mg/g',
                    r'rac[:\s]+(\d+\.?\d*)\s*mg/g',
                    r'índice\s+alb[úu]mina[/\s]+creatinina[:\s]+(\d+\.?\d*)'
                ],
                'microalbuminuria': [
                    r'(?:micro)?alb[úu]mina\s+(?:en\s+)?orina[:\s]+(\d+\.?\d*)\s*mg',
                    r'microalbuminuria[:\s]+(\d+\.?\d*)'
                ]
            },
            
            # Perfil lipídico
            'lipids': {
                'colesterol_total': r'colesterol\s+total[:\s]+(\d+\.?\d*)',
                'ldl': r'(?:colesterol\s+)?ldl[:\s]+(\d+\.?\d*)',
                'hdl': r'(?:colesterol\s+)?hdl[:\s]+(\d+\.?\d*)',
                'trigliceridos': r'triglic[ée]ridos?[:\s]+(\d+\.?\d*)'
            },
            
            # Control diabético
            'diabetes': {
                'glicemia': r'(?:glicemia|glucosa)(?:\s+en\s+ayunas)?[:\s]+(\d+\.?\d*)',
                'hba1c': r'(?:hemoglobina\s+)?(?:glicosilada|hba1c|a1c)[:\s]+(\d+\.?\d*)'
            }
        }
        
    def parse(self, text):
        """Parsea el texto y extrae valores de laboratorio"""
        if not text:
            return {'success': False, 'error': 'No se proporcionó texto'}
        
        # Normalizar texto
        text = self._normalize_text(text)
        results = {}
        
        # Extraer por categorías
        for category, patterns in self.patterns.items():
            if isinstance(patterns, dict):
                for key, pattern_list in patterns.items():
                    value = self._extract_value(text, pattern_list if isinstance(pattern_list, list) else [pattern_list])
                    if value is not None:
                        results[key] = value
        
        # Validaciones específicas
        results = self._validate_results(results, text)
        
        return {
            'success': True,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def _normalize_text(self, text):
        """Normaliza el texto para mejor parsing"""
        # Convertir a minúsculas
        text = text.lower()
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        # Normalizar puntuación
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r'['']', "'", text)
        return text.strip()
    
    def _extract_value(self, text, patterns):
        """Extrae valor usando múltiples patterns"""
        for pattern in patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    return self._process_value(match.group(1))
            except Exception as e:
                logger.warning(f"Error en pattern {pattern}: {e}")
        return None
    
    def _process_value(self, value):
        """Procesa y convierte el valor extraído"""
        if not value:
            return None
            
        value = value.strip()
        
        # Intentar convertir a número
        try:
            if '.' in value or ',' in value:
                # Manejar decimales con coma
                value = value.replace(',', '.')
                return float(value)
            else:
                return int(value)
        except ValueError:
            # Si no es número, devolver como string
            return value
    
    def _validate_results(self, results, original_text):
        """Valida y corrige resultados extraídos"""
        
        # Validar creatinina - NO debe ser de orina
        if 'creatinina_suero' in results:
            # Buscar indicadores de que es creatinina en orina
            orina_patterns = [
                r'creatinina.{0,20}orina',
                r'orina.{0,20}creatinina',
                r'creatinina\s+urinaria'
            ]
            
            for pattern in orina_patterns:
                if re.search(pattern, original_text, re.IGNORECASE):
                    # Verificar que realmente no es de suero
                    if not re.search(r'creatinina.{0,10}(?:suero|sérica|plasma)', original_text, re.IGNORECASE):
                        logger.warning("Creatinina detectada parece ser de orina, eliminando")
                        results.pop('creatinina_suero', None)
                        break
        
        # Normalizar sexo
        if 'sexo' in results:
            sex_map = {
                'masculino': 'M', 'hombre': 'M', 'm': 'M', 'male': 'M',
                'femenino': 'F', 'mujer': 'F', 'f': 'F', 'female': 'F'
            }
            results['sexo'] = sex_map.get(str(results['sexo']).lower(), results['sexo'])
        
        # Validar edad
        if 'edad' in results:
            edad = results['edad']
            if isinstance(edad, (int, float)):
                if not (0 < edad < 150):
                    logger.warning(f"Edad fuera de rango válido: {edad}")
                    results.pop('edad', None)
        
        # Validar RAC (debe estar en mg/g)
        if 'rac' in results:
            rac = results['rac']
            if isinstance(rac, (int, float)):
                # Si el valor es muy alto, podría estar en µg/mg
                if rac > 1000:
                    logger.info(f"RAC muy alto ({rac}), posiblemente en µg/mg, convirtiendo a mg/g")
                    results['rac'] = rac / 1000
        
        return results

# Función helper para usar el parser
def parse_lab_results(text):
    """Función wrapper para compatibilidad"""
    parser = ImprovedLabParser()
    return parser.parse(text)
