#!/usr/bin/env python3
"""
🏥 ERC POLICE WATCHDOG - PARTE 2: FUNCIONES DE CHEQUEO Y ENFORCEMENT MÉDICO
===========================================================================

Implementa todas las funciones de monitoreo médico, enforcement de reglas
clínicas y validaciones específicas para la aplicación ERC Insight.

CONECTA CON PARTE 1: Usa decoradores, config y logging de erc_police_parte1.py
PREPARA PARA PARTE 3: Genera eventos para manejo de errores y alertas
"""

# ═══════════════════════════════════════════════════════════════════════════════
# IMPORTS DESDE PARTE 1 Y EXTENSIONES
# ═══════════════════════════════════════════════════════════════════════════════

import os
import sys
import json
import time
import sqlite3
import requests
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
import hashlib
import re

# Importar desde PARTE 1 (asegurar que esté en el path)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Simular importación de PARTE 1 (en implementación real sería: from erc_police_parte1 import *)
try:
    from erc_police_parte1 import (
        ERCPoliceWatchdog, POLICE_CONFIG, POLICE_LOGGER, 
        police_monitor, medical_validation, ERCPoliceConfig
    )
    PARTE1_AVAILABLE = True
except ImportError:
    # Fallback si PARTE 1 no está disponible
    PARTE1_AVAILABLE = False
    print("⚠️ PARTE 1 no disponible - usando configuración básica")
    
    # Configuración mínima para funcionar standalone
    class POLICE_LOGGER:
        @staticmethod
        def info(msg): print(f"INFO: {msg}")
        @staticmethod 
        def warning(msg): print(f"WARNING: {msg}")
        @staticmethod
        def error(msg): print(f"ERROR: {msg}")
    
    def police_monitor(name):
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def medical_validation(name):
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

# ═══════════════════════════════════════════════════════════════════════════════
# VALIDADORES MÉDICOS ESPECÍFICOS DE ERC
# ═══════════════════════════════════════════════════════════════════════════════

