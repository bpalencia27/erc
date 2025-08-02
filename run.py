"""
Punto de entrada para ejecutar la aplicación en modo desarrollo
"""
from app import create_app
import os

app = create_app('config.DevelopmentConfig')
@app.route('/erc-insight')
def erc_insight():
    return render_template('erc_insight.html')

# Endpoints de API para la nueva interfaz
@app.route('/api/parse_lab_report', methods=['POST'])
def parse_lab_report_api():
    data = request.json
    text = data.get('text', '')
    
    # Puedes llamar a tus funciones existentes aquí
    # Por ejemplo: results = parse_lab_data(text)
    
    # Por ahora, devolvemos datos de ejemplo:
    return jsonify({
        "nombre_paciente": "Nombre extraído del documento",
        "edad_paciente": 65,
        "sexo_paciente": "m",
        "fecha_informe": "2023-08-02",
        "resultados": [
            {"nombre": "creatinina", "resultado": 1.2, "unidades": "mg/dL"}
        ]
    })

@app.route('/api/generate_report', methods=['POST'])
def generate_report_api():
    data = request.json
    
    # Puedes usar tus funciones existentes aquí
    # Por ejemplo: report = generate_patient_report(data)
    
    # Devolvemos el HTML del informe:
    return jsonify({
        "html_content": "<h1>Informe del Paciente</h1><p>Este es un informe de ejemplo.</p>"
    })
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
