/**
 * Clasificador de riesgo en tiempo real que se integra con las reglas del backend
 */
class RealTimeRiskClassifier {
  constructor(formSelector, displaySelector) {
    this.form = document.querySelector(formSelector);
    this.display = document.querySelector(displaySelector);
    this.debounceTimeout = null;
    this.debounceDelay = 300; // ms
    this.apiBridge = apiRulesBridge;
    
    this.init();
  }
  
  /**
   * Inicializa el clasificador
   */
  init() {
    if (!this.form || !this.display) {
      console.error('No se encontraron los elementos necesarios para el clasificador de riesgo');
      return;
    }
    
    // Obtener todos los campos relevantes para la clasificación
    const relevantFields = this.form.querySelectorAll('input, select, textarea');
    
    // Añadir listener a cada campo
    relevantFields.forEach(field => {
      field.addEventListener('input', this.handleInputChange.bind(this));
      field.addEventListener('change', this.handleInputChange.bind(this));
    });
    
    // Clasificación inicial si hay datos
    this.updateRiskClassification();
    
    console.log('Clasificador de riesgo en tiempo real inicializado');
  }
  
  /**
   * Maneja cambios en los campos del formulario
   */
  handleInputChange() {
    // Usar debounce para evitar llamadas excesivas
    clearTimeout(this.debounceTimeout);
    this.debounceTimeout = setTimeout(() => {
      this.updateRiskClassification();
    }, this.debounceDelay);
  }
  
  /**
   * Actualiza la clasificación de riesgo
   */
  async updateRiskClassification() {
    try {
      // Mostrar indicador de carga
      this.showLoadingState();
      
      // Recopilar datos del formulario
      const formData = this.collectFormData();
      
      // Si no hay suficientes datos para clasificar, salir
      if (!this.hasMinimumRequiredData(formData)) {
        this.showIncompleteDataMessage();
        return;
      }
      
      // Obtener clasificación desde el backend
      const classification = await this.apiBridge.classifyRisk(formData);
      
      // Mostrar resultados
      this.updateDisplay(classification);
      
      // Si hay clasificación completa, programar seguimiento
      if (classification.riskLevel) {
        const followUp = await this.apiBridge.scheduleFollowUp(formData);
        this.updateFollowUpDisplay(followUp);
      }
      
    } catch (error) {
      console.error('Error al actualizar clasificación:', error);
      this.showErrorState(error.message);
    }
  }
  
  /**
   * Recopila datos del formulario
   * @returns {Object} Datos del formulario
   */
  collectFormData() {
    const formData = {};
    
    // Extraer valores de todos los campos con nombre
    Array.from(this.form.elements).forEach(element => {
      if (element.name) {
        if (element.type === 'checkbox') {
          formData[element.name] = element.checked;
        } else if (element.type === 'radio') {
          if (element.checked) {
            formData[element.name] = element.value;
          }
        } else {
          formData[element.name] = element.value;
        }
      }
    });
    
    return formData;
  }
  
  /**
   * Verifica si hay datos mínimos para clasificar
   * @param {Object} data - Datos del formulario
   * @returns {Boolean} - True si hay datos suficientes
   */
  hasMinimumRequiredData(data) {
    // Ajustar según los campos mínimos requeridos por tus reglas
    const requiredFields = ['edad', 'sexo'];
    
    return requiredFields.every(field => {
      return data[field] !== undefined && data[field] !== '';
    });
  }
  
  /**
   * Muestra estado de carga
   */
  showLoadingState() {
    if (!this.display) return;
    
    this.display.innerHTML = `
      <div class="loading-indicator">
        <div class="spinner"></div>
        <p>Calculando riesgo cardiovascular...</p>
      </div>
    `;
  }
  
  /**
   * Muestra mensaje de datos incompletos
   */
  showIncompleteDataMessage() {
    if (!this.display) return;
    
    this.display.innerHTML = `
      <div class="incomplete-data-message">
        <p>Se requieren más datos para calcular el riesgo cardiovascular.</p>
        <p>Complete al menos edad y sexo del paciente.</p>
      </div>
    `;
  }
  
  /**
   * Muestra estado de error
   */
  showErrorState(message) {
    if (!this.display) return;
    
    this.display.innerHTML = `
      <div class="error-state">
        <p>Error al calcular riesgo: ${message}</p>
        <button class="retry-button">Reintentar</button>
      </div>
    `;
    
    // Añadir funcionalidad al botón de reintentar
    this.display.querySelector('.retry-button').addEventListener('click', () => {
      this.updateRiskClassification();
    });
  }
  
  /**
   * Actualiza la visualización con los resultados
   * @param {Object} classification - Datos de clasificación
   */
  updateDisplay(classification) {
    if (!this.display) return;
    
    // Colores según nivel de riesgo
    const riskColors = {
      'bajo': '#4caf50',
      'moderado': '#ff9800',
      'alto': '#f44336',
      'muy alto': '#9c27b0'
    };
    
    const riskLevel = classification.riskLevel?.toLowerCase() || 'desconocido';
    const color = riskColors[riskLevel] || '#9e9e9e';
    
    this.display.innerHTML = `
      <div class="risk-classification" style="border-color: ${color}">
        <h3>Clasificación de Riesgo Cardiovascular</h3>
        <div class="risk-level" style="background-color: ${color}">
          ${classification.riskLevel || 'No determinado'}
        </div>
        <div class="risk-details">
          ${classification.details ? `<p>${classification.details}</p>` : ''}
          ${classification.recommendations ? `
            <div class="recommendations">
              <h4>Recomendaciones:</h4>
              <ul>
                ${classification.recommendations.map(rec => `<li>${rec}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
        </div>
      </div>
    `;
  }
  
  /**
   * Actualiza la visualización del seguimiento
   * @param {Object} followUp - Datos de seguimiento
   */
  updateFollowUpDisplay(followUp) {
    if (!this.display) return;
    
    // Buscar el contenedor de clasificación de riesgo
    const riskClassification = this.display.querySelector('.risk-classification');
    if (!riskClassification) return;
    
    // Crear elemento para mostrar información de seguimiento
    const followUpElement = document.createElement('div');
    followUpElement.className = 'follow-up-info';
    followUpElement.innerHTML = `
      <h4>Programa de Seguimiento:</h4>
      <ul>
        ${followUp.nextLabDate ? `<li>Próximos laboratorios: ${followUp.nextLabDate}</li>` : ''}
        ${followUp.nextAppointment ? `<li>Próxima cita médica: ${followUp.nextAppointment}</li>` : ''}
      </ul>
    `;
    
    // Añadir al final de la clasificación de riesgo
    riskClassification.appendChild(followUpElement);
  }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  const riskClassifier = new RealTimeRiskClassifier('#patient-form', '#risk-classification-display');
});