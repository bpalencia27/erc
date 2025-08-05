"""
Módulo para la evaluación de pacientes y cálculos clínicos
"""
import math
from datetime import datetime, timedelta

def calcular_tfg(edad, peso, creatinina, sexo):
    """
    Calcula la Tasa de Filtración Glomerular utilizando la fórmula de Cockcroft-Gault.
    
    Args:
        edad (int): Edad del paciente en años
        peso (float): Peso del paciente en kg
        creatinina (float): Nivel de creatinina en mg/dL
        sexo (str): Sexo del paciente ('m' para masculino, 'f' para femenino)
        
    Returns:
        float: TFG calculada
    """
    if creatinina <= 0:
        creatinina = 1.0
    if edad <= 0 or peso <= 0:
        return 0.0

    factor_sexo = 0.85 if sexo.lower() == "f" else 1.0
    tfg = ((140 - edad) * peso * factor_sexo) / (72 * creatinina)
    return round(tfg, 2)

def determinar_etapa_erc(tfg):
    """
    Determina el estadio G de la Enfermedad Renal Crónica según KDIGO.
    
    Args:
        tfg (float): TFG en ml/min/1.73m²
        
    Returns:
        str: Código de etapa ('g1', 'g2', 'g3a', 'g3b', 'g4', 'g5')
    """
    if tfg >= 90: return "g1"
    if tfg >= 60: return "g2"
    if tfg >= 45: return "g3a"
    if tfg >= 30: return "g3b"
    if tfg >= 15: return "g4"
    return "g5"

def clasificar_riesgo_cv(paciente, tfg):
    """
    Clasifica el riesgo cardiovascular del paciente.
    
    Args:
        paciente (dict): Datos del paciente
        tfg (float): Tasa de filtración glomerular
        
    Returns:
        str: Nivel de riesgo ('bajo', 'moderado', 'alto', 'muy_alto')
    """
    # Factores que determinan riesgo muy alto
    if (paciente.get("dm2", False) and paciente.get("lesion_organo_blanco", False)) or tfg < 30:
        return "muy_alto"
    
    # Factores que determinan riesgo alto
    if paciente.get("dm2", False) or tfg < 60 or paciente.get("erc", False):
        return "alto"
    
    # Factores que determinan riesgo moderado
    if paciente.get("hta", False) or paciente.get("dislipidemia", False) or paciente.get("tabaquismo", False):
        return "moderado"
    
    # Por defecto, riesgo bajo
    return "bajo"

def generar_informe_base(paciente, laboratorios):
    """
    Genera un objeto base con toda la información necesaria para el informe.
    
    Args:
        paciente (dict): Datos del paciente
        laboratorios (dict): Datos de laboratorios
        
    Returns:
        dict: Objeto con información procesada
    """
    # Copia de paciente para cálculos
    paciente_calculo = paciente.copy()
    
    # Extraer valores de laboratorios
    for lab_key, lab_data in laboratorios.items():
        if isinstance(lab_data, dict) and 'valor' in lab_data:
            paciente_calculo[lab_key] = lab_data['valor']

    # Calcular TFG
    tfg = calcular_tfg(
        paciente_calculo.get("edad", 0), 
        paciente_calculo.get("peso", 0), 
        paciente_calculo.get("creatinina", 1.0), 
        paciente_calculo.get("sexo", "m")
    )
    
    # Determinar etapa ERC
    etapa_erc = determinar_etapa_erc(tfg)
    
    # Determinar riesgo cardiovascular
    riesgo_cv = clasificar_riesgo_cv(paciente_calculo, tfg)
    
    # Construir objeto informe
    informe = {
        "paciente": paciente,
        "laboratorios": laboratorios,
        "valores": {
            "tfg": tfg,
            "etapa_erc": etapa_erc,
            "riesgo_cv": riesgo_cv
        },
        "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return informe
