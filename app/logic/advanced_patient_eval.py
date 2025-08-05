"""
Módulo principal de evaluación clínica para ERC Insight.
Implementa las reglas de negocio avanzadas para la evaluación de pacientes con ERC.
"""
import math
import json
import os
from datetime import datetime, timedelta

# Constantes y configuraciones
LAB_VALIDITY_CONFIG = {
    "g1": {
        "parcial_orina": 180,
        "creatinina": 180,
        "glicemia": 180,
        "colesterol_total": 180,
        "colesterol_ldl": 180,
        "trigliceridos": 180,
        "hba1c": 180,
        "microalbuminuria": 180,
        "hemoglobina": 365,
        "hematocrito": 365,
        "depuracion_creatinina_24h": 365
    },
    "g2": {
        "parcial_orina": 180,
        "creatinina": 180,
        "glicemia": 180,
        "colesterol_total": 180,
        "colesterol_ldl": 180,
        "trigliceridos": 180,
        "hba1c": 180,
        "microalbuminuria": 180,
        "hemoglobina": 365,
        "hematocrito": 365,
        "pth": 365,
        "depuracion_creatinina_24h": 180
    },
    "g3a": {
        "parcial_orina": 180,
        "creatinina": [90, 121],  # Rango mínimo-máximo de días
        "glicemia": 180,
        "colesterol_total": 180,
        "colesterol_ldl": 180,
        "trigliceridos": 180,
        "hba1c": 180,
        "microalbuminuria": 180,
        "hemoglobina": 365,
        "hematocrito": 365,
        "pth": 365,
        "depuracion_creatinina_24h": 180
    },
    "g3b": {
        "parcial_orina": 180,
        "creatinina": [90, 121],
        "glicemia": 180,
        "colesterol_total": 180,
        "colesterol_ldl": 180,
        "trigliceridos": 180,
        "hba1c": 180,
        "microalbuminuria": 180,
        "hemoglobina": 365,
        "hematocrito": 365,
        "pth": 365,
        "albumina": 365,
        "fosforo": 365,
        "depuracion_creatinina_24h": 180
    },
    "g4": {
        "parcial_orina": 120,
        "creatinina": [60, 93],
        "glicemia": 60,
        "colesterol_total": 120,
        "colesterol_ldl": 180,
        "trigliceridos": 120,
        "hba1c": 120,
        "microalbuminuria": 180,
        "hemoglobina": 180,
        "hematocrito": 180,
        "pth": 180,
        "albumina": 365,
        "fosforo": 365,
        "depuracion_creatinina_24h": 90
    },
    "g5": {
        "parcial_orina": 90,
        "creatinina": 30,
        "glicemia": 30,
        "colesterol_total": 90,
        "colesterol_ldl": 180,
        "trigliceridos": 90,
        "hba1c": 90,
        "microalbuminuria": 180,
        "hemoglobina": 90,
        "hematocrito": 90,
        "pth": 90,
        "albumina": 180,
        "fosforo": 180,
        "depuracion_creatinina_24h": 30
    }
}

# Matriz de puntuación para metas terapéuticas
PUNTAJE_METAS = {
    "glicemia": {
        "erc123_dm2": 4,
        "erc4_dm2": 5,
        "erc123_nodm2": 5,
        "erc4_nodm2": 10
    },
    "colesterol_ldl": {
        "erc123_dm2": 20,
        "erc4_dm2": 0,
        "erc123_nodm2": 25,
        "erc4_nodm2": 0
    },
    "hdl": {
        "erc123_dm2": 4,
        "erc4_dm2": 5,
        "erc123_nodm2": 5,
        "erc4_nodm2": 10
    },
    "trigliceridos": {
        "erc123_dm2": 4,
        "erc4_dm2": 5,
        "erc123_nodm2": 5,
        "erc4_nodm2": 10
    },
    "presion_arterial": {
        "erc123_dm2": 20,
        "erc4_dm2": 30,
        "erc123_nodm2": 25,
        "erc4_nodm2": 40
    },
    "rac": {
        "erc123_dm2": 20,
        "erc4_dm2": 15,
        "erc123_nodm2": 25,
        "erc4_nodm2": 10
    },
    "perimetro_abdominal": {
        "erc123_dm2": 4,
        "erc4_dm2": 5,
        "erc123_nodm2": 5,
        "erc4_nodm2": 10
    },
    "imc": {
        "erc123_dm2": 4,
        "erc4_dm2": 5,
        "erc123_nodm2": 5,
        "erc4_nodm2": 10
    },
    "hba1c": {
        "erc123_dm2": 20,
        "erc4_dm2": 30,
        "erc123_nodm2": 0,
        "erc4_nodm2": 0
    }
}

