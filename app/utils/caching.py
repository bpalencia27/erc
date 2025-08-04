import functools
import time
from datetime import datetime, timedelta
import hashlib
import json
import os
import pickle

class SimpleCache:
    """Implementación simple de caché en memoria con expiración."""
    
    def __init__(self, expiration_seconds=3600):
        self.cache = {}
        self.expiration = expiration_seconds
    
    def get(self, key):
        """Obtiene un valor de la caché si existe y no ha expirado."""
        if key not in self.cache:
            return None
            
        timestamp, value = self.cache[key]
        if datetime.now() - timestamp > timedelta(seconds=self.expiration):
            # Valor expirado
            del self.cache[key]
            return None
            
        return value
    
    def set(self, key, value):
        """Almacena un valor en la caché con timestamp actual."""
        self.cache[key] = (datetime.now(), value)
    
    def clear(self):
        """Limpia toda la caché."""
        self.cache.clear()
    
    def clean_expired(self):
        """Elimina entradas expiradas de la caché."""
        now = datetime.now()
        expired_keys = [
            key for key, (timestamp, _) in self.cache.items()
            if now - timestamp > timedelta(seconds=self.expiration)
        ]
        
        for key in expired_keys:
            del self.cache[key]

# Caché para resultados de informes
report_cache = SimpleCache(expiration_seconds=1800)  # 30 minutos

def cache_key(func_name, *args, **kwargs):
    """Genera una clave única para la caché basada en la función y argumentos."""
    key_parts = [func_name]
    
    # Convertir args a representación de cadena
    for arg in args:
        if isinstance(arg, dict):
            # Para diccionarios, ordenamos las claves para consistencia
            key_parts.append(json.dumps(arg, sort_keys=True))
        else:
            key_parts.append(str(arg))
    
    # Convertir kwargs a representación de cadena
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")
    
    # Crear hash MD5 para obtener una clave de longitud fija
    return hashlib.md5(":".join(key_parts).encode()).hexdigest()

def cached_result(expiration_seconds=1800):
    """Decorador para cachear resultados de funciones."""
    def decorator(func):
        # Crear caché específica para esta función
        func_cache = SimpleCache(expiration_seconds=expiration_seconds)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave única para esta invocación
            key = cache_key(func.__name__, *args, **kwargs)
            
            # Intentar obtener de caché
            cached_value = func_cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Calcular resultado y almacenar en caché
            result = func(*args, **kwargs)
            func_cache.set(key, result)
            return result
        
        return wrapper
    
    return decorator