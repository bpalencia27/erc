/**
 * Componente mejorado para subida y extracción de archivos
 */
class FileUploader {
  constructor(uploaderId, previewerId) {
    this.uploader = document.getElementById(uploaderId);
    this.previewer = document.getElementById(previewerId);
    this.fileInput = null;
    this.dropZone = null;
    this.apiBridge = apiRulesBridge;
    this.progressInterval = null;
    
    this.init();
  }
  
  /**
   * Inicializa el componente
   */
  init() {
    if (!this.uploader) {
      console.error("No se encontró el elemento uploader");
      return;
    }
    
    // Crear estructura del uploader
    this.createUploaderStructure();
    
    // Configurar event listeners
    this.setupEventListeners();
    
    console.log("Uploader de archivos inicializado");
  }
  
  /**
   * Crea la estructura HTML del uploader
   */
  createUploaderStructure() {
    this.uploader.innerHTML = `
      <div class="file-drop-zone">
        <input type="file" class="file-input" accept=".pdf,.txt" />
        <div class="drop-zone-prompt">
          <i class="upload-icon"></i>
          <p>Arrastra un archivo PDF o TXT aquí</p>
          <p>o</p>
          <button type="button" class="browse-button">Seleccionar archivo</button>
        </div>
      </div>
      <div class="upload-error-message hidden"></div>
      <div class="upload-progress hidden">
        <div class="progress-bar">
          <div class="progress-fill"></div>
        </div>
        <p class="progress-text">Procesando archivo...</p>
      </div>
    `;
    
    this.fileInput = this.uploader.querySelector(".file-input");
    this.dropZone = this.uploader.querySelector(".file-drop-zone");
    this.errorMessage = this.uploader.querySelector(".upload-error-message");
    this.progressContainer = this.uploader.querySelector(".upload-progress");
    this.progressBar = this.uploader.querySelector(".progress-fill");
    this.progressText = this.uploader.querySelector(".progress-text");
  }
  
  /**
   * Configura los event listeners
   */
  setupEventListeners() {
    // Click en botón de seleccionar archivo
    this.uploader.querySelector(".browse-button").addEventListener("click", () => {
      this.fileInput.click();
    });
    
    // Cambio en input de archivo
    this.fileInput.addEventListener("change", (e) => {
      if (e.target.files.length > 0) {
        this.handleFile(e.target.files[0]);
      }
    });
    
    // Eventos de drag and drop
    this.dropZone.addEventListener("dragover", (e) => {
      e.preventDefault();
      this.dropZone.classList.add("drag-over");
    });
    
    this.dropZone.addEventListener("dragleave", () => {
      this.dropZone.classList.remove("drag-over");
    });
    
    this.dropZone.addEventListener("drop", (e) => {
      e.preventDefault();
      this.dropZone.classList.remove("drag-over");
      
      if (e.dataTransfer.files.length > 0) {
        this.handleFile(e.dataTransfer.files[0]);
      }
    });
  }
  
  /**
   * Verifica si el tipo de archivo es válido
   * @param {File} file - Archivo a verificar
   * @returns {Boolean} - True si es válido
   */
  isValidFileType(file) {
    const validTypes = [
      "application/pdf",
      "text/plain"
    ];
    return validTypes.includes(file.type);
  }
  
  /**
   * Maneja el archivo seleccionado
   * @param {File} file - Archivo seleccionado
   */
  async handleFile(file) {
    // Verificar tipo de archivo
    if (!this.isValidFileType(file)) {
      this.showError("Tipo de archivo no válido. Solo se permiten archivos PDF y TXT.");
      return;
    }
    
    try {
      // Mostrar progreso
      this.showProgress();
      
      // Crear FormData para enviar el archivo
      const formData = new FormData();
      formData.append("file", file);
      
      // Enviar archivo al backend para extracción
      const extractedData = await this.apiBridge.parseFileData(formData);
      
      // Ocultar progreso
      this.hideProgress();
      
      // Mostrar datos extraídos
      this.displayExtractedData(extractedData);
      
      // Llenar automáticamente los campos del formulario
      this.fillFormFields(extractedData);
      
    } catch (error) {
      console.error("Error al procesar archivo:", error);
      this.showError("No se pudo procesar el archivo. " + error.message);
    }
  }
  