# Metas terapéuticas por perfil
METAS_TERAPEUTICAS = {
    "glicemia": {
        "default": 130
    },
    "colesterol_ldl": {
        "default": 100,
        "muy_alto_riesgo": 55,
        "alto_riesgo": 70
    },
    "hdl": {
        "hombre": 40,
        "mujer": 50
    },
    "trigliceridos": {
        "default": 150
    },
    "presion_arterial": {
        "default": "140/90",
        "erc_con_proteinuria": "130/80"
    },
    "rac": {
        "default": 30
    },
    "perimetro_abdominal": {
        "hombre": 94,
        "mujer": 90
    },
    "imc": {
        "default": 25
    },
    "hba1c": {
        "default": 7.0,
        "edad_mayor_75": 8.0,
        "ecv_establecida": 8.0
    }
}

def calcular_tfg_cockcroft_gault(creatinina, edad, sexo, peso):
    """
    Calcula la Tasa de Filtración Glomerular utilizando la fórmula de Cockcroft-Gault.
    
    Args:
        creatinina (float): Nivel de creatinina en mg/dL
        edad (int): Edad del paciente en años
        sexo (str): 'M' para masculino, 'F' para femenino
        peso (float): Peso del paciente en kg
        
    Returns:
        float: TFG calculada
    """
    # Validar parámetros de entrada
    if creatinina <= 0:
        creatinina = 1.0
    
    if edad <= 0 or peso <= 0:
        return 0.0

    factor_sexo = 0.85 if sexo == 'F' else 1.0
    tfg = ((140 - edad) * peso * factor_sexo) / (72 * creatinina)
    return round(tfg, 2)

def determinar_etapa_erc(tfg):
    """
    Determina la etapa de ERC según la clasificación KDIGO.
    
    Args:
        tfg (float): Tasa de Filtración Glomerular en ml/min/1.73m²
        
    Returns:
        str: Etapa de ERC (1, 2, 3a, 3b, 4, 5)
    """
    if tfg >= 90:
        return 1
    elif tfg >= 60:
        return 2
    elif tfg >= 45:
        return "3a"
    elif tfg >= 30:
        return "3b"
    elif tfg >= 15:
        return 4
    else:
        return 5

def calcular_etapa_erc_para_config(tfg):
    """
    Determina la etapa de ERC para usar en la configuración de validez de laboratorios.
    
    Args:
        tfg (float): Tasa de Filtración Glomerular en ml/min/1.73m²
        
    Returns:
        str: Etapa de ERC en formato 'g1', 'g2', 'g3a', 'g3b', 'g4', 'g5'
    """
    etapa = determinar_etapa_erc(tfg)
    return f"g{etapa}"

def evaluar_fragilidad(respuestas_fried):
    """
    Evalúa la fragilidad del paciente según la escala de Fried.
    
    Args:
        respuestas_fried (dict): Diccionario con las respuestas al cuestionario de Fried
            Las claves deben ser: 'perdida_peso', 'agotamiento', 'actividad_fisica',
            'velocidad_marcha', 'fuerza_prension'
            
    Returns:
        bool: True si el paciente es frágil, False en caso contrario
    """
    if not respuestas_fried:
        return False
        
    criterios_positivos = sum(1 for valor in respuestas_fried.values() if valor)
    
    # 3 o más criterios positivos indican fragilidad
    return criterios_positivos >= 3