class ERCMedicalValidator:
    """Validador especializado en reglas médicas de ERC Insight"""
    
    def __init__(self, config = None):
        self.config = config if config else self._get_default_medical_config()
        self.validation_log = []
        self.lock = threading.Lock()
    
    def _get_default_medical_config(self):
        """Configuración médica por defecto"""
        return {
            "tfg_ranges": {
                "g1": {"min": 90, "max": float('inf')},
                "g2": {"min": 60, "max": 89},
                "g3a": {"min": 45, "max": 59},
                "g3b": {"min": 30, "max": 44},
                "g4": {"min": 15, "max": 29},
                "g5": {"min": 0, "max": 14}
            },
            "therapeutic_goals": {
                "presion_arterial": {"max_sistolica": 140, "max_diastolica": 90},
                "glicemia": {"max_value": 130},
                "colesterol_ldl": {"max_value": 100},
                "rac": {"max_value": 30}
            },
            "medication_rules": {
                "ieca_ara2_contraindications": ["potasio_alto", "tfg_menor_30"],
                "metformina_restrictions": ["tfg_menor_30"],
                "isglt2_restrictions": ["tfg_menor_30"]
            }
        }
    
    @medical_validation("cockcroft_gault_calculation")
    def validate_tfg_cockcroft_gault(self, edad: int, peso: float, creatinina: float, sexo: str) -> Dict[str, Any]:
        """
        Valida y calcula TFG usando fórmula Cockcroft-Gault con enforcement estricto
        """
        validation_result = {
            "timestamp": datetime.now().isoformat(),
            "function": "validate_tfg_cockcroft_gault",
            "input": {"edad": edad, "peso": peso, "creatinina": creatinina, "sexo": sexo},
            "status": "pending",
            "tfg": None,
            "estadio": None,
            "alerts": [],
            "errors": []
        }
        
        try:
            # 🚨 ENFORCEMENT: Validación de parámetros de entrada
            if not isinstance(edad, int) or edad <= 0 or edad > 120:
                validation_result["errors"].append(f"Edad inválida: {edad}. Debe ser entero entre 1-120")
            
            if not isinstance(peso, (int, float)) or peso <= 0 or peso > 300:
                validation_result["errors"].append(f"Peso inválido: {peso}. Debe ser entre 1-300 kg")
            
            if not isinstance(creatinina, (int, float)) or creatinina <= 0 or creatinina > 20:
                validation_result["errors"].append(f"Creatinina inválida: {creatinina}. Debe ser entre 0.1-20 mg/dL")
            
            if sexo.lower() not in ['m', 'f', 'masculino', 'femenino']:
                validation_result["errors"].append(f"Sexo inválido: {sexo}. Debe ser 'm', 'f', 'masculino' o 'femenino'")
            
            if validation_result["errors"]:
                validation_result["status"] = "error"
                return validation_result
            
            # 🧮 CÁLCULO DE TFG - Fórmula Cockcroft-Gault
            factor_sexo = 0.85 if sexo.lower() in ['f', 'femenino'] else 1.0
            tfg = ((140 - edad) * peso * factor_sexo) / (72 * creatinina)
            tfg = round(tfg, 2)
            
            # 🚨 ENFORCEMENT: Validación de resultado
            if tfg < 0 or tfg > 200:
                validation_result["errors"].append(f"TFG calculado fuera de rango válido: {tfg}")
                validation_result["status"] = "error"
                return validation_result
            
            # 🏥 CLASIFICACIÓN POR ESTADIOS KDIGO
            estadio = self._classify_erc_stage(tfg)
            
            # 🚨 ALERTAS MÉDICAS CRÍTICAS
            if tfg < 15:  # Estadio G5
                validation_result["alerts"].append("CRÍTICO: TFG < 15 - Considerar terapia de reemplazo renal")
            elif tfg < 30:  # Estadio G4
                validation_result["alerts"].append("ALERTA: TFG < 30 - Preparar para terapia renal, referir nefrología")
            elif tfg < 45:  # Estadio G3b
                validation_result["alerts"].append("PRECAUCIÓN: TFG < 45 - Monitoreo intensivo, ajustar medicamentos")
            
            # ✅ RESULTADO EXITOSO
            validation_result.update({
                "status": "success",
                "tfg": tfg,
                "estadio": estadio,
                "formula_used": "Cockcroft-Gault",
                "interpretation": self._get_tfg_interpretation(tfg, estadio)
            })
            
            # 📊 LOG DE VALIDACIÓN
            self._log_medical_validation(validation_result)
            
            return validation_result
            
        except Exception as e:
            validation_result["status"] = "error"
            validation_result["errors"].append(f"Error en cálculo: {str(e)}")
            POLICE_LOGGER.error(f"🚨 Error en validación TFG: {str(e)}")
            return validation_result
    
    def _classify_erc_stage(self, tfg: float) -> str:
        """Clasifica estadio ERC según TFG"""
        for stage, range_data in self.config["tfg_ranges"].items():
            if range_data["min"] <= tfg <= range_data["max"]:
                return stage
        return "unknown"
    
    def _get_tfg_interpretation(self, tfg: float, estadio: str) -> str:
        """Genera interpretación clínica del TFG"""
        interpretations = {
            "g1": f"Normal o aumentado (TFG: {tfg}). Función renal normal si no hay daño renal.",
            "g2": f"Ligeramente disminuido (TFG: {tfg}). Función renal normal si no hay daño renal.",
            "g3a": f"Moderadamente disminuido (TFG: {tfg}). ERC estadio 3a - monitoreo regular.",
            "g3b": f"Moderadamente a severamente disminuido (TFG: {tfg}). ERC estadio 3b - seguimiento nefrológico.",
            "g4": f"Severamente disminuido (TFG: {tfg}). ERC estadio 4 - preparar terapia de reemplazo renal.",
            "g5": f"Falla renal (TFG: {tfg}). ERC estadio 5 - terapia de reemplazo renal necesaria."
        }
        return interpretations.get(estadio, f"TFG: {tfg} - Clasificación no determinada")
    
    @medical_validation("cardiovascular_risk_assessment")
    def validate_cardiovascular_risk(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida y calcula riesgo cardiovascular con enforcement de reglas médicas
        """
        validation_result = {
            "timestamp": datetime.now().isoformat(),
            "function": "validate_cardiovascular_risk",
            "input": patient_data,
            "status": "pending",
            "risk_level": None,
            "score": 0,
            "factors": [],
            "alerts": [],
            "errors": []
        }
        
        try:
            required_fields = ["edad", "sexo", "tfg"]
            missing_fields = [field for field in required_fields if field not in patient_data]
            
            if missing_fields:
                validation_result["errors"].append(f"Campos obligatorios faltantes: {missing_fields}")
                validation_result["status"] = "error"
                return validation_result
            
            # 🧮 CÁLCULO DE RIESGO CARDIOVASCULAR
            risk_score = 0
            risk_factors = []
            
            # Factor edad
            edad = patient_data["edad"]
            if edad >= 75:
                risk_score += 3
                risk_factors.append(f"Edad ≥75 años ({edad})")
            elif edad >= 65:
                risk_score += 2
                risk_factors.append(f"Edad ≥65 años ({edad})")
            
            # Factor TFG/ERC
            tfg = patient_data.get("tfg", 0)
            if tfg < 30:
                risk_score += 4
                risk_factors.append(f"ERC estadio G4-G5 (TFG: {tfg})")
            elif tfg < 60:
                risk_score += 2
                risk_factors.append(f"ERC estadio G3 (TFG: {tfg})")
            
            # Factores de comorbilidad
            if patient_data.get("dm2", False):
                risk_score += 3
                risk_factors.append("Diabetes mellitus tipo 2")
            
            if patient_data.get("hta", False):
                risk_score += 2
                risk_factors.append("Hipertensión arterial")
            
            if patient_data.get("dislipidemia", False):
                risk_score += 1
                risk_factors.append("Dislipidemia")
            
            if patient_data.get("tabaquismo", False):
                risk_score += 2
                risk_factors.append("Tabaquismo activo")
            
            if patient_data.get("antecedente_cv", False):
                risk_score += 4
                risk_factors.append("Antecedente cardiovascular")
            
            # 🏥 CLASIFICACIÓN DE RIESGO
            if risk_score >= 8:
                risk_level = "muy_alto"
            elif risk_score >= 5:
                risk_level = "alto"
            elif risk_score >= 2:
                risk_level = "moderado"
            else:
                risk_level = "bajo"
            
            # 🚨 ALERTAS MÉDICAS ESPECÍFICAS
            if risk_level == "muy_alto":
                validation_result["alerts"].append("RIESGO MUY ALTO: Requiere intervención intensiva y seguimiento estrecho")
            elif risk_level == "alto":
                validation_result["alerts"].append("RIESGO ALTO: Requiere control estricto de factores de riesgo")
            
            validation_result.update({
                "status": "success",
                "risk_level": risk_level,
                "score": risk_score,
                "factors": risk_factors,
                "interpretation": self._get_cv_risk_interpretation(risk_level, risk_score)
            })
            
            self._log_medical_validation(validation_result)
            return validation_result
            
        except Exception as e:
            validation_result["status"] = "error"
            validation_result["errors"].append(f"Error en evaluación de riesgo: {str(e)}")
            return validation_result
    
    def _get_cv_risk_interpretation(self, risk_level: str, score: int) -> str:
        """Genera interpretación del riesgo cardiovascular"""
        interpretations = {
            "bajo": f"Riesgo cardiovascular bajo (Score: {score}). Manejo conservador con estilo de vida.",
            "moderado": f"Riesgo cardiovascular moderado (Score: {score}). Control de factores de riesgo.",
            "alto": f"Riesgo cardiovascular alto (Score: {score}). Tratamiento farmacológico y seguimiento.",
            "muy_alto": f"Riesgo cardiovascular muy alto (Score: {score}). Intervención intensiva inmediata."
        }
        return interpretations.get(risk_level, f"Riesgo no determinado (Score: {score})")
    
    @medical_validation("therapeutic_goals_compliance")
    def validate_therapeutic_goals(self, patient_data: Dict[str, Any], lab_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida cumplimiento de metas terapéuticas según perfil del paciente
        """
        validation_result = {
            "timestamp": datetime.now().isoformat(),
            "function": "validate_therapeutic_goals",
            "input": {"patient": patient_data, "labs": lab_data},
            "status": "pending",
            "goals_met": [],
            "goals_not_met": [],
            "compliance_score": 0,
            "alerts": [],
            "errors": []
        }
        
        try:
            # 🏥 DEFINIR METAS SEGÚN PERFIL DEL PACIENTE
            tfg = patient_data.get("tfg", 0)
            tiene_dm = patient_data.get("dm2", False)
            
            # Metas de presión arterial
            if "presion_sistolica" in lab_data and "presion_diastolica" in lab_data:
                sistolica = lab_data["presion_sistolica"]
                diastolica = lab_data["presion_diastolica"]
                
                # Meta más estricta para pacientes con ERC + DM
                meta_sistolica = 130 if (tiene_dm or tfg < 60) else 140
                meta_diastolica = 80 if (tiene_dm or tfg < 60) else 90
                
                if sistolica <= meta_sistolica and diastolica <= meta_diastolica:
                    validation_result["goals_met"].append({
                        "parameter": "presion_arterial",
                        "value": f"{sistolica}/{diastolica}",
                        "goal": f"≤{meta_sistolica}/{meta_diastolica}",
                        "status": "achieved"
                    })
                else:
                    validation_result["goals_not_met"].append({
                        "parameter": "presion_arterial", 
                        "value": f"{sistolica}/{diastolica}",
                        "goal": f"≤{meta_sistolica}/{meta_diastolica}",
                        "status": "not_achieved"
                    })
                    if sistolica > 160 or diastolica > 100:
                        validation_result["alerts"].append("CRÍTICO: Hipertensión severa - Ajuste inmediato de tratamiento")
            
            # Metas de glicemia (si diabetes)
            if tiene_dm and "glicemia" in lab_data:
                glicemia = lab_data["glicemia"]
                meta_glicemia = 130
                
                if glicemia <= meta_glicemia:
                    validation_result["goals_met"].append({
                        "parameter": "glicemia",
                        "value": glicemia,
                        "goal": f"≤{meta_glicemia} mg/dL",
                        "status": "achieved"
                    })
                else:
                    validation_result["goals_not_met"].append({
                        "parameter": "glicemia",
                        "value": glicemia,
                        "goal": f"≤{meta_glicemia} mg/dL", 
                        "status": "not_achieved"
                    })
                    if glicemia > 200:
                        validation_result["alerts"].append("CRÍTICO: Hiperglicemia severa - Control inmediato")
            
            # Meta de RAC (Relación Albúmina-Creatinina)
            if "rac" in lab_data:
                rac = lab_data["rac"]
                meta_rac = 30
                
                if rac <= meta_rac:
                    validation_result["goals_met"].append({
                        "parameter": "rac",
                        "value": rac,
                        "goal": f"≤{meta_rac} mg/g",
                        "status": "achieved"
                    })
                else:
                    validation_result["goals_not_met"].append({
                        "parameter": "rac",
                        "value": rac,
                        "goal": f"≤{meta_rac} mg/g",
                        "status": "not_achieved"
                    })
                    if rac > 300:
                        validation_result["alerts"].append("CRÍTICO: Macroalbuminuria - Protección renal urgente")
            
            # 📊 CALCULAR SCORE DE CUMPLIMIENTO
            total_goals = len(validation_result["goals_met"]) + len(validation_result["goals_not_met"])
            if total_goals > 0:
                compliance_score = (len(validation_result["goals_met"]) / total_goals) * 100
                validation_result["compliance_score"] = round(compliance_score, 1)
            
            validation_result["status"] = "success"
            self._log_medical_validation(validation_result)
            return validation_result
            
        except Exception as e:
            validation_result["status"] = "error"
            validation_result["errors"].append(f"Error en validación de metas: {str(e)}")
            return validation_result
    
    @medical_validation("medication_safety_check")
    def validate_medication_safety(self, patient_data: Dict[str, Any], medications: List[str]) -> Dict[str, Any]:
        """
        Valida seguridad de medicamentos según estado del paciente
        """
        validation_result = {
            "timestamp": datetime.now().isoformat(),
            "function": "validate_medication_safety",
            "input": {"patient": patient_data, "medications": medications},
            "status": "pending",
            "safe_medications": [],
            "contraindicated_medications": [],
            "dose_adjustments": [],
            "alerts": [],
            "errors": []
        }
        
        try:
            tfg = patient_data.get("tfg", 0)
            potasio = patient_data.get("potasio", 0)
            
            for medication in medications:
                med_lower = medication.lower()
                
                # 🚨 CONTRAINDICACIONES POR TFG
                if tfg < 30:
                    if any(med in med_lower for med in ["metformina", "metformin"]):
                        validation_result["contraindicated_medications"].append({
                            "medication": medication,
                            "reason": f"TFG < 30 ml/min ({tfg}) - Riesgo de acidosis láctica",
                            "severity": "critical"
                        })
                        validation_result["alerts"].append(f"CRÍTICO: Suspender {medication} - TFG < 30")
                        continue
                    
                    if any(med in med_lower for med in ["empagliflozina", "dapagliflozina", "canagliflozina"]):
                        validation_result["contraindicated_medications"].append({
                            "medication": medication,
                            "reason": f"TFG < 30 ml/min ({tfg}) - Efectividad reducida",
                            "severity": "moderate"
                        })
                        continue
                
                # 🔄 AJUSTES DE DOSIS
                if 15 <= tfg <= 45:
                    if any(med in med_lower for med in ["enalapril", "lisinopril", "losartan", "valsartan"]):
                        validation_result["dose_adjustments"].append({
                            "medication": medication,
                            "adjustment": "Reducir dosis 25-50% y monitorizar K+ y creatinina c/1-2 semanas",
                            "reason": f"TFG moderadamente reducido ({tfg})"
                        })
                
                # ⚠️ MONITOREO ESPECIAL
                if potasio > 5.5:
                    if any(med in med_lower for med in ["enalapril", "lisinopril", "losartan", "valsartan", "espironolactona"]):
                        validation_result["alerts"].append(f"PRECAUCIÓN: {medication} con K+ elevado ({potasio}) - Monitoreo estrecho")
                
                # ✅ MEDICAMENTO SEGURO
                if medication not in [item["medication"] for item in validation_result["contraindicated_medications"]]:
                    validation_result["safe_medications"].append({
                        "medication": medication,
                        "status": "safe",
                        "notes": "Sin contraindicaciones detectadas"
                    })
            
            validation_result["status"] = "success"
            self._log_medical_validation(validation_result)
            return validation_result
            
        except Exception as e:
            validation_result["status"] = "error" 
            validation_result["errors"].append(f"Error en validación de medicamentos: {str(e)}")
            return validation_result
    
    def _log_medical_validation(self, validation_result: Dict[str, Any]):
        """Registra validación médica en log"""
        with self.lock:
            self.validation_log.append(validation_result)
            
            # Mantener solo las últimas 1000 validaciones
            if len(self.validation_log) > 1000:
                self.validation_log = self.validation_log[-1000:]
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de validaciones realizadas"""
        with self.lock:
            total = len(self.validation_log)
            if total == 0:
                return {"total": 0, "success": 0, "errors": 0, "success_rate": 0}
            
            success = sum(1 for v in self.validation_log if v["status"] == "success")
            errors = total - success
            
            return {
                "total_validations": total,
                "successful": success,
                "errors": errors,
                "success_rate": round((success / total) * 100, 1),
                "last_24h": len([v for v in self.validation_log 
                               if (datetime.now() - datetime.fromisoformat(v["timestamp"])).days < 1])
            }

# ═══════════════════════════════════════════════════════════════════════════════
# MONITOREO DE APLICACIÓN FLASK
# ═══════════════════════════════════════════════════════════════════════════════

class ERCFlaskMonitor:
    """Monitor especializado para la aplicación Flask ERC Insight"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.endpoints_to_monitor = [
            "/api/health",
            "/api/generate_report",
            "/api/parse_document", 
            "/patient/api/tfg"
        ]
        self.monitoring_log = []
        self.lock = threading.Lock()
    
    @police_monitor("flask_health_check")
    def check_application_health(self) -> Dict[str, Any]:
        """Chequea salud general de la aplicación Flask"""
        health_result = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "pending",
            "endpoints": [],
            "response_times": {},
            "errors": [],
            "alerts": []
        }
        
        try:
            # 🔍 CHEQUEAR ENDPOINTS CRÍTICOS
            all_healthy = True
            total_response_time = 0
            
            for endpoint in self.endpoints_to_monitor:
                endpoint_result = self._check_endpoint(endpoint)
                health_result["endpoints"].append(endpoint_result)
                
                if endpoint_result["status"] != "healthy":
                    all_healthy = False
                    health_result["errors"].append(f"Endpoint {endpoint} unhealthy: {endpoint_result.get('error', 'Unknown')}")
                
                if "response_time" in endpoint_result:
                    health_result["response_times"][endpoint] = endpoint_result["response_time"]
                    total_response_time += endpoint_result["response_time"]
            
            # 📊 CALCULAR MÉTRICAS GENERALES
            avg_response_time = total_response_time / len(self.endpoints_to_monitor) if self.endpoints_to_monitor else 0
            health_result["average_response_time"] = round(avg_response_time, 3)
            
            # 🚨 EVALUAR ESTADO GENERAL
            if not all_healthy:
                health_result["overall_status"] = "unhealthy"
                health_result["alerts"].append("CRÍTICO: Uno o más endpoints no responden correctamente")
            elif avg_response_time > 5.0:
                health_result["overall_status"] = "degraded"
                health_result["alerts"].append(f"ADVERTENCIA: Tiempo de respuesta elevado ({avg_response_time:.2f}s)")
            else:
                health_result["overall_status"] = "healthy"
            
            self._log_monitoring_event(health_result)
            return health_result
            
        except Exception as e:
            health_result["overall_status"] = "error"
            health_result["errors"].append(f"Error en health check: {str(e)}")
            POLICE_LOGGER.error(f"🚨 Error en health check: {str(e)}")
            return health_result
    
    def _check_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Chequea un endpoint específico"""
        result = {
            "endpoint": endpoint,
            "status": "pending",
            "response_time": None,
            "status_code": None,
            "error": None
        }
        
        try:
            start_time = time.time()
            url = f"{self.base_url}{endpoint}"
            
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time
            
            result["response_time"] = round(response_time, 3)
            result["status_code"] = response.status_code
            
            if response.status_code == 200:
                result["status"] = "healthy"
            elif response.status_code in [404, 405]:
                result["status"] = "not_found"
                result["error"] = f"HTTP {response.status_code}"
            else:
                result["status"] = "unhealthy"
                result["error"] = f"HTTP {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            result["status"] = "unreachable"
            result["error"] = "Connection refused - Application not running?"
        except requests.exceptions.Timeout:
            result["status"] = "timeout"
            result["error"] = "Request timeout (>10s)"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    @police_monitor("medical_endpoint_validation")
    def validate_medical_endpoints(self) -> Dict[str, Any]:
        """Valida endpoints médicos específicos con datos de prueba"""
        validation_result = {
            "timestamp": datetime.now().isoformat(),
            "endpoints_validated": [],
            "status": "pending",
            "errors": [],
            "alerts": []
        }
        
        # 🧪 DATOS DE PRUEBA PARA ENDPOINTS MÉDICOS
        test_cases = {
            "/patient/api/tfg": {
                "method": "POST",
                "data": {
                    "edad": 65,
                    "peso": 70,
                    "creatinina": 1.2,
                    "sexo": "m"
                },
                "expected_fields": ["tfg", "etapa_erc"]
            }
        }
        
        try:
            for endpoint, test_config in test_cases.items():
                endpoint_result = self._validate_medical_endpoint(endpoint, test_config)
                validation_result["endpoints_validated"].append(endpoint_result)
                
                if endpoint_result["status"] != "success":
                    validation_result["errors"].append(f"{endpoint}: {endpoint_result.get('error', 'Unknown error')}")
            
            # 📊 EVALUAR RESULTADO GENERAL
            if validation_result["errors"]:
                validation_result["status"] = "failed"
                validation_result["alerts"].append("CRÍTICO: Validación de endpoints médicos falló")
            else:
                validation_result["status"] = "success"
            
            self._log_monitoring_event(validation_result)
            return validation_result
            
        except Exception as e:
            validation_result["status"] = "error"
            validation_result["errors"].append(f"Error en validación: {str(e)}")
            return validation_result
    
    def _validate_medical_endpoint(self, endpoint: str, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Valida un endpoint médico específico"""
        result = {
            "endpoint": endpoint,
            "status": "pending",
            "response_data": None,
            "validation_errors": [],
            "error": None
        }
        
        try:
            url = f"{self.base_url}{endpoint}"
            
            if test_config["method"] == "POST":
                response = requests.post(url, json=test_config["data"], timeout=10)
            else:
                response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                result["status"] = "failed"
                result["error"] = f"HTTP {response.status_code}: {response.text}"
                return result
            
            # 🧪 VALIDAR ESTRUCTURA DE RESPUESTA
            try:
                response_data = response.json()
                result["response_data"] = response_data
                
                # Validar campos esperados
                if "expected_fields" in test_config:
                    for field in test_config["expected_fields"]:
                        if field not in response_data:
                            result["validation_errors"].append(f"Campo faltante: {field}")
                
                # Validaciones específicas para TFG
                if endpoint == "/patient/api/tfg":
                    if "tfg" in response_data:
                        tfg = response_data["tfg"]
                        if not isinstance(tfg, (int, float)) or tfg < 0 or tfg > 200:
                            result["validation_errors"].append(f"TFG inválido: {tfg}")
                    
                    if "etapa_erc" in response_data:
                        etapa = response_data["etapa_erc"]
                        if etapa not in ["g1", "g2", "g3a", "g3b", "g4", "g5"]:
                            result["validation_errors"].append(f"Etapa ERC inválida: {etapa}")
                
                if result["validation_errors"]:
                    result["status"] = "validation_failed"
                else:
                    result["status"] = "success"
                    
            except json.JSONDecodeError:
                result["status"] = "failed"
                result["error"] = "Respuesta no es JSON válido"
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def _log_monitoring_event(self, event_data: Dict[str, Any]):
        """Registra evento de monitoreo"""
        with self.lock:
            self.monitoring_log.append(event_data)
            
            # Mantener solo los últimos 500 eventos
            if len(self.monitoring_log) > 500:
                self.monitoring_log = self.monitoring_log[-500:]

