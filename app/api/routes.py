from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import tempfile
from datetime import datetime
import traceback

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.api.gemini_helpers import get_gemini_client, PromptStrategy
from app.parsers.pdf_extractor import extract_pdf_content
from app.parsers.txt_extractor import parse_txt_file
from app.parsers.lab_parser import LabParser
from app.logic.patient_eval import PatientEvaluator
from app.api.report_generator import AdvancedReportGenerator
from app.utils.validators import validate_file_upload, validate_patient_data
from app.utils.cache_manager import cache_result, get_cached_result
from app.extensions import db

bp = Blueprint('api', __name__)

# Configuración
ALLOWED_EXTENSIONS = {'pdf', 'txt'}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15MB

limiter = Limiter(
    app=current_app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "10 per minute"],
    storage_uri="redis://localhost:6379" if os.getenv('REDIS_URL') else "memory://"
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload', methods=['POST'])
def upload_file():
    """Endpoint para cargar archivos de laboratorio"""
    try:
        # Validar archivo
        if 'file' not in request.files:
            return jsonify({"error": "No se encontró archivo"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No se seleccionó archivo"}), 400
            
        if not allowed_file(file.filename):
            return jsonify({"error": f"Tipo de archivo no permitido. Use: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
        
        # Validar tamaño
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({"error": f"Archivo muy grande. Máximo: {MAX_FILE_SIZE/1024/1024:.1f}MB"}), 400
        
        # Procesar archivo
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as tmp_file:
            file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # Extraer contenido según tipo
            if file_ext == 'pdf':
                content = extract_pdf_content(tmp_path)
            else:  # txt
                content = parse_txt_file(tmp_path)
            
            # Usar cliente Gemini mejorado para extraer valores
            gemini_client = get_gemini_client()
            extraction_result = gemini_client.extract_lab_values(content)
            
            if extraction_result['success'] and extraction_result.get('values'):
                lab_values = extraction_result['values']
            else:
                # Fallback: parser tradicional
                parser = LabParser()
                lab_values = parser.parse_labs(content)
            
            return jsonify({
                "success": True,
                "filename": filename,
                "content": content[:500] + "..." if len(content) > 500 else content,
                "lab_values": lab_values,
                "extraction_method": extraction_result.get('source', 'traditional_parser')
            })
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        current_app.logger.error(f"Error procesando archivo: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"Error procesando archivo: {str(e)}"}), 500

@bp.route('/analyze', methods=['POST'])
def analyze_patient():
    """Endpoint para análisis completo del paciente"""
    try:
        data = request.get_json()
        
        # Validar datos
        validation_error = validate_patient_data(data)
        if validation_error:
            return jsonify({"error": validation_error}), 400
        
        # Verificar caché
        cache_key = f"analysis_{data.get('patient_id', 'anonymous')}_{datetime.now().strftime('%Y%m%d')}"
        cached_result = get_cached_result(cache_key)
        if cached_result:
            return jsonify(cached_result)
        
        # Preparar datos del paciente
        patient_data = {
            "age": data.get('age'),
            "sex": data.get('sex'),
            "weight": data.get('weight'),
            "height": data.get('height'),
            "creatinine": data.get('creatinine'),
            "lab_values": data.get('lab_values', {}),
            "medical_history": data.get('medical_history', []),
            "medications": data.get('medications', [])
        }
        
        # Usar evaluador tradicional para cálculos básicos
        evaluator = PatientEvaluator()
        basic_evaluation = evaluator.evaluate(patient_data)
        
        # Enriquecer con análisis de Gemini
        gemini_client = get_gemini_client()
        ai_analysis = gemini_client.analyze_patient(
            patient_data, 
            strategy=PromptStrategy.MEDICAL_EXPERT
        )
        
        # Generar objetivos terapéuticos
        goals_result = gemini_client.generate_therapeutic_goals(
            patient_data,
            ai_analysis.get('analysis', '')
        )
        
        # Combinar resultados
        result = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "patient_id": data.get('patient_id', 'anonymous'),
            "basic_evaluation": basic_evaluation,
            "ai_analysis": ai_analysis,
            "therapeutic_goals": goals_result,
            "recommendations": _generate_recommendations(basic_evaluation, ai_analysis)
        }
        
        # Cachear resultado
        cache_result(cache_key, result, ttl=3600)  # 1 hora
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error en análisis: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"Error en análisis: {str(e)}"}), 500

@bp.route('/generate-report', methods=['POST'])
def generate_report():
    """Endpoint para generar informe completo"""
    try:
        data = request.get_json()
        
        if not data.get('analysis_id') and not data.get('patient_data'):
            return jsonify({"error": "Se requiere analysis_id o patient_data"}), 400
        
        patient_data = request.json.get('patient')
        
        # AÑADIR validación de datos críticos
        required_fields = ['nombre', 'edad', 'creatinina', 'diagnosticos']
        missing = [f for f in required_fields if not patient_data.get(f)]
        if missing:
            return jsonify({
                'success': False,
                'error': f'Campos requeridos faltantes: {", ".join(missing)}'
            }), 400
        
        # AÑADIR prompts mejorados con chain-of-thought
        enhanced_prompt = f"""
        Analiza paso a paso los siguientes datos del paciente con ERC:
        
        1. DATOS BÁSICOS:
        - Nombre: {patient_data['nombre']}
        - Edad: {patient_data['edad']} años
        - TFG: {patient_data.get('tfg', 'No calculado')}
        
        2. RAZONAMIENTO CLÍNICO:
        a) Primero, clasifica la etapa de ERC según TFG
        b) Luego, evalúa factores de riesgo cardiovascular
        c) Después, determina metas terapéuticas específicas
        d) Finalmente, genera recomendaciones personalizadas
        
        3. FORMATO REQUERIDO:
        - NO uses información externa o guías web
        - Basa todo en los datos proporcionados
        - Sé específico con valores y rangos
        - Evita recomendaciones genéricas
        """
        
        # Validar respuesta para evitar alucinaciones
        response = gemini_client.generate_report(enhanced_prompt)
        
        # AÑADIR verificación de calidad
        quality_checks = [
            'TFG' in response,  # Debe mencionar TFG
            patient_data['nombre'] in response,  # Debe usar nombre real
            len(response) > 500,  # Longitud mínima
            'http' not in response.lower()  # No referencias web
        ]
        
        if not all(quality_checks):
            logger.warning("Informe de baja calidad detectado")
            # Reintentar con prompt más estricto
        
        # Generar informe
        generator = AdvancedReportGenerator()
        report_data = generator.generate_report(data)
        
        return jsonify({
            "success": True,
            "report": report_data,
            "download_url": f"/api/download-report/{report_data['report_id']}"
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generando informe: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"Error generando informe: {str(e)}"}), 500

@bp.route('/validate-gemini', methods=['GET'])
def validate_gemini():
    """Endpoint para validar conexión con Gemini"""
    try:
        gemini_client = get_gemini_client()
        validation_result = gemini_client.validate_connection()
        
        return jsonify(validation_result)
        
    except Exception as e:
        return jsonify({
            "connected": False,
            "error": str(e)
        }), 500

@bp.route('/health')
def health_check():
    """Endpoint para verificar el estado de la API"""
    try:
        # Verificar servicios
        gemini_client = get_gemini_client()
        gemini_status = gemini_client.validate_connection()
        
        return jsonify({
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "api": "healthy",
                "gemini": "healthy" if gemini_status.get('connected') else "degraded",
                "fallback": "available" if gemini_status.get('fallback_available') else "unavailable"
            },
            "message": "ERC Insight API está funcionando correctamente"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@bp.route('/save_report', methods=['POST'])
def save_report():
    """Endpoint para guardar informes en la base de datos"""
    try:
        data = request.get_json()
        
        if not data.get('patient_id') or not data.get('report_content'):
            return jsonify({"error": "Se requiere patient_id y report_content"}), 400
        
        from app.models.report import Report
        from app.models.patient import Patient
        
        # Verificar si el paciente existe, si no, crearlo
        patient = Patient.query.filter_by(document_id=data.get('patient_id')).first()
        
        if not patient:
            # Crear un nuevo paciente
            patient = Patient(
                document_id=data.get('patient_id'),
                document_type='CC',  # Por defecto
                first_name=data.get('patient_name', 'Paciente'),
                last_name='',
                birth_date=datetime.now(),  # Fecha por defecto
                gender='U'  # Desconocido por defecto
            )
            db.session.add(patient)
            db.session.commit()
        
        # Crear el informe
        report = Report(
            patient_id=patient.id,
            title=f"Informe clínico generado el {datetime.now().strftime('%Y-%m-%d')}",
            content=data.get('report_content'),
            report_type='ai_generated',
            created_by='system'  # O usar el ID del usuario autenticado si está disponible
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Informe guardado correctamente",
            "report_id": report.id
        })
        
    except Exception as e:
        current_app.logger.error(f"Error guardando informe: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"Error guardando informe: {str(e)}"}), 500

@bp.route('/parse_document', methods=['POST'])
@limiter.limit("5 per minute")  # Límite específico para este endpoint
def parse_document():
    """Endpoint para analizar documentos de laboratorio (PDF, TXT)"""
    try:
        # Validar archivo
        if 'file' not in request.files:
            return jsonify({"error": "No se encontró archivo"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No se seleccionó archivo"}), 400
            
        if not allowed_file(file.filename):
            return jsonify({"error": f"Tipo de archivo no permitido. Use: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
        
        # Validar tamaño
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({"error": f"Archivo muy grande. Máximo: {MAX_FILE_SIZE/1024/1024:.1f}MB"}), 400
        
        # Procesar archivo
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as tmp_file:
            file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # Extraer contenido según tipo
            if file_ext == 'pdf':
                content = extract_pdf_content(tmp_path)
            else:  # txt
                content = parse_txt_file(tmp_path)
            
            return jsonify({
                "success": True,
                "filename": filename,
                "content": content[:500] + "..." if len(content) > 500 else content
            })
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        current_app.logger.error(f"Error procesando archivo: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"Error procesando archivo: {str(e)}"}), 500

def _generate_recommendations(basic_eval, ai_analysis):
    """Genera recomendaciones combinando evaluación básica y análisis IA"""
    recommendations = []
    
    # Recomendaciones basadas en TFG
    if basic_eval.get('tfg', 0) < 60:
        recommendations.append({
            "priority": "high",
            "category": "renal",
            "recommendation": "Referir a nefrología para evaluación especializada"
        })
    
    # Recomendaciones basadas en IA (si está disponible)
    if ai_analysis.get('success') and 'analysis' in ai_analysis:
        # Extraer recomendaciones del texto de IA
        ai_text = ai_analysis['analysis']
        if 'RECOMENDACIONES' in ai_text:
            recommendations.append({
                "priority": "medium",
                "category": "ai_generated",
                "recommendation": "Ver recomendaciones detalladas en el análisis de IA"
            })
    
    # Recomendaciones estándar
    recommendations.extend([
        {
            "priority": "medium",
            "category": "lifestyle",
            "recommendation": "Mantener dieta baja en sodio (<2g/día)"
        },
        {
            "priority": "medium",
            "category": "monitoring",
            "recommendation": "Control de laboratorio en 3-6 meses"
        }
    ])
    
    return recommendations