"""
Cliente para interactuar con la API de Google Gemini
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# En una implementación real, importaríamos google.generativeai
# Este es un ejemplo simplificado para ilustrar la estructura

class GeminiClient:
    """Cliente para interactuar con la API de Google Gemini."""
    
    def __init__(self):
        """Inicializa el cliente con la API key y configura el modelo."""
        self.api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not self.api_key:
            logging.warning("API key de Google Gemini no configurada, usando modo simulado")
        
        # En una implementación real, configuramos el cliente de Gemini aquí
        self.use_simulation = not self.api_key
    
    def generate_report(self, patient_data: Dict[str, Any], base_report: str) -> str:
        """
        Genera un informe médico utilizando la API de Gemini.
        
        Args:
            patient_data: Datos del paciente en formato diccionario
            base_report: Informe base generado por la lógica convencional
            
        Returns:
            Informe HTML enriquecido por la IA
        """
        if self.use_simulation:
            return self._generate_simulated_report(patient_data, base_report)
        
        try:
            # Aquí iría la integración real con Gemini API
            # Ejemplo:
            # response = genai.generate_content(
            #    prompt=self._create_prompt(patient_data, base_report)
            # )
            # return self._format_response(response)
            
            # Por ahora, usamos la simulación
            return self._generate_simulated_report(patient_data, base_report)
            
        except Exception as e:
            logging.error(f"Error al generar informe con Gemini: {str(e)}")
            # Si falla la API, devolvemos el informe base
            return base_report
    
    def _create_prompt(self, patient_data: Dict[str, Any], base_report: str) -> str:
        """
        Crea el prompt para la API de Gemini.
        
        Args:
            patient_data: Datos del paciente
            base_report: Informe base
            
        Returns:
            Prompt formateado para la API
        """
        return f"""
        Eres un especialista en nefrología generando un informe médico.
        
        DATOS DEL PACIENTE:
        {json.dumps(patient_data, indent=2, ensure_ascii=False)}
        
        INFORME BASE:
        {base_report}
        
        Amplía este informe con un análisis médico detallado sobre la enfermedad renal.
        Incluye interpretación de valores de laboratorio, posibles complicaciones,
        y recomendaciones de tratamiento basadas en las guías KDIGO.
        Formato el resultado en HTML con estilos profesionales.
        """
    
    def _generate_simulated_report(self, patient_data: Dict[str, Any], base_report: str) -> str:
        """
        Genera un informe simulado cuando no hay API key disponible.
        
        Args:
            patient_data: Datos del paciente
            base_report: Informe base
            
        Returns:
            Informe HTML simulado
        """
        nombre = patient_data.get('nombre', 'Paciente')
        edad = patient_data.get('edad', 'N/A')
        sexo = patient_data.get('sexo', 'N/A')
        creatinina = patient_data.get('creatinina', 'N/A')
        
        # Simulamos un informe más elaborado
        return f"""
        <div class="ai-report">
            <h1>Informe Médico: Evaluación Renal</h1>
            <div class="patient-info">
                <h2>Datos del Paciente</h2>
                <p><strong>Nombre:</strong> {nombre}</p>
                <p><strong>Edad:</strong> {edad} años</p>
                <p><strong>Sexo:</strong> {sexo}</p>
            </div>
            
            <div class="medical-evaluation">
                <h2>Evaluación Médica</h2>
                {base_report}
                
                <h3>Análisis Ampliado (Simulación)</h3>
                <p>Este es un informe simulado generado localmente. En un entorno de producción, 
                esta sección sería generada por la API de Google Gemini con un análisis más completo
                y personalizado.</p>
                
                <p>La evaluación muestra que el paciente presenta valores de creatinina de {creatinina} mg/dL.
                Es importante considerar una evaluación completa de la función renal que incluya también
                proteinuria, análisis de sedimento urinario y estudios de imagen.</p>
                
                <div class="recommendations">
                    <h3>Recomendaciones Generales</h3>
                    <ul>
                        <li>Control periódico de la función renal cada 3-6 meses</li>
                        <li>Mantener una dieta baja en sodio y proteínas según sea apropiado</li>
                        <li>Control estricto de presión arterial y glucemia</li>
                        <li>Evitar medicamentos nefrotóxicos</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer">
                <p>Informe generado el {datetime.now().strftime('%d/%m/%Y')} (versión simulada)</p>
            </div>
        </div>
        """
        
    def process_advanced_evaluation(self, payload: Dict[str, Any]) -> str:
        """
        Procesa un payload estructurado y genera un informe médico avanzado.
        
        Args:
            payload: Estructura de datos con información del paciente,
                    laboratorios, diagnósticos, metas y plan de seguimiento
                    
        Returns:
            Informe HTML avanzado estructurado
        """
        if self.use_simulation:
            return self._generate_advanced_simulation(payload)
            
        try:
            # Aquí iría la integración real con Gemini API
            # Ejemplo:
            # response = genai.generate_content(
            #    prompt=self._create_advanced_prompt(payload)
            # )
            # return self._format_response(response)
            
            # Por ahora, usamos la simulación
            return self._generate_advanced_simulation(payload)
            
        except Exception as e:
            logging.error(f"Error al generar informe avanzado con Gemini: {str(e)}")
            # Si falla, devolvemos un informe de error
            return f"""
            <div class="error-report">
                <h1>Error al generar el informe</h1>
                <p>Se ha producido un error al procesar los datos del paciente.</p>
                <p>Por favor, inténtelo de nuevo más tarde.</p>
            </div>
            """
    
    def _create_advanced_prompt(self, payload: Dict[str, Any]) -> str:
        """
        Crea un prompt avanzado para la API de Gemini.
        
        Args:
            payload: Estructura de datos completa del paciente
            
        Returns:
            Prompt formateado para la API
        """
        return f"""
        Eres un especialista en nefrología generando un informe médico detallado.
        
        DATOS COMPLETOS:
        {json.dumps(payload, indent=2, ensure_ascii=False)}
        
        Genera un informe médico completo y estructurado en HTML que incluya:
        
        1. Datos del paciente
        2. Resultados de laboratorio relevantes
        3. Evaluación de la función renal (TFG y estadio ERC)
        4. Evaluación del riesgo cardiovascular
        5. Análisis de comorbilidades
        6. Metas terapéuticas (indicando si se cumplen o no)
        7. Plan de seguimiento recomendado
        8. Recomendaciones específicas según la condición del paciente
        
        Utiliza las guías KDIGO más recientes y asegúrate de que el informe sea
        claro, preciso y profesional. Formatea el resultado en HTML con estilos
        que faciliten la lectura y comprensión.
        """
    
    def _generate_advanced_simulation(self, payload: Dict[str, Any]) -> str:
        """
        Genera un informe avanzado simulado basado en el payload completo.
        
        Args:
            payload: Estructura de datos completa del paciente
            
        Returns:
            Informe HTML simulado avanzado
        """
        # Extraer datos del paciente
        paciente = payload.get("paciente", {})
        nombre = paciente.get("nombre", "Paciente sin nombre")
        edad = paciente.get("edad", "N/A")
        sexo = paciente.get("sexo", "N/A")
        peso = paciente.get("peso", "N/A")
        talla = paciente.get("talla", "N/A")
        imc = paciente.get("imc", "N/A")
        
        # Extraer evaluación diagnóstica
        diagnosticos = payload.get("evaluacion_diagnosticos", {})
        tfg = diagnosticos.get("tfg_valor", "N/A")
        etapa_erc = diagnosticos.get("erc_estadio", "No determinada")
        riesgo_cv = diagnosticos.get("riesgo_cardiovascular", "No determinado")
        comorbilidades = diagnosticos.get("comorbilidades", [])
        
        # Extraer metas terapéuticas
        metas = payload.get("metas_terapeuticas", [])
        
        # Extraer plan de seguimiento
        seguimiento = payload.get("plan_seguimiento", {})
        fecha_labs = seguimiento.get("laboratorios", "No especificada")
        fecha_consulta = seguimiento.get("consulta_control", "No especificada")
        
        # Generar informe HTML simulado
        return f"""
        <div class="advanced-report">
            <header class="report-header">
                <h1>Informe Médico Avanzado: Evaluación ERC</h1>
                <p class="report-date">Fecha: {datetime.now().strftime('%d/%m/%Y')}</p>
            </header>
            
            <section class="patient-section">
                <h2>Datos del Paciente</h2>
                <div class="patient-data">
                    <p><strong>Nombre:</strong> {nombre}</p>
                    <p><strong>Edad:</strong> {edad} años</p>
                    <p><strong>Sexo:</strong> {sexo}</p>
                    <p><strong>Peso:</strong> {peso} kg</p>
                    <p><strong>Talla:</strong> {talla} cm</p>
                    <p><strong>IMC:</strong> {imc} kg/m {" (Obesidad)" if isinstance(imc, (int, float)) and imc >= 30 else ""}</p>
                </div>
            </section>
            
            <section class="evaluation-section">
                <h2>Evaluación Renal</h2>
                <div class="evaluation-data">
                    <p><strong>Tasa de Filtración Glomerular (TFG):</strong> {tfg} ml/min/1.73m</p>
                    <p><strong>Clasificación ERC:</strong> <span class="highlight">{etapa_erc.upper() if isinstance(etapa_erc, str) else etapa_erc}</span></p>
                    <p><strong>Riesgo Cardiovascular:</strong> <span class="highlight">{riesgo_cv.replace('_', ' ').title() if isinstance(riesgo_cv, str) else riesgo_cv}</span></p>
                </div>
                
                <div class="comorbidities">
                    <h3>Comorbilidades</h3>
                    <ul>
                        {'' if not comorbilidades else ''.join([f'<li>{c}</li>' for c in comorbilidades])}
                        {'' if comorbilidades else '<li>No se registran comorbilidades</li>'}
                    </ul>
                </div>
            </section>
            
            <section class="goals-section">
                <h2>Metas Terapéuticas</h2>
                <table class="goals-table">
                    <thead>
                        <tr>
                            <th>Parámetro</th>
                            <th>Valor Actual</th>
                            <th>Meta</th>
                            <th>Estado</th>
                        </tr>
                    </thead>
                    <tbody>
                        {'' if not metas else ''.join([f'''
                        <tr>
                            <td>{meta.get('parametro', '')}</td>
                            <td>{meta.get('valor_actual', '')}</td>
                            <td>{meta.get('meta', '')}</td>
                            <td class="{'goal-met' if meta.get('cumple', False) else 'goal-pending'}">
                                {(' Cumple' if meta.get('cumple', False) else ' No Cumple')}
                            </td>
                        </tr>
                        ''' for meta in metas])}
                        {'' if metas else '<tr><td colspan="4">No se han definido metas terapéuticas</td></tr>'}
                    </tbody>
                </table>
            </section>
            
            <section class="follow-up-section">
                <h2>Plan de Seguimiento</h2>
                <div class="follow-up-data">
                    <p><strong>Próximos Laboratorios:</strong> {fecha_labs}</p>
                    <p><strong>Próxima Consulta:</strong> {fecha_consulta}</p>
                </div>
                
                <div class="recommendations">
                    <h3>Recomendaciones Generales</h3>
                    <ul>
                        <li>Control periódico de la función renal según el plan establecido</li>
                        <li>Mantener una dieta baja en sodio {'' if tfg and tfg < 60 else 'si es necesario'}</li>
                        <li>Control estricto de presión arterial {f'(meta: {metas[0]["meta"]} mmHg)' if metas and metas[0].get('parametro') == 'Presión Arterial' else ''}</li>
                        <li>Evitar medicamentos nefrotóxicos (AINEs, aminoglucósidos)</li>
                        {'<li>Control glicémico estricto</li>' if 'Diabetes Mellitus' in comorbilidades else ''}
                    </ul>
                </div>
            </section>
            
            <footer class="report-footer">
                <p>Informe generado el {datetime.now().strftime('%d/%m/%Y')} (versión simulada)</p>
                <p class="note">Este informe es generado automáticamente y debe ser validado por un profesional médico.</p>
            </footer>
            
            <style>
                .advanced-report {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .report-header {
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }
                section {
                    margin-bottom: 25px;
                    padding: 15px;
                    background: #f9f9f9;
                    border-radius: 5px;
                }
                h2 {
                    color: #2980b9;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 8px;
                }
                .highlight {
                    font-weight: bold;
                    color: #e74c3c;
                }
                .goals-table {
                    width: 100%;
                    border-collapse: collapse;
                }
                .goals-table th, .goals-table td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                .goals-table th {
                    background-color: #f2f2f2;
                }
                .goal-met {
                    color: green;
                    font-weight: bold;
                }
                .goal-pending {
                    color: red;
                }
                ul {
                    padding-left: 20px;
                }
                .report-footer {
                    margin-top: 30px;
                    border-top: 1px solid #ddd;
                    padding-top: 10px;
                    font-size: 0.9em;
                    color: #777;
                }
                .note {
                    font-style: italic;
                }
            </style>
        </div>
        """
