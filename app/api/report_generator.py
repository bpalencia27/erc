"""
Módulo de integración con la API de Gemini para generar informes avanzados
"""
import os
import logging
import json
from datetime import datetime, timedelta
from app.api.gemini_client import GeminiClient
from app.logic.patient_eval import determinar_etapa_erc, clasificar_riesgo_cv

class AdvancedReportGenerator:
    """
    Generador de informes médicos avanzados utilizando la API de Gemini.
    Esta clase coordina la generación de informes basados en IA.
    """
    
    def __init__(self):
        """Inicializa el generador de informes."""
        self.gemini_client = GeminiClient()
        self.logger = logging.getLogger(__name__)
    
    def generate_report(self, patient_data, base_report=None):
        """
        Genera un informe médico completo utilizando la API de Gemini.
        
        Args:
            patient_data (dict): Datos del paciente
            base_report (str, optional): Informe base generado con la lógica convencional
            
        Returns:
            str: Informe HTML generado
        """
        if not base_report:
            base_report = self._generate_base_report(patient_data)
        
        try:
            # Usamos el cliente de Gemini para enriquecer el informe
            enriched_report = self.gemini_client.generate_report(patient_data, base_report)
            return enriched_report
        except Exception as e:
            self.logger.error(f"Error generando informe avanzado: {str(e)}")
            # Si falla, devolvemos el informe base
            return base_report
    
    def process_patient_data(self, patient_data, labs_data):
        """
        Procesa los datos del paciente y genera un informe médico avanzado.
        
        Args:
            patient_data (dict): Datos del paciente
            labs_data (dict): Resultados de laboratorio
            
        Returns:
            dict: Resultado con el informe y metadatos
        """
        try:
            # Preparar el payload utilizando los datos combinados
            payload = self._prepare_gemini_payload(patient_data, labs_data)
            
            # Generar el informe avanzado usando el cliente Gemini
            report_text = self.gemini_client.process_advanced_evaluation(payload)
            
            # Guardar metadatos relevantes
            result = {
                "report": report_text,
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "report_type": "advanced_erc",
                    "tfg": payload.get("evaluacion_diagnosticos", {}).get("tfg_valor", 0),
                    "erc_stage": payload.get("evaluacion_diagnosticos", {}).get("erc_estadio", "No determinado"),
                    "cv_risk": payload.get("evaluacion_diagnosticos", {}).get("riesgo_cardiovascular", "No determinado")
                }
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error al generar informe avanzado: {str(e)}")
            return {
                "report": "Error al generar el informe. Por favor, inténtelo de nuevo.",
                "error": str(e)
            }
    
    def _prepare_gemini_payload(self, patient_data, labs_data):
        """
        Prepara el payload para la API de Gemini en el formato requerido.
        
        Args:
            patient_data (dict): Datos del paciente
            labs_data (dict): Resultados de laboratorio
            
        Returns:
            dict: Payload estructurado para Gemini
        """
        # Calcular TFG si tenemos los datos necesarios
        tfg = None
        if all(k in patient_data for k in ['edad', 'peso', 'creatinina']):
            from app.logic.patient_eval import calcular_tfg
            tfg = calcular_tfg(
                patient_data.get('edad', 0),
                patient_data.get('peso', 0),
                patient_data.get('creatinina', 1.0),
                patient_data.get('sexo', 'm')
            )
        
        # Determinar etapa ERC y riesgo cardiovascular
        etapa_erc = "No determinada"
        riesgo_cv = "No determinado"
        
        if tfg:
            etapa_erc = determinar_etapa_erc(tfg)
            # Factores de riesgo básicos
            risk_factors = {
                "diabetes": patient_data.get('diabetes', False),
                "hipertension": patient_data.get('hipertension', False),
                "fumador": patient_data.get('fumador', False),
                "edad": patient_data.get('edad', 0)
            }
            # Enriquecer con datos calculados
            enriched = self._enrich_data(patient_data)
            risk_factors.update(enriched)
            
            # Calcular riesgo cardiovascular
            riesgo_cv = clasificar_riesgo_cv(risk_factors, tfg)
        
        # Construir las metas terapéuticas
        metas_terapeuticas = self._build_therapeutic_goals(patient_data, labs_data, tfg, riesgo_cv)
        
        # Construir el plan de seguimiento
        plan_seguimiento = self._build_follow_up_plan(etapa_erc, riesgo_cv)
        
        # Crear el payload estructurado
        payload = {
            "paciente": {
                "nombre": patient_data.get('nombre', 'Paciente sin nombre'),
                "edad": patient_data.get('edad', 'N/A'),
                "sexo": patient_data.get('sexo', 'N/A'),
                "peso": patient_data.get('peso', 'N/A'),
                "talla": patient_data.get('altura', 'N/A'),
                "imc": enriched.get('imc', 'N/A') if 'imc' in enriched else 'N/A'
            },
            "laboratorios": labs_data,
            "evaluacion_diagnosticos": {
                "tfg_valor": tfg,
                "erc_estadio": etapa_erc,
                "riesgo_cardiovascular": riesgo_cv,
                "comorbilidades": self._get_comorbidities(patient_data)
            },
            "metas_terapeuticas": metas_terapeuticas,
            "plan_seguimiento": plan_seguimiento
        }
        
        return payload
    
    def _get_comorbidities(self, patient_data):
        """Extrae las comorbilidades del paciente."""
        comorbilidades = []
        
        if patient_data.get('diabetes', False):
            comorbilidades.append("Diabetes Mellitus")
        if patient_data.get('hipertension', False):
            comorbilidades.append("Hipertensión Arterial")
        if patient_data.get('dislipidemia', False) or (patient_data.get('colesterol_total', 0) > 200):
            comorbilidades.append("Dislipidemia")
        if patient_data.get('obesidad', False) or (patient_data.get('imc', 0) >= 30):
            comorbilidades.append("Obesidad")
        if patient_data.get('fumador', False):
            comorbilidades.append("Tabaquismo")
            
        return comorbilidades
    
    def _build_therapeutic_goals(self, patient_data, labs_data, tfg, riesgo_cv):
        """Construye las metas terapéuticas basadas en los datos del paciente."""
        metas = []
        
        # Meta de presión arterial según etapa ERC y riesgo CV
        pa_sistolica = patient_data.get('pa_sistolica', 0)
        pa_diastolica = patient_data.get('pa_diastolica', 0)
        
        meta_pa = "<130/80" if tfg and tfg < 60 else "<140/90"
        cumple_pa = (pa_sistolica < 130 and pa_diastolica < 80) if tfg and tfg < 60 else (pa_sistolica < 140 and pa_diastolica < 90)
        
        metas.append({
            "parametro": "Presión Arterial",
            "valor_actual": f"{pa_sistolica}/{pa_diastolica}",
            "meta": meta_pa,
            "cumple": cumple_pa
        })
        
        # Meta de glucemia si tiene diabetes
        if patient_data.get('diabetes', False):
            glucemia = labs_data.get('glucemia', 0)
            hba1c = labs_data.get('hba1c', 0)
            
            metas.append({
                "parametro": "Glucemia en ayunas",
                "valor_actual": glucemia,
                "meta": "<126 mg/dL",
                "cumple": glucemia < 126
            })
            
            metas.append({
                "parametro": "HbA1c",
                "valor_actual": hba1c,
                "meta": "<7.0%",
                "cumple": hba1c < 7.0
            })
        
        # Meta de LDL según riesgo CV
        colesterol_ldl = labs_data.get('ldl', 0)
        
        if riesgo_cv == "muy_alto":
            meta_ldl = "<55 mg/dL"
            cumple_ldl = colesterol_ldl < 55
        elif riesgo_cv == "alto":
            meta_ldl = "<70 mg/dL"
            cumple_ldl = colesterol_ldl < 70
        else:
            meta_ldl = "<100 mg/dL"
            cumple_ldl = colesterol_ldl < 100
            
        metas.append({
            "parametro": "Colesterol LDL",
            "valor_actual": colesterol_ldl,
            "meta": meta_ldl,
            "cumple": cumple_ldl
        })
        
        return metas
    
    def _build_follow_up_plan(self, etapa_erc, riesgo_cv, metas_evaluacion=None):
        """Construye el plan de seguimiento según la etapa ERC y riesgo CV."""
        # Calcular fechas de seguimiento
        hoy = datetime.now()
        
        # Seguimiento según etapa ERC
        if etapa_erc in ["g4", "g5"]:
            labs_follow_up = hoy + timedelta(days=30)  # 1 mes
            consult_follow_up = hoy + timedelta(days=30)
        elif etapa_erc in ["g3a", "g3b"]:
            labs_follow_up = hoy + timedelta(days=90)  # 3 meses
            consult_follow_up = hoy + timedelta(days=90)
        else:
            labs_follow_up = hoy + timedelta(days=180)  # 6 meses
            consult_follow_up = hoy + timedelta(days=180)
        
        # Ajustar según riesgo CV
        if riesgo_cv == "muy_alto" and etapa_erc not in ["g4", "g5"]:
            labs_follow_up = hoy + timedelta(days=60)  # 2 meses
            consult_follow_up = hoy + timedelta(days=60)
        
        # Crear estructura extendida de respuesta
        result = {
            "laboratorios": labs_follow_up.strftime("%d/%m/%Y"),
            "consulta_control": consult_follow_up.strftime("%d/%m/%Y"),
            "laboratorios_detallados": [
                {"nombre": "Creatinina sérica", "fecha": labs_follow_up.strftime("%d/%m/%Y")},
                {"nombre": "Nitrógeno ureico", "fecha": labs_follow_up.strftime("%d/%m/%Y")},
                {"nombre": "Perfil lipídico", "fecha": labs_follow_up.strftime("%d/%m/%Y")},
            ],
            "recomendacion": "Continuar con el tratamiento actual y seguimiento según plan.",
            "nivel_cumplimiento": "regular" if metas_evaluacion and metas_evaluacion.get("porcentaje_cumplimiento", 0) < 70 else "bueno"
        }
        
        return result
    
    def _generate_base_report(self, patient_data):
        """
        Genera un informe base simple cuando no se proporciona uno.
        
        Args:
            patient_data (dict): Datos del paciente
            
        Returns:
            str: Informe HTML básico
        """
        # Extraer datos básicos
        nombre = patient_data.get('nombre', 'Paciente sin nombre')
        edad = patient_data.get('edad', 'N/A')
        sexo = patient_data.get('sexo', 'N/A')
        
        # Calcular algunos valores básicos si están disponibles
        tfg = None
        etapa_erc = "No determinada"
        riesgo_cv = "No determinado"
        
        if all(k in patient_data for k in ['edad', 'peso', 'creatinina']):
            from app.logic.patient_eval import calcular_tfg
            tfg = calcular_tfg(
                patient_data.get('edad', 0),
                patient_data.get('peso', 0),
                patient_data.get('creatinina', 1.0),
                patient_data.get('sexo', 'm')
            )
            
            if tfg:
                etapa_erc = determinar_etapa_erc(tfg)
                # Creamos un conjunto básico de factores de riesgo
                risk_factors = {
                    "diabetes": patient_data.get('diabetes', False),
                    "hipertension": patient_data.get('hipertension', False),
                    "fumador": patient_data.get('fumador', False),
                    "edad": patient_data.get('edad', 0)
                }
                # Enriquecemos con más datos si están disponibles
                enriched = self._enrich_data(patient_data)
                risk_factors.update(enriched)
                
                # Calculamos el riesgo cardiovascular
                riesgo_cv = clasificar_riesgo_cv(risk_factors, tfg)
        
        # Generar informe HTML básico
        return f"""
        <div class="report-container">
            <h1>Informe Médico: {nombre}</h1>
            <div class="patient-data">
                <p><strong>Edad:</strong> {edad} años</p>
                <p><strong>Sexo:</strong> {sexo}</p>
            </div>
            
            <div class="medical-evaluation">
                <h2>Evaluación Renal Básica</h2>
                
                <div class="results">
                    <p><strong>Tasa de Filtración Glomerular:</strong> {tfg if tfg else 'No calculada'} ml/min/1.73m</p>
                    <p><strong>Etapa ERC:</strong> {etapa_erc}</p>
                    <p><strong>Riesgo Cardiovascular:</strong> {riesgo_cv}</p>
                </div>
            </div>
            
            <div class="footer">
                <p>Informe generado el {datetime.now().strftime('%d/%m/%Y')}</p>
                <p class="note">Este es un informe básico. Para un análisis completo, consulte a su médico.</p>
            </div>
        </div>
        """
    
    def _enrich_data(self, patient_data):
        """
        Enriquece los datos del paciente con cálculos adicionales.
        
        Args:
            patient_data (dict): Datos del paciente
            
        Returns:
            dict: Datos enriquecidos
        """
        enriched = {}
        
        # Calcular IMC si tenemos peso y altura
        if 'peso' in patient_data and 'altura' in patient_data:
            peso = float(patient_data['peso'])
            altura_m = float(patient_data['altura']) / 100  # convertir cm a m
            if altura_m > 0:
                imc = peso / (altura_m * altura_m)
                enriched['imc'] = round(imc, 2)
                enriched['obesidad'] = imc >= 30
        
        # Evaluar dislipidemia
        if any(lab in patient_data for lab in ['colesterol_total', 'ldl', 'hdl', 'trigliceridos']):
            col_total = float(patient_data.get('colesterol_total', 0))
            ldl = float(patient_data.get('ldl', 0))
            enriched['dislipidemia'] = col_total > 200 or ldl > 130
        
        return enriched
    
    def generate_pdf(self, report_data):
        """
        Genera un archivo PDF a partir del informe.
        
        Args:
            report_data (dict): Datos del informe
            
        Returns:
            str: Ruta al archivo PDF generado
        """
        # Esta función se implementaría para convertir el informe a PDF
        # Por ahora devolvemos solo un mensaje
        return "PDF generation not implemented yet"
