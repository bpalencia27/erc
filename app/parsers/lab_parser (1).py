"""
Módulo para parsear resultados de laboratorio de diferentes fuentes
"""
import re
import logging
from datetime import datetime

def parse_lab_results(text):
    """
    Parsea resultados de laboratorio desde texto.
    
    Args:
        text (str): Texto del documento a analizar
        
    Returns:
        dict: Valores de laboratorio estructurados
    """
    if not text:
        return {}
    
    # Extraer valores de laboratorio usando expresiones regulares
    lab_values = {}
    
    # Patrones para diferentes tipos de laboratorios (más flexibles)
    patterns = [
        # Patrones de creatinina mejorados
        {'name': 'creatinina', 'regex': r'(?:CREATININA|Creatinina|creatinina|CREAT\.?|Creat\.?|creat\.?).{0,30}?(\d+\.?\d*)\s*(?:mg/dL|mg/dl)', 'unit': 'mg/dL'},
        {'name': 'creatinina', 'regex': r'(?:Cr|CR|cr)(?:\s|:).{0,10}?(\d+\.?\d*)\s*(?:mg/dL|mg/dl)', 'unit': 'mg/dL'},
        {'name': 'creatinina', 'regex': r'CREATININA.*?(\d+[.,]\d+)\s*(?:mg/dL|mg/dl)', 'unit': 'mg/dL'},
        {'name': 'creatinina', 'regex': r'Creatinina.*?(\d+[.,]\d+)\s*(?:mg/dL|mg/dl)', 'unit': 'mg/dL'},
        {'name': 'creatinina', 'regex': r'creatinina.*?(\d+[.,]\d+)\s*(?:mg/dL|mg/dl)', 'unit': 'mg/dL'},
        
        # Resto de patrones
        {'name': 'glucosa', 'regex': r'(?:GLUCOSA|Glucosa|glucosa).{0,30}?(\d+\.?\d*)\s*(?:mg/dL|mg/dl)', 'unit': 'mg/dL'},
        {'name': 'colesterol', 'regex': r'(?:COLESTEROL TOTAL|Colesterol total|colesterol).{0,30}?(\d+\.?\d*)\s*(?:mg/dL|mg/dl)', 'unit': 'mg/dL'},
        {'name': 'ldl', 'regex': r'(?:COLESTEROL DE BAJA DENSIDAD|LDL|ldl).{0,30}?(\d+\.?\d*)\s*(?:mg/dL|mg/dl)', 'unit': 'mg/dL'},
        {'name': 'hdl', 'regex': r'(?:COLESTEROL DE ALTA DENSIDAD|HDL|hdl).{0,30}?(\d+\.?\d*)\s*(?:mg/dL|mg/dl)', 'unit': 'mg/dL'},
        {'name': 'trigliceridos', 'regex': r'(?:TRIGLICERIDOS|Trigliceridos|triglicéridos).{0,30}?(\d+\.?\d*)\s*(?:mg/dL|mg/dl)', 'unit': 'mg/dL'},
        {'name': 'rac', 'regex': r'(?:RELACION MICROALBUMINURIA CREATININA|MICROALBUMINURIA).{0,30}?(\d+\.?\d*)\s*(?:mg/gr|mg/g)', 'unit': 'mg/g'},
        {'name': 'hba1c', 'regex': r'(?:HbA1c|Hemoglobina Glicosilada|hemoglobina glicosilada).{0,30}?(\d+\.?\d*)\s*(?:%|por ciento)', 'unit': '%'},
        {'name': 'potasio', 'regex': r'(?:POTASIO|Potasio|potasio).{0,30}?(\d+\.?\d*)\s*(?:mEq/L|mmol/L)', 'unit': 'mEq/L'},
        {'name': 'calcio', 'regex': r'(?:CALCIO|Calcio|calcio).{0,30}?(\d+\.?\d*)\s*(?:mg/dL|mg/dl)', 'unit': 'mg/dL'},
        {'name': 'fosforo', 'regex': r'(?:FOSFORO|Fósforo|fosforo).{0,30}?(\d+\.?\d*)\s*(?:mg/dL|mg/dl)', 'unit': 'mg/dL'},
        {'name': 'albumina', 'regex': r'(?:ALBUMINA|Albúmina|albumina).{0,30}?(\d+\.?\d*)\s*(?:g/dL|g/dl)', 'unit': 'g/dL'},
        {'name': 'sodio', 'regex': r'(?:SODIO|Sodio|sodio).{0,30}?(\d+\.?\d*)\s*(?:mEq/L|mmol/L)', 'unit': 'mEq/L'},
        {'name': 'pth', 'regex': r'(?:PARATIROIDEA|PTH|Paratiroidea).{0,30}?(\d+\.?\d*)\s*(?:pg/mL|pg/ml)', 'unit': 'pg/mL'},
        {'name': 'bun', 'regex': r'(?:BUN|Bun|bun|NITROGENO UREICO).{0,30}?(\d+\.?\d*)\s*(?:mg/dL|mg/dl)', 'unit': 'mg/dL'},
        {'name': 'acido_urico', 'regex': r'(?:ACIDO URICO|Ácido Úrico|acido urico).{0,30}?(\d+\.?\d*)\s*(?:mg/dL|mg/dl)', 'unit': 'mg/dL'},
        {'name': 'hemoglobina', 'regex': r'(?:HEMOGLOBINA|Hemoglobina|hemoglobina).{0,30}?(\d+\.?\d*)\s*(?:g/dL|g/dl)', 'unit': 'g/dL'},
        {'name': 'ferritina', 'regex': r'(?:FERRITINA|Ferritina|ferritina).{0,30}?(\d+\.?\d*)\s*(?:ng/mL|ng/ml)', 'unit': 'ng/mL'},
        {'name': 'urea', 'regex': r'(?:UREA|Urea|urea).{0,30}?(\d+\.?\d*)\s*(?:mg/dL|mg/dl)', 'unit': 'mg/dL'},
    ]
    
    # Extraer datos del paciente
    patient_data = {}
    
    # Patrones para datos del paciente
    nombre_match = re.search(r'Paciente:?\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]+)', text)
    if nombre_match:
        patient_data['nombre'] = nombre_match.group(1).strip()
    
    # Buscar identificación (múltiples formatos posibles)
    id_match = re.search(r'(?:Identificación|Identificacion|ID|Id)(?:\.)?:?\s*([A-Z]{1,2})?\s*(\d[\d\s.-]+)', text)
    if id_match:
        tipo_id = id_match.group(1) if id_match.group(1) else ''
        num_id = id_match.group(2).strip().replace(' ', '')
        patient_data['identificacion'] = f"{tipo_id} {num_id}".strip()
    
    # Buscar edad y sexo
    edad_sexo_match = re.search(r'Edad\s*(?:/\s*Sexo)?:?\s*(\d+)\s*(?:Años|años|Años|AÑOS)(?:[^F|M]*?)([F|M])', text)
    if edad_sexo_match:
        patient_data['edad'] = int(edad_sexo_match.group(1))
        patient_data['sexo'] = 'f' if edad_sexo_match.group(2) == 'F' else 'm'
    
    # Buscar fecha del informe
    fecha_match = re.search(r'Fecha(?:\s*(?:Ingreso|impresión|Informe))?:?\s*(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', text)
    if fecha_match:
        try:
            dia = int(fecha_match.group(1))
            mes = int(fecha_match.group(2))
            anio = int(fecha_match.group(3))
            if anio < 100:  # Ajustar año si es de dos dígitos
                anio += 2000
            patient_data['fecha_informe'] = f"{anio:04d}-{mes:02d}-{dia:02d}"
        except (ValueError, TypeError) as e:
            logging.error(f"Error al parsear fecha: {e}")
    
    # Extraer cada valor de laboratorio
    for pattern in patterns:
        match = re.search(pattern['regex'], text, re.IGNORECASE)
        if match:
            try:
                value = float(match.group(1))
                lab_values[pattern['name']] = {
                    'value': match.group(1),  # Mantener como string para preservar decimales exactos
                    'unit': pattern['unit']
                }
            except (ValueError, TypeError) as e:
                logging.error(f"Error al parsear valor de {pattern['name']}: {e}")
    
    result = {
        'results': lab_values
    }
    
    # Incluir datos del paciente si están disponibles
    if patient_data:
        result['patient_data'] = patient_data
    
    return result