def calcular_riesgo_cardiovascular(paciente):
    """
    Calcula el riesgo cardiovascular según el protocolo completo especificado.
    
    Args:
        paciente (dict): Diccionario con datos del paciente
            
    Returns:
        dict: Diccionario con 'nivel' de riesgo y 'justificacion'
    """
    # Extraer datos relevantes
    tfg = paciente.get("tfg", 90)
    edad = paciente.get("edad", 0)
    sexo = paciente.get("sexo", "M")
    dm = paciente.get("dm2", False)
    ecv_establecida = paciente.get("ecv_establecida", False)
    dano_organo_blanco = paciente.get("dano_organo_blanco", False)
    factores_riesgo = paciente.get("factores_riesgo", [])
    duracion_dm = paciente.get("duracion_dm", 0)  # en años
    pa_sistolica = paciente.get("pa_sistolica", 120)
    pa_diastolica = paciente.get("pa_diastolica", 80)
    colesterol_ldl = paciente.get("colesterol_ldl", 0)
    
    # Conteo de factores de riesgo adicionales
    num_factores_riesgo = len(factores_riesgo)
    if edad >= 75:
        num_factores_riesgo += 2  # edad > 75 cuenta como 2 factores
    elif edad >= 65:
        num_factores_riesgo += 1
    
    # Paso 1: Identificar MUY ALTO RIESGO
    if (ecv_establecida or 
        tfg <= 30 or 
        (dm and dano_organo_blanco) or 
        (dm and num_factores_riesgo >= 3) or
        (dm and duracion_dm > 10)):
        
        justificacion = ""
        if ecv_establecida:
            justificacion = "enfermedad cardiovascular aterosclerótica establecida"
        elif tfg <= 30:
            justificacion = f"ERC con TFGe ≤ 30 ml/min (actual: {tfg} ml/min)"
        elif dm and dano_organo_blanco:
            justificacion = "Diabetes con daño de órgano blanco"
        elif dm and num_factores_riesgo >= 3:
            justificacion = "Diabetes con tres o más factores de riesgo adicionales"
        elif dm and duracion_dm > 10:
            justificacion = f"Diabetes con duración mayor a 10 años (actual: {duracion_dm} años)"
        
        return {
            "nivel": "muy alto",
            "justificacion": justificacion
        }
    
    # Paso 2: Identificar ALTO RIESGO
    if (30 < tfg <= 60 or 
        pa_sistolica >= 180 or pa_diastolica >= 110 or 
        colesterol_ldl > 190 or
        num_factores_riesgo >= 3):
        
        justificacion = ""
        if 30 < tfg <= 60:
            justificacion = f"ERC con TFGe entre 30-60 ml/min (actual: {tfg} ml/min)"
        elif pa_sistolica >= 180 or pa_diastolica >= 110:
            justificacion = f"Presión arterial marcadamente elevada: {pa_sistolica}/{pa_diastolica} mmHg"
        elif colesterol_ldl > 190:
            justificacion = f"cLDL marcadamente elevado: {colesterol_ldl} mg/dL"
        elif num_factores_riesgo >= 3:
            justificacion = "Presencia de 3 o más factores de riesgo adicionales"
        
        return {
            "nivel": "alto",
            "justificacion": justificacion
        }
    
    # Paso 3: Contar factores potenciadores
    potenciadores = paciente.get("factores_potenciadores", [])
    num_potenciadores = len(potenciadores)
    
    if num_potenciadores >= 3:
        return {
            "nivel": "alto",
            "justificacion": "Presencia de 3 o más factores potenciadores de riesgo"
        }
    elif num_potenciadores >= 1:
        return {
            "nivel": "moderado",
            "justificacion": "Presencia de 1-2 factores potenciadores de riesgo"
        }
    
    # Paso 4: ASCVD (No implementado, requeriría algoritmo específico ajustado para Colombia)
    # Por defecto, si no se clasifica en ninguna categoría anterior:
    return {
        "nivel": "moderado",
        "justificacion": "Evaluación general de factores de riesgo cardiovascular"
    }

def determinar_perfil_paciente(estadio_erc, tiene_dm2):
    """
    Determina el perfil del paciente para la matriz de puntuación.
    
    Args:
        estadio_erc (str o int): Estadio de ERC
        tiene_dm2 (bool): Si el paciente tiene diabetes tipo 2
        
    Returns:
        str: Clave para la matriz de puntuación
    """
    # Convertir estadio a string para comparación
    estadio_str = str(estadio_erc)
    
    # Determinar si está en estadios 1,2,3 o en estadio 4
    if estadio_str in ["1", "2", "3", "3a", "3b"]:
        grupo_erc = "erc123"
    else:
        grupo_erc = "erc4"
    
    # Determinar si tiene DM2
    sufijo_dm = "dm2" if tiene_dm2 else "nodm2"
    
    # Componer la clave
    return f"{grupo_erc}_{sufijo_dm}"

