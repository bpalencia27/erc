"""
Modelo de paciente para la aplicación ERC Insight
"""
from datetime import datetime
from app import db

class Patient(db.Model):
    """Modelo para almacenar información de pacientes."""
    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(db.String(20), nullable=False)
    document_number = db.Column(db.String(30), nullable=False, unique=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(1), nullable=False)  # 'M' o 'F'
    ethnicity = db.Column(db.String(20))  # 'negro' o 'no_negro'
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    lab_results = db.relationship('LabResult', backref='patient', lazy='dynamic')
    reports = db.relationship('Report', backref='patient', lazy='dynamic')
    
    def __repr__(self):
        return f'<Patient {self.first_name} {self.last_name}>'
    
    @property
    def full_name(self):
        """Devuelve el nombre completo del paciente."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calcula la edad actual del paciente."""
        today = datetime.now().date()
        born = self.date_of_birth
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return age
    
    def to_dict(self):
        """Convierte el modelo a un diccionario."""
        return {
            'id': self.id,
            'document_type': self.document_type,
            'document_number': self.document_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat(),
            'age': self.age,
            'gender': self.gender,
            'ethnicity': self.ethnicity,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
