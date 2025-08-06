# Script de utilidades para limpieza y generación de reportes
# Solo contiene código de programación, no referencias a guías médicas

import os
import re

def clean_duplicate_files():
    """
    Limpia archivos duplicados con el patrón (1) en el nombre
    """
    duplicates = []
    for root, dirs, files in os.walk('.'):
        for filename in files:
            if re.search(r'\s*\(\d+\)\s*\.', filename):
                filepath = os.path.join(root, filename)
                duplicates.append(filepath)
    
    return duplicates

def apply_pdf_styles():
    """
    Aplica estilos para generación de reportes en PDF usando ReportLab
    """
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), '#4C6EF5'),
        ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), '#f0f0f0'),
        ('GRID', (0, 0), (-1, -1), 1, 'black')
    ]
    return table_style

if __name__ == "__main__":
    print("Script de limpieza y estilos para reportes")
    duplicates = clean_duplicate_files()
    print(f"Archivos duplicados encontrados: {len(duplicates)}")
