"""
Modelo para informes médicos generados
"""
from datetime import datetime
from app import db

class Report(db.Model):
    """Modelo para almacenar informes médicos generados."""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100))  # ID o nombre del usuario que generó el informe
    report_type = db.Column(db.String(50))  # Tipo de informe (seguimiento, inicial, etc.)
    
    def __repr__(self):
        return f'<Report {self.title} for patient {self.patient_id}>'
    
    def to_dict(self):
        """Convierte el modelo a un diccionario."""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'title': self.title,
            'content': self.content,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'created_by': self.created_by,
            'report_type': self.report_type
        }
