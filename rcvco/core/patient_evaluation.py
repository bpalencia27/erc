"""
Módulo core para evaluación de pacientes con enfoque en RCV
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from dataclasses import dataclass
from pydantic import BaseModel, Field, validator
import pytz

BOGOTA_TZ = pytz.timezone('America/Bogota')

@dataclass
class PatientData:
    """Modelo de datos del paciente con validación"""
    edad: int
    peso: float
    talla: float
    sexo: str
    creatinina: float
    pa_sistolica: Optional[int] = None
    pa_diastolica: Optional[int] = None
    diabetes: bool = False
    hipertension: bool = False
    ecv: bool = False
    tabaquismo: bool = False
    imc: Optional[float] = None

    def __post_init__(self):
        """Validación posterior a inicialización"""
        if self.edad < 18 or self.edad > 120:
            raise ValueError("Edad debe estar entre 18 y 120 años")
        if self.peso < 30 or self.peso > 300:
            raise ValueError("Peso debe estar entre 30 y 300 kg")
        if self.talla < 100 or self.talla > 250:
            raise ValueError("Talla debe estar entre 100 y 250 cm")
        if self.sexo not in ['M', 'F']:
            raise ValueError("Sexo debe ser 'M' o 'F'")
        
        # Calcular IMC si no fue proporcionado
        if self.imc is None:
            self.imc = self.calcular_imc()

    def calcular_imc(self) -> float:
        """Calcula el IMC usando peso y talla"""
        talla_m = self.talla / 100
        return round(self.peso / (talla_m * talla_m), 1)

def calculate_tfg(patient: PatientData) -> float:
    """
    Calcula la Tasa de Filtración Glomerular usando Cockcroft-Gault
    
    Args:
        patient: Objeto PatientData con datos necesarios
        
    Returns:
        float: TFG calculada en mL/min
        
    Raises:
        ValueError: Si faltan datos requeridos o están fuera de rango
    """
    if not all([patient.edad, patient.peso, patient.creatinina, patient.sexo]):
        raise ValueError("Faltan datos requeridos para calcular TFG")
    
    # Fórmula Cockcroft-Gault
    tfg = ((140 - patient.edad) * patient.peso) / (72 * patient.creatinina)
    
    # Ajuste para mujeres
    if patient.sexo == 'F':
        tfg *= 0.85
    
    return round(tfg, 1)

def evaluate_risk_factors(patient: PatientData) -> Tuple[str, List[str]]:
    """
    Evalúa factores de riesgo y determina nivel
    
    Args:
        patient: Objeto PatientData con información del paciente
        
    Returns:
        Tuple[str, List[str]]: (nivel de riesgo, lista de factores)
    """
    risk_factors = []
    risk_score = 0
    
    if patient.edad > 65:
        risk_factors.append("Edad > 65 años")
        risk_score += 1
        
    if patient.diabetes:
        risk_factors.append("Diabetes Mellitus")
        risk_score += 2
        
    if patient.hipertension:
        risk_factors.append("Hipertensión Arterial")
        risk_score += 1
        
    if patient.ecv:
        risk_factors.append("Enfermedad Cardiovascular")
        risk_score += 3
        
    if patient.tabaquismo:
        risk_factors.append("Tabaquismo activo")
        risk_score += 1
    
    # Evaluar IMC
    if patient.imc >= 30:
        risk_factors.append(f"Obesidad (IMC: {patient.imc})")
        risk_score += 1
    
    # Determinar nivel de riesgo
    if risk_score >= 5 or patient.ecv:
        nivel = "MUY ALTO"
    elif risk_score >= 3:
        nivel = "ALTO"
    elif risk_score >= 1:
        nivel = "MODERADO"
    else:
        nivel = "BAJO"
    
    return nivel, risk_factors

def get_therapeutic_goals(risk_level: str, patient: PatientData) -> Dict[str, dict]:
    """
    Define metas terapéuticas según nivel de riesgo
    
    Args:
        risk_level: Nivel de riesgo ('BAJO', 'MODERADO', 'ALTO', 'MUY ALTO')
        patient: Objeto PatientData con información del paciente
    
    Returns:
        Dict[str, dict]: Metas para cada parámetro
    """
    goals = {}
    
    # Meta de presión arterial
    if patient.diabetes or patient.ecv:
        goals['pa'] = {
            'sistolica': {'meta': 130, 'actual': patient.pa_sistolica},
            'diastolica': {'meta': 80, 'actual': patient.pa_diastolica}
        }
    else:
        goals['pa'] = {
            'sistolica': {'meta': 140, 'actual': patient.pa_sistolica},
            'diastolica': {'meta': 90, 'actual': patient.pa_diastolica}
        }
    
    # Meta de LDL según riesgo
    if risk_level == "MUY ALTO":
        goals['ldl'] = {'meta': 55, 'unidad': 'mg/dL'}
    elif risk_level == "ALTO":
        goals['ldl'] = {'meta': 70, 'unidad': 'mg/dL'}
    else:
        goals['ldl'] = {'meta': 100, 'unidad': 'mg/dL'}
    
    # Meta de HbA1c para diabéticos
    if patient.diabetes:
        goals['hba1c'] = {
            'meta': 7.0 if patient.edad < 65 else 8.0,
            'unidad': '%'
        }
    
    return goals

def generate_recommendations(patient: PatientData, risk_level: str, goals: Dict[str, dict]) -> List[str]:
    """
    Genera recomendaciones personalizadas
    
    Args:
        patient: Objeto PatientData
        risk_level: Nivel de riesgo
        goals: Metas terapéuticas definidas
    
    Returns:
        List[str]: Lista de recomendaciones
    """
    recommendations = []
    
    # Recomendaciones generales
    recommendations.append("Mantener un estilo de vida saludable")
    recommendations.append("Realizar actividad física regular")
    
    if patient.tabaquismo:
        recommendations.append("Cesar el consumo de tabaco")
    
    if patient.imc >= 25:
        recommendations.append(f"Reducir peso - IMC actual: {patient.imc}")
    
    # Recomendaciones específicas según riesgo
    if risk_level in ["MUY ALTO", "ALTO"]:
        recommendations.append("Control médico cada 3 meses")
        recommendations.append(f"Mantener LDL < {goals['ldl']['meta']} mg/dL")
    
    if patient.diabetes:
        recommendations.append(
            f"Control de HbA1c - Meta < {goals['hba1c']['meta']}%"
        )
    
    return recommendations
        """Validate max_days is greater than min_days."""
        if 'min_days' in values and v <= values['min_days']:
            raise ValueError('max_days must be greater than min_days')
        return v

class LabValidityConfig(TypedDict):
    """Type definition for laboratory test validity configuration with strict typing."""
    parcial_orina: int
    creatinina: Union[int, List[int]]
    glicemia: int
    colesterol_total: int
    colesterol_ldl: int
    trigliceridos: int
    hba1c: int
    microalbuminuria: int
    hemoglobina: int
    hematocrito: int
    pth: Optional[int]
    depuracion_creatinina_24h: int

# Configuration constants
LAB_VALIDITY_CONFIG: Dict[str, LabValidityConfig] = {
    "g1": {
        "parcial_orina": 180,
        "creatinina": 180,
        "glicemia": 180,
        "colesterol_total": 180,
        "colesterol_ldl": 180,
        "trigliceridos": 180,
        "hba1c": 180,
        "microalbuminuria": 180,
        "hemoglobina": 365,
        "hematocrito": 365,
        "depuracion_creatinina_24h": 365
    },
    "g2": {
        "parcial_orina": 180,
        "creatinina": 180,
        "glicemia": 180,
        "colesterol_total": 180,
        "colesterol_ldl": 180,
        "trigliceridos": 180,
        "hba1c": 180,
        "microalbuminuria": 180,
        "hemoglobina": 365,
        "hematocrito": 365,
        "pth": 365,
        "depuracion_creatinina_24h": 180
    },
    "g3a": {
        "parcial_orina": 180,
        "creatinina": [90, 121],  # Min-max days range
        "glicemia": 180,
        "colesterol_total": 180,
        "colesterol_ldl": 180,
        "trigliceridos": 180,
        "hba1c": 180,
        "microalbuminuria": 180,
        "hemoglobina": 365,
        "hematocrito": 365,
        "pth": 365,
        "depuracion_creatinina_24h": 180
    }
}

class PatientEvaluation:
    """Core class for patient clinical evaluation"""
    
    def __init__(self):
        """Initialize patient evaluation engine"""
        self.bogota_tz = BOGOTA_TZ
    
    def evaluate_patient(self, patient_data: Dict, lab_results: Dict) -> Dict:
        """
        Evaluates patient data and generates clinical assessment
        
        Args:
            patient_data (Dict): Patient demographic and clinical data
            lab_results (Dict): Laboratory test results
            
        Returns:
            Dict: Clinical evaluation results including:
                - CKD stage
                - Cardiovascular risk
                - Therapeutic goals compliance
                - Recommendations
        """
        try:
            # Crear objeto PatientData validado
            patient = PatientData(**patient_data)
            
            # Calcular TFG
            tfg = calculate_tfg(patient)
            
            # Evaluar factores de riesgo
            risk_level, risk_factors = evaluate_risk_factors(patient)
            
            # Obtener metas terapéuticas
            goals = get_therapeutic_goals(risk_level, patient)
            
            # Generar recomendaciones
            recommendations = generate_recommendations(patient, risk_level, goals)
            
            # Construir resultado
            evaluation = {
                "fecha_evaluacion": datetime.now(self.bogota_tz).strftime("%Y-%m-%d %H:%M:%S"),
                "tfg": tfg,
                "riesgo_cardiovascular": {
                    "nivel": risk_level,
                    "factores": risk_factors
                },
                "metas_terapeuticas": goals,
                "recomendaciones": recommendations,
                "laboratorios_vigentes": self._check_lab_validity(lab_results, tfg)
            }
            
            return evaluation
            
        except Exception as e:
            raise ValueError(f"Error en evaluación del paciente: {str(e)}")
    
    def _check_lab_validity(self, lab_results: Dict, tfg: float) -> Dict[str, bool]:
        """Verifica vigencia de laboratorios según TFG"""
        validity = {}
        
        # Determinar grupo de validez según TFG
        if tfg >= 90:
            config = LAB_VALIDITY_CONFIG["g1"]
        elif tfg >= 60:
            config = LAB_VALIDITY_CONFIG["g2"]
        else:
            config = LAB_VALIDITY_CONFIG["g3a"]
        
        # Verificar cada laboratorio
        for lab_name, lab_data in lab_results.items():
            if lab_name not in config:
                continue
                
            validity_days = config[lab_name]
            if isinstance(validity_days, list):
                min_days, max_days = validity_days
                validity[lab_name] = min_days <= lab_data.get("dias_desde_toma", 0) <= max_days
            else:
                validity[lab_name] = lab_data.get("dias_desde_toma", 0) <= validity_days
        
        return validity