  /**
   * Muestra un mensaje de error
   * @param {String} message - Mensaje de error
   */
  showError(message) {
    this.hideProgress();
    this.errorMessage.textContent = message;
    this.errorMessage.classList.remove("hidden");
    
    // Ocultar después de 5 segundos
    setTimeout(() => {
      this.errorMessage.classList.add("hidden");
    }, 5000);
  }
  
  /**
   * Muestra el indicador de progreso
   */
  showProgress() {
    this.errorMessage.classList.add("hidden");
    this.progressContainer.classList.remove("hidden");
    this.progressBar.style.width = "0%";
    
    // Animar la barra de progreso
    let progress = 0;
    this.progressInterval = setInterval(() => {
      if (progress < 90) {
        progress += 5;
        this.progressBar.style.width = progress + "%";
      }
    }, 300);
  }
  
  /**
   * Oculta el indicador de progreso
   */
  hideProgress() {
    if (this.progressInterval) {
      clearInterval(this.progressInterval);
    }
    
    // Completar la barra antes de ocultar
    this.progressBar.style.width = "100%";
    
    setTimeout(() => {
      this.progressContainer.classList.add("hidden");
    }, 500);
  }
  
  /**
   * Muestra los datos extraídos
   * @param {Object} data - Datos extraídos
   */
  displayExtractedData(data) {
    if (!this.previewer) return;
    
    this.previewer.innerHTML = `
      <div class="extracted-data-preview">
        <h3>Datos Extraídos:</h3>
        <div class="data-grid">
          ${data.nombre ? `<div class="data-row"><span>Nombre:</span> <strong>${data.nombre}</strong></div>` : ""}
          ${data.sexo ? `<div class="data-row"><span>Sexo:</span> <strong>${data.sexo}</strong></div>` : ""}
          ${data.edad ? `<div class="data-row"><span>Edad:</span> <strong>${data.edad} años</strong></div>` : ""}
          ${data.factoresRiesgo && data.factoresRiesgo.length ? `
            <div class="data-row"><span>Factores de riesgo:</span> <strong>${data.factoresRiesgo.join(", ")}</strong></div>
          ` : ""}
        </div>
        <div class="data-actions">
          <button type="button" class="edit-data-btn">Editar datos</button>
          <button type="button" class="apply-data-btn">Aplicar datos</button>
        </div>
      </div>
    `;
    
    this.previewer.querySelector(".edit-data-btn").addEventListener("click", () => {
      this.showDataEditor(data);
    });
    
    this.previewer.querySelector(".apply-data-btn").addEventListener("click", () => {
      this.fillFormFields(data);
    });
  }
  
  /**
   * Muestra editor para los datos extraídos
   * @param {Object} data - Datos extraídos
   */
  showDataEditor(data) {
    this.previewer.innerHTML = `
      <div class="data-editor">
        <h3>Editar Datos Extraídos:</h3>
        <form class="edit-data-form">
          <div class="form-group">
            <label for="edit-nombre">Nombre:</label>
            <input type="text" id="edit-nombre" value="${data.nombre || ""}" />
          </div>
          <div class="form-group">
            <label for="edit-sexo">Sexo:</label>
            <select id="edit-sexo">
              <option value="">Seleccionar</option>
              <option value="Masculino" ${data.sexo === "Masculino" ? "selected" : ""}>Masculino</option>
              <option value="Femenino" ${data.sexo === "Femenino" ? "selected" : ""}>Femenino</option>
            </select>
          </div>
          <div class="form-group">
            <label for="edit-edad">Edad:</label>
            <input type="number" id="edit-edad" value="${data.edad || ""}" min="0" max="120" />
          </div>
          <div class="form-group">
            <label>Factores de riesgo:</label>
            <div class="risk-factors-checkboxes">
              ${this.generateRiskFactorsCheckboxes(data.factoresRiesgo || [])}
            </div>
          </div>
          <div class="form-actions">
            <button type="button" class="save-edits-btn">Guardar Cambios</button>
            <button type="button" class="cancel-edits-btn">Cancelar</button>
          </div>
        </form>
      </div>
    `;
    
    this.previewer.querySelector(".save-edits-btn").addEventListener("click", () => {
      const editedData = this.collectEditedData();
      this.displayExtractedData(editedData);
    });
    
    this.previewer.querySelector(".cancel-edits-btn").addEventListener("click", () => {
      this.displayExtractedData(data);
    });
  }
  
