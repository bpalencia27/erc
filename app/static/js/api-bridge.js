/**
 * Puente de API para conectar con las reglas existentes en el backend Python
 */
class ApiRulesBridge {
  constructor() {
    this.endpoints = {
      riskClassification: '/api/risk/classify',
      therapeuticGoals: '/api/goals/evaluate',
      followUpSchedule: '/api/followup/schedule',
      dataParsing: '/api/data/parse'
    };
    this.cachedResponses = new Map();
  }

  /**
   * Clasifica el riesgo cardiovascular usando las reglas del backend
   * @param {Object} patientData - Datos del paciente
   * @returns {Promise<Object>} - Clasificación de riesgo
   */
  async classifyRisk(patientData) {
    try {
      const response = await this.postData(this.endpoints.riskClassification, patientData);
      return response;
    } catch (error) {
      console.error('Error al clasificar riesgo:', error);
      throw new Error('No se pudo obtener la clasificación de riesgo');
    }
  }

  /**
   * Evalúa las metas terapéuticas según reglas del consenso médico
   * @param {Object} patientData - Datos completos del paciente y sus métricas
   * @returns {Promise<Object>} - Estado de metas (no cumple, mínimo, satisfactorio, sobresaliente)
   */
  async evaluateTherapeuticGoals(patientData) {
    try {
      const response = await this.postData(this.endpoints.therapeuticGoals, patientData);
      return response;
    } catch (error) {
      console.error('Error al evaluar metas terapéuticas:', error);
      throw new Error('No se pudieron evaluar las metas terapéuticas');
    }
  }

  /**
   * Programa seguimiento de laboratorios y próxima cita
   * @param {Object} patientData - Datos del paciente y clasificación
   * @returns {Promise<Object>} - Fechas recomendadas de seguimiento
   */
  async scheduleFollowUp(patientData) {
    try {
      const response = await this.postData(this.endpoints.followUpSchedule, patientData);
      return response;
    } catch (error) {
      console.error('Error al programar seguimiento:', error);
      throw new Error('No se pudo programar el seguimiento');
    }
  }

  /**
   * Extrae datos de archivos usando el parser del backend
   * @param {FormData} formData - FormData con el archivo a procesar
   * @returns {Promise<Object>} - Datos extraídos
   */
  async parseFileData(formData) {
    try {
      const response = await fetch(this.endpoints.dataParsing, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      });
      
      if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error al extraer datos del archivo:', error);
      throw new Error('No se pudieron extraer los datos del archivo');
    }
  }

  /**
   * Método genérico para enviar datos al backend
   * @private
   */
  async postData(url, data) {
    // Crear clave de cache
    const cacheKey = `${url}-${JSON.stringify(data)}`;
    
    // Verificar si tenemos una respuesta en cache para solicitudes idénticas
    if (this.cachedResponses.has(cacheKey)) {
      return this.cachedResponses.get(cacheKey);
    }
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': this.getCsrfToken()
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status}`);
      }
      
      const responseData = await response.json();
      
      // Almacenar en cache para futuras solicitudes idénticas
      this.cachedResponses.set(cacheKey, responseData);
      
      return responseData;
    } catch (error) {
      console.error(`Error al comunicarse con ${url}:`, error);
      throw error;
    }
  }

  /**
   * Obtiene el token CSRF de las cookies
   * @private
   */
  getCsrfToken() {
    const name = 'csrftoken';
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
  }
}

// Exportar instancia única
const apiRulesBridge = new ApiRulesBridge();