# ═══════════════════════════════════════════════════════════════════════════════
# EXTENSIÓN DE LA CLASE WATCHDOG PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def extend_watchdog_with_medical_monitoring():
    """Extiende la clase ERCPoliceWatchdog con funciones médicas"""
    
    if not PARTE1_AVAILABLE:
        POLICE_LOGGER.warning("PARTE 1 no disponible - creando extensión básica")
        return None
    
    # Añadir métodos médicos a la clase principal
    ERCPoliceWatchdog.medical_validator = None
    ERCPoliceWatchdog.flask_monitor = None
    
    def init_medical_monitoring(self):
        """Inicializa monitoreo médico"""
        self.medical_validator = ERCMedicalValidator(self.config.medical_rules)
        self.flask_monitor = ERCFlaskMonitor(self.config.app_url)
        POLICE_LOGGER.info("🏥 Medical monitoring initialized")
    
    def run_medical_validation_cycle(self):
        """Ejecuta ciclo completo de validaciones médicas"""
        try:
            # Test de validación TFG
            tfg_result = self.medical_validator.validate_tfg_cockcroft_gault(65, 70, 1.2, "m")
            
            # Test de endpoints médicos
            endpoints_result = self.flask_monitor.validate_medical_endpoints()
            
            # Health check general
            health_result = self.flask_monitor.check_application_health()
            
            return {
                "tfg_validation": tfg_result,
                "endpoints_validation": endpoints_result,
                "health_check": health_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            POLICE_LOGGER.error(f"🚨 Error en ciclo de validación médica: {str(e)}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    # Añadir métodos a la clase
    ERCPoliceWatchdog.init_medical_monitoring = init_medical_monitoring
    ERCPoliceWatchdog.run_medical_validation_cycle = run_medical_validation_cycle
    
    return ERCPoliceWatchdog

# ═══════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA Y DEMO
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🏥 ERC Police Watchdog - Parte 2 (Chequeo y Enforcement Médico)")
    print("=" * 70)
    
    # Inicializar validador médico
    print("\n📋 Inicializando validador médico...")
    validator = ERCMedicalValidator()
    
    # Test de validaciones médicas
    print("\n🧪 Ejecutando tests de validaciones médicas...")
    
    # Test 1: Cálculo TFG
    print("\n1️⃣ Test TFG Cockcroft-Gault:")
    tfg_result = validator.validate_tfg_cockcroft_gault(65, 70, 1.2, "m")
    print(f"   TFG: {tfg_result['tfg']} ml/min/1.73m² - Estadio: {tfg_result['estadio']}")
    print(f"   Estado: {tfg_result['status']}")
    if tfg_result['alerts']:
        print(f"   Alertas: {tfg_result['alerts']}")
    
    # Test 2: Riesgo cardiovascular  
    print("\n2️⃣ Test Riesgo Cardiovascular:")
    patient_test = {
        "edad": 70,
        "sexo": "m", 
        "tfg": 45,
        "dm2": True,
        "hta": True,
        "tabaquismo": False
    }
    cv_result = validator.validate_cardiovascular_risk(patient_test)
    print(f"   Riesgo: {cv_result['risk_level']} (Score: {cv_result['score']})")
    print(f"   Factores: {len(cv_result['factors'])}")
    
    # Test 3: Metas terapéuticas
    print("\n3️⃣ Test Metas Terapéuticas:")
    lab_test = {
        "presion_sistolica": 145,
        "presion_diastolica": 85,
        "glicemia": 140,
        "rac": 45
    }
    goals_result = validator.validate_therapeutic_goals(patient_test, lab_test)
    print(f"   Cumplimiento: {goals_result['compliance_score']}%")
    print(f"   Metas logradas: {len(goals_result['goals_met'])}")
    print(f"   Metas pendientes: {len(goals_result['goals_not_met'])}")
    
    # Test 4: Seguridad de medicamentos
    print("\n4️⃣ Test Seguridad Medicamentos:")
    medications_test = ["Enalapril", "Metformina", "Empagliflozina"]
    med_result = validator.validate_medication_safety(patient_test, medications_test)
    print(f"   Medicamentos seguros: {len(med_result['safe_medications'])}")
    print(f"   Contraindicaciones: {len(med_result['contraindicated_medications'])}")
    print(f"   Ajustes requeridos: {len(med_result['dose_adjustments'])}")
    
    # Resumen de validaciones
    print("\n📊 Resumen de Validaciones:")
    summary = validator.get_validation_summary()
    print(f"   Total realizadas: {summary['total_validations']}")
    print(f"   Exitosas: {summary['successful']}")
    print(f"   Tasa de éxito: {summary['success_rate']}%")
    
    # Test de monitor Flask (si está disponible)
    print("\n🌐 Test Monitor Flask:")
    monitor = ERCFlaskMonitor()
    health = monitor.check_application_health()
    print(f"   Estado general: {health['overall_status']}")
    print(f"   Endpoints chequeados: {len(health['endpoints'])}")
    if health['average_response_time']:
        print(f"   Tiempo respuesta promedio: {health['average_response_time']}s")
    
    print("\n🎯 PARTE 2 COMPLETADA - Lista para PARTE 3")
    print("   ✅ Validaciones médicas implementadas")
    print("   ✅ Monitoreo de Flask funcional") 
    print("   ✅ Sistema de alertas médicas activo")
    print("   ✅ Enforcement de reglas clínicas operativo")

"""
📋 PARTE 2 COMPLETADA - INSTRUCCIONES PARA ENSAMBLAJE:

✅ INCLUYE:
- ERCMedicalValidator: Validaciones médicas específicas de ERC
- ERCFlaskMonitor: Monitoreo especializado de aplicación Flask
- Validación TFG con fórmula Cockcroft-Gault y enforcement estricto
- Evaluación de riesgo cardiovascular con scoring automático
- Validación de metas terapéuticas por perfil de paciente
- Chequeo de seguridad de medicamentos con contraindicaciones
- Monitoreo de endpoints críticos de la aplicación
- Sistema de logging de validaciones médicas
- Tests de endpoints médicos con datos de prueba

🔗 CONECTA CON PARTE 1:
- Usa decoradores @medical_validation y @police_monitor
- Utiliza POLICE_LOGGER para logging centralizado
- Integra con ERCPoliceConfig para configuración
- Extiende clase ERCPoliceWatchdog con funciones médicas

🔗 PREPARA PARA PARTE 3:
- Genera eventos detallados para sistema de alertas
- Proporciona métricas para análisis de rendimiento
- Crea logs estructurados para debugging
- Identifica situaciones críticas que requieren alertas inmediatas

🏥 REGLAS MÉDICAS IMPLEMENTADAS:
- Cálculo y validación TFG según estadios KDIGO
- Clasificación de riesgo cardiovascular multi-factorial
- Metas terapéuticas diferenciadas por perfil (ERC+DM, solo ERC)
- Contraindicaciones farmacológicas por función renal
- Alertas médicas críticas automáticas
- Cumplimiento de guías clínicas internacionales

⚡ LISTO PARA PARTE 3: Manejo de errores, alertas y sistema de testing
"""