  /**
   * Genera checkboxes para factores de riesgo
   * @param {Array} selectedFactors - Factores seleccionados
   * @returns {String} - HTML de checkboxes
   */
  generateRiskFactorsCheckboxes(selectedFactors) {
    const commonFactors = [
      "diabetes", "hipertensión", "obesidad", "tabaquismo", 
      "dislipidemia", "enfermedad cardiovascular"
    ];
    
    return commonFactors.map(factor => {
      const isChecked = selectedFactors.includes(factor);
      return `
        <div class="checkbox-item">
          <input type="checkbox" id="factor-${factor}" value="${factor}" ${isChecked ? "checked" : ""} />
          <label for="factor-${factor}">${factor.charAt(0).toUpperCase() + factor.slice(1)}</label>
        </div>
      `;
    }).join("");
  }
  
  /**
   * Recopila los datos editados
   * @returns {Object} - Datos editados
   */
  collectEditedData() {
    const editedData = {
      nombre: this.previewer.querySelector("#edit-nombre").value,
      sexo: this.previewer.querySelector("#edit-sexo").value,
      edad: this.previewer.querySelector("#edit-edad").value,
      factoresRiesgo: []
    };
    
    // Recopilar factores de riesgo seleccionados
    this.previewer.querySelectorAll(".risk-factors-checkboxes input:checked").forEach(checkbox => {
      editedData.factoresRiesgo.push(checkbox.value);
    });
    
    return editedData;
  }
  
  /**
   * Llena los campos del formulario con los datos extraídos
   * @param {Object} data - Datos extraídos
   */
  fillFormFields(data) {
    // Nombre
    const nameField = document.querySelector("input[name=\"nombre\"]");
    if (nameField && data.nombre) {
      nameField.value = data.nombre;
      // Disparar evento para actualizar validaciones
      nameField.dispatchEvent(new Event("input", { bubbles: true }));
    }
    
    // Sexo
    if (data.sexo) {
      const sexoValue = data.sexo.toLowerCase().startsWith("m") ? "m" : "f";
      const sexoSelect = document.querySelector("select[name=\"sexo\"]");
      if (sexoSelect) {
        sexoSelect.value = sexoValue;
        sexoSelect.dispatchEvent(new Event("change", { bubbles: true }));
      }
    }
    
    // Edad
    const edadField = document.querySelector("input[name=\"edad\"]");
    if (edadField && data.edad) {
      edadField.value = data.edad;
      edadField.dispatchEvent(new Event("input", { bubbles: true }));
    }
    
    // Factores de riesgo
    if (data.factoresRiesgo && data.factoresRiesgo.length) {
      if (data.factoresRiesgo.includes("diabetes")) {
        const dmCheckbox = document.querySelector("#dm2");
        if (dmCheckbox) {
          dmCheckbox.checked = true;
          dmCheckbox.dispatchEvent(new Event("change", { bubbles: true }));
        }
      }
      
      if (data.factoresRiesgo.includes("hipertensión")) {
        const htaCheckbox = document.querySelector("#hta");
        if (htaCheckbox) {
          htaCheckbox.checked = true;
          htaCheckbox.dispatchEvent(new Event("change", { bubbles: true }));
        }
      }
    }
    
    // Disparar evento para actualizar la clasificación de riesgo
    document.dispatchEvent(new CustomEvent("patient-data-updated", { detail: data }));
  }
}

// Inicializar cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", () => {
  const fileUploader = new FileUploader("file-uploader", "data-preview");
});
