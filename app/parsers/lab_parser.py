"""
Módulo para parsear resultados de laboratorio de diferentes fuentes
"""
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AdvancedLabParser:
    """Parser avanzado para resultados de laboratorio con validaciones específicas"""
    
    def __init__(self):
        # Patterns específicos para cada tipo de prueba
        self.patterns = {
            # DATOS DEL PACIENTE - Mejorados
            'patient_info': {
                'nombre': [
                    r'(?:nombre|paciente)[:\s]+([A-Za-záéíóúñÁÉÍÓÚÑ\s]+?)(?=\n|(?:documento|cc|edad|sexo))',
                    r'paciente[:\s]+([A-Za-záéíóúñÁÉÍÓÚÑ\s]+?)(?=\n|$)',
                    r'nombre\s+completo[:\s]+([A-Za-záéíóúñÁÉÍÓÚÑ\s]+?)(?=\n|$)'
                ],
                'sexo': [
                    r'(?:sexo|género)[:\s]*(masculino|femenino|m|f|hombre|mujer)',
                    r'(?:^|\n)\s*(?:sexo|genero)[:\s]*(masculino|femenino|m|f)',
                    r'(?:masculino|femenino)\s*(?=\n|$)'
                ],
                'edad': [
                    r'edad[:\s]+(\d+)\s*(?:años?)?',
                    r'(\d+)\s*años?\s*(?:de\s*edad)?',
                    r'edad\s*del\s*paciente[:\s]+(\d+)'
                ]
            },
            
            # CREATININA - CRÍTICO: Solo capturar de suero/sérica
            'renal_critical': {
                'creatinina_serica': [
                    # Patrones específicos para creatinina en suero
                    r'creatinina\s+(?:en\s+)?(?:suero|sérica|serica|plasma)[:\s]+(\d+[.,]?\d*)\s*(?:mg/dl|mg/dL)',
                    r'creatinina\s+sérica[:\s]+(\d+[.,]?\d*)',
                    r'creatinina[:\s]+(\d+[.,]?\d*)\s*mg/dl(?!\s*(?:en\s+)?orina)',
                    r'CREATININA\s+SERICA[:\s]+(\d+[.,]?\d*)',
                    # Evitar falsos positivos
                    r'(?<!orina\s)(?<!urinaria\s)creatinina[:\s]+(\d+[.,]?\d*)\s*mg/dl'
                ],
                'rac': [
                    # Relación Albúmina/Creatinina en mg/g
                    r'(?:relaci[óo]n\s+)?(?:alb[úu]mina|microalb[úu]mina)[/\s]+creatinina[:\s]+(\d+[.,]?\d*)\s*mg/g',
                    r'rac[:\s]+(\d+[.,]?\d*)\s*mg/g',
                    r'índice\s+alb[úu]mina[/\s]+creatinina[:\s]+(\d+[.,]?\d*)',
                    r'microalbuminuria[/\s]+creatinina[:\s]+(\d+[.,]?\d*)\s*mg/g',
                    r'cociente\s+alb[úu]mina[/\s]+creatinina[:\s]+(\d+[.,]?\d*)'
                ],
                'microalbuminuria': [
                    r'(?:micro)?alb[úu]mina\s+(?:en\s+)?orina[:\s]+(\d+[.,]?\d*)\s*mg',
                    r'microalbuminuria[:\s]+(\d+[.,]?\d*)\s*mg/(?:24h|día)',
                    r'alb[úu]mina\s+urinaria[:\s]+(\d+[.,]?\d*)'
                ]
            },
            
            # PERFIL LIPÍDICO
            'lipids': {
                'colesterol_total': [
                    r'colesterol\s+total[:\s]+(\d+[.,]?\d*)',
                    r'col\.\s*total[:\s]+(\d+[.,]?\d*)',
                    r'ct[:\s]+(\d+[.,]?\d*)\s*mg/dl'
                ],
                'ldl': [
                    r'(?:colesterol\s+)?ldl[:\s]+(\d+[.,]?\d*)',
                    r'c-ldl[:\s]+(\d+[.,]?\d*)',
                    r'ldl-c[:\s]+(\d+[.,]?\d*)'
                ],
                'hdl': [
                    r'(?:colesterol\s+)?hdl[:\s]+(\d+[.,]?\d*)',
                    r'c-hdl[:\s]+(\d+[.,]?\d*)',
                    r'hdl-c[:\s]+(\d+[.,]?\d*)'
                ],
                'trigliceridos': [
                    r'triglic[ée]ridos?[:\s]+(\d+[.,]?\d*)',
                    r'tg[:\s]+(\d+[.,]?\d*)\s*mg/dl'
                ]
            },
            
            # CONTROL DIABÉTICO
            'diabetes': {
                'glicemia': [
                    r'(?:glicemia|glucosa)(?:\s+en\s+ayunas)?[:\s]+(\d+[.,]?\d*)',
                    r'glucemia[:\s]+(\d+[.,]?\d*)',
                    r'glucosa\s+basal[:\s]+(\d+[.,]?\d*)'
                ],
                'hba1c': [
                    r'(?:hemoglobina\s+)?(?:glicosilada|glicada|hba1c|a1c)[:\s]+(\d+[.,]?\d*)',
                    r'hb\s*a1c[:\s]+(\d+[.,]?\d*)',
                    r'a1c[:\s]+(\d+[.,]?\d*)%?'
                ]
            },
            
            # OTROS VALORES IMPORTANTES
            'additional': {
                'hemoglobina': r'hemoglobina[:\s]+(\d+[.,]?\d*)',
                'hematocrito': r'hematocrito[:\s]+(\d+[.,]?\d*)',
                'albumina': r'alb[úu]mina\s+(?:sérica|en\s+suero)?[:\s]+(\d+[.,]?\d*)',
                'acido_urico': r'[áa]cido\s+[úu]rico[:\s]+(\d+[.,]?\d*)',
                'urea': r'(?:urea|bun)[:\s]+(\d+[.,]?\d*)',
                'sodio': r'(?:sodio|na)[:\s]+(\d+[.,]?\d*)',
                'potasio': r'(?:potasio|k)[:\s]+(\d+[.,]?\d*)',
                'calcio': r'(?:calcio|ca)[:\s]+(\d+[.,]?\d*)',
                'fosforo': r'(?:f[óo]sforo|p)[:\s]+(\d+[.,]?\d*)',
                'pth': r'(?:pth|paratohormona)[:\s]+(\d+[.,]?\d*)'
            }
        }
        
        # Patrones de exclusión para evitar falsos positivos
        self.exclusion_patterns = {
            'creatinina_orina': [
                r'creatinina\s+(?:en\s+)?orina',
                r'creatinina\s+urinaria',
                r'orina.*creatinina',
                r'creatinina.*orina\s+espont[áa]nea'
            ]
        }
    
    def parse(self, text):
        """
        Parsea el texto y extrae valores de laboratorio con validaciones mejoradas
        
        Args:
            text (str): Texto del laboratorio a parsear
            
        Returns:
            dict: Resultados parseados con estructura mejorada
        """
        if not text:
            return {'success': False, 'error': 'No se proporcionó texto'}
        
        # Normalizar texto
        text_normalized = self._normalize_text(text)
        
        # Verificar exclusiones primero
        if self._should_exclude_creatinine(text_normalized):
            logger.warning("Detectada creatinina en orina, será excluida del parsing")
        
        results = {
            'patient_data': {},
            'lab_results': {},
            'metadata': {
                'parsed_at': datetime.now().isoformat(),
                'warnings': []
            }
        }
        
        # Extraer información del paciente
        for field, patterns in self.patterns['patient_info'].items():
            value = self._extract_with_patterns(text_normalized, patterns)
            if value:
                if field == 'nombre':
                    results['patient_data'][field] = self._clean_name(value)
                elif field == 'sexo':
                    results['patient_data'][field] = self._normalize_sex(value)
                elif field == 'edad':
                    try:
                        results['patient_data'][field] = int(value)
                    except ValueError:
                        logger.warning(f"No se pudo convertir edad a entero: {value}")
        
        # Extraer valores de laboratorio críticos
        for category in ['renal_critical', 'lipids', 'diabetes', 'additional']:
            for key, patterns in self.patterns[category].items():
                if isinstance(patterns, list):
                    value = self._extract_with_patterns(text_normalized, patterns)
                else:
                    value = self._extract_with_patterns(text_normalized, [patterns])
                
                if value:
                    # Validaciones especiales
                    if key == 'creatinina_serica':
                        # Verificar que no sea de orina
                        if not self._is_creatinine_from_serum(text_normalized, value):
                            results['metadata']['warnings'].append(
                                "Creatinina encontrada pero parece ser de orina, omitida"
                            )
                            continue
                    
                    # Convertir y validar valor numérico
                    numeric_value = self._to_numeric(value)
                    if numeric_value is not None:
                        results['lab_results'][key] = numeric_value
                        
                        # Validaciones de rango
                        if key == 'rac' and numeric_value > 1000:
                            # Posiblemente en µg/mg, convertir a mg/g
                            results['lab_results'][key] = numeric_value / 1000
                            results['metadata']['warnings'].append(
                                f"RAC convertido de µg/mg a mg/g: {numeric_value} → {numeric_value/1000}"
                            )
        
        results['success'] = bool(results['lab_results'])
        return results
    
    def _normalize_text(self, text):
        """Normaliza el texto para mejor parsing"""
        # Convertir a minúsculas
        text = text.lower()
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        # Normalizar puntuación
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r'['']', "'", text)
        # Mantener saltos de línea para contexto
        text = re.sub(r'\r\n', '\n', text)
        return text.strip()
    
    def _extract_with_patterns(self, text, patterns):
        """Extrae valor usando múltiples patterns"""
        for pattern in patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    return match.group(1).strip()
            except Exception as e:
                logger.debug(f"Error en pattern {pattern}: {e}")
        return None
    
    def _should_exclude_creatinine(self, text):
        """Verifica si la creatinina debe ser excluida (es de orina)"""
        for pattern in self.exclusion_patterns['creatinina_orina']:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _is_creatinine_from_serum(self, text, value):
        """Verifica que la creatinina sea de suero y no de orina"""
        # Buscar contexto alrededor del valor
        value_pattern = re.escape(str(value))
        context_pattern = rf'.{{0,50}}{value_pattern}.{{0,50}}'
        
        match = re.search(context_pattern, text, re.IGNORECASE)
        if match:
            context = match.group(0)
            # Verificar indicadores de orina
            if any(word in context for word in ['orina', 'urinaria', 'micción', 'espontánea']):
                return False
            # Verificar indicadores de suero
            if any(word in context for word in ['suero', 'sérica', 'plasma', 'sangre']):
                return True
        
        # Por defecto, asumir que es de suero si no hay indicadores de orina
        return True
    
    def _clean_name(self, name):
        """Limpia y formatea el nombre del paciente"""
        # Eliminar números y caracteres especiales
        name = re.sub(r'[0-9]', '', name)
        name = re.sub(r'[^\w\s\-áéíóúñÁÉÍÓÚÑ]', '', name)
        # Capitalizar palabras
        return ' '.join(word.capitalize() for word in name.split())
    
    def _normalize_sex(self, sex_value):
        """Normaliza el valor del sexo a M o F"""
        sex_map = {
            'masculino': 'M', 'hombre': 'M', 'm': 'M', 'male': 'M', 'varón': 'M',
            'femenino': 'F', 'mujer': 'F', 'f': 'F', 'female': 'F', 'dama': 'F'
        }
        return sex_map.get(sex_value.lower(), sex_value.upper())
    
    def _to_numeric(self, value):
        """Convierte valor a numérico manejando comas y puntos"""
        if not value:
            return None
        
        try:
            # Manejar decimales con coma
            value = str(value).replace(',', '.')
            # Eliminar espacios
            value = value.strip()
            # Convertir
            return float(value)
        except ValueError:
            logger.warning(f"No se pudo convertir a número: {value}")
            return None

# Función wrapper para compatibilidad
def parse_lab_results(text):
    """Función de compatibilidad con el parser anterior"""
    parser = AdvancedLabParser()
    result = parser.parse(text)
    
    # Convertir al formato esperado por el código existente
    if result['success']:
        formatted_results = {}
        
        # Combinar patient_data y lab_results
        formatted_results.update(result['patient_data'])
        formatted_results.update(result['lab_results'])
        
        return {
            'success': True,
            'results': formatted_results,
            'metadata': result.get('metadata', {})
        }
    
    return result
