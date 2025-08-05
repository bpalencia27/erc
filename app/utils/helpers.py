"""
Funciones de utilidad para la aplicación
"""
import re
from datetime import datetime

def parse_dose_to_number(dose_str):
    """
    Extrae el valor numérico de una cadena de dosis (ej. '500mg' -> 500).
    """
    if not isinstance(dose_str, str):
        return 0.0
    match = re.search(r"(\d+\.?\d*)", dose_str)
    return float(match.group(1)) if match else 0.0

def calcular_pa_promedio(pa_values):
    """
    Calcula el promedio de una lista de lecturas de presión arterial.
    
    Args:
        pa_values (list): Lista de lecturas de PA en formato "120/80"
        
    Returns:
        str: Promedio de PA en formato "120/80"
    """
    if not pa_values: return "N/A"
    
    sistolicas, diastolicas = [], []
    for pa in pa_values:
        try:
            s, d = map(int, str(pa).split('/'))
            sistolicas.append(s)
            diastolicas.append(d)
        except (ValueError, IndexError):
            continue
    
    if not sistolicas: return "N/A"
    return f"{round(sum(sistolicas)/len(sistolicas))}/{round(sum(diastolicas)/len(diastolicas))}"

def calcular_imc(peso, talla):
    """
    Calcula el Índice de Masa Corporal.
    """
    if peso <= 0 or talla <= 0:
        return 0.0
    
    # Convertir talla de cm a metros
    talla_m = talla / 100
    
    # Calcular IMC
    imc = peso / (talla_m * talla_m)
    
    return round(imc, 1)

def formatear_fecha(fecha_str, formato_salida="%d/%m/%Y"):
    """
    Formatea una fecha en el formato especificado.
    """
    try:
        # Intentar parsear la fecha
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d")
        # Formatear según el formato de salida
        return fecha_obj.strftime(formato_salida)
    except (ValueError, TypeError):
        # Si hay error, devolver la fecha original
        return fecha_str
