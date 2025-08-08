"""
Módulo de integración con la API de Gemini para generar informes avanzados
"""
import os
import logging
import json
from datetime import datetime
from app.api.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class AdvancedReportGenerator:
    """
    Clase para generar informes médicos avanzados utilizando 
    el motor de lógica de negocio y la API de Gemini.
    """
    
    def __init__(self):
        """Inicializa el generador de informes."""
        self.gemini_client = GeminiClient()
    
    def process_patient_data(self, patient_data, labs_data):
        """
        Procesa los datos del paciente y genera un informe médico avanzado.
        
        Args:
            patient_data (dict): Datos del paciente
            labs_data (dict): Resultados de laboratorio
            
        Returns:
            dict: Resultado con el informe y metadatos
        """
        from app.logic.advanced_patient_eval import generar_payload_gemini, evaluar_cumplimiento_metas
        
        try:
            # Generar el payload usando la lógica de negocio avanzada
            payload = generar_payload_gemini(patient_data, labs_data)
            
            # Evaluar cumplimiento de metas terapéuticas
            etapa_erc = payload["evaluacion_diagnosticos"]["erc_estadio"]
            riesgo_cv = payload["evaluacion_diagnosticos"]["riesgo_cardiovascular"]
            
            # Evaluar metas y calcular porcentaje de cumplimiento
            if "metas_terapeuticas" in payload:
                metas_cumplidas = sum(1 for meta in payload["metas_terapeuticas"] if meta.get("cumple", False))
                total_metas = len(payload["metas_terapeuticas"])
                porcentaje_cumplimiento = (metas_cumplidas / total_metas * 100) if total_metas > 0 else 50
                
                metas_evaluacion = {
                    "metas_cumplidas": metas_cumplidas,
                    "total_metas": total_metas,
                    "porcentaje_cumplimiento": porcentaje_cumplimiento
                }
            else:
                metas_evaluacion = None
            
            # Generar plan de seguimiento detallado
            plan_seguimiento = self._build_follow_up_plan(etapa_erc, riesgo_cv, metas_evaluacion)
            
            # Añadir el plan de seguimiento al payload
            payload["plan_seguimiento"] = plan_seguimiento
            
            # Generar el informe usando la API de Gemini
            report_text = self.gemini_client.process_advanced_evaluation(payload)
            
            # Guardar metadatos relevantes
            result = {
                "report": report_text,
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "report_type": "advanced_erc",
                    "tfg": payload["evaluacion_diagnosticos"]["tfg_valor"],
                    "erc_stage": etapa_erc,
                    "cv_risk": riesgo_cv,
                    "plan_seguimiento": plan_seguimiento
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error al generar informe avanzado: {str(e)}")
            return {
                "report": "Error al generar el informe. Por favor, inténtelo de nuevo.",
                "error": str(e)
            }
    
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
    
    def _build_follow_up_plan(self, etapa_erc, riesgo_cv, metas_evaluacion=None):
        """
        Construye el plan de seguimiento según la etapa ERC, riesgo CV y cumplimiento de metas.
        Implementa el "segundo camino" con plan detallado por tipo de laboratorio.
        
        Args:
            etapa_erc (str): Etapa de ERC (g1, g2, g3a, g3b, g4, g5)
            riesgo_cv (str): Nivel de riesgo cardiovascular (bajo, moderado, alto, muy_alto)
            metas_evaluacion (dict, opcional): Evaluación de cumplimiento de metas terapéuticas
                con formato {"metas_cumplidas": int, "total_metas": int, "porcentaje_cumplimiento": float}
        
        Returns:
            dict: Plan de seguimiento con estructura:
                {
                    "laboratorios": str (fecha del próximo control de laboratorios más cercano),
                    "consulta_control": str (fecha de la próxima consulta médica),
                    "laboratorios_detallados": dict (mapa de fechas a lista de laboratorios),
                    "recomendacion": str (texto con recomendaciones de seguimiento),
                    "nivel_cumplimiento": str (bueno, regular, deficiente)
                }
        """
        from datetime import datetime, timedelta
        
        # Calcular fechas de seguimiento
        hoy = datetime.now()
        
        # Determinar el nivel de cumplimiento de metas (si está disponible)
        nivel_cumplimiento = "regular"
        if metas_evaluacion and 'porcentaje_cumplimiento' in metas_evaluacion:
            porcentaje = metas_evaluacion['porcentaje_cumplimiento']
            if porcentaje >= 80:
                nivel_cumplimiento = "bueno"
            elif porcentaje <= 40:
                nivel_cumplimiento = "deficiente"
        
        # SEGUNDO CAMINO: Plan detallado por tipo de laboratorio
        plan_laboratorios = {}
        
        # Determinar la frecuencia base según etapa ERC
        if etapa_erc in ["g4", "g5"]:
            # Para G4-G5: seguimiento mensual (mayor frecuencia)
            frecuencia_base = 30  # 1 mes en días
            
            # Laboratorios específicos para ERC avanzada
            plan_laboratorios = {
                "bioquímica_general": hoy + timedelta(days=30),
                "hemograma": hoy + timedelta(days=30),
                "perfil_lipídico": hoy + timedelta(days=90),
                "hemoglobina_glicosilada": hoy + timedelta(days=90),
                "función_renal": hoy + timedelta(days=30),
                "albuminuria": hoy + timedelta(days=30),
                "electrolitos": hoy + timedelta(days=30),
                "calcio_fósforo": hoy + timedelta(days=30),
                "pth": hoy + timedelta(days=90)
            }
            
        elif etapa_erc in ["g3a", "g3b"]:
            # Para G3: seguimiento trimestral
            frecuencia_base = 90  # 3 meses en días
            
            plan_laboratorios = {
                "bioquímica_general": hoy + timedelta(days=90),
                "hemograma": hoy + timedelta(days=90),
                "perfil_lipídico": hoy + timedelta(days=90),
                "hemoglobina_glicosilada": hoy + timedelta(days=90),
                "función_renal": hoy + timedelta(days=90),
                "albuminuria": hoy + timedelta(days=90),
                "electrolitos": hoy + timedelta(days=90),
                "calcio_fósforo": hoy + timedelta(days=180),
                "pth": hoy + timedelta(days=180)
            }
            
        else:  # G1, G2
            # Para G1-G2: seguimiento semestral
            frecuencia_base = 180  # 6 meses en días
            
            plan_laboratorios = {
                "bioquímica_general": hoy + timedelta(days=180),
                "hemograma": hoy + timedelta(days=180),
                "perfil_lipídico": hoy + timedelta(days=180),
                "hemoglobina_glicosilada": hoy + timedelta(days=180),
                "función_renal": hoy + timedelta(days=180),
                "albuminuria": hoy + timedelta(days=180),
                "electrolitos": hoy + timedelta(days=180),
                "calcio_fósforo": hoy + timedelta(days=365),
                "pth": hoy + timedelta(days=365)
            }
        
        # Ajustar según riesgo CV
        if riesgo_cv == "muy_alto" and etapa_erc not in ["g4", "g5"]:
            # Aumentar frecuencia para riesgo muy alto
            frecuencia_base = min(frecuencia_base, 60)  # Máximo 2 meses
            
            # Actualizar fechas específicas
            for key in plan_laboratorios:
                if "lipídico" in key or "glicosilada" in key:
                    plan_laboratorios[key] = hoy + timedelta(days=60)
        
        # Ajustar según nivel de cumplimiento
        if nivel_cumplimiento == "deficiente":
            # Si el cumplimiento es deficiente, acortar el tiempo de seguimiento
            factor_ajuste = 0.5  # Reducir a la mitad
            for key in plan_laboratorios:
                dias_original = (plan_laboratorios[key] - hoy).days
                dias_ajustados = max(30, int(dias_original * factor_ajuste))
                plan_laboratorios[key] = hoy + timedelta(days=dias_ajustados)
        
        # Determinar la fecha más próxima para laboratorios
        fecha_proximos_labs = min(plan_laboratorios.values())
        
        # Programar consulta 7 días después de los laboratorios
        fecha_consulta = fecha_proximos_labs + timedelta(days=7)
        
        # Agrupar laboratorios por fecha
        labs_agrupados = {}
        for tipo, fecha in plan_laboratorios.items():
            fecha_str = fecha.strftime("%d/%m/%Y")
            if fecha_str not in labs_agrupados:
                labs_agrupados[fecha_str] = []
            labs_agrupados[fecha_str].append(tipo.replace("_", " ").title())
        
        # Crear texto de recomendación
        recomendacion = "Se recomienda seguimiento "
        if etapa_erc in ["g4", "g5"]:
            recomendacion += "mensual "
        elif etapa_erc in ["g3a", "g3b"]:
            recomendacion += "trimestral "
        else:
            recomendacion += "semestral "
        
        recomendacion += f"debido a ERC estadio {etapa_erc.upper()}. "
        
        if riesgo_cv == "muy_alto":
            recomendacion += "Se enfatiza control estricto por riesgo cardiovascular muy alto. "
            
        if nivel_cumplimiento == "deficiente":
            recomendacion += "Se acorta tiempo de seguimiento por cumplimiento deficiente de metas terapéuticas."
        
        # Resultado final con el segundo camino implementado
        return {
            "laboratorios": fecha_proximos_labs.strftime("%d/%m/%Y"),
            "consulta_control": fecha_consulta.strftime("%d/%m/%Y"),
            "laboratorios_detallados": labs_agrupados,
            "recomendacion": recomendacion,
            "nivel_cumplimiento": nivel_cumplimiento
        }

    def _build_therapeutic_goals(self, patient_data, labs_data, tfg, riesgo_cv):
        """
        Construye la lista de metas terapéuticas con puntajes según perfil.
        Devuelve una lista de dicts con al menos 'parametro' y 'puntaje'.
        """
        try:
            # Definiciones mínimas para pruebas (evitamos import con espacio en 'RCV IA')
            from app.logic.advanced_patient_eval import determinar_etapa_erc as det_etapa
            PUNTAJE_METAS = {
                "rac": {"erc123_dm2": 20, "erc4_dm2": 15, "erc123_nodm2": 25, "erc4_nodm2": 10},
                "glicemia": {"erc123_dm2": 4, "erc4_dm2": 5, "erc123_nodm2": 5, "erc4_nodm2": 10},
                "hdl": {"erc123_dm2": 4, "erc4_dm2": 5, "erc123_nodm2": 5, "erc4_nodm2": 10},
            }
            METAS_TERAPEUTICAS = {
                "rac": {"default": 30},
                "glicemia": {"default": 130},
                "hdl": {"hombre": 40, "mujer": 50},
            }

            # Determinar perfil simple como en RCV IA
            def _perfil(estadio, tiene_dm2):
                es = str(estadio)
                grupo = "erc123" if es in ["1", "2", "3", "3a", "3b"] else "erc4"
                return f"{grupo}_{'dm2' if tiene_dm2 else 'nodm2'}"

            from app.logic.advanced_patient_eval import determinar_etapa_erc as det_etapa_local
            estadio = det_etapa_local(tfg)
            perfil = _perfil(estadio, bool(patient_data.get("tiene_dm2") or patient_data.get("dm2")))

            metas = []
            # RAC
            if "rac" in labs_data:
                puntaje = PUNTAJE_METAS.get("rac", {}).get(perfil, 0)
                metas.append({"parametro": "RAC", "puntaje": puntaje})
            # Glicemia
            if "glicemia" in labs_data:
                puntaje = PUNTAJE_METAS.get("glicemia", {}).get(perfil, 0)
                metas.append({"parametro": "Glicemia", "puntaje": puntaje})
            # HDL
            if "hdl" in labs_data:
                puntaje = PUNTAJE_METAS.get("hdl", {}).get(perfil, 0)
                metas.append({"parametro": "HDL", "puntaje": puntaje})

            return metas
        except Exception as e:
            logger.warning(f"No fue posible construir metas terapéuticas: {e}")
            return []
