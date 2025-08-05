"""
API endpoints para la integración con el frontend
"""
from flask import request, jsonify, current_app, Response
from app.api import bp
from app.api.report_generator import AdvancedReportGenerator
from app.logic.patient_eval import calcular_tfg, determinar_etapa_erc
from app.utils.security import DataValidator
from app.parsers.lab_parser import parse_lab_results
from app.api.gemini_client import GeminiClient
from app.logic.advanced_patient_eval import calcular_riesgo_cardiovascular, clasificar_riesgo_cv
from datetime import datetime, timedelta
import os
import json
import traceback

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
        current_app.logger.error(f"Error al generar informe: {str(e)}")
        
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

@bp.route('/risk/classify', methods=['POST'])
def classify_risk():
    """Endpoint para clasificar el riesgo cardiovascular del paciente."""
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No se proporcionaron datos"}), 400
        
        # Validar datos mínimos requeridos
        required_fields = ['edad', 'sexo']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Falta el campo requerido: {field}"}), 400
        
        # Calcular TFG si tenemos los datos necesarios
        tfg = None
        if 'creatinina' in data and 'peso' in data:
            try:
                tfg = calcular_tfg(
                    edad=int(data.get('edad', 0)), 
                    peso=float(data.get('peso', 70)), 
                    creatinina=float(data.get('creatinina', 1.0)),
                    sexo=data.get('sexo', 'm')
                )
                # Determinar etapa ERC
                etapa_erc = determinar_etapa_erc(tfg)
                data['erc'] = True if etapa_erc not in ['g1', 'g2'] else data.get('erc', False)
            except Exception as e:
                current_app.logger.error(f"Error al calcular TFG: {str(e)}")
                # Continuamos sin TFG
        
        # Clasificar riesgo cardiovascular
        risk_level = clasificar_riesgo_cv(data, tfg)
        
        # Generar recomendaciones basadas en el nivel de riesgo
        recommendations = []
        if risk_level == 'bajo':
            recommendations = [
                "Mantener estilo de vida saludable",
                "Control médico anual",
                "Continuar con actividad física regular"
            ]
        elif risk_level == 'moderado':
            recommendations = [
                "Optimizar factores de riesgo",
                "Control médico semestral",
                "Evaluación de perfil lipídico anual",
                "Considerar estatinas de intensidad moderada si LDL ≥ 130 mg/dL"
            ]
        elif risk_level == 'alto':
            recommendations = [
                "Control médico trimestral",
                "Evaluación de perfil lipídico cada 6 meses",
                "Estatinas de intensidad alta si LDL ≥ 100 mg/dL",
                "Control estricto de presión arterial y glucemia"
            ]
        elif risk_level == 'muy alto':
            recommendations = [
                "Control médico mensual o bimensual",
                "Evaluación de perfil lipídico trimestral",
                "Estatinas de alta intensidad para reducir LDL > 50%",
                "Considerar terapia combinada para dislipidemia",
                "Manejo integral por equipo multidisciplinario"
            ]
        
        # Detalles específicos según los factores de riesgo
        details = "Clasificación basada en "
        factors = []
        
        if data.get('dm2', False):
            factors.append("diabetes")
        if data.get('hta', False):
            factors.append("hipertensión arterial")
        if data.get('dislipidemia', False):
            factors.append("dislipidemia")
        if data.get('erc', False):
            factors.append("enfermedad renal crónica")
        if data.get('tabaquismo', False):
            factors.append("tabaquismo")
        if tfg and tfg < 60:
            factors.append(f"TFG reducida ({tfg} ml/min/1.73m²)")
        
        if factors:
            details += "los siguientes factores: " + ", ".join(factors)
        else:
            details += "edad y sexo"
        
        return jsonify({
            "success": True,
            "riskLevel": risk_level.capitalize(),
            "details": details,
            "recommendations": recommendations,
            "tfg": tfg
        })
        
    except Exception as e:
        current_app.logger.error(f"Error al clasificar riesgo: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route('/goals/evaluate', methods=['POST'])
def evaluate_therapeutic_goals():
    """Endpoint para evaluar metas terapéuticas según consenso médico."""
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No se proporcionaron datos"}), 400
        
        # Obtener el nivel de riesgo (calcularlo si no está presente)
        risk_level = data.get('riskLevel', '').lower()
        if not risk_level:
            # Calcular TFG
            tfg = None
            if 'creatinina' in data and 'peso' in data and 'edad' in data and 'sexo' in data:
                tfg = calcular_tfg(
                    edad=int(data.get('edad', 0)), 
                    peso=float(data.get('peso', 70)), 
                    creatinina=float(data.get('creatinina', 1.0)),
                    sexo=data.get('sexo', 'm')
                )
            
            # Clasificar riesgo
            risk_level = clasificar_riesgo_cv(data, tfg)
        
        # Definir metas según nivel de riesgo
        ldl_goal = None
        bp_goal = None
        hba1c_goal = None
        
        # Metas de LDL según nivel de riesgo
        if risk_level == 'bajo':
            ldl_goal = {"min": None, "optimal": 115, "unit": "mg/dL"}
        elif risk_level == 'moderado':
            ldl_goal = {"min": 115, "optimal": 100, "unit": "mg/dL"}
        elif risk_level == 'alto':
            ldl_goal = {"min": 100, "optimal": 70, "unit": "mg/dL"}
        elif risk_level == 'muy alto':
            ldl_goal = {"min": 70, "optimal": 55, "unit": "mg/dL"}
        
        # Metas de presión arterial
        bp_goal = {"systolic": {"min": None, "optimal": 130}, "diastolic": {"min": None, "optimal": 80}, "unit": "mmHg"}
        if data.get('dm2', False) or data.get('erc', False):
            bp_goal = {"systolic": {"min": None, "optimal": 130}, "diastolic": {"min": None, "optimal": 80}, "unit": "mmHg"}
        
        # Metas de HbA1c para pacientes con diabetes
        if data.get('dm2', False):
            hba1c_goal = {"min": None, "optimal": 7.0, "unit": "%"}
            if data.get('edad', 0) > 65 or data.get('fragil', False):
                hba1c_goal = {"min": None, "optimal": 8.0, "unit": "%"}
        
        # Evaluar cumplimiento de metas
        goals_status = {}
        
        # Evaluar LDL
        if ldl_goal and 'ldl' in data:
            ldl = float(data.get('ldl', 0))
            if ldl <= ldl_goal["optimal"]:
                goals_status["ldl"] = "sobresaliente"
            elif ldl_goal["min"] and ldl <= ldl_goal["min"]:
                goals_status["ldl"] = "satisfactorio"
            else:
                goals_status["ldl"] = "no cumple"
        
        # Evaluar presión arterial
        if bp_goal and 'pa_sistolica' in data and 'pa_diastolica' in data:
            systolic = float(data.get('pa_sistolica', 0))
            diastolic = float(data.get('pa_diastolica', 0))
            
            if systolic <= bp_goal["systolic"]["optimal"] and diastolic <= bp_goal["diastolic"]["optimal"]:
                goals_status["bp"] = "sobresaliente"
            else:
                goals_status["bp"] = "no cumple"
        
        # Evaluar HbA1c
        if hba1c_goal and 'hba1c' in data:
            hba1c = float(data.get('hba1c', 0))
            if hba1c <= hba1c_goal["optimal"]:
                goals_status["hba1c"] = "sobresaliente"
            else:
                goals_status["hba1c"] = "no cumple"
        
        return jsonify({
            "success": True,
            "goals": {
                "ldl": ldl_goal,
                "bp": bp_goal,
                "hba1c": hba1c_goal
            },
            "status": goals_status,
            "riskLevel": risk_level.capitalize()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error al evaluar metas terapéuticas: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route('/followup/schedule', methods=['POST'])
def schedule_followup():
    """Endpoint para programar seguimiento médico y de laboratorios."""
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No se proporcionaron datos"}), 400
        
        # Obtener el nivel de riesgo (calcularlo si no está presente)
        risk_level = data.get('riskLevel', '').lower()
        if not risk_level:
            # Calcular TFG
            tfg = None
            if 'creatinina' in data and 'peso' in data and 'edad' in data and 'sexo' in data:
                tfg = calcular_tfg(
                    edad=int(data.get('edad', 0)), 
                    peso=float(data.get('peso', 70)), 
                    creatinina=float(data.get('creatinina', 1.0)),
                    sexo=data.get('sexo', 'm')
                )
            
            # Clasificar riesgo
            risk_level = clasificar_riesgo_cv(data, tfg)
        
        # Determinar intervalos según nivel de riesgo
        today = datetime.now()
        
        if risk_level == 'bajo':
            lab_interval = 12  # meses
            appointment_interval = 12  # meses
        elif risk_level == 'moderado':
            lab_interval = 6
            appointment_interval = 6
        elif risk_level == 'alto':
            lab_interval = 3
            appointment_interval = 3
        elif risk_level == 'muy alto':
            lab_interval = 2
            appointment_interval = 1
        else:  # Por defecto
            lab_interval = 6
            appointment_interval = 6
        
        # Ajustar para pacientes con condiciones especiales
        if data.get('dm2', False) and appointment_interval > 3:
            appointment_interval = 3
            
        if data.get('erc', False) and appointment_interval > 3:
            appointment_interval = 3
            
        if data.get('tfg', 0) < 30 and appointment_interval > 1:
            appointment_interval = 1
            lab_interval = 1
        
        # Calcular fechas de próximas visitas
        next_lab_date = today + timedelta(days=lab_interval * 30)
        next_appointment = today + timedelta(days=appointment_interval * 30)
        
        # Formatear fechas para respuesta
        next_lab_date_str = next_lab_date.strftime('%d/%m/%Y')
        next_appointment_str = next_appointment.strftime('%d/%m/%Y')
        
        return jsonify({
            "success": True,
            "nextLabDate": next_lab_date_str,
            "nextAppointment": next_appointment_str,
            "labInterval": lab_interval,
            "appointmentInterval": appointment_interval,
            "riskLevel": risk_level.capitalize()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error al programar seguimiento: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route('/data/parse', methods=['POST'])
def parse_file_data():
    """Endpoint para extraer datos de archivos PDF o TXT."""
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No se proporcionó archivo"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "Nombre de archivo vacío"}), 400
            
        # Verificar extensión del archivo
        allowed_extensions = {'pdf', 'txt'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({"success": False, "error": "Formato de archivo no permitido"}), 400
        
        # Guardar archivo temporalmente
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp', file.filename)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        file.save(temp_path)
        
        # Extraer texto del archivo según tipo
        extracted_text = ""
        if file_ext == 'pdf':
            from app.parsers.pdf_extractor import extract_text_from_pdf
            extracted_text = extract_text_from_pdf(temp_path)
        else:
            from app.parsers.txt_extractor import extract_text_from_txt
            extracted_text = extract_text_from_txt(temp_path)
        
        # Analizar texto para extraer datos
        parsed_data = parse_lab_results(extracted_text)
        
        # Si no hay resultados con el parser, intentar con IA
        if not parsed_data or 'results' not in parsed_data or len(parsed_data['results']) == 0:
            try:
                gemini = GeminiClient()
                parsed_data = gemini.extract_lab_results(extracted_text)
            except Exception as e:
                current_app.logger.error(f"Error al usar IA para extraer resultados: {str(e)}")
                # Continuamos con los resultados que tengamos (aunque sean vacíos)
        
        # Extraer datos de paciente y factores de riesgo
        patient_data = parsed_data.get('patient_data', {})
        factores_riesgo = []
        
        if patient_data.get('diabetes', False):
            factores_riesgo.append('diabetes')
        if patient_data.get('hipertension', False):
            factores_riesgo.append('hipertensión')
        if patient_data.get('dislipidemia', False):
            factores_riesgo.append('dislipidemia')
        
        # Eliminar archivo temporal
        try:
            os.remove(temp_path)
        except:
            pass
        
        return jsonify({
            "success": True,
            "nombre": patient_data.get('nombre', ''),
            "edad": patient_data.get('edad', ''),
            "sexo": patient_data.get('sexo', ''),
            "factoresRiesgo": factores_riesgo,
            "resultados": parsed_data.get('results', {}),
            "source": file.filename
        })
        
    except Exception as e:
        current_app.logger.error(f"Error al analizar archivo: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route('/test')
def test():
    return {"message": "API funcionando correctamente"}
