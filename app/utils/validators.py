"""
Funciones de validación para la aplicación
"""
from typing import Dict, Any, Optional, List
import os
from werkzeug.utils import secure_filename

def validate_file_upload(file) -> Optional[str]:
    """
    Valida un archivo cargado
    
    Args:
        file: El archivo cargado
        
    Returns:
        str: Mensaje de error si hay algún problema, None si el archivo es válido
    """
    # Verificar si se proporcionó un archivo
    if not file:
        return "No se proporcionó archivo"
    
    # Verificar si el archivo tiene un nombre
    if file.filename == '':
        return "No se seleccionó ningún archivo"
    
    # Verificar la extensión
    allowed_extensions = {'pdf', 'txt', 'csv', 'xlsx'}
    filename = secure_filename(file.filename)
    if not '.' in filename or filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return f"Tipo de archivo no permitido. Use: {', '.join(allowed_extensions)}"
    
    # Verificar tamaño (15MB máximo)
    max_size = 15 * 1024 * 1024
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > max_size:
        return f"Archivo demasiado grande. Tamaño máximo: 15MB"
    
    return None

def validate_patient_data(data: Dict[str, Any]) -> Optional[str]:
    """
    Valida los datos del paciente
    
    Args:
        data: Diccionario con los datos del paciente
        
    Returns:
        str: Mensaje de error si hay algún problema, None si los datos son válidos
    """
    # Verificar datos básicos
    if not data:
        return "No se proporcionaron datos del paciente"
    
    # Verificar campos requeridos
    required_fields = ['edad', 'sexo']
    for field in required_fields:
        if field not in data:
            return f"Falta el campo requerido: {field}"
    
    # Validar edad
    try:
        edad = int(data['edad'])
        if edad < 0 or edad > 120:
            return "Edad fuera de rango (0-120)"
    except (ValueError, TypeError):
        return "La edad debe ser un número entero"
    
    # Validar sexo
    if data['sexo'] not in ['M', 'F']:
        return "Sexo debe ser 'M' o 'F'"
    
    # Validar valores de laboratorio
    if 'lab_values' in data:
        # Aquí se podrían validar los valores específicos de laboratorio
        pass
    
    return None