def evaluar_cumplimiento_metas(paciente, valores_lab, riesgo_cv):
    """
    Evalúa el cumplimiento de metas terapéuticas y asigna puntajes.
    
    Args:
        paciente (dict): Datos del paciente
        valores_lab (dict): Valores de laboratorio actuales
        riesgo_cv (dict): Clasificación de riesgo cardiovascular
        
    Returns:
        dict: Resultados de la evaluación con metas, cumplimiento y puntajes
    """
    # Determinar el perfil del paciente
    estadio_erc = determinar_etapa_erc(paciente.get("tfg", 90))
    tiene_dm2 = paciente.get("dm2", False)
    perfil = determinar_perfil_paciente(estadio_erc, tiene_dm2)
    
    # Inicializar resultados
    resultados = {
        "metas": [],
        "puntaje_total": 0,
        "puntaje_maximo": 0,
        "porcentaje_cumplimiento": 0
    }
    
    # Evaluar cada parámetro
    
    # 1. Glicemia
    if "glicemia" in valores_lab:
        meta_glicemia = METAS_TERAPEUTICAS["glicemia"]["default"]
        valor_actual = valores_lab["glicemia"]
        puntaje_maximo = PUNTAJE_METAS["glicemia"][perfil]
        cumple = valor_actual <= meta_glicemia
        puntaje_obtenido = puntaje_maximo if cumple else 0
        
        resultados["metas"].append({
            "parametro": "Glicemia",
            "estado": "Cumple" if cumple else "No cumple",
            "valor_actual": valor_actual,
            "meta_definida": meta_glicemia,
            "puntaje_obtenido": puntaje_obtenido,
            "puntaje_maximo": puntaje_maximo
        })
        
        resultados["puntaje_total"] += puntaje_obtenido
        resultados["puntaje_maximo"] += puntaje_maximo
    
    # 2. Colesterol LDL
    if "colesterol_ldl" in valores_lab:
        # Determinar meta según riesgo CV
        if riesgo_cv["nivel"] == "muy alto":
            meta_ldl = METAS_TERAPEUTICAS["colesterol_ldl"]["muy_alto_riesgo"]
        elif riesgo_cv["nivel"] == "alto":
            meta_ldl = METAS_TERAPEUTICAS["colesterol_ldl"]["alto_riesgo"]
        else:
            meta_ldl = METAS_TERAPEUTICAS["colesterol_ldl"]["default"]
        
        valor_actual = valores_lab["colesterol_ldl"]
        puntaje_maximo = PUNTAJE_METAS["colesterol_ldl"][perfil]
        cumple = valor_actual <= meta_ldl
        puntaje_obtenido = puntaje_maximo if cumple else 0
        
        resultados["metas"].append({
            "parametro": "Colesterol LDL",
            "estado": "Cumple" if cumple else "No cumple",
            "valor_actual": valor_actual,
            "meta_definida": meta_ldl,
            "puntaje_obtenido": puntaje_obtenido,
            "puntaje_maximo": puntaje_maximo
        })
        
        resultados["puntaje_total"] += puntaje_obtenido
        resultados["puntaje_maximo"] += puntaje_maximo
    
    # 3. HDL
    if "hdl" in valores_lab:
        # Meta según sexo
        if paciente.get("sexo", "M") == "F":
            meta_hdl = METAS_TERAPEUTICAS["hdl"]["mujer"]
        else:
            meta_hdl = METAS_TERAPEUTICAS["hdl"]["hombre"]
        
        valor_actual = valores_lab["hdl"]
        puntaje_maximo = PUNTAJE_METAS["hdl"][perfil]
        cumple = valor_actual >= meta_hdl
        puntaje_obtenido = puntaje_maximo if cumple else 0
        
        resultados["metas"].append({
            "parametro": "Colesterol HDL",
            "estado": "Cumple" if cumple else "No cumple",
            "valor_actual": valor_actual,
            "meta_definida": meta_hdl,
            "puntaje_obtenido": puntaje_obtenido,
            "puntaje_maximo": puntaje_maximo
        })
        
        resultados["puntaje_total"] += puntaje_obtenido
        resultados["puntaje_maximo"] += puntaje_maximo
    
    # 4. Triglicéridos
    if "trigliceridos" in valores_lab:
        meta_tg = METAS_TERAPEUTICAS["trigliceridos"]["default"]
        valor_actual = valores_lab["trigliceridos"]
        puntaje_maximo = PUNTAJE_METAS["trigliceridos"][perfil]
        cumple = valor_actual <= meta_tg
        puntaje_obtenido = puntaje_maximo if cumple else 0
        
        resultados["metas"].append({
            "parametro": "Triglicéridos",
            "estado": "Cumple" if cumple else "No cumple",
            "valor_actual": valor_actual,
            "meta_definida": meta_tg,
            "puntaje_obtenido": puntaje_obtenido,
            "puntaje_maximo": puntaje_maximo
        })
        
        resultados["puntaje_total"] += puntaje_obtenido
        resultados["puntaje_maximo"] += puntaje_maximo
    
    # 5. Presión Arterial
    if "pa_sistolica" in valores_lab and "pa_diastolica" in valores_lab:
        # Determinar meta según presencia de proteinuria
        if paciente.get("proteinuria", False):
            meta_pa = METAS_TERAPEUTICAS["presion_arterial"]["erc_con_proteinuria"]
        else:
            meta_pa = METAS_TERAPEUTICAS["presion_arterial"]["default"]
        
        meta_sistolica, meta_diastolica = map(int, meta_pa.split('/'))
        valor_sistolica = valores_lab["pa_sistolica"]
        valor_diastolica = valores_lab["pa_diastolica"]
        valor_actual = f"{valor_sistolica}/{valor_diastolica}"
        
        puntaje_maximo = PUNTAJE_METAS["presion_arterial"][perfil]
        cumple = valor_sistolica <= meta_sistolica and valor_diastolica <= meta_diastolica
        puntaje_obtenido = puntaje_maximo if cumple else 0
        
        resultados["metas"].append({
            "parametro": "Presión Arterial",
            "estado": "Cumple" if cumple else "No cumple",
            "valor_actual": valor_actual,
            "meta_definida": meta_pa,
            "puntaje_obtenido": puntaje_obtenido,
            "puntaje_maximo": puntaje_maximo
        })
        
        resultados["puntaje_total"] += puntaje_obtenido
        resultados["puntaje_maximo"] += puntaje_maximo
    
    # 6. RAC (Relación Albúmina/Creatinina)
    if "rac" in valores_lab:
        meta_rac = METAS_TERAPEUTICAS["rac"]["default"]
        valor_actual = valores_lab["rac"]
        puntaje_maximo = PUNTAJE_METAS["rac"][perfil]
        cumple = valor_actual <= meta_rac
        puntaje_obtenido = puntaje_maximo if cumple else 0
        
        resultados["metas"].append({
            "parametro": "Relación Albúmina/Creatinina",
            "estado": "Cumple" if cumple else "No cumple",
            "valor_actual": valor_actual,
            "meta_definida": meta_rac,
            "puntaje_obtenido": puntaje_obtenido,
            "puntaje_maximo": puntaje_maximo
        })
        
        resultados["puntaje_total"] += puntaje_obtenido
        resultados["puntaje_maximo"] += puntaje_maximo
    
    # 7. Perímetro Abdominal
    if "perimetro_abdominal" in valores_lab:
        if paciente.get("sexo", "M") == "F":
            meta_per_abd = METAS_TERAPEUTICAS["perimetro_abdominal"]["mujer"]
        else:
            meta_per_abd = METAS_TERAPEUTICAS["perimetro_abdominal"]["hombre"]
        
        valor_actual = valores_lab["perimetro_abdominal"]
        puntaje_maximo = PUNTAJE_METAS["perimetro_abdominal"][perfil]
        cumple = valor_actual <= meta_per_abd
        puntaje_obtenido = puntaje_maximo if cumple else 0
        
        resultados["metas"].append({
            "parametro": "Perímetro Abdominal",
            "estado": "Cumple" if cumple else "No cumple",
            "valor_actual": valor_actual,
            "meta_definida": meta_per_abd,
            "puntaje_obtenido": puntaje_obtenido,
            "puntaje_maximo": puntaje_maximo
        })
        
        resultados["puntaje_total"] += puntaje_obtenido
        resultados["puntaje_maximo"] += puntaje_maximo
    
    # 8. IMC
    if "imc" in valores_lab:
        meta_imc = METAS_TERAPEUTICAS["imc"]["default"]
        valor_actual = valores_lab["imc"]
        puntaje_maximo = PUNTAJE_METAS["imc"][perfil]
        cumple = valor_actual <= meta_imc
        puntaje_obtenido = puntaje_maximo if cumple else 0
        
        resultados["metas"].append({
            "parametro": "IMC",
            "estado": "Cumple" if cumple else "No cumple",
            "valor_actual": valor_actual,
            "meta_definida": meta_imc,
            "puntaje_obtenido": puntaje_obtenido,
            "puntaje_maximo": puntaje_maximo
        })
        
        resultados["puntaje_total"] += puntaje_obtenido
        resultados["puntaje_maximo"] += puntaje_maximo
    
    # 9. HbA1c (solo para diabéticos)
    if "hba1c" in valores_lab and paciente.get("dm2", False):
        # Determinar meta según edad y presencia de ECV
        if paciente.get("edad", 0) > 75:
            meta_hba1c = METAS_TERAPEUTICAS["hba1c"]["edad_mayor_75"]
        elif paciente.get("ecv_establecida", False):
            meta_hba1c = METAS_TERAPEUTICAS["hba1c"]["ecv_establecida"]
        else:
            meta_hba1c = METAS_TERAPEUTICAS["hba1c"]["default"]
        
        valor_actual = valores_lab["hba1c"]
        puntaje_maximo = PUNTAJE_METAS["hba1c"][perfil]
        cumple = valor_actual <= meta_hba1c
        puntaje_obtenido = puntaje_maximo if cumple else 0
        
        resultados["metas"].append({
            "parametro": "HbA1c",
            "estado": "Cumple" if cumple else "No cumple",
            "valor_actual": valor_actual,
            "meta_definida": meta_hba1c,
            "puntaje_obtenido": puntaje_obtenido,
            "puntaje_maximo": puntaje_maximo
        })
        
        resultados["puntaje_total"] += puntaje_obtenido
        resultados["puntaje_maximo"] += puntaje_maximo
    
    # Calcular porcentaje de cumplimiento
    if resultados["puntaje_maximo"] > 0:
        resultados["porcentaje_cumplimiento"] = round((resultados["puntaje_total"] / resultados["puntaje_maximo"]) * 100, 1)
    
    # Determinar estado de cumplimiento
    if resultados["porcentaje_cumplimiento"] >= 80:
        resultados["estado_cumplimiento"] = "Excelente"
    elif resultados["porcentaje_cumplimiento"] >= 60:
        resultados["estado_cumplimiento"] = "Bueno"
    elif resultados["porcentaje_cumplimiento"] >= 40:
        resultados["estado_cumplimiento"] = "Regular"
    else:
        resultados["estado_cumplimiento"] = "Deficiente"
    
    return resultados

