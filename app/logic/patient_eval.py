"""
Módulo para la evaluación de pacientes y cálculos clínicos relacionados con la ERC.

Este módulo implementa las fórmulas y criterios principales para la evaluación de la
Enfermedad Renal Crónica (ERC) según las guías KDIGO 2012, incluyendo:

- Cálculo de TFG usando fórmulas CKD-EPI y Cockcroft-Gault
- Clasificación de estadios de ERC
- Evaluación de riesgo cardiovascular
- Generación de informes clínicos

Ejemplo de uso:
    >>> from app.logic.patient_eval import calcular_tfg, determinar_etapa_erc
    >>> tfg = calcular_tfg(creatinina=1.2, edad=50, sexo='M', peso=70)
    >>> etapa = determinar_etapa_erc(tfg)
    >>> print(f"TFG: {tfg}, Etapa ERC: {etapa}")

Referencias:
    - KDIGO 2012 Clinical Practice Guideline
    - Cockcroft-Gault Formula (1976)
    - CKD-EPI Equation (2009)

Autores:
    Brandon Palencia
    Versión: 1.0.0
"""
import math
import logging
from datetime import datetime, timedelta
import pytz
from datetime import datetime
from typing import Dict, List, Optional, Union, Callable, Tuple, Any, TypedDict

# Zona horaria de Bogotá
BOGOTA_TZ = pytz.timezone('America/Bogota')
from functools import wraps, lru_cache
from threading import Lock

# Configuración del logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ParametroInvalidoError(ValueError):
    """Error personalizado para parámetros inválidos en cálculos clínicos."""
    pass

