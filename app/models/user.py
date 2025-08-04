"""
Modelo de usuario para autenticación en ERC Insight
"""
from datetime import datetime
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """Modelo para almacenar información de usuarios."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Establece el hash de contraseña para el usuario."""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Verifica si la contraseña es correcta."""
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_authenticated(self):
        """Propiedad para Flask-Login."""
        return True
        
    @property
    def is_active(self):
        """Propiedad para Flask-Login."""
        return True
        
    @property
    def is_anonymous(self):
        """Propiedad para Flask-Login."""
        return False
        
    def get_id(self):
        """Método para Flask-Login."""
        return str(self.id)
