"""
Patrones de expresiones regulares para extracción de laboratorios
"""

CREATININA_PATTERNS = [
    {
        'name': 'creatinina_serica',
        'include': [
            # Patrón principal con especificadores de tipo
            r'(?:CREATININA|Creatinina|creatinina)(?:\s+S[EÉ]RICA|(?:\s+EN\s+)?SUERO|\s+PLASM[AÁ]TICA|\s+EN\s+SANGRE)?\s*(?::|=|\s)\s*(\d+[.,]\d+|\d+)\s*(?:mg/dL|mg/dl|MG/DL)',
            # Patrón abreviado con especificadores
            r'(?:Creat\.|CREAT\.|creat\.)(?:\s+s[eé]r\.?|\s+suero)?\s*(?::|=|\s)\s*(\d+[.,]\d+|\d+)\s*(?:mg/dL|mg/dl|MG/DL)',
            # Patrón para formatos alternativos
            r'(?:Cr|CR)(?:\s+s[eé]rica|\s+suero)?\s*(?::|=|\s)\s*(\d+[.,]\d+|\d+)\s*(?:mg/dL|mg/dl|MG/DL)',
            # Patrón para valores en tablas
            r'(?<=\n|\t|^)(?:Cr|CR|CREAT)\.?\s*(\d+[.,]\d+|\d+)\s*(?:mg/dL|mg/dl|MG/DL)(?=\s|$|\n)',
        ],
        'exclude': [
            # Patrones de exclusión mejorados
            r'(?:ORINA|orina|URINARIA|urinaria|DEPURACI[OÓ]N|CLEARANCE|[24]4\s*HRS?|RECOLEC)',
            r'(?:ACLARAMIENTO|DEPURACION|EXCRE[CS]I[OÓ]N).*(?:CREATININA|Creatinina)',
            r'CREATININA.*(?:ORINA|URINARIA|[24]4\s*HRS?)',
            r'(?:mg|µg|mcg)/(?:min|hora|hr|h|día|day)',
            r'CREATININA\s+U'
        ],
        'unit': 'mg/dL',
        'validation': {
            'min_value': 0.2,
            'max_value': 20.0,
            'decimals': 2
        }
    },
    {
        'name': 'creatinina_urgente',
        'include': [
            # Patrones específicos para resultados urgentes/emergencia
            r'(?:CREATININA|Creatinina|CREAT)(?:\s+STAT|\s+URG|\s+EMERGENCIA)?\s*(?::|=|\s)\s*(\d+[.,]\d+|\d+)\s*(?:mg/dL|mg/dl|MG/DL)',
            r'(?:\*\s*)?(?:Cr|CR)(?:\s+STAT|\s+URG)?\s*(?::|=|\s)\s*(\d+[.,]\d+|\d+)\s*(?:mg/dL|mg/dl|MG/DL)'
        ],
        'exclude': [
            r'(?:ORINA|orina|URINARIA|urinaria|DEPURACI[OÓ]N|CLEARANCE)',
            r'(?:mg|µg|mcg)/(?:min|hora|hr|h|día|day)'
        ],
        'unit': 'mg/dL',
        'validation': {
            'min_value': 0.2,
            'max_value': 20.0,
            'decimals': 2
        },
        'priority': 'high'
    }
]

LAB_PATTERNS = {
    'glucosa': {
        'regex': r'(?:GLUCOSA|Glucosa|glucosa)(?:\s+EN\s+AYUNAS|\s+BASAL)?\s*(?::|=|\s)\s*(\d+[.,]\d+|\d+)\s*(?:mg/dL|mg/dl|MG/DL)',
        'unit': 'mg/dL'
    },
    'hba1c': {
        'regex': r'(?:HBA1C|HbA1c|HEMOGLOBINA\s+GLICOSILADA|Hemoglobina\s+[Gg]licosilada)\s*(?::|=|\s)\s*(\d+[.,]\d+|\d+)\s*%',
        'unit': '%'
    },
    'ldl': {
        'regex': r'(?:LDL|Ldl|COLESTEROL\s+LDL|Colesterol\s+LDL)\s*(?::|=|\s)\s*(\d+[.,]\d+|\d+)\s*(?:mg/dL|mg/dl|MG/DL)',
        'unit': 'mg/dL'
    },
    'hdl': {
        'regex': r'(?:HDL|Hdl|COLESTEROL\s+HDL|Colesterol\s+HDL)\s*(?::|=|\s)\s*(\d+[.,]\d+|\d+)\s*(?:mg/dL|mg/dl|MG/DL)',
        'unit': 'mg/dL'
    },
    'trigliceridos': {
        'regex': r'(?:TRIGLIC[EÉ]RIDOS|Triglic[eé]ridos)\s*(?::|=|\s)\s*(\d+[.,]\d+|\d+)\s*(?:mg/dL|mg/dl|MG/DL)',
        'unit': 'mg/dL'
    },
    'rac': {
        'regex': r'(?:RAC|RELACI[OÓ]N\s+ALBUMINA[/-]CREATININA)\s*(?::|=|\s)\s*(\d+[.,]\d+|\d+)\s*(?:mg/g|MG/G|mg/gr)',
        'unit': 'mg/g'
    },
    'potasio': {
        'regex': r'(?:POTASIO|Potasio|K\+?)\s*(?:S[EÉ]RICO)?\s*(?::|=|\s)\s*(\d+[.,]\d+|\d+)\s*(?:mEq/L|mmol/L)',
        'unit': 'mEq/L'
    }
}

PATIENT_PATTERNS = {
    'nombre': {
        'regex': r'(?:PACIENTE|Paciente|NOMBRE DEL PACIENTE|Nombre)?\s*(?::|=|\s)\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,3})',
        'validate': lambda x: len(x.split()) >= 2  # Al menos nombre y apellido
    },
    'edad': {
        'regex': r'(?:EDAD|Edad)\s*(?::|=|\s)\s*(\d{1,3})\s*(?:años|AÑOS|Años|aa|AA)',
        'validate': lambda x: 0 < int(x) < 120  # Edad válida entre 1 y 120 años
    },
    'sexo': {
        'regex': r'(?:SEXO|Sexo|GÉNERO|Género)\s*(?::|=|\s)\s*([MF]|(?:MAS|FEM|MASCULINO|FEMENINO|Masculino|Femenino))',
        'transform': lambda x: 'm' if x.upper().startswith('M') else 'f'
    },
    'identificacion': {
        'regex': r'(?:ID|IDENTIFICACI[OÓ]N|C[EÉ]DULA)\s*(?::|=|\s)\s*(\d[\d\s.-]+)',
        'transform': lambda x: x.replace(' ', '').replace('-', '').replace('.', '')
    }
}
