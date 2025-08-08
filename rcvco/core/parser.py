"""
Content parser for lab results.
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LabValue:
    """Represents a single laboratory test result."""
    name: str
    value: float
    unit: str
    reference_range: Optional[str] = None
    is_abnormal: Optional[bool] = None

@dataclass
class LabReport:
    """Represents a complete laboratory report."""
    date: Optional[datetime]
    patient_name: Optional[str]
    patient_id: Optional[str]
    patient_age: Optional[int]
    patient_gender: Optional[str]
    values: List[LabValue]
    source_file: Path
    raw_text: str

class LabParser:
    """Parser for extracting structured lab data from text content."""
    
    def __init__(self):
        self.patterns = {
            'creatinina': {
                'pattern': r'Creatinina:\s*(\d+\.?\d*)\s*(mg/dL)',
                'unit': 'mg/dL'
            },
            'glicemia': {
                'pattern': r'Glucosa:\s*(\d+\.?\d*)\s*(mg/dL)',
                'unit': 'mg/dL'
            },
            'colesterol_total': {
                'pattern': r'Colesterol Total:\s*(\d+\.?\d*)\s*(mg/dL)',
                'unit': 'mg/dL'
            },
            'ldl': {
                'pattern': r'LDL:\s*(\d+\.?\d*)\s*(mg/dL)',
                'unit': 'mg/dL'
            },
            'hdl': {
                'pattern': r'HDL:\s*(\d+\.?\d*)\s*(mg/dL)',
                'unit': 'mg/dL'
            },
            'trigliceridos': {
                'pattern': r'Triglicéridos:\s*(\d+\.?\d*)\s*(mg/dL)',
                'unit': 'mg/dL'
            },
            'rac': {
                'pattern': r'Relación Microalbuminuria/Creatinina:\s*(\d+\.?\d*)\s*(mg/g)',
                'unit': 'mg/g'
            },
            'hba1c': {
                'pattern': r'HbA1c:\s*(\d+\.?\d*)\s*(%)',
                'unit': '%'
            }
        }

    def parse(self, text: str, source_file: Path) -> LabReport:
        """
        Parse lab results from text content.
        
        Args:
            text (str): The text content to parse
            source_file (Path): Path to the source file
            
        Returns:
            LabReport: Structured lab report data
        """
        values = []
        for name, config in self.patterns.items():
            match = re.search(config['pattern'], text)
            if match:
                values.append(LabValue(
                    name=name,
                    value=float(match.group(1)),
                    unit=match.group(2) or config['unit']
                ))

        return LabReport(
            date=self._extract_date(text),
            patient_name=self._extract_patient_name(text),
            patient_id=self._extract_patient_id(text),
            patient_age=self._extract_patient_age(text),
            patient_gender=self._extract_patient_gender(text),
            values=values,
            source_file=source_file,
            raw_text=text
        )

    def _extract_date(self, text: str) -> Optional[datetime]:
        """Extract report date from text."""
        patterns = [
            r'Fecha:\s*(\d{4}-\d{2}-\d{2})',  # 2025-07-15
            r'Fecha:\s*(\d{2}/\d{2}/\d{4})',  # 15/07/2025
            r'Fecha\s+de\s+muestra:\s*(\d{2}-\d{2}-\d{4})'  # 15-07-2025
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(1)
                try:
                    if '/' in date_str:
                        return datetime.strptime(date_str, '%d/%m/%Y')
                    return datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    continue
        return None

    def _extract_patient_name(self, text: str) -> Optional[str]:
        """Extract patient name from text."""
        patterns = [
            r'Paciente:?\s*([A-Za-zÁÉÍÓÚáéíóúÑñ\s]+?)(?:\s+(?:edad|sexo|fecha))',
            r'Nombre:?\s*([A-Za-zÁÉÍÓÚáéíóúÑñ\s]+?)(?:\s+(?:edad|sexo|fecha))'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None

    def _extract_patient_id(self, text: str) -> Optional[str]:
        """Extract patient ID from text."""
        match = re.search(r'ID:?\s*([A-Z0-9-]+)', text)
        return match.group(1) if match else None

    def _extract_patient_age(self, text: str) -> Optional[int]:
        """Extract patient age from text."""
        match = re.search(r'Edad:?\s*(\d+)', text)
        return int(match.group(1)) if match else None

    def _extract_patient_gender(self, text: str) -> Optional[str]:
        """Extract patient gender from text."""
        match = re.search(r'(?:Género|Sexo):?\s*([MF]|Masculino|Femenino)', text)
        if match:
            gender = match.group(1).lower()
            if gender in ['m', 'masculino']:
                return 'M'
            if gender in ['f', 'femenino']:
                return 'F'
        return None
