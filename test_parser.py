# Crear archivo de test
from app.parsers.lab_parser import parse_lab_results

test_text = """
Nombre: Juan Pérez
Edad: 65 años
Sexo: Masculino
Creatinina en suero: 1.2 mg/dl
Creatinina en orina: 150 mg/dl (DEBE IGNORARSE)
Relación albúmina/creatinina: 45 mg/g
"""

result = parse_lab_results(test_text)
print(result)
# Debe mostrar solo creatinina_suero: 1.2, NO la de orina