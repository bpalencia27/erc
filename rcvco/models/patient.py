"""
Patient model for RCV-CO system
"""
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Patient:
    """Data class for storing patient information"""
    id: int
    document_type: str
    document_number: str
    first_name: str
    last_name: str
    date_of_birth: datetime
    gender: str  # 'M' or 'F'
    ethnicity: Optional[str]  # 'black' or 'non_black'
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    @property
    def full_name(self) -> str:
        """Returns patient's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> int:
        """Calculates current patient age"""
        today = datetime.now().date()
        born = self.date_of_birth.date()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    
    def to_dict(self) -> dict:
        """Converts model to dictionary"""
        return {
            'id': self.id,
            'document_type': self.document_type,
            'document_number': self.document_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat(),
            'gender': self.gender,
            'ethnicity': self.ethnicity,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