def log_error(func):
    """
    Decorador para logging de errores en funciones críticas.
    
    Args:
        func: Función a decorar
    Returns:
        wrapper: Función decorada con logging de errores
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Error en {func.__name__}: {str(e)}"
            )
            raise
    return wrapper

# Constantes para cálculos
FACTOR_SEXO_FEMENINO = 0.85
FACTOR_SEXO_MASCULINO = 1.0
FACTOR_BASE_CG = 1.0738  # Factor de calibración para Cockcroft-Gault

# Cache y optimización
_cache_lock = Lock()
_CACHE_SIZE = 1024  # Tamaño máximo del caché

def thread_safe_cache(func: Callable) -> Callable:
    """
    Decorador que combina @lru_cache con thread-safety.
    
    Args:
        func: Función a decorar
    Returns:
        Callable: Función decorada con caché thread-safe
    """
    cached_func = lru_cache(maxsize=_CACHE_SIZE)(func)
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        with _cache_lock:
            return cached_func(*args, **kwargs)
    return wrapper

def validar_parametros_numericos(**kwargs) -> Tuple[bool, str]:
    """
    Valida que los parámetros numéricos sean válidos y positivos.
    
    Args:
        **kwargs: Diccionario de parámetros a validar
        
    Returns:
        Tuple[bool, str]: (es_valido, mensaje_error)
        
    Raises:
        ParametroInvalidoError: Si algún parámetro no es válido
    """
    try:
        for nombre, valor in kwargs.items():
            try:
                valor_float = float(valor)
                if valor_float <= 0:
                    mensaje = f"El parámetro {nombre} debe ser mayor que 0"
                    logger.warning(f"Validación fallida: {mensaje}")
                    return False, mensaje
            except (ValueError, TypeError):
                mensaje = f"El parámetro {nombre} no es un número válido"
                logger.error(f"Error de tipo: {mensaje}")
                return False, mensaje
        return True, ""
    except Exception as e:
        logger.error(f"Error inesperado en validación: {str(e)}")
        raise ParametroInvalidoError(f"Error en la validación: {str(e)}")

def normalizar_sexo(sexo: str) -> Optional[str]:
    """
    Normaliza el parámetro sexo a formato estándar.
    
    Args:
        sexo: String que representa el sexo ('m'/'f', 'M'/'F', etc)
        
    Returns:
        str: 'm' o 'f' normalizado, o None si es inválido
    """
    if not isinstance(sexo, str):
        return None
    sexo_norm = sexo.lower().strip()
    return sexo_norm if sexo_norm in ['m', 'f'] else None

def calcular_tfg_ckd_epi(creatinina, edad, sexo, raza="no_negro", peso=70):
    """
    Calcula la TFG estimada (eGFR) usando CKD-EPI 2009 (ml/min/1.73m²).

    Args:
        creatinina (float): Creatinina sérica en mg/dL
        edad (int): Edad en años
        sexo (str): 'm'/'f'
        raza (str): 'negro' aplica factor 1.159; otros 1.0
        peso (float): Ignorado (compatibilidad)

    Returns:
        float: eGFR redondeada a 2 decimales
    """
    try:
        creatinina = float(creatinina)
    except Exception:
        # Si no convertible, usar valor de seguridad
        creatinina = 1.0
    if creatinina <= 0:
        creatinina = 1.0
    if edad <= 0:
        return 0.0

    sexo_lower = str(sexo).lower()
    if sexo_lower == "f":
        k = 0.7
        a = -0.329
        sex_coeff = 1.018
    else:
        k = 0.9
        a = -0.411
        sex_coeff = 1.0

    scr_k = creatinina / k
    import math
    egfr = 141.0 * (min(scr_k, 1) ** a) * (max(scr_k, 1) ** -1.209) * (0.993 ** edad) * sex_coeff
    race_lower = str(raza or "").lower()
    if race_lower in {"negro", "black", "afro", "afrodescendiente"}:
        egfr *= 1.159
    return round(egfr, 2)

@log_error
@thread_safe_cache
def calcular_tfg(creatinina: float, edad: float, sexo: str, raza: str = "no_negro", peso: float = 70) -> float:
    """
    Calcula la TFG usando Cockcroft-Gault (ml/min).
    
    Fórmula:
    CG = [(140 - edad) × peso × factor_sexo × factor_base] / (72 × creatinina)
    donde:
    - factor_sexo = 0.85 para mujeres, 1.0 para hombres
    - factor_base = 1.0738 (factor de calibración)
    - peso en kg
    - edad en años
    - creatinina en mg/dL
    
    Raises:
        ParametroInvalidoError: Si algún parámetro no es válido
        ValueError: Si los cálculos producen resultados inválidos

    Args:
        creatinina (float): Creatinina sérica en mg/dL
        edad (int): Edad en años
        sexo (str): 'm'/'f' ('M'/'F')
        raza (str): Ignorado (compatibilidad)
        peso (float): Peso en kg, por defecto 70

    Returns:
        float: TFG redondeada a 2 decimales
    """
    try:
        creatinina = float(creatinina)
        edad = float(edad)
        peso = float(peso)
    except (ValueError, TypeError):
        raise ValueError("Valores numéricos inválidos")

    if creatinina <= 0:
        raise ValueError("La creatinina debe ser mayor que 0")
    if edad < 18:
        raise ValueError("La edad mínima es 18 años")
    if peso <= 0:
        raise ValueError("El peso debe ser mayor que 0")

    # Validación y normalización de parámetros
    sexo_norm = normalizar_sexo(sexo)
    if sexo_norm is None:
        raise ValueError("Sexo debe ser 'M' o 'F'")

    # Factor de corrección por sexo según literatura médica
    factor_sexo = FACTOR_SEXO_FEMENINO if sexo_norm == 'f' else FACTOR_SEXO_MASCULINO
    
    # Fórmula de Cockcroft-Gault con ajustes de precisión
    tfg = ((140 - edad) * peso * factor_sexo * FACTOR_BASE_CG) / (72 * creatinina)
    
    # Redondeo a 2 decimales para estandarización
    return round(tfg, 2)

@log_error
@thread_safe_cache
def determinar_etapa_erc(tfg: float) -> Optional[Union[int, str]]:
    """
    Determina el estadio G de la Enfermedad Renal Crónica según KDIGO 2012.
    
    La clasificación se basa en los siguientes rangos:
    - G1: ≥90 ml/min/1.73m² (Función renal normal o alta)
    - G2: 60-89 ml/min/1.73m² (Reducción leve)
    - G3a: 45-59 ml/min/1.73m² (Reducción leve a moderada)
    - G3b: 30-44 ml/min/1.73m² (Reducción moderada a severa)
    - G4: 15-29 ml/min/1.73m² (Reducción severa)
    - G5: <15 ml/min/1.73m² (Fallo renal)
    
    Args:
        tfg: Tasa de Filtración Glomerular en ml/min/1.73m²
        
    Returns:
        Optional[Union[int,str]]: Estadio de ERC (1,2,"3a","3b",4,5)
        None si el valor es inválido
        
    Raises:
        ParametroInvalidoError: Si el TFG no es un número válido
    """
    try:
        tfg = float(tfg)
    except (ValueError, TypeError):
        raise ValueError("TFG debe ser un número")
        
    if tfg <= 0:
        raise ValueError("TFG debe ser mayor que 0")
        
    if tfg >= 90: return 1    # G1: Función renal normal o alta
    if tfg >= 60: return 2    # G2: Reducción leve
    if tfg >= 45: return "3a" # G3a: Reducción leve a moderada
    if tfg >= 30: return "3b" # G3b: Reducción moderada a severa
    if tfg >= 15: return 4    # G4: Reducción severa
    return 5                  # G5: Fallo renal

@log_error
@thread_safe_cache
def clasificar_riesgo_cv(paciente: Dict[str, Any], tfg: float) -> str:
    """
    Clasifica el riesgo cardiovascular del paciente según criterios KDIGO.
    
    La clasificación se basa en:
    1. Nivel de TFG
    2. Presencia de diabetes (DM2)
    3. Lesión de órgano blanco
    4. Factores de riesgo tradicionales
    
    Args:
        paciente: Diccionario con datos del paciente incluyendo:
                 - dm2: bool
                 - lesion_organo_blanco: bool
                 - hta: bool
                 - dislipidemia: bool
                 - tabaquismo: bool
        tfg: Tasa de filtración glomerular actual
        
    Returns:
        str: Nivel de riesgo ('bajo', 'moderado', 'alto', 'muy_alto')
        
    Raises:
        ParametroInvalidoError: Si faltan datos críticos del paciente
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

