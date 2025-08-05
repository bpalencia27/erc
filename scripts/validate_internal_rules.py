import ast
import os

def check_external_references(filepath):
    """Verifica que no haya referencias a guías externas"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Buscar referencias prohibidas
    prohibited = [
        'http://', 'https://', 'www.',
        'kdigo.org', 'guidelines', 'external_api',
        'web_scraping', 'requests.get'
    ]
    violations = []
    for term in prohibited:
        if term in content.lower():
            violations.append(f"Referencia externa encontrada: {term}")
    return violations

if __name__ == "__main__":
    print("Validando reglas internas en archivos .py del proyecto...")
    for root, dirs, files in os.walk('app'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                violations = check_external_references(filepath)
                if violations:
                    print(f"❌ {filepath}:")
                    for v in violations:
                        print(f"   - {v}")
    print("Validación completada.")
