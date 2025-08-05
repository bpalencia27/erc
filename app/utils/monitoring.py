# Agregar logging mejorado
import logging
import traceback
from functools import wraps

def log_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error en {func.__name__}: {str(e)}", exc_info=True)
            # Guardar traza de la excepción para debug
            error_details = traceback.format_exc()
            logging.debug(f"Detalles completos del error en {func.__name__}:\n{error_details}")
            raise
    return wrapper