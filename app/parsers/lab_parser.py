"""
Módulo para parsear resultados de laboratorio de diferentes fuentes
"""
import re
import logging

def parse_lab_results(raw_data):
    """
    Parsea resultados de laboratorio desde datos extraídos de documentos.
    
    Args:
        raw_data (dict): Datos extraídos del documento
        
    Returns:
        dict: Valores de laboratorio estructurados
    """
    if 'error' in raw_data:
        return {'error': raw_data['error']}
    
    text = raw_data.get('texto_completo', '')
    date = raw_data.get('fecha')
    
    # Extraer valores de laboratorio usando expresiones regulares
    lab_values = {}
    
    # Patrones para diferentes tipos de laboratorios
    patterns = {
        'creatinina': r'Creatinina:?\s*(\d+\.?\d*)\s*(?:mg/dL|mg/dl)',
        'glucosa': r'Glucosa:?\s*(\d+\.?\d*)\s*(?:mg/dL|mg/dl)',
        'glicemia': r'Glicemia:?\s*(\d+\.?\d*)\s*(?:mg/dL|mg/dl)',
        'colesterol_total': r'Colesterol(?:\s+Total)?:?\s*(\d+\.?\d*)\s*(?:mg/dL|mg/dl)',
        'ldl': r'(?:Colesterol\s+)?LDL:?\s*(\d+\.?\d*)\s*(?:mg/dL|mg/dl)',
        'hdl': r'(?:Colesterol\s+)?HDL:?\s*(\d+\.?\d*)\s*(?:mg/dL|mg/dl)',
        'trigliceridos': r'Triglicéridos:?\s*(\d+\.?\d*)\s*(?:mg/dL|mg/dl)',
        'hba1c': r'Hemoglobina\s+(?:Glicosilada|glucosilada|HbA1c):?\s*(\d+\.?\d*)\s*(?:%|por ciento)',
        'rac': r'(?:Relación\s+)?Albumina[/-]Creatinina:?\s*(\d+\.?\d*)\s*(?:mg/g|mcg/mg)',
        'potasio': r'Potasio:?\s*(\d+\.?\d*)\s*(?:mEq/L|mmol/L)',
        'calcio': r'Calcio:?\s*(\d+\.?\d*)\s*(?:mg/dL|mg/dl)',
        'fosforo': r'Fósforo:?\s*(\d+\.?\d*)\s*(?:mg/dL|mg/dl)',
        'pth': r'(?:Hormona\s+)?Paratiroidea:?\s*(\d+\.?\d*)\s*(?:pg/mL|pg/ml)',
    }
    
    # Extraer cada valor de laboratorio
    for lab_name, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                lab_values[lab_name] = {
                    'valor': float(match.group(1)),
                    'fecha': date
                }
            except (ValueError, TypeError):
                logging.warning(f"No se pudo convertir el valor de {lab_name} a número")
    
    # Si no se encontró ningún valor, devolver error
    if not lab_values:
        return {'error': 'No se encontraron valores de laboratorio en el documento'}
    
    return lab_values