def calcular_fechas_laboratorios(fecha_base, etapa_erc, valores_lab, tiene_dm2, indicaciones_especiales=None):
    """
    Calcula las fechas para los próximos laboratorios basados en la etapa de ERC.
    
    Args:
        fecha_base (str): Fecha base para el cálculo en formato 'YYYY-MM-DD'
        etapa_erc (str): Etapa de ERC (1, 2, 3a, 3b, 4, 5)
        valores_lab (dict): Valores actuales de laboratorio
        tiene_dm2 (bool): Si el paciente tiene diabetes tipo 2
        indicaciones_especiales (dict): Indicaciones especiales para exámenes específicos
        
    Returns:
        list: Lista de diccionarios con fecha_programada y examenes
    """
    # Convertir etapa a string para acceder a la configuración
    etapa_str = f"g{etapa_erc}"
    
    # Validar que la etapa exista en la configuración
    if etapa_str not in LAB_VALIDITY_CONFIG:
        etapa_str = "g1"  # Usar g1 como fallback
    
    # Inicializar indicaciones si es None
    if indicaciones_especiales is None:
        indicaciones_especiales = {}
    
    # Convertir fecha base a objeto datetime
    try:
        fecha_obj = datetime.strptime(fecha_base, "%Y-%m-%d")
    except ValueError:
        # Si hay error en el formato, usar la fecha actual
        fecha_obj = datetime.now()
    
    # Agrupar laboratorios por fecha de próxima toma
    lab_por_fecha = {}
    
    # Recorrer todos los exámenes configurados para la etapa
    for lab_key, dias_validez in LAB_VALIDITY_CONFIG[etapa_str].items():
        # Saltar PTH en estadios iniciales si no hay indicación específica
        if lab_key == "pth" and etapa_str in ["g1", "g2"] and not indicaciones_especiales.get("indicacion_pth", False):
            continue
        
        # Saltar HbA1c si no es diabético
        if lab_key == "hba1c" and not tiene_dm2:
            continue
        
        # Determinar días de validez
        if isinstance(dias_validez, list):
            # Si es un rango, usar el valor mínimo por defecto
            dias = dias_validez[0]
        else:
            dias = dias_validez
        
        # Calcular fecha próxima
        fecha_proxima = fecha_obj + timedelta(days=dias)
        fecha_proxima_str = fecha_proxima.strftime("%d/%m/%Y")
        
        # Agrupar por fecha
        if fecha_proxima_str not in lab_por_fecha:
            lab_por_fecha[fecha_proxima_str] = []
        
        # Normalizar nombre del examen para presentación
        nombre_lab = lab_key.replace("_", " ").title()
        lab_por_fecha[fecha_proxima_str].append(nombre_lab)
    
    # Convertir a lista de resultados
    resultado = []
    for fecha, examenes in lab_por_fecha.items():
        resultado.append({
            "fecha_programada": fecha,
            "examenes": examenes
        })
    
    # Ordenar por fecha
    resultado.sort(key=lambda x: datetime.strptime(x["fecha_programada"], "%d/%m/%Y"))
    
    return resultado

