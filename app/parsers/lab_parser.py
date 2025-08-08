"""
Módulo para parsear resultados de laboratorio de diferentes fuentes
"""
import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from app.parsers.pdf_extractor import extract_data_from_pdf
from app.parsers.txt_extractor import extract_data_from_txt
from app.parsers.lab_patterns import CREATININA_PATTERNS, LAB_PATTERNS, PATIENT_PATTERNS

def parse_lab_results(text: str) -> Dict[str, Any]:
    """
    Parsea resultados de laboratorio desde texto.
    
    Args:
        text (str): Texto del documento a analizar
        
    Returns:
        dict: Valores de laboratorio estructurados y datos del paciente
    """
    # Validación inicial
    if not text:
        return {'results': {}, 'patient_data': {}, 'status': 'error', 'message': 'No hay texto para analizar'}
    
    # Si text es un diccionario (del extractor), extraer el texto
    if isinstance(text, dict):
        if 'error' in text:
            return {'results': {}, 'patient_data': {}, 'status': 'error', 'message': text['error']}
        text = text.get('texto_completo', str(text))
    
    # Inicializar variables
    lab_values = {}
    patient_data = {}
    matched_patterns = set()
    status = 'success'
    message = 'Análisis completado exitosamente'
    
    try:
        # 1. Procesar patrones de creatinina
        excluded_regions = set()
        creatinine_found = False

        # Identificar regiones a excluir
        for pattern in CREATININA_PATTERNS:
            for exclude_pattern in pattern['exclude']:
                for match in re.finditer(exclude_pattern, text, re.IGNORECASE | re.MULTILINE):
                    excluded_regions.add((match.start(), match.end()))

        # Procesar patrones por prioridad
        for pattern in sorted(CREATININA_PATTERNS, 
                            key=lambda x: x.get('priority', 'normal') == 'high',
                            reverse=True):
            if creatinine_found:
                break

            for include_pattern in pattern['include']:
                if creatinine_found:
                    break

                for match in re.finditer(include_pattern, text, re.IGNORECASE | re.MULTILINE):
                    if creatinine_found:
                        break

                    # Verificar exclusiones
                    match_start, match_end = match.span()
                    is_excluded = any(
                        start <= match_start <= end or start <= match_end <= end
                        for start, end in excluded_regions
                    )

                    if not is_excluded:
                        try:
                            value = float(match.group(1).replace(',', '.'))
                            validation = pattern.get('validation', {})
                            min_value = validation.get('min_value', float('-inf'))
                            max_value = validation.get('max_value', float('inf'))

                            if min_value <= value <= max_value:
                                if 'decimals' in validation:
                                    value = round(value, validation['decimals'])

                                lab_values['creatinina'] = {
                                    'valor': value,
                                    'unidad': pattern['unit'],
                                    'confianza': 0.95 if pattern.get('priority') == 'high' else 0.9,
                                    'tipo': pattern['name']
                                }
                                matched_patterns.add('creatinina')
                                creatinine_found = True
                                break
                            else:
                                logging.warning(f"Valor de creatinina {value} fuera de rango válido")
                        except (ValueError, IndexError) as e:
                            logging.warning(f"Error al procesar valor de creatinina en patrón {pattern['name']}: {e}")
                    else:
                        logging.debug(f"Coincidencia de creatinina en {pattern['name']} encontrada en contexto excluido")

        # 2. Procesar otros patrones de laboratorio
        for lab_name, lab_info in LAB_PATTERNS.items():
            if lab_name in matched_patterns:
                continue

            pattern = lab_info['regex']
            match = re.search(pattern, text, re.IGNORECASE)
            
            if match:
                try:
                    value = float(match.group(1).replace(',', '.'))
                    if 'multiplier' in lab_info:
                        value *= lab_info['multiplier']
                        
                    lab_values[lab_name] = {
                        'valor': value,
                        'unidad': lab_info['unit'],
                        'confianza': lab_info.get('confidence', 0.8)
                    }
                    matched_patterns.add(lab_name)
                except (ValueError, AttributeError) as e:
                    logging.warning(f"Error procesando {lab_name}: {str(e)}")

        # 3. Buscar datos del paciente
        for field_name, pattern_info in PATIENT_PATTERNS.items():
            match = re.search(pattern_info['regex'], text, re.IGNORECASE)
            if match:
                try:
                    patient_data[field_name] = match.group(1).strip()
                except (IndexError, AttributeError) as e:
                    logging.warning(f"Error procesando dato de paciente {field_name}: {str(e)}")

    except Exception as e:
        logging.error(f"Error general en el procesamiento: {str(e)}")
        status = 'error'
        message = f'Error en el procesamiento: {str(e)}'

    # 4. Validar resultados
    if not lab_values and not patient_data:
        status = 'warning'
        message = 'No se encontraron resultados ni datos del paciente'
    elif not lab_values:
        status = 'warning'
        message = 'No se encontraron resultados de laboratorio'
    elif not patient_data:
        status = 'warning'
        message = 'No se encontraron datos del paciente'

    # 5. Preparar respuesta
    return {
        'results': lab_values,
        'patient_data': patient_data,
        'status': status,
        'message': message
    }
