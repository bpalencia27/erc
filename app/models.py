from app.extensions import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relaciones
    patients = db.relationship('Patient', backref='doctor', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    document_id = db.Column(db.String(64), unique=True)
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(1))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lab_results = db.relationship('LabResult', backref='patient', lazy='dynamic')
    reports = db.relationship('Report', backref='patient', lazy='dynamic')
    
    def __repr__(self):
        return f'<Patient {self.name}>'

class LabResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    test_date = db.Column(db.DateTime, default=datetime.utcnow)
    test_name = db.Column(db.String(64), nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(32))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LabResult {self.test_name}: {self.value}>'

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    report_date = db.Column(db.DateTime, default=datetime.utcnow)
    report_type = db.Column(db.String(64))
    content = db.Column(db.Text, nullable=False)
    metadata = db.Column(db.Text)  # JSON serializado
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Report {self.id} for Patient {self.patient_id}>'