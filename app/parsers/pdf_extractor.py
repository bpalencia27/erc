"""
Módulo para la extracción de documentos PDF
"""
import re
import logging
import os
import PyPDF2

def extract_data_from_pdf(pdf_path):
    """
    Extrae datos de un archivo PDF de laboratorio.
    
    Args:
        pdf_path (str): Ruta al archivo PDF
        
    Returns:
        dict: Datos extraídos en formato estructurado
    """
    try:
        if not os.path.exists(pdf_path):
            logging.error(f"Archivo PDF no encontrado: {pdf_path}")
            return {'error': 'Archivo no encontrado'}
        
        # Extraer texto usando PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Extraer texto de todas las páginas
            texto_completo = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                texto_completo += page.extract_text() + "\n"
            
            # Intentar extraer fecha del documento
            fecha_match = re.search(r'Fecha[:\s]+(\d{2}[-/]\d{2}[-/]\d{4})', texto_completo)
            fecha = fecha_match.group(1) if fecha_match else None
            
            # Crear diccionario con datos extraídos
            extracted_data = {
                'texto_completo': texto_completo,
                'fecha': fecha
            }
            
            return extracted_data
        
    except Exception as e:
        logging.error(f"Error al extraer datos del PDF {pdf_path}: {str(e)}")
        return {'error': str(e)}
        
def extract_lab_values(text):
    """
    Extrae valores de laboratorio del texto utilizando expresiones regulares.
    
    Args:
        text (str): Texto extraído del PDF
        
    Returns:
        dict: Valores de laboratorio extraídos
    """
    lab_values = {}
    
    # Patrones para diferentes tipos de laboratorios
    patterns = {
        'creatinina': r'Creatinina:\s*(\d+\.?\d*)\s*mg/dL',
        'glicemia': r'Glucosa:\s*(\d+\.?\d*)\s*mg/dL',
        'colesterol_total': r'Colesterol Total:\s*(\d+\.?\d*)\s*mg/dL',
        'ldl': r'LDL:\s*(\d+\.?\d*)\s*mg/dL',
        'hdl': r'HDL:\s*(\d+\.?\d*)\s*mg/dL',
        'trigliceridos': r'Triglicéridos:\s*(\d+\.?\d*)\s*mg/dL',
        'rac': r'Relación Microalbuminuria/Creatinina:\s*(\d+\.?\d*)\s*mg/g',
        'hba1c': r'HbA1c:\s*(\d+\.?\d*)\s*%'
    }
    
    # Extracción de datos del paciente
    patient_data = {}
    
    # Extraer nombre del paciente
    name_match = re.search(r'Paciente:?\s*([A-Za-zÁÉÍÓÚáéíóúÑñ\s]+)', text)
    if name_match:
        patient_data['nombre'] = name_match.group(1).strip()
    
    # Extraer fecha de nacimiento o edad
    dob_match = re.search(r'Fecha de Nacimiento:?\s*(\d{2}[-/]\d{2}[-/]\d{4})', text)
    age_match = re.search(r'Edad:?\s*(\d+)', text)
    if dob_match:
        patient_data['fecha_nacimiento'] = dob_match.group(1)
    elif age_match:
        patient_data['edad'] = age_match.group(1)
    
    # Extraer género
    gender_match = re.search(r'(Género|Sexo):?\s*([MF]|Masculino|Femenino)', text)
    if gender_match:
        gender = gender_match.group(2)
        if gender.lower() in ['m', 'masculino']:
            patient_data['sexo'] = 'M'
        elif gender.lower() in ['f', 'femenino']:
            patient_data['sexo'] = 'F'
    
    # Extraer valores de laboratorio
    for lab_name, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            lab_values[lab_name] = {
                'value': match.group(1),
                'unit': 'mg/dL' if lab_name != 'hba1c' else '%'
            }
    
    return {
        'results': lab_values,
        'patient_data': patient_data
    }