def obtener_metas_terapeuticas(paciente: Dict[str, Any], riesgo_cv: str) -> Dict[str, Any]:
    """
    Define metas terapéuticas según nivel de riesgo y condiciones del paciente.
    
    Args:
        paciente: Diccionario con datos del paciente
        riesgo_cv: Nivel de riesgo cardiovascular
    
    Returns:
        Dict con metas terapéuticas específicas
    """
    metas = {}
    
    # Meta de presión arterial
    if paciente.get("dm2", False) or paciente.get("ecv", False):
        metas["presion_arterial"] = {
            "sistolica": {"meta": 130, "unidad": "mmHg"},
            "diastolica": {"meta": 80, "unidad": "mmHg"}
        }
    else:
        metas["presion_arterial"] = {
            "sistolica": {"meta": 140, "unidad": "mmHg"},
            "diastolica": {"meta": 90, "unidad": "mmHg"}
        }
    
    # Meta de LDL según riesgo
    if riesgo_cv == "muy_alto":
        metas["ldl"] = {"meta": 55, "unidad": "mg/dL"}
    elif riesgo_cv == "alto":
        metas["ldl"] = {"meta": 70, "unidad": "mg/dL"}
    else:
        metas["ldl"] = {"meta": 100, "unidad": "mg/dL"}
    
    # Meta de HbA1c para diabéticos
    if paciente.get("dm2", False):
        metas["hba1c"] = {
            "meta": 7.0 if paciente.get("edad", 0) < 65 else 8.0,
            "unidad": "%"
        }
    
    return metas

