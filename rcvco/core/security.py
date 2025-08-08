"""
Módulo de seguridad centralizado para RCV-CO
"""
from typing import Optional
import re
from pydantic import BaseModel, validator
import bleach
import secrets
from datetime import datetime, timedelta

class SanitizedInput(BaseModel):
    """Modelo base para sanitización de inputs"""
    
    @validator("*", pre=True)
    def sanitize_strings(cls, v):
        """Sanitiza strings para prevenir XSS"""
        if isinstance(v, str):
            return bleach.clean(v)
        return v

class UserInput(SanitizedInput):
    """Modelo para inputs de usuario"""
    username: str
    password: Optional[str]
    email: Optional[str]

    @validator("username")
    def username_alphanumeric(cls, v):
        if not re.match("^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username debe ser alfanumérico")
        return v

    @validator("email")
    def email_valid(cls, v):
        if v and not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Email inválido")
        return v

def generate_csrf_token() -> str:
    """Genera token CSRF seguro"""
    return secrets.token_urlsafe(32)

def validate_csrf_token(token: str, session_token: str) -> bool:
    """Valida token CSRF"""
    return secrets.compare_digest(token, session_token)
