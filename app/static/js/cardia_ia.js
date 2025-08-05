document.addEventListener('DOMContentLoaded', function() {
    // All the application's JavaScript logic will go inside this function.
    console.log("DOM fully loaded and parsed. Initializing app logic...");

    // Referencias a elementos DOM
    const form = document.getElementById('clinical-form');
    const generateReportBtn = document.getElementById('generate-report-btn');
    const reportOutput = document.getElementById('report-output');
    const reportOutputContainer = document.getElementById('report-output-container');
    const reportPlaceholder = document.getElementById('report-placeholder');
    const reportLoader = document.getElementById('report-loader');
    const riskLevelIndicator = document.getElementById('risk-level-indicator');
    const riskFactorsSummary = document.getElementById('risk-factors-summary');
    const goalsPreviewContent = document.getElementById('goals-preview-content');
    const fileUpload = document.getElementById('lab-file-upload');
    const fileLoader = document.getElementById('file-loader');
    const loadedLabsContainer = document.getElementById('loaded-labs-container');
    const manualLabToggle = document.getElementById('manual-lab-toggle');
    const manualLabInputs = document.getElementById('manual-lab-inputs');
    const labUploadContainer = document.getElementById('lab-upload-container');
    const addPaBtn = document.getElementById('add-pa-btn');
    const paContainer = document.getElementById('pa-container');
    const addMedicamentoBtn = document.getElementById('add-medicamento-btn');
    const medicamentosContainer = document.getElementById('medicamentos-container');
    const quickMedBtns = document.querySelectorAll('.quick-med-btn');
    const highContrastToggle = document.getElementById('high-contrast-toggle');
    const dmCheckbox = document.getElementById('dm-checkbox');
    const duracionDmContainer = document.getElementById('duracion-dm-container');
    const ercCheckbox = document.getElementById('erc-checkbox');
    const ercAlertIcon = document.getElementById('erc-alert-icon');
    const evalFragilidadBtn = document.getElementById('eval-fragilidad-btn');
    const fragilityModal = document.getElementById('fragility-modal');
    const closeFragilityModal = document.getElementById('close-fragility-modal');
    const friedCriteria = document.getElementById('fried-criteria');
    const frailtyStatus = document.getElementById('frailty-status');
    const frailtyMarker = document.getElementById('frailty-marker');
    const fragilCheckbox = document.getElementById('fragil');
    const alertModal = document.getElementById('alert-modal');
    const alertTitle = document.getElementById('alert-title');
    const alertMessage = document.getElementById('alert-message');
    const closeAlertModal = document.getElementById('close-alert-modal');
    const openHistoryBtn = document.getElementById('open-history-btn');
    const historyModal = document.getElementById('history-modal');
    const closeHistoryModal = document.getElementById('close-history-modal');
    const patientHistoryList = document.getElementById('patient-history-list');
    const printReportBtn = document.getElementById('print-report-btn');
    const copyReportBtn = document.getElementById('copy-report-btn');
    const predialysisSection = document.getElementById('predialysis-section');
    const pesoInput = document.getElementById('peso');
    const tallaInput = document.getElementById('talla');
    const imcInput = document.getElementById('imc');
    const creatininaInput = document.getElementById('creatinina');
    const tfgDisplay = document.getElementById('tfg-display');
    const creatininaDateInput = document.getElementById('creatinina_date');
    const sexoInput = document.getElementById('sexo');
    const edadInput = document.getElementById('edad');

    // Estado global de la aplicación
    const appState = {
        highContrast: false,
        patientHistory: [],
        labResults: {},
        fileContents: {},
        currentPatient: null,
        riskLevel: null
    };

    // Inicializar la fecha de hoy en el campo de fecha de creatinina
    const today = new Date();
    const formattedDate = today.toISOString().split('T')[0];
    if (creatininaDateInput) {
        creatininaDateInput.value = formattedDate;
    }

    // Cargar historial de pacientes desde localStorage
    function loadPatientHistory() {
        const savedHistory = localStorage.getItem('patientHistory');
        if (savedHistory) {
            try {
                appState.patientHistory = JSON.parse(savedHistory);
                updatePatientHistoryUI();
            } catch (e) {
                console.error('Error loading patient history:', e);
            }
        }
    }

    // Guardar historial de pacientes en localStorage
    function savePatientHistory() {
        try {
            localStorage.setItem('patientHistory', JSON.stringify(appState.patientHistory));
        } catch (e) {
            console.error('Error saving patient history:', e);
            showAlert('Error', 'No se pudo guardar el historial de pacientes en el almacenamiento local.');
        }
    }

    // Actualizar UI del historial de pacientes
    function updatePatientHistoryUI() {
        if (!patientHistoryList) return;
        
        if (appState.patientHistory.length === 0) {
            patientHistoryList.innerHTML = '<p class="text-sm text-gray-500">No hay pacientes guardados.</p>';
            return;
        }

        patientHistoryList.innerHTML = '';
        appState.patientHistory.forEach((patient, index) => {
            const patientCard = document.createElement('div');
            patientCard.className = 'bg-white rounded-lg p-3 shadow-sm border border-gray-100';
            
            const dateStr = new Date(patient.timestamp).toLocaleDateString('es-ES', {
                day: 'numeric', month: 'short', year: 'numeric'
            });
            
            patientCard.innerHTML = `
                <div class="flex justify-between items-center">
                    <div>
                        <h4 class="font-bold">${patient.nombre}</h4>
                        <p class="text-sm text-gray-500">${dateStr} · ${patient.edad} años · ${patient.sexo === 'm' ? 'Masculino' : 'Femenino'}</p>
                    </div>
                    <div class="flex gap-2">
                        <button class="load-patient-btn text-primary hover:text-primary-light p-1" data-index="${index}" title="Cargar paciente">
                            <i class="fas fa-arrow-right-to-bracket"></i>
                        </button>
                        <button class="delete-patient-btn text-red-500 hover:text-red-600 p-1" data-index="${index}" title="Eliminar paciente">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </div>
            `;
            patientHistoryList.appendChild(patientCard);
        });

        // Agregar event listeners a los botones
        document.querySelectorAll('.load-patient-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const index = parseInt(this.dataset.index);
                loadPatientFromHistory(index);
                closeHistoryModal.click();
            });
        });

        document.querySelectorAll('.delete-patient-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const index = parseInt(this.dataset.index);
                appState.patientHistory.splice(index, 1);
                savePatientHistory();
                updatePatientHistoryUI();
            });
        });
    }

    // Cargar paciente desde el historial
    function loadPatientFromHistory(index) {
        const patient = appState.patientHistory[index];
        if (!patient) return;

        // Poblar el formulario con los datos del paciente
        form.reset(); // Limpiar el formulario primero
        
        // Datos básicos
        document.getElementById('nombre').value = patient.nombre || '';
        document.getElementById('edad').value = patient.edad || '';
        document.getElementById('sexo').value = patient.sexo || 'm';
        document.getElementById('peso').value = patient.peso || '';
        document.getElementById('talla').value = patient.talla || '';
        document.getElementById('per_abd').value = patient.perAbdominal || '';
        document.getElementById('imc').value = patient.imc || '';
        
        // Diagnósticos
        if (patient.diagnosticos) {
            document.querySelectorAll('input[name="diagnostico"]').forEach(checkbox => {
                checkbox.checked = patient.diagnosticos.includes(checkbox.value);
            });
            
            if (patient.diagnosticos.includes('DM')) {
                duracionDmContainer.classList.remove('hidden');
                document.getElementById('duracion_dm').value = patient.duracionDM || '';
            }
        }
        
        // Condiciones adicionales
        document.getElementById('ecv_establecida').checked = patient.ecvEstablecida || false;
        document.getElementById('tabaquismo').checked = patient.tabaquismo || false;
        document.getElementById('cond_socioeconomicas').checked = patient.condSocioeconomicas || false;
        document.getElementById('fragil').checked = patient.fragil || false;
        
        // Adherencia
        document.getElementById('adherencia').value = patient.adherencia || 'buena';
        document.getElementById('barreras_acceso').checked = patient.barrerasAcceso || false;
        
        // Laboratorios
        document.getElementById('creatinina').value = patient.creatinina || '';
        
        // Medicamentos
        if (patient.medicamentos && patient.medicamentos.length > 0) {
            medicamentosContainer.innerHTML = '';
            patient.medicamentos.forEach(med => {
                addMedicamento(med.nombre, med.dosis, med.frecuencia);
            });
        }
        
        // Presión arterial
        if (patient.presionArterial && patient.presionArterial.length > 0) {
            paContainer.innerHTML = '';
            patient.presionArterial.forEach(pa => {
                addPresionArterial(pa.sistolica, pa.diastolica, pa.fecha);
            });
        }
        
        // Calcular IMC
        calcularIMC();
        
        // Actualizar el riesgo
        updateRiskAssessment();
    }

    // Agregar un nuevo campo de presión arterial
    function addPresionArterial(sistolica = '', diastolica = '', fecha = formattedDate) {
        const paItem = document.createElement('div');
        paItem.className = 'pa-item grid grid-cols-3 gap-2';
        paItem.innerHTML = `
            <div>
                <label class="font-medium text-xs mb-1 block">Sistólica (mmHg)</label>
                <input type="number" name="pa_sistolica" class="input-field" min="60" max="250" value="${sistolica}" required>
            </div>
            <div>
                <label class="font-medium text-xs mb-1 block">Diastólica (mmHg)</label>
                <input type="number" name="pa_diastolica" class="input-field" min="40" max="180" value="${diastolica}" required>
            </div>
            <div class="flex items-end">
                <input type="date" name="pa_fecha" class="input-field w-4/5" value="${fecha}">
                <button type="button" class="remove-pa-btn ml-1 bg-gray-200 hover:bg-gray-300 text-gray-600 rounded-md p-2"><i class="fas fa-times"></i></button>
            </div>
        `;
        paContainer.appendChild(paItem);
        
        // Agregar event listener al botón de eliminar
        paItem.querySelector('.remove-pa-btn').addEventListener('click', function() {
            paItem.remove();
        });
    }

    // Agregar un nuevo medicamento
    function addMedicamento(nombre = '', dosis = '', frecuencia = '') {
        const medItem = document.createElement('div');
        medItem.className = 'med-item grid grid-cols-3 gap-2';
        medItem.innerHTML = `
            <div>
                <label class="font-medium text-xs mb-1 block">Medicamento</label>
                <input type="text" name="med_nombre" class="input-field" value="${nombre}">
            </div>
            <div>
                <label class="font-medium text-xs mb-1 block">Dosis</label>
                <input type="text" name="med_dosis" class="input-field" value="${dosis}">
            </div>
            <div class="flex items-end">
                <input type="text" name="med_frecuencia" placeholder="Frecuencia" class="input-field w-4/5" value="${frecuencia}">
                <button type="button" class="remove-med-btn ml-1 bg-gray-200 hover:bg-gray-300 text-gray-600 rounded-md p-2"><i class="fas fa-times"></i></button>
            </div>
        `;
        medicamentosContainer.appendChild(medItem);
        
        // Agregar event listener al botón de eliminar
        medItem.querySelector('.remove-med-btn').addEventListener('click', function() {
            medItem.remove();
        });
    }

    // Calcular IMC
    function calcularIMC() {
        const peso = parseFloat(pesoInput.value);
        const talla = parseFloat(tallaInput.value);
        
        if (peso && talla) {
            const tallaMt = talla / 100;
            const imc = peso / (tallaMt * tallaMt);
            imcInput.value = imc.toFixed(1);
        } else {
            imcInput.value = '';
        }
    }

    // Calcular TFG usando Cockcroft-Gault
    function calcularTFG() {
        const creatinina = parseFloat(creatininaInput.value);
        const peso = parseFloat(pesoInput.value);
        const edad = parseInt(edadInput.value);
        const sexo = sexoInput.value;
        
        if (creatinina && peso && edad && sexo) {
            // Fórmula Cockcroft-Gault
            let tfg = ((140 - edad) * peso) / (72 * creatinina);
            // Ajuste para mujeres
            if (sexo === 'f') {
                tfg *= 0.85;
            }
            
            tfgDisplay.value = tfg.toFixed(1) + ' ml/min';
            
            // Mostrar sección de prediálisis si TFG <= 20
            if (tfg <= 20) {
                predialysisSection.classList.remove('hidden');
            } else {
                predialysisSection.classList.add('hidden');
            }
            
            // Actualizar evaluación de riesgo
            updateRiskAssessment();
            
            return tfg;
        } else {
            tfgDisplay.value = '';
            predialysisSection.classList.add('hidden');
            return null;
        }
    }

    // Actualizar evaluación de riesgo
    function updateRiskAssessment() {
        // Obtener valores del formulario
        const tfgValue = calcularTFG();
        const hasDM = dmCheckbox.checked;
        const hasERC = ercCheckbox.checked;
        const hasHTA = document.querySelector('input[value="HTA"]').checked;
        const hasECV = document.getElementById('ecv_establecida').checked;
        const hasTobacco = document.getElementById('tabaquismo').checked;
        
        let riskLevel = 'INCOMPLETO';
        let riskColor = 'bg-gray-400';
        let riskFactors = [];
        
        // Verificar si tenemos suficientes datos
        if (tfgValue !== null) {
            // Contar factores de riesgo
            let factorCount = 0;
            
            if (hasDM) {
                factorCount++;
                riskFactors.push('Diabetes Mellitus');
            }
            
            if (hasERC || tfgValue < 60) {
                factorCount++;
                riskFactors.push('Enfermedad Renal Crónica');
                
                // Mostrar icono de alerta ERC
                ercAlertIcon.classList.remove('hidden');
                ercCheckbox.checked = true;
            } else {
                ercAlertIcon.classList.add('hidden');
            }
            
            if (hasHTA) {
                factorCount++;
                riskFactors.push('Hipertensión Arterial');
            }
            
            if (hasECV) {
                factorCount++;
                riskFactors.push('Enfermedad Cardiovascular Establecida');
            }
            
            if (hasTobacco) {
                factorCount++;
                riskFactors.push('Tabaquismo Activo');
            }
            
            // Determinar nivel de riesgo
            if (factorCount === 0) {
                riskLevel = 'BAJO';
                riskColor = 'bg-green-500';
            } else if (factorCount === 1) {
                riskLevel = 'MODERADO';
                riskColor = 'bg-yellow-500';
            } else if (factorCount === 2) {
                riskLevel = 'ALTO';
                riskColor = 'bg-red-500';
            } else if (factorCount >= 3) {
                riskLevel = 'MUY ALTO';
                riskColor = 'bg-red-800';
            }
            
            // Actualizar UI
            riskLevelIndicator.textContent = riskLevel;
            riskLevelIndicator.className = `text-center font-extrabold text-3xl py-4 rounded-lg text-white transition-all duration-500 ${riskColor}`;
            
            // Actualizar panel de factores de riesgo
            if (riskFactors.length > 0) {
                riskFactorsSummary.innerHTML = `
                    <p class="font-medium">Factores presentes:</p>
                    <ul class="list-disc pl-5">
                        ${riskFactors.map(factor => `<li>${factor}</li>`).join('')}
                    </ul>
                `;
            } else {
                riskFactorsSummary.innerHTML = `<p>Sin factores de riesgo significativos.</p>`;
            }
            
            // Actualizar metas terapéuticas
            updateTherapeuticGoals(riskLevel, tfgValue, hasDM);
            
            // Guardar estado
            appState.riskLevel = riskLevel;
        } else {
            // Datos incompletos
            riskLevelIndicator.textContent = 'INCOMPLETO';
            riskLevelIndicator.className = 'text-center font-extrabold text-3xl py-4 rounded-lg text-white transition-all duration-500 bg-gray-400';
            riskFactorsSummary.innerHTML = '<p>Complete los datos para calcular el riesgo.</p>';
            goalsPreviewContent.innerHTML = '<p class="text-center text-sm text-gray-400">Los datos de metas aparecerán aquí.</p>';
        }
    }

    // Actualizar metas terapéuticas
    function updateTherapeuticGoals(riskLevel, tfg, hasDM) {
        if (!riskLevel || riskLevel === 'INCOMPLETO') {
            goalsPreviewContent.innerHTML = '<p class="text-center text-sm text-gray-400">Los datos de metas aparecerán aquí.</p>';
            return;
        }
        
        let goals = [];
        
        // Metas de presión arterial
        let paMeta = '';
        if (tfg < 60) {
            paMeta = '< 140/90 mmHg';
        } else if (hasDM) {
            paMeta = '< 130/80 mmHg';
        } else if (riskLevel === 'MUY ALTO' || riskLevel === 'ALTO') {
            paMeta = '< 130/80 mmHg';
        } else {
            paMeta = '< 140/90 mmHg';
        }
        goals.push({
            name: 'Presión Arterial',
            value: paMeta,
            icon: 'fa-heart-pulse'
        });
        
        // Meta LDL
        let ldlMeta = '';
        if (riskLevel === 'MUY ALTO') {
            ldlMeta = '< 55 mg/dl';
        } else if (riskLevel === 'ALTO') {
            ldlMeta = '< 70 mg/dl';
        } else if (riskLevel === 'MODERADO') {
            ldlMeta = '< 100 mg/dl';
        } else {
            ldlMeta = '< 116 mg/dl';
        }
        goals.push({
            name: 'LDL-c',
            value: ldlMeta,
            icon: 'fa-droplet'
        });
        
        // Meta A1c si tiene diabetes
        if (hasDM) {
            goals.push({
                name: 'HbA1c',
                value: '< 7.0%',
                icon: 'fa-percent'
            });
        }
        
        // Construir HTML de metas
        goalsPreviewContent.innerHTML = goals.map(goal => `
            <div class="flex items-center justify-between">
                <div class="flex items-center">
                    <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center mr-3">
                        <i class="fas ${goal.icon} text-primary"></i>
                    </div>
                    <span class="font-medium">${goal.name}</span>
                </div>
                <span class="font-bold text-primary">${goal.value}</span>
            </div>
        `).join('');
    }

    // Procesar archivos de laboratorio
    function processLabFiles(files) {
        if (!files || files.length === 0) return;
        
        fileLoader.classList.remove('hidden');
        fileLoader.classList.add('flex');
        
        const promises = [];
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const fileName = file.name;
            
            // Verificar tipo de archivo
            if (file.type === 'application/pdf') {
                promises.push(processPdfFile(file, fileName));
            } else if (fileName.endsWith('.txt') || file.type === 'text/plain') {
                promises.push(processTxtFile(file, fileName));
            } else {
                showAlert('Formato no soportado', `El formato del archivo ${fileName} no es compatible. Use archivos PDF o TXT.`);
            }
        }
        
        Promise.all(promises)
            .then(results => {
                fileLoader.classList.add('hidden');
                fileLoader.classList.remove('flex');
                
                // Filtrar resultados válidos
                const validResults = results.filter(result => result && result.success);
                
                if (validResults.length === 0) {
                    showAlert('Sin resultados', 'No se pudieron extraer datos de los archivos.');
                }
            })
            .catch(err => {
                fileLoader.classList.add('hidden');
                fileLoader.classList.remove('flex');
                console.error('Error processing files:', err);
                showAlert('Error', 'Ocurrió un error al procesar los archivos.');
            });
    }

    // Procesar archivo PDF
    function processPdfFile(file, fileName) {
        return new Promise((resolve, reject) => {
            const fileReader = new FileReader();
            fileReader.onload = function(event) {
                const typedarray = new Uint8Array(event.target.result);
                
                // Usar PDF.js para leer el PDF
                pdfjsLib.getDocument(typedarray).promise.then(pdf => {
                    let extractedText = '';
                    const numPages = pdf.numPages;
                    let processedPages = 0;
                    
                    for (let i = 1; i <= numPages; i++) {
                        pdf.getPage(i).then(page => {
                            return page.getTextContent();
                        }).then(textContent => {
                            textContent.items.forEach(item => {
                                extractedText += item.str + ' ';
                            });
                            
                            processedPages++;
                            if (processedPages === numPages) {
                                appState.fileContents[fileName] = extractedText;
                                
                                // Enviar el texto al servidor para análisis
                                parseLabResults(extractedText, fileName).then(labResults => {
                                    resolve({
                                        success: true,
                                        fileName: fileName,
                                        labResults: labResults
                                    });
                                }).catch(err => {
                                    resolve({
                                        success: false,
                                        fileName: fileName,
                                        error: err
                                    });
                                });
                            }
                        }).catch(err => {
                            console.error('Error extracting text from PDF page:', err);
                            reject(err);
                        });
                    }
                }).catch(err => {
                    console.error('Error loading PDF:', err);
                    reject(err);
                });
            };
            fileReader.onerror = reject;
            fileReader.readAsArrayBuffer(file);
        });
    }

    // Procesar archivo TXT
    function processTxtFile(file, fileName) {
        return new Promise((resolve, reject) => {
            const fileReader = new FileReader();
            fileReader.onload = function(event) {
                const content = event.target.result;
                appState.fileContents[fileName] = content;
                
                // Enviar el texto al servidor para análisis
                parseLabResults(content, fileName).then(labResults => {
                    resolve({
                        success: true,
                        fileName: fileName,
                        labResults: labResults
                    });
                }).catch(err => {
                    resolve({
                        success: false,
                        fileName: fileName,
                        error: err
                    });
                });
            };
            fileReader.onerror = reject;
            fileReader.readAsText(file);
        });
    }

    // Parsear resultados de laboratorio (usando IA o backend)
    async function parseLabResults(text, fileName) {
        try {
            // MEJORAR manejo de errores y retry logic
            const maxRetries = 3;
            let lastError = null;
            
            for (let i = 0; i < maxRetries; i++) {
                try {
                    const response = await fetch('/api/parse_document', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ 
                            text: text, 
                            filename: fileName 
                        }),
                        signal: AbortSignal.timeout(30000) // 30s timeout
                    });
                    
                    if (!response.ok) {
                        if (response.status === 404) {
                            console.error('Endpoint /api/parse_document no encontrado');
                            showAlert('Error', 'Servicio no disponible. Usando extracción local.');
                            break;
                        }
                        throw new Error(`HTTP ${response.status}`);
                    }
                    
                    const data = await response.json();
                    if (data.success) {
                        displayLabResults(fileName, data.results);
                        if (data.patient_data) {
                            updatePatientDataFromLab(data.patient_data);
                        }
                        return data.results;
                    }
                } catch (err) {
                    lastError = err;
                    if (i < maxRetries - 1) {
                        await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
                    }
                }
            }
            
            // Fallback a extracción local
            console.warn('Usando extracción local después de fallos:', lastError);
            const localResults = extractLabResultsWithRegex(text);
            if (localResults && Object.keys(localResults).length > 0) {
                displayLabResults(fileName, localResults);
                return localResults;
            }
            
            return null;
        } catch (error) {
            console.error('Error crítico:', error);
            showAlert('Error', 'No se pudo procesar el archivo');
            return null;
        }
    }
    
    // Actualizar datos del paciente desde información extraída del laboratorio
    function updatePatientDataFromLab(patientData) {
        if(patientData.nombre) document.getElementById('nombre').value = patientData.nombre;
        if(patientData.edad) document.getElementById('edad').value = patientData.edad;
        if(patientData.sexo) document.getElementById('sexo').value = patientData.sexo;
    }

    // Extracción de resultados de laboratorio con expresiones regulares
    function extractLabResultsWithRegex(text) {
        // Variables para almacenar información del paciente
        let patientData = {};
        
        // Extraer el nombre del paciente (diferentes formatos)
        const nombrePatrones = [
            /Paciente:[\s\r\n]*([A-Za-zÁÉÍÓÚáéíóúÑñ\s.,]+)(?=\r|\n|$|Edad|Sexo|Fecha)/i,
            /Nombre:[\s\r\n]*([A-Za-zÁÉÍÓÚáéíóúÑñ\s.,]+)(?=\r|\n|$|Edad|Sexo|Fecha)/i,
            /Nombre del paciente:[\s\r\n]*([A-Za-zÁÉÍÓÚáéíóúÑñ\s.,]+)(?=\r|\n|$|Edad|Sexo|Fecha)/i,
            /Nombre(?:[\s\r\n]*del)?(?:[\s\r\n]*Paciente)?:[\s\r\n]*([A-Za-zÁÉÍÓÚáéíóúÑñ\s.,]+)/i
        ];
        
        for (const patron of nombrePatrones) {
            const match = text.match(patron);
            if (match && match[1]) {
                patientData.nombre = match[1].trim();
                break;
            }
        }
        
        // Extraer la edad
        const edadMatch = text.match(/Edad:?\s*(\d+)\s*(?:años|year|a[ñn]os)?/i);
        if (edadMatch && edadMatch[1]) {
            patientData.edad = edadMatch[1];
        }
        
        // Extraer el sexo
        const sexoMatch = text.match(/Sexo:?\s*(masculino|femenino|hombre|mujer|male|female|m|f)/i);
        if (sexoMatch && sexoMatch[1]) {
            const sexoValue = sexoMatch[1].toLowerCase();
            if (['masculino', 'hombre', 'male', 'm'].includes(sexoValue)) {
                patientData.sexo = 'm';
            } else if (['femenino', 'mujer', 'female', 'f'].includes(sexoValue)) {
                patientData.sexo = 'f';
            }
        }
        
        // Extraer fecha del informe
        const fechaPatrones = [
            /Fecha:?\s*(\d{1,2}\/\d{1,2}\/\d{2,4})/i,
            /Fecha:?\s*(\d{1,2}-\d{1,2}-\d{2,4})/i,
            /Fecha del informe:?\s*(\d{1,2}\/\d{1,2}\/\d{2,4})/i,
            /Fecha del informe:?\s*(\d{1,2}-\d{1,2}-\d{2,4})/i
        ];
        
        for (const patron of fechaPatrones) {
            const match = text.match(patron);
            if (match && match[1]) {
                patientData.fecha_informe = match[1].trim();
                break;
            }
        }
        
        // Objeto para almacenar resultados
        const results = {};
        
        // Si encontramos datos del paciente, incluirlos en los resultados
        if (Object.keys(patientData).length > 0) {
            results._patientData = patientData;
        }
        
        // Definir patrones múltiples para cada tipo de prueba
        const labPatterns = [
            // Creatinina - CRUCIAL: múltiples patrones para capturar diferentes formatos
            { name: 'creatinina', regex: /creatinina:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            { name: 'creatinina', regex: /creatinina sérica:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            { name: 'creatinina', regex: /creat\.?:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            { name: 'creatinina', regex: /crea\.?:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            { name: 'creatinina', regex: /(?<!\w)cr:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            { name: 'creatinina', regex: /CREATININA.*?(\d+[.,]\d+)\s*(?:mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            { name: 'creatinina', regex: /Creatinina.*?(\d+[.,]\d+)\s*(?:mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            
            // Urea y BUN
            { name: 'urea', regex: /urea:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            { name: 'urea', regex: /nitrógeno ureico:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            { name: 'urea', regex: /bun:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            
            // Glucosa
            { name: 'glucosa', regex: /glucosa:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            { name: 'glucosa', regex: /gluc?:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            { name: 'glucosa', regex: /glucemia:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            
            // Colesterol y lípidos
            { name: 'colesterol', regex: /colesterol:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            { name: 'colesterol', regex: /colesterol total:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            
            { name: 'ldl', regex: /ldl:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            { name: 'ldl', regex: /ldl-c:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            { name: 'ldl', regex: /colesterol ldl:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            
            { name: 'hdl', regex: /hdl:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            { name: 'hdl', regex: /hdl-c:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            { name: 'hdl', regex: /colesterol hdl:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            
            { name: 'trigliceridos', regex: /triglicéridos:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            { name: 'trigliceridos', regex: /tgl?:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            { name: 'trigliceridos', regex: /triglic(?:eridos)?:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mg%)/i, unit: 'mg/dL' },
            
            // HbA1c
            { name: 'hba1c', regex: /hb(?:a)?1c:?\s*([\d.,]+)\s*(%)/i, unit: '%' },
            { name: 'hba1c', regex: /hemoglobina glicosilada:?\s*([\d.,]+)\s*(%)/i, unit: '%' },
            { name: 'hba1c', regex: /hemoglobina a1c:?\s*([\d.,]+)\s*(%)/i, unit: '%' },
            
            // Electrolitos
            { name: 'potasio', regex: /potasio:?\s*([\d.,]+)\s*(mmol\/L|mEq\/L)/i, unit: 'mEq/L' },
            { name: 'potasio', regex: /k\+:?\s*([\d.,]+)\s*(mmol\/L|mEq\/L)/i, unit: 'mEq/L' },
            { name: 'potasio', regex: /potasio sérico:?\s*([\d.,]+)\s*(mmol\/L|mEq\/L)/i, unit: 'mEq/L' },
            
            { name: 'sodio', regex: /sodio:?\s*([\d.,]+)\s*(mmol\/L|mEq\/L)/i, unit: 'mEq/L' },
            { name: 'sodio', regex: /na\+:?\s*([\d.,]+)\s*(mmol\/L|mEq\/L)/i, unit: 'mEq/L' },
            { name: 'sodio', regex: /sodio sérico:?\s*([\d.,]+)\s*(mmol\/L|mEq\/L)/i, unit: 'mEq/L' },
            
            { name: 'calcio', regex: /calcio:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mmol\/L)/i, unit: 'mg/dL' },
            { name: 'calcio', regex: /ca\+:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mmol\/L)/i, unit: 'mg/dL' },
            { name: 'calcio', regex: /ca\s*\(?2\+\)?:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mmol\/L)/i, unit: 'mg/dL' },
            
            { name: 'fosforo', regex: /fósforo:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mmol\/L)/i, unit: 'mg/dL' },
            { name: 'fosforo', regex: /ph?:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mmol\/L)/i, unit: 'mg/dL' },
            { name: 'fosforo', regex: /fosfato:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl|mmol\/L)/i, unit: 'mg/dL' },
            
            // Otros
            { name: 'pth', regex: /pth:?\s*([\d.,]+)\s*(pg\/mL|pg\/ml)/i, unit: 'pg/mL' },
            { name: 'pth', regex: /paratohormona:?\s*([\d.,]+)\s*(pg\/mL|pg\/ml)/i, unit: 'pg/mL' },
            { name: 'pth', regex: /hormona paratiroidea:?\s*([\d.,]+)\s*(pg\/mL|pg\/ml)/i, unit: 'pg/mL' },
            
            { name: 'hb', regex: /h(?:emo)?globina:?\s*([\d.,]+)\s*(g\/dL|g\/dl)/i, unit: 'g/dL' },
            { name: 'hb', regex: /\bhb:?\s*([\d.,]+)\s*(g\/dL|g\/dl)/i, unit: 'g/dL' },
            { name: 'hb', regex: /\bhemoglobina:?\s*([\d.,]+)\s*(g\/dL|g\/dl)/i, unit: 'g/dL' },
            
            { name: 'hto', regex: /h(?:ema)?tocrito:?\s*([\d.,]+)\s*(%)/i, unit: '%' },
            { name: 'hto', regex: /\bhto:?\s*([\d.,]+)\s*(%)/i, unit: '%' },
            { name: 'hto', regex: /\bhct:?\s*([\d.,]+)\s*(%)/i, unit: '%' },
            
            { name: 'albumina', regex: /albúmina:?\s*([\d.,]+)\s*(g\/dL|g\/dl)/i, unit: 'g/dL' },
            { name: 'albumina', regex: /\balb:?\s*([\d.,]+)\s*(g\/dL|g\/dl)/i, unit: 'g/dL' },
            { name: 'albumina', regex: /\balbumina sérica:?\s*([\d.,]+)\s*(g\/dL|g\/dl)/i, unit: 'g/dL' },
            
            { name: 'acido_urico', regex: /ácido úrico:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl)/i, unit: 'mg/dL' },
            { name: 'acido_urico', regex: /\bacid(?:o)? ur(?:ic)?o:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl)/i, unit: 'mg/dL' },
            { name: 'acido_urico', regex: /\burato:?\s*([\d.,]+)\s*(mg\/dL|mg\/dl)/i, unit: 'mg/dL' },
            
            // Proteinuria
            { name: 'proteinuria', regex: /proteinuria:?\s*([\d.,]+)\s*(mg\/24h|g\/24h)/i, unit: 'mg/24h' },
            { name: 'proteinuria', regex: /\bprot(?:eina)?\s+en\s+orina:?\s*([\d.,]+)\s*(mg\/24h|g\/24h)/i, unit: 'mg/24h' },
            { name: 'proteinuria', regex: /\bproteínas en orina de 24h:?\s*([\d.,]+)\s*(mg\/24h|g\/24h)/i, unit: 'mg/24h' },
            
            // RAC
            { name: 'rac', regex: /relación\s+albúmina[-\/]creatinina:?\s*([\d.,]+)\s*(mg\/g|g\/g)/i, unit: 'mg/g' },
            { name: 'rac', regex: /\braco:?\s*([\d.,]+)\s*(mg\/g|g\/g)/i, unit: 'mg/g' },
            { name: 'rac', regex: /\brelación\s+alb\/crea:?\s*([\d.,]+)\s*(mg\/g|g\/g)/i, unit: 'mg/g' },
            { name: 'rac', regex: /\balb\/crea:?\s*([\d.,]+)\s*(mg\/g|g\/g)/i, unit: 'mg/g' },
            
            // Antropometría
            { name: 'peso', regex: /peso:?\s*([\d.,]+)\s*(kg)/i, unit: 'kg' },
            { name: 'peso', regex: /\bpeso corporal:?\s*([\d.,]+)\s*(kg)/i, unit: 'kg' },
            { name: 'peso', regex: /\bpeso del paciente:?\s*([\d.,]+)\s*(kg)/i, unit: 'kg' },
            
            { name: 'talla', regex: /talla:?\s*([\d.,]+)\s*(cm|m)/i, unit: 'cm' },
            { name: 'talla', regex: /\baltura:?\s*([\d.,]+)\s*(cm|m)/i, unit: 'cm' },
            { name: 'talla', regex: /\bestatura:?\s*([\d.,]+)\s*(cm|m)/i, unit: 'cm' }
        ];
        
        // Procesar todos los patrones
        for (const pattern of labPatterns) {
            // Solo buscar si aún no tenemos un valor para este lab
            if (!results[pattern.name]) {
                const match = text.match(pattern.regex);
                if (match && match[1]) {
                    // Normalizar el valor para que use punto como separador decimal
                    let value = match[1].replace(',', '.');
                    
                    // Asegurarse de que sea un número válido
                    if (!isNaN(parseFloat(value))) {
                        results[pattern.name] = {
                            value: parseFloat(value),
                            unit: pattern.unit
                        };
                    }
                }
            }
        }
        
        return results;
    }

    // Mostrar resultados de laboratorio en la interfaz
    function displayLabResults(fileName, results) {
        if (!results || Object.keys(results).length === 0) {
            showAlert('Sin resultados', `No se pudieron extraer datos del archivo ${fileName}.`);
            return;
        }
        
        // Guardar en el estado de la aplicación
        Object.assign(appState.labResults, results);
        
        // Crear tarjeta de resultados
        const labCard = document.createElement('div');
        labCard.className = 'lab-result-card bg-white p-3 rounded-lg shadow-sm border border-gray-200 mb-3';
        
        let labContent = `
            <div class="flex justify-between items-center mb-2">
                <div class="flex items-center gap-2">
                    <input type="checkbox" class="lab-select" data-filename="${fileName}">
                    <h4 class="font-bold">${fileName} <span class="text-xs text-blue-500">(Extraído)</span></h4>
                </div>
                <button type="button" class="remove-lab-btn text-red-500 hover:text-red-700 p-1" data-filename="${fileName}">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </div>
        `;
        labContent += '<div class="space-y-1">';
        
        // Procesar resultados especiales, como datos del paciente
        if (results._patientData) {
            updatePatientDataFromLab(results._patientData);
            delete results._patientData; // Remover para no mostrarlo como un resultado
        }
        
        // Ordenar los resultados alfabéticamente
        const sortedResults = Object.keys(results).sort().reduce((obj, key) => {
            obj[key] = results[key];
            return obj;
        }, {});
        
        // Mostrar cada resultado y bloquear el campo manual correspondiente
        Object.entries(sortedResults).forEach(([key, value]) => {
            const formattedKey = key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ');
            labContent += `<p class="text-sm"><span class="font-medium">${formattedKey}:</span> ${value.value} ${value.unit}</p>`;
            
            // Si es creatinina, actualizar el campo y calcular TFG
            if (key === 'creatinina') {
                creatininaInput.value = value.value;
                creatininaInput.setAttribute('readonly', 'true');
                creatininaInput.classList.add('bg-gray-100');
                creatininaInput.title = `Valor extraído de ${fileName}`;
                calcularTFG();
            }
            
            // Bloquear y actualizar TODOS los campos manuales correspondientes
            const manualField = document.getElementById(key);
            if (manualField) {
                manualField.value = value.value;
                manualField.classList.add('bg-blue-50', 'editable-lab');
                manualField.removeAttribute('readonly'); // Permitir edición
                
                // Crear contenedor para botón si no existe
                let btnContainer = manualField.parentElement.querySelector('.lab-actions');
                if (!btnContainer) {
                    btnContainer = document.createElement('div');
                    btnContainer.className = 'lab-actions flex gap-1 mt-1';
                    manualField.parentElement.appendChild(btnContainer);
                }
                
                // Botón guardar
                const saveBtn = document.createElement('button');
                saveBtn.type = 'button';
                saveBtn.className = 'btn btn-xs btn-success';
                saveBtn.innerHTML = '<i class="fas fa-save"></i> Guardar';
                saveBtn.onclick = () => {
                    appState.labResults[key].value = parseFloat(manualField.value);
                    showAlert('Guardado', `${key} actualizado a ${manualField.value}`);
                    saveBtn.disabled = true;
                    setTimeout(() => saveBtn.disabled = false, 1000);
                };
                
                btnContainer.appendChild(saveBtn);
            }
        });
        
        labContent += '</div>';
        labCard.innerHTML = labContent;
        
        loadedLabsContainer.appendChild(labCard);
        
        // Añadir event listener para el botón de eliminar
        const removeBtn = labCard.querySelector('.remove-lab-btn');
        if (removeBtn) {
            removeBtn.addEventListener('click', function() {
                const fileName = this.dataset.filename;
                removeLabResults(fileName, labCard);
            });
        }
    }
    
    // Función para eliminar resultados de laboratorio
    function removeLabResults(fileName, labCard) {
        // Eliminar la tarjeta de la interfaz
        labCard.remove();
        
        // Eliminar resultados del estado de la aplicación
        if (appState.fileContents[fileName]) {
            delete appState.fileContents[fileName];
        }
        
        // Restaurar los campos manuales que fueron bloqueados
        document.querySelectorAll('#manual-lab-inputs input[readonly]').forEach(input => {
            input.removeAttribute('readonly');
            input.classList.remove('bg-gray-100');
            input.value = '';
            input.title = '';
            
            // También eliminamos el resultado del estado
            if (appState.labResults[input.id]) {
                delete appState.labResults[input.id];
            }
        });
        
        // Específicamente verificar el campo de creatinina
        if (creatininaInput.hasAttribute('readonly')) {
            creatininaInput.removeAttribute('readonly');
            creatininaInput.classList.remove('bg-gray-100');
            creatininaInput.value = '';
            creatininaInput.title = '';
            
            // Recalcular TFG
            calcularTFG();
        }
        
        // Mostrar mensaje
        showAlert('Laboratorio eliminado', `Se ha eliminado el archivo ${fileName} y se han restaurado los campos manuales.`);
    }
    
    // Actualizar datos del paciente desde información extraída del laboratorio
    function updatePatientDataFromLab(patientData) {
        if(patientData.nombre) document.getElementById('nombre').value = patientData.nombre;
        if(patientData.edad) document.getElementById('edad').value = patientData.edad;
        if(patientData.sexo) document.getElementById('sexo').value = patientData.sexo;
    }

    // Generar informe con IA
    async function generateReportWithAI(patientData) {
        try {
            // Mostrar loader
            reportPlaceholder.classList.add('hidden');
            reportLoader.classList.remove('hidden');
            reportOutputContainer.classList.add('hidden');
            
            // En un entorno real, esto debería ser una llamada a tu API backend para proteger la API key
            const response = await fetch('/api/generate_report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ patient: patientData })
            });
            
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            
            const data = await response.json();
            
            // Ocultar loader y mostrar resultado
            reportLoader.classList.add('hidden');
            reportOutputContainer.classList.remove('hidden');
            
            // Formatear el informe con Markdown o HTML
            reportOutput.innerHTML = data.report;
            
            // Guardar paciente en historial
            savePatientToHistory(patientData);
            
        } catch (error) {
            console.error('Error generating report:', error);
            reportLoader.classList.add('hidden');
            reportPlaceholder.classList.remove('hidden');
            showAlert('Error', 'No se pudo generar el informe. Intente nuevamente más tarde.');
        }
    }

    // Guardar paciente en historial
    function savePatientToHistory(patientData) {
        // Evitar duplicados
        const existingIndex = appState.patientHistory.findIndex(p => p.nombre === patientData.nombre);
        if (existingIndex !== -1) {
            appState.patientHistory.splice(existingIndex, 1);
        }
        
        // Limitar a 10 pacientes
        if (appState.patientHistory.length >= 10) {
            appState.patientHistory.pop();
        }
        
        // Añadir timestamp
        patientData.timestamp = new Date().toISOString();
        
        // Añadir al inicio
        appState.patientHistory.unshift(patientData);
        
        // Guardar y actualizar UI
        savePatientHistory();
        updatePatientHistoryUI();
    }

    // Función para mostrar alerta
    function showAlert(title, message) {
        alertTitle.textContent = title;
        alertMessage.textContent = message;
        alertModal.classList.add('visible');
        
        // AÑADIDO: Cerrar con X
        const closeBtn = alertModal.querySelector('.close-modal');
closeBtn.onclick = () => alertModal.classList.remove('visible');
    }

    // Event Listeners
    
    // Evento de envío del formulario
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Recopilar datos del formulario
            const formData = new FormData(form);
            
            // Construir objeto de datos del paciente
            const patientData = {
                nombre: formData.get('nombre'),
                edad: formData.get('edad'),
                sexo: formData.get('sexo'),
                peso: formData.get('peso'),
                talla: formData.get('talla'),
                imc: formData.get('imc'),
                perAbdominal: formData.get('per_abd'),
                diagnosticos: [],
                ecvEstablecida: formData.get('ecv_establecida') === 'on',
                tabaquismo: formData.get('tabaquismo') === 'on',
                condSocioeconomicas: formData.get('cond_socioeconomicas') === 'on',
                fragil: formData.get('fragil') === 'on',
                adherencia: formData.get('adherencia') || 'buena',
                barrerasAcceso: formData.get('barreras_acceso') === 'on',
                creatinina: formData.get('creatinina'),
                creatininaFecha: formData.get('creatinina_date'),
                tfg: tfgDisplay.value,
                riesgoCardiovascular: appState.riskLevel,
                labResults: appState.labResults,
                predialisis: document.querySelector('input[name="predialysis_status"]:checked')?.value || null
            };
            
            // Recopilar diagnósticos
            document.querySelectorAll('input[name="diagnostico"]:checked').forEach(checkbox => {
                patientData.diagnosticos.push(checkbox.value);
            });
            
            // Duración de DM si aplica
            if (patientData.diagnosticos.includes('DM')) {
                patientData.duracionDM = formData.get('duracion_dm');
            }
            
            // Recopilar medicamentos
            patientData.medicamentos = [];
            document.querySelectorAll('.med-item').forEach(item => {
                const nombre = item.querySelector('input[name="med_nombre"]').value;
                const dosis = item.querySelector('input[name="med_dosis"]').value;
                const frecuencia = item.querySelector('input[name="med_frecuencia"]').value;
                
                if (nombre) {
                    patientData.medicamentos.push({ nombre, dosis, frecuencia });
                }
            });
            
            // Recopilar presión arterial
            patientData.presionArterial = [];
            document.querySelectorAll('.pa-item').forEach(item => {
                const sistolica = item.querySelector('input[name="pa_sistolica"]').value;
                const diastolica = item.querySelector('input[name="pa_diastolica"]').value;
                const fecha = item.querySelector('input[name="pa_fecha"]').value;
                
                if (sistolica && diastolica) {
                    patientData.presionArterial.push({ sistolica, diastolica, fecha });
                }
            });
            
            console.log('Datos del paciente:', patientData);
            
            // Generar informe
            generateReportWithAI(patientData);
        });
    }
    
    // Evento para añadir medición de presión arterial
    if (addPaBtn) {
        addPaBtn.addEventListener('click', function() {
            addPresionArterial();
        });
    }
    
    // Evento para añadir medicamento
    if (addMedicamentoBtn) {
        addMedicamentoBtn.addEventListener('click', function() {
            addMedicamento();
        });
    }
    
    // Eventos para botones de medicamentos rápidos
    if (quickMedBtns.length > 0) {
        quickMedBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const med = this.dataset.med;
                const dosis = this.dataset.dosis;
                const freq = this.dataset.freq;
                addMedicamento(med, dosis, freq);
            });
        });
    }
    
    // Eventos para calcular IMC
    if (pesoInput && tallaInput) {
        pesoInput.addEventListener('input', calcularIMC);
        tallaInput.addEventListener('input', calcularIMC);
    }
    
    // Eventos para calcular TFG
    if (creatininaInput) {
        creatininaInput.addEventListener('input', calcularTFG);
        sexoInput.addEventListener('change', calcularTFG);
        edadInput.addEventListener('input', calcularTFG);
        pesoInput.addEventListener('input', calcularTFG);
    }
    
    // AÑADIR event listeners para campos críticos
    ['edad','creatinina','peso','talla'].forEach(id => {
        const elem = document.getElementById(id);
        if(elem) elem.addEventListener('input', () => {
            calcularTFG();
            updateRiskAssessment();
        });
    });
    
    // Evento para mostrar/ocultar duración DM
    if (dmCheckbox) {
        dmCheckbox.addEventListener('change', function() {
            if (this.checked) {
                duracionDmContainer.classList.remove('hidden');
            } else {
                duracionDmContainer.classList.add('hidden');
            }
            updateRiskAssessment();
        });
    }
    
    // Evento para ERC checkbox
    if (ercCheckbox) {
        ercCheckbox.addEventListener('change', updateRiskAssessment);
    }
    
    // Eventos para diagnósticos y condiciones
    document.querySelectorAll('input[name="diagnostico"], #ecv_establecida, #tabaquismo').forEach(checkbox => {
        checkbox.addEventListener('change', updateRiskAssessment);
    });
    
    // Evento para toggle manual de laboratorios
    if (manualLabToggle) {
        manualLabToggle.addEventListener('change', function() {
            if (this.checked) {
                manualLabInputs.classList.remove('hidden');
                labUploadContainer.classList.add('hidden');
            } else {
                manualLabInputs.classList.add('hidden');
                labUploadContainer.classList.remove('hidden');
            }
        });
    }
    
    // Evento para upload de archivos
    if (fileUpload) {
        fileUpload.addEventListener('change', function(e) {
            processLabFiles(e.target.files);
        });
        
        // Drag and drop
        const dropArea = document.querySelector('.file-drop-area');
        if (dropArea) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropArea.addEventListener(eventName, function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                }, false);
            });
            
            ['dragenter', 'dragover'].forEach(eventName => {
                dropArea.addEventListener(eventName, function() {
                    this.classList.add('active');
                }, false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                dropArea.addEventListener(eventName, function() {
                    this.classList.remove('active');
                }, false);
            });
            
            dropArea.addEventListener('drop', function(e) {
                const files = e.dataTransfer.files;
                processLabFiles(files);
            }, false);
        }
    }
    
    // Evento para evaluar fragilidad
    if (evalFragilidadBtn) {
        evalFragilidadBtn.addEventListener('click', function() {
            fragilityModal.classList.add('visible');
        });
    }
    
    // Eventos para modal de fragilidad
    if (closeFragilityModal) {
        closeFragilityModal.addEventListener('click', function() {
            fragilityModal.classList.remove('visible');
        });
        
        document.querySelectorAll('#fried-criteria input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const checkedCount = document.querySelectorAll('#fried-criteria input[type="checkbox"]:checked').length;
                const isFragile = checkedCount >= 3;
                
                frailtyStatus.textContent = isFragile ? 'Frágil' : 'No Frágil';
                frailtyMarker.style.left = `${(checkedCount / 5) * 100}%`;
                
                // Actualizar checkbox en el formulario principal
                fragilCheckbox.checked = isFragile;
                fragilCheckbox.disabled = true;
            });
        });
    }
    
    // Eventos para modales
    if (closeAlertModal) {
        closeAlertModal.addEventListener('click', function() {
            alertModal.classList.remove('visible');
        });
    }
    
    // Eventos para historial
    if (openHistoryBtn) {
        openHistoryBtn.addEventListener('click', function() {
            historyModal.classList.add('visible');
        });
    }
    
    if (closeHistoryModal) {
        closeHistoryModal.addEventListener('click', function() {
            historyModal.classList.remove('visible');
        });
    }
    
    // Eventos para imprimir/copiar informe
    if (printReportBtn) {
        printReportBtn.addEventListener('click', function() {
            window.print();
        });
    }
    
    if (copyReportBtn) {
        copyReportBtn.addEventListener('click', function() {
            const reportText = reportOutput.textContent;
            navigator.clipboard.writeText(reportText)
                .then(() => {
                    // Mostrar feedback
                    this.innerHTML = '<i class="fas fa-check"></i>';
                    setTimeout(() => {
                        this.innerHTML = '<i class="fas fa-copy"></i>';
                    }, 2000);
                })
                .catch(err => {
                    console.error('Error copying text: ', err);
                    showAlert('Error', 'No se pudo copiar el texto al portapapeles.');
                });
        });
    }
    
    // Toggle de alto contraste
    if (highContrastToggle) {
        highContrastToggle.addEventListener('click', function() {
            document.body.classList.toggle('high-contrast');
            appState.highContrast = document.body.classList.contains('high-contrast');
            
            // Guardar preferencia
            localStorage.setItem('highContrast', appState.highContrast);
        });
        
        // Cargar preferencia guardada
        const savedHighContrast = localStorage.getItem('highContrast');
        if (savedHighContrast === 'true') {
            document.body.classList.add('high-contrast');
            appState.highContrast = true;
        }
    }
    
    // Inicialización
    loadPatientHistory();
    
    // Añadir campo inicial de presión arterial si no hay ninguno
    if (paContainer && paContainer.children.length === 0) {
        addPresionArterial();
    }
    
    // Crear campos para entrada manual de laboratorios
    if (manualLabInputs) {
        const commonLabTests = [
            { name: 'glucosa', label: 'Glucosa', unit: 'mg/dL' },
            { name: 'urea', label: 'Urea', unit: 'mg/dL' },
            { name: 'colesterol', label: 'Colesterol Total', unit: 'mg/dL' },
            { name: 'ldl', label: 'LDL-c', unit: 'mg/dL' },
            { name: 'hdl', label: 'HDL-c', unit: 'mg/dL' },
            { name: 'trigliceridos', label: 'Triglicéridos', unit: 'mg/dL' },
            { name: 'hba1c', label: 'HbA1c', unit: '%' },
            { name: 'potasio', label: 'Potasio', unit: 'mEq/L' },
            { name: 'sodio', label: 'Sodio', unit: 'mEq/L' },
            { name: 'calcio', label: 'Calcio', unit: 'mg/dL' },
            { name: 'fosforo', label: 'Fósforo', unit: 'mg/dL' },
            { name: 'albumina', label: 'Albúmina', unit: 'g/dL' }
        ];
        
        let labInputsHTML = '<div class="grid grid-cols-1 md:grid-cols-3 gap-4">';
        
        commonLabTests.forEach(test => {
            labInputsHTML += `
                <div>
                    <label for="${test.name}" class="font-medium text-sm mb-1 block">${test.label}</label>
                    <div class="flex">
                        <input type="number" id="${test.name}" name="${test.name}" step="0.01" class="input-field">
                        <span class="ml-2 text-sm text-gray-500 flex items-center">${test.unit}</span>
                    </div>
                </div>
            `;
        });
        
        labInputsHTML += '</div>';
        manualLabInputs.innerHTML = labInputsHTML;
        
        // Añadir event listeners para actualizar el estado
        document.querySelectorAll('#manual-lab-inputs input').forEach(input => {
            input.addEventListener('change', function() {
                if (this.value) {
                    appState.labResults[this.name] = {
                        value: this.value,
                        unit: commonLabTests.find(test => test.name === this.name)?.unit || ''
                    };
                }
            });
        });
    }
    
    // Agregar después de loadedLabsContainer en cardia_ia.js
function initializeLabSelection() {
    if (!document.querySelector('.lab-controls')) {
        const controlsDiv = document.createElement('div');
        controlsDiv.className = 'lab-controls mb-3 flex gap-2';
        
        // Botón seleccionar todos
        const selectAllBtn = document.createElement('button');
        selectAllBtn.type = 'button';
        selectAllBtn.className = 'btn btn-sm btn-outline-primary';
        selectAllBtn.innerHTML = '<i class="fas fa-check-square"></i> Seleccionar Todos';
        selectAllBtn.onclick = toggleSelectAll;
        
        // Botón eliminar seleccionados
        const deleteSelectedBtn = document.createElement('button');
        deleteSelectedBtn.type = 'button';
        deleteSelectedBtn.className = 'btn btn-sm btn-danger';
        deleteSelectedBtn.innerHTML = '<i class="fas fa-trash"></i> Eliminar Seleccionados';
        deleteSelectedBtn.onclick = deleteSelected;
        
        controlsDiv.appendChild(selectAllBtn);
        controlsDiv.appendChild(deleteSelectedBtn);
        loadedLabsContainer.insertBefore(controlsDiv, loadedLabsContainer.firstChild);
    }
}

function toggleSelectAll() {
    const checkboxes = document.querySelectorAll('.lab-select');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    checkboxes.forEach(cb => cb.checked = !allChecked);
}

function deleteSelected() {
    const selected = document.querySelectorAll('.lab-select:checked');
    if (selected.length === 0) {
        showAlert('Atención', 'No hay archivos seleccionados');
        return;
    }
    
    if (confirm(`¿Eliminar ${selected.length} archivo(s)?`)) {
        selected.forEach(cb => {
            const card = cb.closest('.lab-result-card');
            const fileName = cb.dataset.filename;
            removeLabResults(fileName, card);
        });
    }
}

// Llamar después de cargar labs
if (loadedLabsContainer) initializeLabSelection();
});