def calcular_proxima_cita_medica(fecha_base, laboratorios_programados):
    """
    Calcula la fecha de la próxima cita médica.
    
    Args:
        fecha_base (str): Fecha base para el cálculo en formato 'YYYY-MM-DD'
        laboratorios_programados (list): Lista de laboratorios programados
        
    Returns:
        dict: Información de la próxima cita
    """
    # Convertir fecha base a objeto datetime
    try:
        fecha_obj = datetime.strptime(fecha_base, "%Y-%m-%d")
    except ValueError:
        # Si hay error en el formato, usar la fecha actual
        fecha_obj = datetime.now()
    
    # Por requisito, la próxima cita es exactamente 7 días después de la fecha base
    fecha_cita = fecha_obj + timedelta(days=7)
    fecha_cita_str = fecha_cita.strftime("%d/%m/%Y")
    
    # Determinar justificación basada en los laboratorios programados
    if laboratorios_programados:
        justificacion = "Seguimiento posterior a toma de exámenes de control"
    else:
        justificacion = "Control médico programado"
    
    return {
        "proxima_cita_medica": fecha_cita_str,
        "justificacion_seguimiento": justificacion
    }

def generar_payload_gemini(paciente, laboratorios):
    """
    Genera el payload JSON completo para enviar a la API de Gemini.
    
    Args:
        paciente (dict): Datos del paciente
        laboratorios (dict): Resultados de laboratorio
        
    Returns:
        dict: Payload JSON estructurado según el formato requerido
    """
    # Extraer datos básicos
    edad = paciente.get("edad", 0)
    sexo = paciente.get("sexo", "M")
    peso = paciente.get("peso", 0)
    creatinina = laboratorios.get("creatinina", {}).get("valor", 1.0)
    raza = paciente.get("raza", "no_negro")
    fecha_base = laboratorios.get("fecha_ingreso", datetime.now().strftime("%Y-%m-%d"))
    
    # Respuestas del cuestionario de fragilidad
    respuestas_fried = paciente.get("escala_fried", {})
    
    # Extraer valores de laboratorio para evaluación
    valores_lab = {}
    for key, lab_data in laboratorios.items():
        if isinstance(lab_data, dict) and "valor" in lab_data:
            valores_lab[key] = lab_data["valor"]
    
    # Calcular TFG
    tfg = calcular_tfg_cockcroft_gault(creatinina, edad, sexo, peso)
    
    # Determinar etapa ERC
    etapa_erc = determinar_etapa_erc(tfg)
    
    # Añadir datos calculados al paciente para evaluaciones posteriores
    paciente_evaluacion = paciente.copy()
    paciente_evaluacion["tfg"] = tfg
    
    # Calcular riesgo cardiovascular
    riesgo_cv = calcular_riesgo_cardiovascular(paciente_evaluacion)
    
    # Evaluar cumplimiento de metas terapéuticas
    cumplimiento = evaluar_cumplimiento_metas(paciente_evaluacion, valores_lab, riesgo_cv)
    
    # Determinar fragilidad
    es_fragil = evaluar_fragilidad(respuestas_fried)
    
    # Calcular fechas de laboratorios
    tiene_dm2 = paciente.get("dm2", False)
    indicaciones_especiales = {
        "indicacion_pth": paciente.get("indicacion_pth", False)
    }
    laboratorios_programados = calcular_fechas_laboratorios(
        fecha_base, 
        etapa_erc, 
        valores_lab, 
        tiene_dm2,
        indicaciones_especiales
    )
    
    # Calcular próxima cita médica
    cita_info = calcular_proxima_cita_medica(fecha_base, laboratorios_programados)
    
    # Construir payload final
    payload = {
        "evaluacion_diagnosticos": {
            "diagnosticos": paciente.get("diagnosticos", []),
            "riesgo_cardiovascular": riesgo_cv["nivel"],
            "justificacion_riesgo": riesgo_cv["justificacion"],
            "tfg_valor": tfg,
            "erc_estadio": f"Estadio {etapa_erc}"
        },
        "cumplimiento_metas": {
            "metas": cumplimiento["metas"],
            "puntaje_total_adherencia": cumplimiento["porcentaje_cumplimiento"],
            "estado_cumplimiento": cumplimiento["estado_cumplimiento"]
        },
        "plan_farmacologico": {
            "medicamentos": paciente.get("medicamentos", [])
        },
        "plan_seguimiento": {
            "laboratorios_programados": laboratorios_programados,
            "proxima_cita_medica": cita_info["proxima_cita_medica"],
            "justificacion_seguimiento": cita_info["justificacion_seguimiento"]
        },
        "datos_adicionales": {
            "es_fragil": es_fragil,
            "edad": edad,
            "sexo": sexo,
            "peso": peso,
            "talla": paciente.get("talla", 0),
            "imc": paciente.get("imc", 0),
            "comorbilidades": paciente.get("comorbilidades", [])
        }
    }
    
    return payload

