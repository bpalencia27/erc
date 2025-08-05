"""
Módulo para la evaluación de pacientes y cálculos clínicos
"""
import math
from datetime import datetime, timedelta

class PatientEvaluator:
    """
    Clase para evaluar datos clínicos de pacientes con ERC
    """
    
    def __init__(self):
        """Inicializar evaluador de pacientes"""
        pass
        
    def calculate_tfg(self, patient_data):
        """
        Calcula la Tasa de Filtración Glomerular
        
        Args:
            patient_data (dict): Datos del paciente (edad, peso, creatinina, sexo)
            
        Returns:
            float: TFG calculada
        """
        edad = patient_data.get('edad', 0)
        peso = patient_data.get('peso', 0)
        creatinina = patient_data.get('creatinina', 0)
        sexo = patient_data.get('sexo', 'M')
        
        return calcular_tfg(edad, peso, creatinina, sexo)
    
    def determine_erc_stage(self, tfg):
        """
        Determina la etapa de la ERC
        
        Args:
            tfg (float): TFG en ml/min/1.73m²
            
        Returns:
            str: Etapa de la ERC
        """
        return determinar_etapa_erc(tfg)
    
    def evaluate_patient(self, patient_data):
        """
        Realiza una evaluación completa del paciente
        
        Args:
            patient_data (dict): Datos del paciente y valores de laboratorio
            
        Returns:
            dict: Resultado de la evaluación
        """
        # Extraer datos básicos
        edad = patient_data.get('edad', 0)
        sexo = patient_data.get('sexo', 'M')
        peso = patient_data.get('peso', 0)
        
        # Extraer valores de laboratorio
        lab_values = patient_data.get('lab_values', {})
        creatinina = float(lab_values.get('creatinina', {}).get('value', 0))
        
        # Calcular TFG
        tfg = calcular_tfg(edad, peso, creatinina, sexo)
        
        # Determinar etapa ERC
        etapa_erc = determinar_etapa_erc(tfg)
        
        # Recomendaciones según etapa
        recomendaciones = generar_recomendaciones(etapa_erc, lab_values)
        
        # Construir resultado
        resultado = {
            'tfg': tfg,
            'etapa_erc': etapa_erc,
            'recomendaciones': recomendaciones,
            'valores_criticos': identificar_valores_criticos(lab_values)
        }
        
        return resultado

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
    # Asegurar que los valores son numéricos
    try:
        creatinina = float(creatinina)
        edad = float(edad)
    except (TypeError, ValueError):
        return 0.0
        
    if creatinina <= 0:
        creatinina = 1.0
    if edad <= 0:
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

def generar_recomendaciones(etapa_erc, lab_values):
    """
    Genera recomendaciones basadas en la etapa de ERC y valores de laboratorio
    
    Args:
        etapa_erc (str): Etapa de ERC (g1, g2, g3a, g3b, g4, g5)
        lab_values (dict): Valores de laboratorio
        
    Returns:
        list: Lista de recomendaciones
    """
    recomendaciones = []
    
    # Recomendaciones básicas para todas las etapas
    recomendaciones.append("Mantener una dieta balanceada baja en sodio")
    recomendaciones.append("Realizar actividad física regular según tolerancia")
    
    # Recomendaciones específicas por etapa
    if etapa_erc == "g1":
        recomendaciones.append("Control de presión arterial cada 6-12 meses")
        recomendaciones.append("Análisis de orina y creatinina anual")
    
    elif etapa_erc == "g2":
        recomendaciones.append("Control de presión arterial cada 3-6 meses")
        recomendaciones.append("Análisis de orina y creatinina cada 6 meses")
        recomendaciones.append("Evaluar factores de riesgo cardiovascular")
    
    elif etapa_erc == "g3a" or etapa_erc == "g3b":
        recomendaciones.append("Control de presión arterial cada 3 meses")
        recomendaciones.append("Análisis de orina y creatinina cada 3-4 meses")
        recomendaciones.append("Evaluar niveles de calcio, fósforo y PTH")
        recomendaciones.append("Consulta con nefrología cada 6-12 meses")
    
    elif etapa_erc == "g4":
        recomendaciones.append("Control de presión arterial mensual")
        recomendaciones.append("Análisis de orina y creatinina cada 1-3 meses")
        recomendaciones.append("Monitoreo de electrolitos y equilibrio ácido-base")
        recomendaciones.append("Consulta con nefrología cada 3 meses")
        recomendaciones.append("Preparación para terapia de reemplazo renal")
    
    elif etapa_erc == "g5":
        recomendaciones.append("Control de presión arterial semanal o bisemanal")
        recomendaciones.append("Análisis de orina y creatinina mensual")
        recomendaciones.append("Consulta con nefrología mensual")
        recomendaciones.append("Iniciar terapia de reemplazo renal o manejo conservador")
    
    # Recomendaciones basadas en valores de laboratorio específicos
    if lab_values.get('potasio', {}).get('value', 0) > 5.5:
        recomendaciones.append("Restricción de alimentos altos en potasio")
    
    if lab_values.get('fosforo', {}).get('value', 0) > 4.5:
        recomendaciones.append("Restricción de alimentos altos en fósforo")
    
    return recomendaciones

def identificar_valores_criticos(lab_values):
    """
    Identifica valores críticos en los resultados de laboratorio
    
    Args:
        lab_values (dict): Valores de laboratorio
        
    Returns:
        list: Lista de valores críticos identificados
    """
    valores_criticos = []
    
    # Definir umbrales críticos
    umbrales = {
        'potasio': {'min': 3.0, 'max': 6.0, 'unidad': 'mEq/L'},
        'sodio': {'min': 130, 'max': 150, 'unidad': 'mEq/L'},
        'creatinina': {'min': None, 'max': 4.0, 'unidad': 'mg/dL'},
        'glucosa': {'min': 70, 'max': 300, 'unidad': 'mg/dL'},
        'calcio': {'min': 7.5, 'max': 11.0, 'unidad': 'mg/dL'}
    }
    
    # Evaluar cada valor de laboratorio
    for param, limits in umbrales.items():
        if param in lab_values:
            valor = float(lab_values[param].get('value', 0))
            
            if limits['min'] is not None and valor < limits['min']:
                valores_criticos.append(f"{param.capitalize()} bajo: {valor} {limits['unidad']}")
            
            if limits['max'] is not None and valor > limits['max']:
                valores_criticos.append(f"{param.capitalize()} alto: {valor} {limits['unidad']}")
    
    return valores_criticos
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
