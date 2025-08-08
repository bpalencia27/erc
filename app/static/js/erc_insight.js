document.addEventListener('DOMContentLoaded', () => {
    // --- Referencias a elementos del DOM ---
    const form = document.getElementById('clinical-form');
    const allFormElements = form.querySelectorAll('input, select');
    const riskIndicator = document.getElementById('risk-level-indicator');
    const riskSummary = document.getElementById('risk-factors-summary');
    const ercAlertIcon = document.getElementById('erc-alert-icon');
    const goalsPreviewContent = document.getElementById('goals-preview-content');
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');

    // --- Configuración de la API ---
    const BACKEND_URL = "/api"; // URL base para las llamadas a tu backend Flask

    // --- Inicialización de elementos UI ---
    initializeTabs();
    initializeTooltips();
    initializeProgressChart();
    
    // --- Lógica de la UI ---
    function initializeTabs() {
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                
                tab.classList.add('active');
                document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
            });
        });
    }
    
    function initializeTooltips() {
        document.querySelectorAll('.enhanced-tooltip').forEach(tooltip => {
            tooltip.addEventListener('mouseenter', () => {
                tooltip.querySelector('.tooltip-content').style.visibility = 'visible';
                tooltip.querySelector('.tooltip-content').style.opacity = '1';
            });
            
            tooltip.addEventListener('mouseleave', () => {
                tooltip.querySelector('.tooltip-content').style.visibility = 'hidden';
                tooltip.querySelector('.tooltip-content').style.opacity = '0';
            });
        });
    }
    
    function initializeProgressChart() {
        const canvas = document.getElementById('goals-progress-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = 45;
        
        function drawCircle(percent) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Círculo base (gris)
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
            ctx.strokeStyle = '#e2e8f0';
            ctx.lineWidth = 10;
            ctx.stroke();
            
            // Círculo de progreso
            if (percent > 0) {
                const startAngle = -0.5 * Math.PI; // Comenzar desde arriba
                const endAngle = startAngle + (2 * Math.PI * (percent / 100));
                
                ctx.beginPath();
                ctx.arc(centerX, centerY, radius, startAngle, endAngle);
                ctx.strokeStyle = getProgressColor(percent);
                ctx.lineWidth = 10;
                ctx.stroke();
            }
            
            // Actualizar el valor de texto
            document.querySelector('.progress-value').textContent = `${Math.round(percent)}%`;
        }
        
        function getProgressColor(percent) {
            if (percent < 30) return '#ef4444'; // Rojo
            if (percent < 70) return '#f59e0b'; // Naranja
            return '#22c55e'; // Verde
        }
        
        // Inicializar con 0%
        drawCircle(0);
        
        // Exponer la función para actualizarla desde otras partes
        window.updateProgressChart = drawCircle;
    }

    const showAlert = (title, message, type = 'error') => {
        // Usar SweetAlert2 para alertas más atractivas
        Swal.fire({
            title: title,
            text: message,
            icon: type,
            confirmButtonText: 'Entendido',
            confirmButtonColor: '#2563eb'
        });
    };

    // Función para conectar con el backend Flask
    const callBackend = async (endpoint, data = {}, method = 'POST') => {
        try {
            const response = await fetch(`${BACKEND_URL}/${endpoint}`, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: method !== 'GET' ? JSON.stringify(data) : undefined
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Error del servidor: ${response.status} - ${errorText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error en la llamada a la API (${endpoint}):`, error);
            throw error;
        }
    };

    // --- Estado de la aplicación ---
    let patientData = {
        laboratorios: [] // Ahora es un array para múltiples entradas
    };
    let charts = {}; // Para almacenar instancias de Chart.js

    // --- Funciones de Cálculo ---
    const calculateTFG = (creatinina, edad, sexo, peso) => {
        if (!creatinina || !edad || !sexo || !peso) return null;
        const scr = parseFloat(creatinina);
        const age = parseInt(edad);
        const weight = parseFloat(peso);
        
        if (scr <= 0 || age <= 0 || weight <= 0) return null;
        
        const factorSexo = (sexo === 'f') ? 0.85 : 1.0;
        const tfg = ((140 - age) * weight * factorSexo) / (72 * scr);
        
        // Actualizar el marcador visual en la escala de TFG
        updateTFGMarker(tfg);
        
        return Math.round(tfg);
    };
    
    const updateTFGMarker = (tfg) => {
        const marker = document.getElementById('tfg-marker');
        if (!marker) return;
        
        let position;
        if (tfg < 15) position = "7.5%";
        else if (tfg < 30) position = "22.5%";
        else if (tfg < 45) position = "37.5%";
        else if (tfg < 60) position = "52.5%";
        else if (tfg < 90) position = "75%";
        else position = "95%";
        
        marker.style.left = position;
        
        // También actualizamos el marcador KDIGO
        updateKDIGOMarker(tfg);
    };
    
    const updateKDIGOMarker = (tfg) => {
        const marker = document.getElementById('kdigo-marker');
        if (!marker) return;
        
        let left, top;
        
        // Posicionamiento aproximado basado en la imagen KDIGO
        if (tfg >= 90) {
            // G1
            left = "20%";
            top = "20%";
        } else if (tfg >= 60) {
            // G2
            left = "20%";
            top = "30%";
        } else if (tfg >= 45) {
            // G3a
            left = "20%";
            top = "40%";
        } else if (tfg >= 30) {
            // G3b
            left = "20%";
            top = "50%";
        } else if (tfg >= 15) {
            // G4
            left = "20%";
            top = "60%";
        } else {
            // G5
            left = "20%";
            top = "70%";
        }
        
        // Obtener RAC para ajustar horizontalmente
        const racLab = patientData.laboratorios.find(lab => lab.id === 'rac');
        if (racLab) {
            const rac = parseFloat(racLab.valor);
            if (rac < 30) {
                left = "20%"; // A1
            } else if (rac < 300) {
                left = "50%"; // A2
            } else {
                left = "80%"; // A3
            }
        }
        
        marker.style.top = top;
        marker.style.left = left;
        marker.style.opacity = "1";
    };

    const calculateIMC = () => {
        const peso = parseFloat(document.getElementById('peso').value);
        const tallaCm = parseFloat(document.getElementById('talla').value);
        const imcInput = document.getElementById('imc');
        if (peso && tallaCm > 0) {
            const tallaM = tallaCm / 100;
            const imc = (peso / (tallaM * tallaM)).toFixed(1);
            imcInput.value = `${imc} kg/m²`;
            
            // Añadir clasificación del IMC
            let clasificacion = "";
            if (imc < 18.5) clasificacion = " (Bajo peso)";
            else if (imc < 25) clasificacion = " (Normal)";
            else if (imc < 30) clasificacion = " (Sobrepeso)";
            else if (imc < 35) clasificacion = " (Obesidad I)";
            else if (imc < 40) clasificacion = " (Obesidad II)";
            else clasificacion = " (Obesidad III)";
            
            imcInput.value += clasificacion;
        } else {
            imcInput.value = '';
        }
    };
    document.getElementById('peso').addEventListener('input', calculateIMC);
    document.getElementById('talla').addEventListener('input', calculateIMC);

    // --- Lógica de Clasificación de Riesgo y UI Dinámica ---
    const updateAllCalculations = () => {
        const data = new FormData(form);
        const formDataObject = Object.fromEntries(data.entries());
        
        // Fusionar datos del formulario con el estado actual
        Object.assign(patientData, formDataObject);
        patientData.diagnostico = data.getAll('diagnostico');
        patientData.medicamentos = Array.from(document.querySelectorAll('#medicamentos-container .grid')).map(row => ({
            nombre: row.querySelector('[name="med-nombre"]').value,
            dosis: row.querySelector('[name="med-dosis"]').value,
            frecuencia: row.querySelector('[name="med-frecuencia"]').value
        })).filter(med => med.nombre);

        patientData.pa_values = Array.from(document.querySelectorAll('#pa-container .grid')).map(row => {
            const sys = row.querySelector('.pa-sys').value;
            const dia = row.querySelector('.pa-dia').value;
            return sys && dia ? `${sys}/${dia}` : null;
        }).filter(Boolean);
        
        // Actualizar laboratorios desde los inputs manuales
        document.querySelectorAll('.lab-entry').forEach(row => {
            const id = row.dataset.labName;
            const value = row.querySelector('.lab-value').value;
            const date = row.querySelector('.lab-date').value;
            
            const existingLabIndex = patientData.laboratorios.findIndex(l => l.id === id);
            if(value) { // Solo añadir o actualizar si hay un valor
                const labEntry = { id, valor: parseFloat(value), fecha: date, nombreCompleto: labs[id].label };
                if (existingLabIndex > -1) {
                    patientData.laboratorios[existingLabIndex] = labEntry;
                } else {
                    patientData.laboratorios.push(labEntry);
                }
            } else { // Si no hay valor, eliminarlo del estado
                if (existingLabIndex > -1) {
                     patientData.laboratorios.splice(existingLabIndex, 1);
                }
            }
        });

        // Calcular TFG
        patientData.tfg = calculateTFG(patientData.creatinina, patientData.edad, patientData.sexo, patientData.peso);
        document.getElementById('tfg-display').value = patientData.tfg ? `${patientData.tfg} mL/min` : '';

        // Lógica de ERC y Prediálisis automática
        const ercCheckbox = document.getElementById('erc-checkbox');
        const predialysisSection = document.getElementById('predialysis-section');
        if (patientData.tfg) {
            if (patientData.tfg <= 60) {
                ercCheckbox.checked = true;
                ercCheckbox.disabled = true;
            } else {
                ercCheckbox.disabled = false;
            }
            predialysisSection.classList.toggle('hidden', patientData.tfg > 20);
        } else {
            ercCheckbox.disabled = false;
            predialysisSection.classList.add('hidden');
        }

        // Actualizar panel de riesgo
        updateRiskPanel();
        
        // Actualizar preview de metas
        updateGoalsPreview();
        
        // Guardar en historial local
        savePatientToHistory();
        
        // Intentar generar recomendaciones de medicamentos basadas en diagnóstico y TFG
        generateMedicationRecommendations();
    };

    const updateRiskPanel = () => {
        if (!patientData.edad || !patientData.creatinina || !patientData.peso || !patientData.diagnostico?.length) {
            riskIndicator.textContent = 'INCOMPLETO';
            riskIndicator.className = 'risk-sphere bg-gray-400';
            riskSummary.innerHTML = '<p>Complete los datos obligatorios (*).</p>';
            ercAlertIcon.classList.add('hidden');
            return;
        }

        let riskScore = 0;
        let riskFactors = [];
        
        patientData.diagnostico.forEach(dx => {
            if(dx === 'DM') { riskScore += 2; riskFactors.push('Diabetes Mellitus'); }
            if(dx === 'HTA') { riskScore += 1; riskFactors.push('Hipertensión Arterial'); }
            if(dx === 'ERC') { riskScore += 2; riskFactors.push('Enf. Renal Crónica'); }
        });

        if (patientData.ecv_establecida) { riskScore += 10; riskFactors.push('ECV establecida'); }
        if (patientData.edad > 65) { riskScore += 2; riskFactors.push('Edad > 65 años'); }
        if (patientData.tfg) {
            riskFactors.push(`TFG: ${patientData.tfg} ml/min`);
            if (patientData.tfg < 30) { riskScore += 4; }
            else if (patientData.tfg < 60) { riskScore += 2; }
        }
        const racLab = patientData.laboratorios.find(lab => lab.id === 'rac');
        if (racLab) {
            riskFactors.push(`RAC: ${racLab.valor} mg/g`);
            if (racLab.valor > 30) { riskScore += 2; }
        }
        if (patientData.tabaquismo) { riskScore += 1; riskFactors.push('Tabaquismo'); }
        if (patientData.fragil) { riskScore += 2; riskFactors.push('Paciente Frágil'); }

        const ercSignificativa = (patientData.tfg && patientData.tfg < 60) || (racLab && racLab.valor > 30);
        ercAlertIcon.classList.toggle('hidden', !ercSignificativa);

        let riskLevel, riskColor;
        if (riskScore >= 10 || (patientData.diagnostico.includes('DM') && patientData.tfg < 30)) {
            riskLevel = 'MUY ALTO'; riskColor = 'var(--risk-very-high)';
        } else if (riskScore >= 5) {
            riskLevel = 'ALTO'; riskColor = 'var(--risk-high)';
        } else if (riskScore >= 2) {
            riskLevel = 'MODERADO'; riskColor = 'var(--risk-moderate)';
        } else {
            riskLevel = 'BAJO'; riskColor = 'var(--risk-low)';
        }
        patientData.riskLevel = riskLevel; // Store for later use
        
        riskIndicator.innerHTML = `<span>${riskLevel}</span>`;
        riskIndicator.style.backgroundColor = riskColor;
        riskSummary.innerHTML = riskFactors.map(f => `<p class="flex items-center"><i class="fas fa-check-circle text-xs mr-2"></i>${f}</p>`).join('');
    };
    
    const updateGoalsPreview = () => {
        const paAvg = patientData.pa_values.length > 0 ? patientData.pa_values[0] : null;
        const ldlLab = patientData.laboratorios.find(lab => lab.id === 'ldl');
        const hba1cLab = patientData.laboratorios.find(lab => lab.id === 'hba1c');

        const goals = {
            pa: { label: "Presión Arterial", target: { sys: 130, dia: 80 }, value: paAvg, unit: "mmHg" },
            ldl: { label: "Colesterol LDL", target: patientData.riskLevel === 'MUY ALTO' ? 55 : 70, value: ldlLab?.valor, unit: "mg/dL" },
            hba1c: { label: "HbA1c", target: 7.0, value: hba1cLab?.valor, unit: "%" }
        };

        goalsPreviewContent.innerHTML = '';
        
        // Contador para metas cumplidas
        let metGoals = 0;
        let totalGoals = 0;
        
        Object.entries(goals).forEach(([key, goal]) => {
            let statusColor = 'text-gray-400';
            let statusIcon = 'fa-minus-circle';
            let isMet = false;

            if (goal.value) {
                totalGoals++;
                if (key === 'pa') {
                    const [sys, dia] = goal.value.split('/').map(Number);
                    isMet = sys < goal.target.sys && dia < goal.target.dia;
                } else {
                    isMet = goal.value < goal.target;
                }
                
                if (isMet) metGoals++;
                
                statusColor = isMet ? 'text-green-500' : 'text-red-500';
                statusIcon = isMet ? 'fa-check-circle' : 'fa-times-circle';
            }

            const goalHtml = `
                <div class="border-t pt-3">
                    <div class="flex justify-between items-center text-sm">
                        <span class="font-semibold">${goal.label}</span>
                        <span class="font-bold ${statusColor}">${goal.value ? `${goal.value} ${goal.unit}` : 'N/A'}</span>
                        <span class="text-xs text-gray-500">(Meta < ${key === 'pa' ? goal.target.sys + '/' + goal.target.dia : goal.target + ' ' + goal.unit})</span>
                        <i class="fas ${statusIcon} ${statusColor}"></i>
                    </div>
                    <div class="goal-chart-container">
                       <canvas id="chart-${key}"></canvas>
                    </div>
                </div>`;
            goalsPreviewContent.innerHTML += goalHtml;
            
            // Render chart for this goal
            renderGoalChart(key, patientData.laboratorios.filter(l => l.id === key));
        });
        
        // Actualizar el gráfico de progreso
        const progressPercent = totalGoals > 0 ? (metGoals / totalGoals) * 100 : 0;
        if (window.updateProgressChart) {
            window.updateProgressChart(progressPercent);
        }
    };

    const renderGoalChart = (key, data) => {
        const ctx = document.getElementById(`chart-${key}`)?.getContext('2d');
        if (!ctx) return;

        if (charts[key]) {
            charts[key].destroy();
        }

        const chartData = data.map(d => ({ x: new Date(d.fecha), y: d.valor })).sort((a,b) => a.x - b.x);

        charts[key] = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: key.toUpperCase(),
                    data: chartData,
                    borderColor: 'rgba(37, 99, 235, 0.8)',
                    backgroundColor: 'rgba(37, 99, 235, 0.2)',
                    borderWidth: 2,
                    pointRadius: 3,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                scales: {
                    x: { type: 'time', time: { unit: 'month' }, display: false },
                    y: { display: false }
                },
                plugins: { legend: { display: false } },
                maintainAspectRatio: false
            }
        });
    };
    
    const generateMedicationRecommendations = () => {
        const recommendationsContainer = document.getElementById('medication-recommendations');
        const recommendationsContent = document.getElementById('medication-recommendations-content');
        
        if (!patientData.diagnostico || !patientData.tfg) {
            recommendationsContainer.classList.add('hidden');
            return;
        }
        
        // Simple recomendaciones basadas en diagnósticos y TFG
        let recommendations = [];
        
        if (patientData.diagnostico.includes('HTA')) {
            if (patientData.tfg < 30) {
                recommendations.push("Considere ARA II a dosis bajas (ej. Losartán 25-50mg/día) con monitorización estrecha de potasio y creatinina.");
            } else {
                recommendations.push("IECA o ARA II en dosis óptimas (ej. Enalapril 10-20mg/día o Losartán 50-100mg/día).");
            }
        }
        
        if (patientData.diagnostico.includes('DM')) {
            if (patientData.tfg > 30) {
                recommendations.push("iSGLT2 (ej. Empagliflozina 10mg/día) para nefroprotección y cardioprotección.");
            } else {
                recommendations.push("Evitar iSGLT2 con TFG < 30. Considerar arGLP1 (ej. Semaglutida) para cardioprotección.");
            }
            
            if (patientData.tfg < 45) {
                recommendations.push("Ajustar dosis de Metformina (máx. 1000mg/día) con TFG < 45 ml/min o considerar alternativa.");
            }
        }
        
        if (patientData.tfg < 60 || patientData.diagnostico.includes('DM')) {
            recommendations.push("Estatina de alta intensidad (ej. Atorvastatina 40-80mg/día) para reducción de riesgo cardiovascular.");
        }
        
        if (patientData.tfg < 20) {
            recommendations.push("Considerar nefrólogo para evaluación de preparación para terapia de reemplazo renal.");
        }
        
        if (recommendations.length > 0) {
            recommendationsContent.innerHTML = recommendations.map(rec => `<p><i class="fas fa-angle-right text-primary mr-2"></i>${rec}</p>`).join('');
            recommendationsContainer.classList.remove('hidden');
        } else {
            recommendationsContainer.classList.add('hidden');
        }
    };

    // --- Lógica de Fragilidad ---
    const fragilityModal = document.getElementById('fragility-modal');
    const friedCriteriaCheckboxes = fragilityModal.querySelectorAll('#fried-criteria input');
    document.getElementById('eval-fragilidad-btn').addEventListener('click', () => fragilityModal.classList.add('visible'));
    document.getElementById('close-fragility-modal').addEventListener('click', () => fragilityModal.classList.remove('visible'));
    
    friedCriteriaCheckboxes.forEach(cb => cb.addEventListener('change', () => {
        const checkedCount = Array.from(friedCriteriaCheckboxes).filter(i => i.checked).length;
        const statusEl = document.getElementById('frailty-status');
        const markerEl = document.getElementById('frailty-marker');
        let statusText = 'No Frágil';
        let markerPos = '0%';
        if (checkedCount >= 3) { statusText = 'Frágil'; markerPos = '100%'; }
        else if (checkedCount > 0) { statusText = 'Pre-Frágil'; markerPos = '50%'; }
        statusEl.textContent = statusText;
        markerEl.style.left = markerPos;
        document.getElementById('fragil').checked = (checkedCount >= 3);
        updateAllCalculations();
    }));

    // --- Lógica de Medicamentos ---
    const medContainer = document.getElementById('medicamentos-container');
    const addMedicamento = (nombre = '', dosis = '', frecuencia = '') => {
        const div = document.createElement('div');
        div.className = 'grid grid-cols-12 gap-2 items-center';
        div.innerHTML = `
            <input type="text" name="med-nombre" placeholder="Nombre genérico" class="input-field col-span-5" value="${nombre}">
            <input type="text" name="med-dosis" placeholder="Dosis" class="input-field col-span-3" value="${dosis}">
            <input type="text" name="med-frecuencia" placeholder="Frecuencia" class="input-field col-span-3" value="${frecuencia}">
            <button type="button" class="remove-med-btn text-red-500 hover:text-red-700 col-span-1" aria-label="Eliminar medicamento"><i class="fas fa-trash"></i></button>
        `;
        medContainer.appendChild(div);
        div.querySelector('.remove-med-btn').addEventListener('click', () => {
            div.classList.add('slide-out-right');
            setTimeout(() => div.remove(), 300);
        });
    };
    document.getElementById('add-medicamento-btn').addEventListener('click', () => addMedicamento());
    document.querySelectorAll('.quick-med-btn').forEach(btn => btn.addEventListener('click', () => {
        addMedicamento(btn.dataset.med, btn.dataset.dosis, btn.dataset.freq);
    }));
    
    // Lógica para categorías de medicamentos
    document.querySelectorAll('.quick-category-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const category = btn.dataset.category;
            let medicamentos = [];
            
            // Obtener medicamentos según la categoría
            switch(category) {
                case 'nefroprotector':
                    medicamentos = [
                        { nombre: 'Losartán', dosis: '50mg', frecuencia: 'Cada 12h' },
                        { nombre: 'Empagliflozina', dosis: '10mg', frecuencia: 'Cada mañana' }
                    ];
                    break;
                case 'antihipertensivo':
                    medicamentos = [
                        { nombre: 'Amlodipino', dosis: '5mg', frecuencia: 'Cada 24h' },
                        { nombre: 'Hidroclorotiazida', dosis: '25mg', frecuencia: 'Cada mañana' }
                    ];
                    break;
                case 'hipolipemiante':
                    medicamentos = [
                        { nombre: 'Atorvastatina', dosis: '40mg', frecuencia: 'Cada noche' },
                        { nombre: 'Ezetimiba', dosis: '10mg', frecuencia: 'Cada 24h' }
                    ];
                    break;
                case 'antidiabetico':
                    medicamentos = [
                        { nombre: 'Metformina', dosis: '850mg', frecuencia: 'Cada 12h' },
                        { nombre: 'Glimepirida', dosis: '2mg', frecuencia: 'Cada mañana' }
                    ];
                    break;
            }
            
            // Mostrar modal de selección
            Swal.fire({
                title: 'Selecciona medicamentos',
                html: medicamentos.map((med, idx) => 
                    `<div class="flex items-center mb-2">
                        <input type="checkbox" id="med_${idx}" class="h-4 w-4 mr-2">
                        <label for="med_${idx}" class="flex-grow text-left ml-2">${med.nombre} ${med.dosis} ${med.frecuencia}</label>
                    </div>`
                ).join(''),
                showCancelButton: true,
                confirmButtonText: 'Añadir Seleccionados',
                cancelButtonText: 'Cancelar',
                confirmButtonColor: '#2563eb',
                preConfirm: () => {
                    return medicamentos.filter((_, idx) => 
                        document.getElementById(`med_${idx}`).checked
                    );
                }
            }).then((result) => {
                if (result.isConfirmed) {
                    result.value.forEach(med => {
                        addMedicamento(med.nombre, med.dosis, med.frecuencia);
                    });
                    updateAllCalculations();
                }
            });
        });
    });
    
    addMedicamento();
    
    // --- Lógica de Presión Arterial ---
    const paContainer = document.getElementById('pa-container');
    const addPaReading = (sys = '', dia = '') => {
         const div = document.createElement('div');
         div.className = 'grid grid-cols-12 gap-2 items-center slide-in-bottom';
         div.innerHTML = `
            <input type="number" placeholder="Sistólica" class="input-field col-span-5 pa-sys" value="${sys}">
            <span class="text-center col-span-1">/</span>
            <input type="number" placeholder="Diastólica" class="input-field col-span-5 pa-dia" value="${dia}">
            <button type="button" class="remove-pa-btn text-red-500 hover:text-red-700 col-span-1" aria-label="Eliminar medición"><i class="fas fa-trash"></i></button>
         `;
         paContainer.appendChild(div);
         div.querySelector('.remove-pa-btn').addEventListener('click', () => {
            div.classList.add('slide-out-right');
            setTimeout(() => div.remove(), 300);
         });
         
         // Colorear según los valores
         const sysInput = div.querySelector('.pa-sys');
         const diaInput = div.querySelector('.pa-dia');
         
         const updatePAColors = () => {
            const sys = parseInt(sysInput.value);
            const dia = parseInt(diaInput.value);
            
            if (isNaN(sys) || isNaN(dia)) {
                sysInput.style.backgroundColor = '';
                diaInput.style.backgroundColor = '';
                return;
            }
            
            // Colores para sistólica
            if (sys < 120) sysInput.style.backgroundColor = '#dcfce7'; // Verde claro
            else if (sys < 130) sysInput.style.backgroundColor = '#fef3c7'; // Amarillo claro
            else sysInput.style.backgroundColor = '#fee2e2'; // Rojo claro
            
            // Colores para diastólica
            if (dia < 80) diaInput.style.backgroundColor = '#dcfce7'; // Verde claro
            else if (dia < 90) diaInput.style.backgroundColor = '#fef3c7'; // Amarillo claro
            else diaInput.style.backgroundColor = '#fee2e2'; // Rojo claro
            
            updateAllCalculations();
         };
         
         sysInput.addEventListener('input', updatePAColors);
         diaInput.addEventListener('input', updatePAColors);
    };
    document.getElementById('add-pa-btn').addEventListener('click', () => addPaReading());

    // --- Lógica de Laboratorios ---
    const labs = {
        hba1c: { label: 'HbA1c (%)', normal: { min: 0, max: 5.7 }, alert: { min: 7, max: 100 } },
        ldl: { label: 'Colesterol LDL (mg/dL)', normal: { min: 0, max: 100 }, alert: { min: 130, max: 1000 } },
        hdl: { label: 'Colesterol HDL (mg/dL)', normal: { min: 40, max: 100 }, alert: { min: 0, max: 35 } },
        trigliceridos: { label: 'Triglicéridos (mg/dL)', normal: { min: 0, max: 150 }, alert: { min: 200, max: 2000 } },
        rac: { label: 'RAC (mg/g)', normal: { min: 0, max: 30 }, alert: { min: 300, max: 10000 } },
        glicemia: { label: 'Glicemia (mg/dL)', normal: { min: 70, max: 100 }, alert: { min: 126, max: 500 } },
        pth: { label: 'PTH (pg/mL)', normal: { min: 15, max: 65 }, alert: { min: 100, max: 1000 } },
        albumina: { label: 'Albúmina (g/dL)', normal: { min: 3.5, max: 5.2 }, alert: { min: 0, max: 3 } },
        potasio: { label: 'Potasio (mEq/L)', normal: { min: 3.5, max: 5.0 }, alert: { min: 5.5, max: 7 } },
        sodio: { label: 'Sodio (mEq/L)', normal: { min: 135, max: 145 }, alert: { min: 0, max: 130 } },
        fosforo: { label: 'Fósforo (mg/dL)', normal: { min: 2.5, max: 4.5 }, alert: { min: 5.5, max: 10 } },
        acido_urico: { label: 'Ácido Úrico (mg/dL)', normal: { min: 2.4, max: 6.0 }, alert: { min: 7, max: 15 } },
        calcio: { label: 'Calcio (mg/dL)', normal: { min: 8.5, max: 10.5 }, alert: { min: 0, max: 8 } },
        hemoglobina: { label: 'Hemoglobina (g/dL)', normal: { min: 12, max: 16 }, alert: { min: 0, max: 10 } },
        ferritina: { label: 'Ferritina (ng/mL)', normal: { min: 30, max: 300 }, alert: { min: 0, max: 15 } },
        bun: { label: 'BUN (mg/dL)', normal: { min: 7, max: 20 }, alert: { min: 50, max: 200 } }
    };

    // Función para verificar si un valor está normal, en alerta o advertencia
    const getLabStatus = (labId, value) => {
        if (!labs[labId] || !value) return '';
        
        const { normal, alert } = labs[labId];
        
        if (value >= normal.min && value <= normal.max) return 'normal';
        if (value >= alert.min && value <= alert.max) return 'alert';
        
        // Si no está en rango normal ni en alerta, está en advertencia
        return 'warning';
    };

    // Función para renderizar los inputs de laboratorios en la interfaz
    const renderLabInputs = () => {
        const labGrid = document.querySelector('.lab-grid');
        if (!labGrid) return;
        
        labGrid.innerHTML = '';
        
        Object.entries(labs).forEach(([key, config]) => {
            const card = document.createElement('div');
            card.className = 'lab-card lab-entry';
            card.dataset.labName = key;
            
            card.innerHTML = `
                <label class="text-xs font-semibold text-gray-700 mb-1 block">${config.label}</label>
                <div class="flex items-center gap-2 mb-2">
                    <input type="number" step="0.01" placeholder="Valor" class="input-field lab-value text-sm">
                    <div class="enhanced-tooltip">
                        <i class="fas fa-info-circle text-gray-400"></i>
                        <div class="tooltip-content">
                            <h4 class="font-medium mb-1">Rangos Referenciales:</h4>
                            <p class="text-xs">Normal: ${config.normal.min} - ${config.normal.max}</p>
                            <p class="text-xs">Alerta: ${config.alert.min > config.alert.max ? '< ' + config.alert.min : '> ' + config.alert.max}</p>
                        </div>
                    </div>
                </div>
                <input type="date" class="input-field lab-date text-sm">
            `;
            
            labGrid.appendChild(card);
            
            // Añadir evento para cambiar el color según el valor
            const valueInput = card.querySelector('.lab-value');
            valueInput.addEventListener('input', () => {
                const value = parseFloat(valueInput.value);
                if (!isNaN(value)) {
                    const status = getLabStatus(key, value);
                    valueInput.className = `input-field lab-value text-sm ${status}`;
                    
                    if (status === 'normal') valueInput.style.backgroundColor = '#dcfce7';
                    else if (status === 'warning') valueInput.style.backgroundColor = '#fef3c7';
                    else if (status === 'alert') valueInput.style.backgroundColor = '#fee2e2';
                    else valueInput.style.backgroundColor = '';
                    
                    updateAllCalculations();
                }
            });
        });
    };

    // Método de entrada de laboratorios
    const labMethodInputs = document.querySelectorAll('input[name="lab-input-method"]');
    const manualLabsContainer = document.getElementById('manual-labs-container');
    const uploadLabsContainer = document.getElementById('upload-labs-container');
    const apiLabsContainer = document.getElementById('api-labs-container');
    
    labMethodInputs.forEach(input => {
        input.addEventListener('change', () => {
            manualLabsContainer.classList.add('hidden');
            uploadLabsContainer.classList.add('hidden');
            apiLabsContainer.classList.add('hidden');
            
            if (input.value === 'manual') {
                manualLabsContainer.classList.remove('hidden');
            } else if (input.value === 'upload') {
                uploadLabsContainer.classList.remove('hidden');
            } else if (input.value === 'api') {
                apiLabsContainer.classList.remove('hidden');
            }
        });
    });

    // Lógica para el contenedor de laboratorios cargados
    const loadedLabsContainer = document.getElementById('loaded-labs-container');
    
    const renderLoadedLabs = () => {
        loadedLabsContainer.innerHTML = '';
        if (patientData.laboratorios.length > 0) {
            loadedLabsContainer.innerHTML = '<h3 class="font-medium text-sm mb-2">Laboratorios Registrados:</h3>';
        }
        patientData.laboratorios.forEach((lab, index) => {
            const labConfig = labs[lab.id] || { label: lab.id };
            const status = getLabStatus(lab.id, lab.valor);
            
            let statusClass = '';
            if (status === 'normal') statusClass = 'normal';
            else if (status === 'warning') statusClass = 'warning';
            else if (status === 'alert') statusClass = 'alert';
            
            const div = document.createElement('div');
            div.className = 'bg-gray-50 p-2 rounded-lg flex items-center justify-between mb-2 card-slide-in';
            div.innerHTML = `
                <div>
                    <span class="font-semibold text-sm">${labConfig.label || lab.id}</span>: 
                    <span class="lab-value-pill ${statusClass}">${lab.valor}</span>
                    <span class="text-xs text-gray-500 ml-2">(${lab.fecha || 'Sin fecha'})</span>
                </div>
                <button type="button" class="remove-lab-btn text-red-400 hover:text-red-600" data-index="${index}" aria-label="Eliminar laboratorio"><i class="fas fa-times-circle"></i></button>
            `;
            loadedLabsContainer.appendChild(div);
        });
    };

    loadedLabsContainer.addEventListener('click', (e) => {
        if (e.target.closest('.remove-lab-btn')) {
            const index = e.target.closest('.remove-lab-btn').dataset.index;
            patientData.laboratorios.splice(index, 1);
            renderLoadedLabs();
            updateAllCalculations();
        }
    });

    // Lógica de arrastrar y soltar para archivos
    const dropArea = document.getElementById('lab-upload-container');
    const labFileUpload = document.getElementById('lab-file-upload');
    const fileLoader = document.getElementById('file-loader');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => dropArea.addEventListener(eventName, e => {
        e.preventDefault();
        e.stopPropagation();
    }));
    ['dragenter', 'dragover'].forEach(eventName => dropArea.addEventListener(eventName, () => dropArea.classList.add('highlight')));
    ['dragleave', 'drop'].forEach(eventName => dropArea.addEventListener(eventName, () => dropArea.classList.remove('highlight')));
    dropArea.addEventListener('drop', e => {
        labFileUpload.files = e.dataTransfer.files;
        const changeEvent = new Event('change', { bubbles: true });
        labFileUpload.dispatchEvent(changeEvent);
    });

    const parseLabReportWithAI = async (text) => {
        fileLoader.classList.remove('hidden');
        
        // Primero intentamos usar el backend de Flask
        try {
            const response = await callBackend('parse_lab_report', { text });
            processLabResults(response);
        } catch (error) {
            // Si falla, usamos la API de Gemini directamente
            try {
                await parseLabReportWithGemini(text);
            } catch (geminiError) {
                console.error("Error al procesar con Gemini:", geminiError);
                showAlert("Error de Análisis", "No se pudo procesar el archivo. Verifique el formato o ingrese los datos manualmente.", "error");
            }
        } finally {
            fileLoader.classList.add('hidden');
        }
    };
    
    const parseLabReportWithGemini = async (text) => {
        const prompt = `Analiza el siguiente reporte de laboratorio de Colombia. Extrae los valores en formato JSON. Devuelve única y exclusivamente el objeto JSON sin texto adicional, explicaciones o markdown. El JSON debe contener "nombre_paciente", "edad_paciente", "sexo_paciente" ('m' o 'f'), "fecha_informe" (YYYY-MM-DD), y un array "resultados" con objetos {"nombre", "resultado", "unidades"}. Valores clave a extraer: creatinina en suero, hemoglobina glicosilada, colesterol ldl, colesterol hdl, trigliceridos, relacion microalbuminuria creatinina, glucosa, pth, albumina, sodio, potasio, fosforo, acido urico, calcio, hemoglobina, ferritina, bun. Texto:\n\n${text}`;
        
        // Usar el backend para parsear el reporte
        const response = await fetch(`${BACKEND_URL}/parse_document`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                text: text,
                use_ai: true
            })
        });
        
        if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
        
        
        const result = await response.json();
        const rawText = result.candidates[0].content.parts[0].text;
        
        const jsonMatch = rawText.match(/```json\s*([\s\S]*?)\s*```|({[\s\S]*})/);
        if (!jsonMatch) throw new Error("No se encontró un bloque JSON válido en la respuesta de la IA.");
        
        const jsonText = jsonMatch[1] || jsonMatch[2];
        const labData = JSON.parse(jsonText);
        
        processLabResults(labData);
    };
    
    const processLabResults = (labData) => {
        // Rellenar datos del paciente si están disponibles
        if (labData.nombre_paciente) document.getElementById('nombre').value = labData.nombre_paciente;
        if (labData.sexo_paciente) document.getElementById('sexo').value = labData.sexo_paciente;
        if (labData.edad_paciente) document.getElementById('edad').value = labData.edad_paciente;
        
        const reportDate = labData.fecha_informe || new Date().toISOString().split('T')[0];
        
        // Procesar resultados
        labData.resultados.forEach(lab => {
            let matchedKey = null;
            const nombreLowerCase = lab.nombre.toLowerCase();
            
            // Mapeo de nombres de laboratorio a claves
            if (/creatinina\s*(en suero|serica)/.test(nombreLowerCase)) matchedKey = 'creatinina';
            if (nombreLowerCase.includes('glicosilada')) matchedKey = 'hba1c';
            if (nombreLowerCase.includes('ldl')) matchedKey = 'ldl';
            if (nombreLowerCase.includes('hdl')) matchedKey = 'hdl';
            if (nombreLowerCase.includes('trigliceridos')) matchedKey = 'trigliceridos';
            if (nombreLowerCase.includes('relacion microalbuminuria')) matchedKey = 'rac';
            if (nombreLowerCase.includes('glucosa')) matchedKey = 'glicemia';
            if (nombreLowerCase.includes('pth')) matchedKey = 'pth';
            if (nombreLowerCase.includes('albumina')) matchedKey = 'albumina';
            if (nombreLowerCase.includes('sodio')) matchedKey = 'sodio';
            if (nombreLowerCase.includes('potasio')) matchedKey = 'potasio';
            if (nombreLowerCase.includes('fosforo')) matchedKey = 'fosforo';
            if (nombreLowerCase.includes('acido urico')) matchedKey = 'acido_urico';
            if (nombreLowerCase.includes('calcio')) matchedKey = 'calcio';
            if (nombreLowerCase.match(/hemoglobina(?!\s*glicosilada)/)) matchedKey = 'hemoglobina';
            if (nombreLowerCase.includes('ferritina')) matchedKey = 'ferritina';
            if (nombreLowerCase.includes('bun') || nombreLowerCase.includes('nitrogeno ureico')) matchedKey = 'bun';
            
            if(matchedKey) {
                // Extraer valor numérico
                let valor = parseFloat(lab.resultado);
                
                // Si no se puede convertir a número, intentar limpiar el texto
                if (isNaN(valor)) {
                    const numericMatch = lab.resultado.match(/(\d+[.,]?\d*)/);
                    if (numericMatch) valor = parseFloat(numericMatch[0].replace(',', '.'));
                }
                
                if (!isNaN(valor)) {
                    // Evitar duplicados
                    patientData.laboratorios = patientData.laboratorios.filter(l => l.id !== matchedKey);
                    patientData.laboratorios.push({ 
                        id: matchedKey, 
                        valor: valor, 
                        fecha: reportDate, 
                        nombreCompleto: labs[matchedKey]?.label || matchedKey,
                        unidades: lab.unidades || ''
                    });
                }
            }
        });
        
        // Actualizar UI con los resultados
        renderLoadedLabs();
        updateAllCalculations();
        
        // Mostrar mensaje de éxito
        showAlert("Análisis Completado", `Se han extraído ${patientData.laboratorios.length} resultados de laboratorio.`, "success");
    };

    labFileUpload.addEventListener('change', (event) => {
        const files = event.target.files;
        if (!files.length) return;
        
        Array.from(files).forEach(file => {
             const reader = new FileReader();
            if (file.type === 'application/pdf') {
                reader.onload = async (e) => {
                    try {
                        const typedarray = new Uint8Array(e.target.result);
                        const pdf = await pdfjsLib.getDocument(typedarray).promise;
                        let fullText = '';
                        for (let i = 1; i <= pdf.numPages; i++) {
                            const page = await pdf.getPage(i);
                            const textContent = await page.getTextContent();
                            fullText += textContent.items.map(item => item.str).join(' ');
                        }
                        parseLabReportWithAI(fullText);
                    } catch (error) {
                        console.error("Error al procesar PDF:", error);
                        showAlert("Error de Lectura", "No se pudo leer el archivo PDF. Intente con otro formato o ingrese los datos manualmente.", "error");
                    }
                };
                reader.readAsArrayBuffer(file);
            } else {
                reader.onload = (e) => parseLabReportWithAI(e.target.result);
                reader.readAsText(file);
            }
        });
    });

    // --- Generación de Informe ---
    const generateReportWithAI = async (data) => {
        document.getElementById('report-placeholder').classList.add('hidden');
        document.getElementById('report-loader').classList.remove('hidden');
        document.getElementById('report-output-container').classList.add('hidden');
        
        // Primero intentamos usar el backend de Flask
        try {
            const report = await callBackend('generate_report', data);
            renderReport(report.html_content || report);
        } catch (error) {
            // Si falla, usamos la API de Gemini directamente
            try {
                await generateReportWithGemini(data);
            } catch (geminiError) {
                console.error("Error al generar informe con Gemini:", geminiError);
                showAlert("Error de Generación", "No se pudo generar el informe. Intente de nuevo.", "error");
                document.getElementById('report-loader').classList.add('hidden');
                document.getElementById('report-placeholder').classList.remove('hidden');
            }
        }
    };
    
    const generateReportWithGemini = async (data) => {
        let maceAlertPrompt = '';
        if (data.adherencia === 'mala' || data.barreras_acceso) {
            maceAlertPrompt = `
            **ALERTA DE ALTO RIESGO MÉDICO-LEGAL:** El paciente reporta ${data.adherencia === 'mala' ? 'mala adherencia' : ''} ${data.barreras_acceso ? 'y barreras de acceso a medicamentos' : ''}.
            **INSTRUCCIÓN CRÍTICA:** En la sección "Análisis y Plan Farmacológico" del informe, debes incluir un párrafo de advertencia severo y explícito. Usa un tono formal y asertivo. Explica que esta situación, de persistir, incrementa de forma exponencial el riesgo a corto y mediano plazo de eventos cardiovasculares mayores (MACE), como infarto agudo de miocardio, accidente cerebrovascular y muerte de origen cardiovascular. Enfatiza que la falta de tratamiento continuo anula los beneficios de la terapia y representa una desviación del cuidado estándar, con potenciales consecuencias graves para la salud del paciente y responsabilidades para el sistema de salud. Enmarca este párrafo en un recuadro o con un título de "ADVERTENCIA".
            `;
        }
        
        let predialysisPrompt = '';
        if (data.predialysis_status) {
             predialysisPrompt = `**NOTA DE PREDIÁLISIS:** El paciente tiene una TFG <= 20 ml/min y está marcado como "${data.predialysis_status}" en el programa. Incluye una recomendación explícita para remitir a enfermería para ${data.predialysis_status === 'primera_vez' ? 'ingreso y educación' : 'control y seguimiento'} por el programa de prediálisis.`;
        }

        const prompt = `
            Actúa como un médico internista experto en riesgo cardiovascular y nefrología, generando un informe para otro colega.
            Basado en los siguientes datos del paciente en formato JSON, redacta un informe clínico completo y estructurado en Markdown, siguiendo rigurosamente las reglas clínicas implícitas en los datos.

            **DATOS DEL PACIENTE:**
            \`\`\`json
            ${JSON.stringify(data, null, 2)}
            \`\`\`

            **INSTRUCCIONES DETALLADAS (CUMPLIR A RAJATABLA):**
            1.  **Resumen Clínico:** Inicia con un párrafo conciso que resuma el caso.
            2.  **Clasificación de Riesgo y Estadio:**
                * **Riesgo Cardiovascular:** Determina el nivel de riesgo (Bajo, Moderado, Alto, Muy Alto) y JUSTIFICA tu decisión.
                * **Estadio ERC (KDIGO):** Clasifica la enfermedad renal usando la TFG y la albuminuria.
            3.  **Evaluación de Metas Terapéuticas:**
                * Para cada parámetro (PA, LDL, HbA1c), establece la meta según el riesgo y declara si está **EN META** o **FUERA DE META**.
            4.  **Análisis y Plan Farmacológico (EMULANDO pharma_engine.py):**
                * Propón un plan óptimo basado en los "4 pilares" (IECA/ARA II, iSGLT2/arGLP-1, Estatinas, Antiagregación).
                * **Justifica cada recomendación**, considerando la TFG para ajustes de dosis o contraindicaciones.
                * ${maceAlertPrompt}
            5.  **Plan de Seguimiento (EMULANDO follow_up.py):**
                * Analiza las FECHAS de los últimos laboratorios. Basado en su vigencia y el riesgo, define la frecuencia de los próximos controles.
                * Establece la fecha de la próxima cita médica.
                * ${predialysisPrompt}
        `;

        // Usar el backend para generar el informe
        const response = await fetch(`${BACKEND_URL}/generate_report`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                patient_data: data,
                prompt_template: prompt 
            })
        });
        
        if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
        
        const result = await response.json();
        const reportText = result.candidates[0].content.parts[0].text;
        
        renderReport(reportText);
    };
    
    const renderReport = (reportText) => {
        let htmlReport = reportText;
        
        // Si el reportText es Markdown, convertirlo a HTML
        if (!reportText.startsWith('<')) {
            htmlReport = reportText
                .replace(/ADVERTENCIA:/g, '<div class="alert-mace"><strong>ADVERTENCIA:</strong>')
                .replace(/(\*\*|__)(.*?)\1/g, '<strong>$2</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/^## (.*$)/gim, '<h2>$1</h2>')
                .replace(/^### (.*$)/gim, '<h3>$1</h3>')
                .replace(/^\* (.*$)/gim, '<li>$1</li>');
            
            htmlReport = htmlReport.replace(/<\/li>\n<li>/gim, '</li><li>');
            htmlReport = htmlReport.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
            htmlReport = htmlReport.replace(/<\/ul>\s*<ul>/g, '');
        }
        
        document.getElementById('report-output').innerHTML = htmlReport;
        document.getElementById('report-loader').classList.add('hidden');
        document.getElementById('report-output-container').classList.remove('hidden');
        
        // Notificar al usuario
        Swal.fire({
            position: 'top-end',
            icon: 'success',
            title: 'Informe generado con éxito',
            showConfirmButton: false,
            timer: 1500
        });
    };

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        updateAllCalculations(); 
        generateReportWithAI(patientData);
    });
    
    // --- Botones del Informe ---
    document.getElementById('copy-report-btn').addEventListener('click', () => {
        navigator.clipboard.writeText(document.getElementById('report-output').innerText)
            .then(() => showAlert("Éxito", "Informe copiado al portapapeles.", "success"))
            .catch(() => showAlert("Error", "No se pudo copiar el informe.", "error"));
    });
    
    document.getElementById('print-report-btn').addEventListener('click', () => {
        const reportContent = document.getElementById('report-output').innerHTML;
        const printWindow = window.open('', '', 'height=600,width=800');
        printWindow.document.write('<html><head><title>Informe Clínico - ERC Insight</title>');
        printWindow.document.write('<style>body{font-family:sans-serif;} h1,h2,h3{color:#1e293b;} h2{border-bottom:1px solid #e2e8f0;padding-bottom:4px;} .alert-mace{background-color:#fffbeb;border-left:4px solid #f59e0b;padding:1rem;margin:1.5rem 0;}</style>');
        printWindow.document.write('</head><body>');
        printWindow.document.write(`
            <div style="text-align:center;margin-bottom:20px;">
                <h1 style="color:#2563eb;margin-bottom:5px;">ERC Insight</h1>
                <p style="margin:0;color:#64748b;">Informe Clínico Generado: ${new Date().toLocaleDateString()}</p>
            </div>
        `);
        printWindow.document.write(reportContent);
        printWindow.document.write('</body></html>');
        printWindow.document.close();
        setTimeout(() => {
            printWindow.print();
        }, 500);
    });
    
    // Nuevo botón para guardar en PDF
    document.getElementById('save-report-btn').addEventListener('click', () => {
        showAlert("Guardando Informe", "Esta función enviará el informe al backend para guardarlo en la base de datos.", "info");
        
        // Aquí iría la lógica para guardar en el backend
        const reportContent = document.getElementById('report-output').innerHTML;
        
        callBackend('save_report', {
            patient_id: patientData.numero_documento || "sin_id",
            patient_name: patientData.nombre,
                report_content: reportContent,
                report_data: patientData
            });
