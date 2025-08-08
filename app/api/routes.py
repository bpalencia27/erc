from flask import request, jsonify, current_app, Response
from app.api import bp  # Importa el blueprint ya definido
from app.api.report_generator import AdvancedReportGenerator  # Ajusta esta ruta según donde esté tu generador
from app.utils.security import DataValidator
from app.parsers.lab_parser import parse_lab_results
from app.api.gemini_client import GeminiClient
from app.logic.patient_eval import PatientEvaluation
import os
import json
import traceback

@bp.route('/parse_document', methods=['POST'])
def parse_document():
    """Endpoint para analizar documentos de laboratorio."""
    try:
        data = request.json
        if not data or not data.get('text'):
            return jsonify({"success": False, "error": "No se proporcionó texto para analizar"}), 400
            
        text = data.get('text')
        filename = data.get('filename', 'documento.txt')
        
        # Analizar el texto usando el parser de laboratorio
        parsed_data = parse_lab_results(text)
        
        # Si no hay resultados con el parser, intentar con IA
        if not parsed_data or 'results' not in parsed_data or len(parsed_data['results']) == 0:
            try:
                gemini = GeminiClient()
                parsed_data = gemini.extract_lab_results(text)
            except Exception as e:
                current_app.logger.error(f"Error al usar IA para extraer resultados: {str(e)}")
                # Continuamos con los resultados que tengamos (aunque sean vacíos)
        
        return jsonify({
            "success": True,
            "results": parsed_data.get('results', {}),
            "patient_data": parsed_data.get('patient_data', {}),
            "source": filename
        })
        
    except Exception as e:
        current_app.logger.error(f"Error al analizar documento: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route('/generate_report', methods=['POST'])
def generate_report():
    """Endpoint para generar informe clínico con IA."""
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No se proporcionaron datos"}), 400
            
        # Validar datos requeridos
        required_fields = ['patient_data', 'lab_results']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Falta el campo {field}"}), 400
        
        # Generar informe usando IA
        report_generator = AdvancedReportGenerator()
        report = report_generator.generate_report(
            patient_data=data['patient_data'],
            lab_results=data['lab_results']
        )
        
        return jsonify({
            "success": True,
            "report": report
        })
        
    except Exception as e:
        current_app.logger.error(f"Error al generar informe: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500
        if not data or not data.get('patient'):
            return jsonify({"success": False, "error": "No se proporcionaron datos del paciente"}), 400
            
        patient_data = data.get('patient')
        
        # Usar Gemini para generar el informe
        gemini = GeminiClient()
        report_html = gemini.generate_patient_report(patient_data)
        
        return jsonify({
            "success": True,
            "report": report_html
        })
        
    except Exception as e:
        current_app.logger.error(f"Error al generar informe: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route('/follow_up_plan', methods=['POST'])
def get_follow_up_plan():
    """Endpoint para obtener un plan de seguimiento detallado."""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
            
        # Extraer datos requeridos
        etapa_erc = data.get('etapa_erc')
        riesgo_cv = data.get('riesgo_cv')
        metas_evaluacion = data.get('metas_evaluacion')
        
        if not etapa_erc or not riesgo_cv:
            return jsonify({"error": "Se requiere etapa_erc y riesgo_cv"}), 400
            
        # Generar plan de seguimiento
        generator = AdvancedReportGenerator()
        plan = generator._build_follow_up_plan(etapa_erc, riesgo_cv, metas_evaluacion)
        
        return jsonify({
            "success": True,
            "plan_seguimiento": plan
        })
        
    except Exception as e:
        current_app.logger.error(f"Error al generar plan de seguimiento: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/process_patient', methods=['POST'])
def process_patient():
    """Procesa datos del paciente y genera un informe."""
    try:
        data = request.json
        
        # Validar datos
        patient_data, patient_errors = DataValidator.validate_patient_data(data.get('patient_data', {}))
        labs_data, lab_errors = DataValidator.validate_lab_data(data.get('labs_data', {}))
        
        # Si hay errores críticos, retornar error
        if patient_errors or lab_errors:
            all_errors = patient_errors + lab_errors
            return jsonify({
                "success": False,
                "error": "Error de validación",
                "details": all_errors
            }), 400
        
        # Continuar con el procesamiento
        generator = AdvancedReportGenerator()
        result = generator.process_patient_data(patient_data, labs_data)
        
        return jsonify({
            "success": True,
            "report": result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error al procesar paciente: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/evaluate_patient', methods=['POST'])
def evaluate_patient():
    """
    Endpoint para evaluación clínica del paciente
    
    Espera JSON con:
    {
        "patient_data": {
            "edad": int,
            "peso": float,
            "talla": float,
            "sexo": str,
            "creatinina": float,
            "pa_sistolica": int,
            "pa_diastolica": int,
            "diabetes": bool,
            "hipertension": bool,
            "ecv": bool,
            "tabaquismo": bool
        },
        "lab_results": {
            "lab_name": {
                "valor": float,
                "unidad": str,
                "fecha": str,
                "dias_desde_toma": int
            },
            ...
        }
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No se proporcionaron datos"}), 400
            
        # Validar datos requeridos
        required_fields = ["patient_data", "lab_results"]
        if not all(field in data for field in required_fields):
            return jsonify({
                "success": False, 
                "error": "Faltan campos requeridos",
                "required": required_fields
            }), 400
        
        # Inicializar evaluador
        evaluator = PatientEvaluation()
        
        # Realizar evaluación
        evaluation = evaluator.evaluate_patient(
            data["patient_data"],
            data["lab_results"]
        )
        
        return jsonify({
            "success": True,
            "evaluation": evaluation
        })
        
    except ValueError as ve:
        return jsonify({
            "success": False,
            "error": "Error de validación",
            "details": str(ve)
        }), 400
        
    except Exception as e:
        current_app.logger.error(f"Error en evaluación: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": "Error interno del servidor",
            "details": str(e)
        }), 500

@bp.route('/test')
def test():
    return {"message": "API funcionando correctamente"}