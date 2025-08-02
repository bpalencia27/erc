"""
Módulo para la extracción de documentos TXT
"""
import re
import logging

def extract_data_from_txt(txt_path):
    """
    Extrae datos de un archivo TXT de laboratorio.
    
    Args:
        txt_path (str): Ruta al archivo TXT
        
    Returns:
        dict: Datos extraídos en formato estructurado
    """
    try:
        # Leer el archivo de texto
        with open(txt_path, 'r', encoding='utf-8') as file:
            text_content = file.read()
        
        # Extraer datos relevantes
        extracted_data = {
            'texto_completo': text_content,
            'fecha': extract_date(text_content)
        }
        
        return extracted_data
        
    except Exception as e:
        logging.error(f"Error al extraer datos del TXT {txt_path}: {str(e)}")
        return {'error': str(e)}

def extract_date(text):
    """
    Extrae la fecha del texto utilizando expresiones regulares.
    
    Args:
        text (str): Texto del documento
        
    Returns:
        str: Fecha en formato YYYY-MM-DD o None si no se encuentra
    """
    # Patrones comunes para fechas
    date_patterns = [
        r'Fecha:\s*(\d{4}-\d{2}-\d{2})',  # 2025-07-15
        r'Fecha:\s*(\d{2}/\d{2}/\d{4})',  # 15/07/2025
        r'Fecha\s+de\s+muestra:\s*(\d{2}-\d{2}-\d{4})'  # 15-07-2025
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            
            # Convertir al formato estándar YYYY-MM-DD si es necesario
            if '/' in date_str:
                parts = date_str.split('/')
                if len(parts) == 3:
                    if len(parts[2]) == 4:  # Formato DD/MM/YYYY
                        return f"{parts[2]}-{parts[1]}-{parts[0]}"
            
            if '-' in date_str and len(date_str.split('-')) == 3:
                parts = date_str.split('-')
                if len(parts[2]) == 4:  # Formato DD-MM-YYYY
                    return f"{parts[2]}-{parts[1]}-{parts[0]}"
            
            return date_str
    
    return None
