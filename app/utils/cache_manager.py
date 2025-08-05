"""
Gestor de caché para optimizar rendimiento
"""
import json
import hashlib
from datetime import datetime, timedelta
from flask_caching import Cache
from typing import Any, Dict, Optional

cache = Cache()

def generate_cache_key(data: Dict[str, Any]) -> str:
    """Genera una clave de caché única basada en los datos"""
    # Serializar datos de forma determinística
    sorted_data = json.dumps(data, sort_keys=True)
    # Generar hash
    return hashlib.md5(sorted_data.encode()).hexdigest()

def cache_result(key: str, data: Any, ttl: int = 3600) -> None:
    """
    Cachea un resultado
    
    Args:
        key: Clave de caché
        data: Datos a cachear
        ttl: Tiempo de vida en segundos (default: 1 hora)
    """
    cache.set(key, data, timeout=ttl)

def get_cached_result(key: str) -> Optional[Any]:
    """
    Obtiene un resultado cacheado
    
    Args:
        key: Clave de caché
        
    Returns:
        Datos cacheados o None si no existe/expiró
    """
    return cache.get(key)

def invalidate_cache(pattern: str) -> None:
    """
    Invalida entradas de caché que coincidan con un patrón
    
    Args:
        pattern: Patrón de claves a invalidar
    """
    # Implementación básica - en producción usar Redis con SCAN
    cache.clear()

def cache_patient_analysis(patient_id: str, analysis_data: Dict[str, Any]) -> None:
    """Cachea análisis de paciente"""
    key = f"patient_analysis_{patient_id}_{datetime.now().strftime('%Y%m%d')}"
    cache_result(key, analysis_data, ttl=7200)  # 2 horas

def get_patient_analysis_cache(patient_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene análisis cacheado del paciente"""
    key = f"patient_analysis_{patient_id}_{datetime.now().strftime('%Y%m%d')}"
    return get_cached_result(key)