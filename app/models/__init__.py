"""
Inicialización del paquete de modelos
"""
# Este archivo permite que Python reconozca el directorio 'models' como un paquete

from app.models.patient import Patient
from app.models.lab_result import LabResult
from app.models.report import Report
from app.models.user import User

# Para facilitar las importaciones
__all__ = ['Patient', 'LabResult', 'Report', 'User']
