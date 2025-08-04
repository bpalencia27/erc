from flask import render_template, request, jsonify, current_app
from app.report import bp
from app.logic.patient_eval import generar_informe_base
from app.api.gemini_client import GeminiClient
from app.api.report_generator import AdvancedReportGenerator
import json
import os
from datetime import datetime

@bp.route('/generate', methods=['POST'])
def generate_report():
    """Genera un informe médico basado en los datos del paciente y laboratorios."""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        # Extraer datos necesarios
        patient_data = data.get('paciente', {})
        lab_data = data.get('laboratorios', {})
        
        # Validar datos mínimos
        if not patient_data:
            return jsonify({"error": "No se proporcionaron datos del paciente"}), 400
        
        # Generar informe base
        informe = generar_informe_base(patient_data, lab_data)
        
        # Intentar generar informe con IA
        try:
            gemini_client = GeminiClient()
            informe_texto = gemini_client.generate_medical_report(informe)
            informe['informe_texto'] = informe_texto
        except Exception as e:
            current_app.logger.error(f"Error al generar informe con IA: {str(e)}")
            informe['informe_texto'] = "No se pudo generar el informe con IA. Por favor, inténtelo de nuevo más tarde."
        
        # Guardar informe para referencia futura
        save_report(informe)
        
        return jsonify({"success": True, "informe": informe})
        
    except Exception as e:
        current_app.logger.error(f"Error al generar informe: {str(e)}")
        return jsonify({"error": f"Error al generar informe: {str(e)}"}), 500

@bp.route('/view/<report_id>')
def view_report(report_id):
    """Muestra un informe previamente generado."""
    try:
        # Intentar cargar el informe desde el archivo
        report_path = os.path.join(current_app.static_folder, 'reports', f"{report_id}.json")
        
        if not os.path.exists(report_path):
            return render_template('error.html', message="Informe no encontrado"), 404
        
        with open(report_path, 'r', encoding='utf-8') as f:
            informe = json.load(f)
        
        return render_template('report/view.html', informe=informe)
        
    except Exception as e:
        current_app.logger.error(f"Error al visualizar informe {report_id}: {str(e)}")
        return render_template('error.html', message=f"Error al cargar el informe: {str(e)}"), 500

@bp.route('/generate_advanced', methods=['POST'])
def generate_advanced_report():
    """
    Genera un informe avanzado utilizando el motor de lógica de negocio mejorado 
    y la integración con la API de Gemini.
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        # Extraer datos necesarios
        patient_data = data.get('patient', {})
        lab_data = data.get('labs', {})
        
        # Validar datos mínimos
        if not patient_data:
            return jsonify({"error": "No se proporcionaron datos del paciente"}), 400
        
        # Generar informe avanzado
        report_generator = AdvancedReportGenerator()
        result = report_generator.process_patient_data(patient_data, lab_data)
        
        # Guardar resultado
        if "error" not in result:
            # Crear estructura para guardar
            informe = {
                "paciente": patient_data,
                "laboratorios": lab_data,
                "informe_texto": result.get("report", ""),
                "metadata": result.get("metadata", {})
            }
            
            # Guardar informe
            report_id = save_report(informe)
            result["report_id"] = report_id
        
        return jsonify({
            "success": "error" not in result,
            "result": result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error al generar informe avanzado: {str(e)}")
        return jsonify({"error": f"Error al generar informe avanzado: {str(e)}"}), 500

def save_report(informe):
    """
    Guarda el informe en un archivo JSON para referencia futura.
    
    Args:
        informe (dict): Datos del informe
    
    Returns:
        str: ID del informe guardado
    """
    # Generar ID único para el informe
    report_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{informe['paciente'].get('nombre', 'unknown').replace(' ', '_')}"
    informe['report_id'] = report_id
    
    # Crear directorio si no existe
    reports_dir = os.path.join(current_app.static_folder, 'reports')
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Guardar informe como JSON
    report_path = os.path.join(reports_dir, f"{report_id}.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(informe, f, ensure_ascii=False, indent=2)
    
    return report_id
