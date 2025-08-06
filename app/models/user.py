"""
Modelo de usuario para autenticación y gestión de usuarios
"""

class User:
    def __init__(self, username, password, email=None):
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return f"<User {self.username}>"

    # Puedes agregar aquí métodos para autenticación, validación, etc.
