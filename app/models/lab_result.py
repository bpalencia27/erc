"""
Modelo para almacenar resultados de laboratorio
"""
from datetime import datetime
from app.extensions import db

class LabResult(db.Model):
    """Modelo para almacenar los resultados de laboratorio de un paciente."""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    test_name = db.Column(db.String(100), nullable=False)
    result_value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))
    reference_range = db.Column(db.String(50))
    test_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LabResult {self.test_name}: {self.result_value} {self.unit}>'
    
    @property
    def is_valid(self):
        """
        Determina si el resultado de laboratorio sigue siendo válido
        basado en la configuración de validez de las pruebas.
        """
        # Esta función debería implementarse consultando el archivo de configuración
        # lab_validity.json para determinar la validez según el tipo de prueba y
        # la etapa de ERC del paciente
        return True  # Placeholder - implementar lógica real
    
    def to_dict(self):
        """Convierte el modelo a un diccionario."""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'test_name': self.test_name,
            'result_value': self.result_value,
            'unit': self.unit,
            'reference_range': self.reference_range,
            'test_date': self.test_date.isoformat() if self.test_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_valid': self.is_valid
        }
    
    @classmethod
    def get_most_recent(cls, patient_id, test_name):
        """Obtiene el resultado más reciente para un paciente y prueba específica."""
        return cls.query.filter_by(
            patient_id=patient_id,
            test_name=test_name
        ).order_by(cls.test_date.desc()).first()
