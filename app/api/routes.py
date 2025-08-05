"""
API endpoints para la integración con el frontend
"""
from flask import request, jsonify
from app.api import bp
from app.api.report_generator import AdvancedReportGenerator
from app.logic.patient_eval import calcular_tfg, determinar_etapa_erc

@bp.route('/generate_report', methods=['POST'])
def generate_report():
    """
    Endpoint para generar un informe médico usando la API de Gemini.
    Recibe los datos del paciente en formato JSON y devuelve el informe HTML.
    """
    if not request.is_json:
        return jsonify({"error": "Se esperaba contenido JSON"}), 400
        
    data = request.get_json()
    
    # Validar datos mínimos necesarios
    required_fields = ['first_name', 'last_name', 'edad', 'sexo', 'peso']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Campo requerido ausente: {field}"}), 400
    
    try:
        # Crear una instancia del generador de informes
        report_generator = AdvancedReportGenerator()
        
        # Preprocesar datos si es necesario
        if 'creatinina' in data and data['creatinina'] and 'tfg' not in data:
            data['tfg'] = calcular_tfg(
                edad=int(data['edad']), 
                peso=float(data['peso']),
                creatinina=float(data['creatinina']), 
                sexo=data['sexo']
            )
        
        # Generar el informe
        report_html = report_generator.generate_patient_report(data)
        
        # Formatear el HTML para el frontend
        formatted_html = format_report_html(report_html)
        
        return jsonify({
            "success": True,
            "html_report": formatted_html
        })
        
    except Exception as e:
        # Registrar error detallado en logs
        import logging
        logging.error(f"Error al generar informe: {str(e)}")
        
        return jsonify({
            "error": "Error al generar el informe",
            "details": str(e)
        }), 500

def format_report_html(report_text):
    """
    Formatea el texto del informe de Gemini a HTML estructurado
    para mostrarlo en el frontend.
    """
    html = report_text
    
    # Aplicar transformaciones de Markdown a HTML
    html = html.replace("ADVERTENCIA:", '<div class="alert-mace"><strong>ADVERTENCIA:</strong>')
    html = html.replace("**", "<strong>").replace("**", "</strong>")
    html = html.replace("*", "<em>").replace("*", "</em>")
    
    # Convertir encabezados
    lines = html.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("## "):
            lines[i] = f"<h2>{line[3:]}</h2>"
        elif line.startswith("### "):
            lines[i] = f"<h3>{line[4:]}</h3>"
        elif line.startswith("* "):
            lines[i] = f"<li>{line[2:]}</li>"
    
    html = "\n".join(lines)
    
    # Limpiar y estructurar listas
    html = html.replace("</li>\n<li>", "</li><li>")
    
    # Agrupar items de lista en <ul>
    import re
    html = re.sub(r'(<li>.*?</li>)+', r'<ul>\g<0></ul>', html)
    html = html.replace("</ul>\n<ul>", "")
    
    return html