def generar_recomendaciones(paciente: Dict[str, Any], riesgo_cv: str, metas: Dict[str, Any]) -> List[str]:
    """
    Genera recomendaciones personalizadas según el perfil del paciente.
    
    Args:
        paciente: Diccionario con datos del paciente
        riesgo_cv: Nivel de riesgo cardiovascular
        metas: Metas terapéuticas definidas
    
    Returns:
        Lista de recomendaciones
    """
    recomendaciones = []
    
    # Recomendaciones generales
    recomendaciones.append("Mantener una dieta saludable baja en sodio")
    recomendaciones.append("Realizar actividad física regular (150 min/semana)")
    
    # Recomendaciones específicas
    if paciente.get("tabaquismo", False):
        recomendaciones.append("Cesar el consumo de tabaco - referir a programa de cesación")
    
    if paciente.get("imc", 0) >= 25:
        recomendaciones.append(f"Control de peso - IMC actual: {paciente.get('imc'):.1f}")
    
    # Recomendaciones según riesgo CV
    if riesgo_cv in ["muy_alto", "alto"]:
        recomendaciones.append("Control médico cada 3 meses")
        recomendaciones.append(f"Mantener LDL < {metas['ldl']['meta']} mg/dL")
        recomendaciones.append("Considerar terapia hipolipemiante intensiva")
    
    if paciente.get("dm2", False):
        recomendaciones.append(
            f"Control estricto de HbA1c - Meta < {metas['hba1c']['meta']}%"
        )
        recomendaciones.append("Automonitoreo regular de glucemia")
    
    # Recomendaciones para ERC
    if paciente.get("etapa_erc"):
        recomendaciones.append("Evitar medicamentos nefrotóxicos")
        recomendaciones.append("Ajustar dosis de medicamentos según TFG")
    
    return recomendaciones

@log_error
def generar_informe_base(paciente: Dict[str, Any], laboratorios: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera un objeto base con toda la información necesaria para el informe clínico.
    
    Esta función:
    1. Procesa y valida los datos del paciente
    2. Calcula la TFG actual
    3. Determina la etapa de ERC
    4. Evalúa el riesgo cardiovascular
    5. Genera recomendaciones básicas
    
    Args:
        paciente: Diccionario con datos del paciente (debe incluir edad, peso, sexo)
        laboratorios: Diccionario con resultados de laboratorio (debe incluir creatinina)
        
    Returns:
        Dict[str, Any]: Objeto con la información procesada incluyendo:
            - tfg_actual: float
            - etapa_erc: Union[int, str]
            - riesgo_cv: str
            - recomendaciones: List[str]
            
    Raises:
        ParametroInvalidoError: Si faltan datos requeridos o son inválidos
    """
    # Copia de paciente para cálculos
    paciente_calculo = paciente.copy()
    
    # Procesar y validar datos
    try:
        # Extraer valores de laboratorios
        for lab_key, lab_data in laboratorios.items():
            if isinstance(lab_data, dict) and 'valor' in lab_data:
                paciente_calculo[lab_key] = lab_data['valor']
        
        # Calcular TFG
        tfg = calcular_tfg(
            creatinina=paciente_calculo.get("creatinina", 1.0),
            edad=paciente_calculo.get("edad", 0),
            sexo=paciente_calculo.get("sexo", "M"),
            peso=paciente_calculo.get("peso", 70)
        )
        
        # Determinar etapa ERC
        etapa_erc = determinar_etapa_erc(tfg)
        
        # Evaluar riesgo cardiovascular
        riesgo_cv = clasificar_riesgo_cv(paciente_calculo, tfg)
        
        # Generar metas terapéuticas
        metas = obtener_metas_terapeuticas(paciente_calculo, riesgo_cv)
        
        # Generar recomendaciones
        recomendaciones = generar_recomendaciones(paciente_calculo, riesgo_cv, metas)
        
        # Construir el informe
        return {
            "fecha_evaluacion": datetime.now(BOGOTA_TZ).strftime("%Y-%m-%d %H:%M:%S"),
            "datos_paciente": paciente,
            "resultados": {
                "tfg": round(tfg, 1),
                "etapa_erc": etapa_erc,
                "riesgo_cv": riesgo_cv,
                "metas_terapeuticas": metas,
                "recomendaciones": recomendaciones
            }
        }
        
    except Exception as e:
        logger.error(f"Error generando informe base: {str(e)}")
        raise ParametroInvalidoError(f"Error en el procesamiento: {str(e)}")

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