def clasificar_riesgo_cv(data, tfg):
    """
    Función de compatibilidad para clasificar el riesgo cardiovascular.
    Esta función mantiene la compatibilidad con el código existente que
    espera una función con esta firma.
    
    Args:
        data (dict): Datos del paciente
        tfg (float): Tasa de Filtración Glomerular
        
    Returns:
        str: Nivel de riesgo ('bajo', 'moderado', 'alto', 'muy alto')
    """
    # Construir objeto de paciente con los campos necesarios
    paciente = {
        "tfg": tfg,
        "edad": data.get("edad", 0),
        "sexo": data.get("sexo", "M"),
        "dm2": data.get("dm2", False),
        "ecv_establecida": data.get("ecv_establecida", False),
        "dano_organo_blanco": data.get("dano_organo_blanco", False),
        "factores_riesgo": data.get("factores_riesgo", []),
        "duracion_dm": data.get("duracion_dm", 0),
        "pa_sistolica": data.get("pa_sistolica", 120),
        "pa_diastolica": data.get("pa_diastolica", 80),
        "colesterol_ldl": data.get("colesterol_ldl", 0),
        "factores_potenciadores": data.get("factores_potenciadores", [])
    }
    
    # Obtener clasificación usando la función nueva
    resultado = calcular_riesgo_cardiovascular(paciente)
    
    # Mapear niveles a la terminología anterior
    nivel = resultado["nivel"]
    if nivel == "muy alto":
        return "muy alto"
    elif nivel == "alto":
        return "alto"
    elif nivel == "moderado":
        return "moderado"
    else:
        return "bajo"
