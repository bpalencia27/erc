// erc_insight.js (versión limpiada)
// ****************************************************
// NOTA: Archivo reconstruido tras corrupción. Se removieron duplicados,
// bloques truncados y handlers repetidos. Mantiene la funcionalidad original
// esencial: cálculo de TFG, riesgo, metas, laboratorios (manual / upload / IA),
// fragilidad, medicamentos y generación de informe.
// ****************************************************

(function() { 'use strict';

// --- Estado Global ---
const patientData = {
  laboratorios: [],
  diagnostico: [],
  medicamentos: [],
  pa_values: [],
  riskLevel: null
};
const charts = {}; // Gráficos de metas
const BACKEND_URL = '/api';

// Utilidad segura de query
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

// --- Helpers generales ---
function showAlert(title, message, type = 'info') {
  if (window.Swal) {
    Swal.fire({ title, text: message, icon: type, confirmButtonColor: '#2563eb' });
  } else {
    alert(`${title}: ${message}`);
  }
}

async function callBackend(endpoint, data = {}, method = 'POST') {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (method !== 'GET') opts.body = JSON.stringify(data);
  const resp = await fetch(`${BACKEND_URL}/${endpoint}`, opts);
  if (!resp.ok) throw new Error(`Error ${resp.status}`);
  return resp.json();
}

// --- Cálculos Clínicos ---
function calculateTFG(creatinina, edad, sexo, peso) {
  if (!creatinina || !edad || !sexo || !peso) return null;
  const scr = parseFloat(creatinina); const age = parseInt(edad); const wt = parseFloat(peso);
  if (scr <= 0 || age <= 0 || wt <= 0) return null;
  const factorSexo = (sexo === 'f') ? 0.85 : 1.0;
  const tfg = ((140 - age) * wt * factorSexo) / (72 * scr);
  updateTFGMarker(tfg); updateKDIGOMarker(tfg);
  return Math.round(tfg);
}

function updateTFGMarker(tfg) {
  const marker = $('#tfg-marker'); if (!marker || !tfg) return;
  let pos = '95%';
  if (tfg < 15) pos = '7.5%'; else if (tfg < 30) pos = '22.5%'; else if (tfg < 45) pos = '37.5%'; else if (tfg < 60) pos = '52.5%'; else if (tfg < 90) pos = '75%';
  marker.style.left = pos;
}

function updateKDIGOMarker(tfg) {
  const marker = $('#kdigo-marker'); if (!marker || !tfg) return;
  let top = '20%';
  if (tfg < 15) top = '70%'; else if (tfg < 30) top = '60%'; else if (tfg < 45) top = '50%'; else if (tfg < 60) top = '40%'; else if (tfg < 90) top = '30%';
  // Ajuste horizontal por RAC
  let left = '20%';
  const racLab = patientData.laboratorios.find(l => l.id === 'rac');
  if (racLab) {
    const rac = parseFloat(racLab.valor);
    if (rac >= 300) left = '80%'; else if (rac >= 30) left = '50%';
  }
  marker.style.top = top; marker.style.left = left; marker.style.opacity = '1';
}

function calculateIMC() {
  const peso = parseFloat($('#peso')?.value); const tallaCm = parseFloat($('#talla')?.value);
  const out = $('#imc'); if (!out) return;
  if (peso && tallaCm > 0) {
    const tM = tallaCm / 100; const imc = (peso / (tM * tM)).toFixed(1);
    let clas = '';
    if (imc < 18.5) clas = ' (Bajo peso)'; else if (imc < 25) clas = ' (Normal)'; else if (imc < 30) clas = ' (Sobrepeso)'; else if (imc < 35) clas = ' (Obesidad I)'; else if (imc < 40) clas = ' (Obesidad II)'; else clas = ' (Obesidad III)';
    out.value = `${imc} kg/m²${clas}`;
  } else out.value = '';
}

// --- Riesgo y Metas ---
function updateRiskPanel() {
  const indicator = $('#risk-level-indicator'); const summary = $('#risk-factors-summary'); const ercIcon = $('#erc-alert-icon');
  if (!indicator || !summary) return;
  if (!patientData.edad || !patientData.creatinina || !patientData.peso || !patientData.diagnostico.length) {
    indicator.textContent = 'INCOMPLETO';
    indicator.className = 'risk-sphere bg-gray-400';
    summary.innerHTML = '<p>Complete los datos obligatorios (*).</p>';
    ercIcon?.classList.add('hidden');
    return;
  }
  let riskScore = 0; const rf = [];
  patientData.diagnostico.forEach(dx => { if (dx === 'DM') { riskScore += 2; rf.push('Diabetes Mellitus'); } if (dx === 'HTA') { riskScore += 1; rf.push('Hipertensión Arterial'); } if (dx === 'ERC') { riskScore += 2; rf.push('Enf. Renal Crónica'); } });
  if (patientData.ecv_establecida) { riskScore += 10; rf.push('ECV establecida'); }
  if (patientData.edad > 65) { riskScore += 2; rf.push('Edad > 65 años'); }
  if (patientData.tfg) { rf.push(`TFG: ${patientData.tfg} ml/min`); if (patientData.tfg < 30) riskScore += 4; else if (patientData.tfg < 60) riskScore += 2; }
  const racLab = patientData.laboratorios.find(l => l.id === 'rac'); if (racLab) { rf.push(`RAC: ${racLab.valor} mg/g`); if (racLab.valor > 30) riskScore += 2; }
  if (patientData.tabaquismo) { riskScore += 1; rf.push('Tabaquismo'); }
  if (patientData.fragil) { riskScore += 2; rf.push('Paciente Frágil'); }
  const ercSignificativa = (patientData.tfg && patientData.tfg < 60) || (racLab && racLab.valor > 30); ercIcon?.classList.toggle('hidden', !ercSignificativa);
  let level = 'BAJO'; let color = 'var(--risk-low)';
  if (riskScore >= 10 || (patientData.diagnostico.includes('DM') && patientData.tfg < 30)) { level = 'MUY ALTO'; color = 'var(--risk-very-high)'; }
  else if (riskScore >= 5) { level = 'ALTO'; color = 'var(--risk-high)'; }
  else if (riskScore >= 2) { level = 'MODERADO'; color = 'var(--risk-moderate)'; }
  patientData.riskLevel = level;
  indicator.innerHTML = `<span>${level}</span>`; indicator.style.backgroundColor = color;
  summary.innerHTML = rf.map(f => `<p class="flex items-center"><i class="fas fa-check-circle text-xs mr-2"></i>${f}</p>`).join('');
}

function updateGoalsPreview() {
  const container = $('#goals-preview-content'); if (!container) return;
  const paAvg = patientData.pa_values.length ? patientData.pa_values[0] : null;
  const ldlLab = patientData.laboratorios.find(l => l.id === 'ldl');
  const hba1cLab = patientData.laboratorios.find(l => l.id === 'hba1c');
  const goals = {
    pa: { label: 'Presión Arterial', target: { sys: 130, dia: 80 }, value: paAvg, unit: 'mmHg' },
    ldl: { label: 'Colesterol LDL', target: patientData.riskLevel === 'MUY ALTO' ? 55 : 70, value: ldlLab?.valor, unit: 'mg/dL' },
    hba1c: { label: 'HbA1c', target: 7.0, value: hba1cLab?.valor, unit: '%' }
  };
  container.innerHTML = '';
  let met = 0; let total = 0;
  Object.entries(goals).forEach(([key, goal]) => {
    let metGoal = false; if (goal.value !== undefined && goal.value !== null) {
      if (key === 'pa' && goal.value) { const [sys, dia] = goal.value.split('/').map(Number); metGoal = sys < goal.target.sys && dia < goal.target.dia; total++; }
      else if (typeof goal.value === 'number') { metGoal = goal.value < goal.target; total++; }
      if (metGoal) met++; }
    const statusIcon = goal.value ? (metGoal ? 'fa-check-circle text-green-500' : 'fa-times-circle text-red-500') : 'fa-minus-circle text-gray-400';
    container.insertAdjacentHTML('beforeend', `
      <div class="border-t pt-3">
        <div class="flex justify-between items-center text-sm">
          <div class="flex-1">
            <span class="font-medium">${goal.label}</span>
            <span class="text-gray-500">: ${goal.value ? `${goal.value} ${goal.unit}` : 'Sin datos'}</span>
            <span class="text-gray-500 ml-2">Meta: ${key === 'pa' ? `${goal.target.sys}/${goal.target.dia}` : goal.target} ${goal.unit}</span>
          </div>
          <i class="fas ${statusIcon}"></i>
        </div>
        <div class="goal-chart-container"><canvas id="chart-${key}"></canvas></div>
      </div>`);
    if (key === 'pa') {
      // Map only systolic for quick line
      const paData = patientData.pa_values.map((pa, i) => { const [s] = pa.split('/').map(Number); return { fecha: new Date(Date.now() - (patientData.pa_values.length - i) * 86400000).toISOString(), valor: s }; });
      renderGoalChart(key, paData);
    } else {
      const labSeries = patientData.laboratorios.filter(l => l.id === key);
      renderGoalChart(key, labSeries);
    }
  });
  if (window.updateProgressChart) window.updateProgressChart(total ? (met / total) * 100 : 0);
}

function renderGoalChart(key, data) {
  const ctx = document.getElementById(`chart-${key}`)?.getContext('2d'); if (!ctx || !window.Chart) return;
  if (charts[key]) charts[key].destroy();
  const chartData = data.map(d => ({ x: d.fecha ? new Date(d.fecha) : new Date(), y: d.valor })).sort((a,b)=>a.x-b.x);
  charts[key] = new Chart(ctx, { type: 'line', data: { datasets: [{ label: key.toUpperCase(), data: chartData, borderColor: '#2563eb', backgroundColor: 'rgba(37,99,235,0.15)', tension: 0.3, fill: true, pointRadius: 2 }] }, options: { responsive:true, maintainAspectRatio:false, parsing:false, scales:{ x:{ type:'time', display:false }, y:{ display:false } }, plugins:{ legend:{ display:false } }}});
}

function generateMedicationRecommendations() {
  const wrapper = $('#medication-recommendations'); const content = $('#medication-recommendations-content');
  if (!wrapper || !content) return;
  if (!patientData.diagnostico.length || !patientData.tfg) { wrapper.classList.add('hidden'); return; }
  const rec = [];
  if (patientData.diagnostico.includes('HTA')) {
    if (patientData.tfg < 30) rec.push('ARA II a dosis bajas con monitorización de potasio y creatinina.');
    else rec.push('IECA o ARA II en dosis óptimas.');
  }
  if (patientData.diagnostico.includes('DM')) {
    if (patientData.tfg > 30) rec.push('iSGLT2 (ej. Empagliflozina 10mg/día) para nefro y cardioprotección.');
    else rec.push('Evitar iSGLT2 con TFG <30. Considerar arGLP1.');
    if (patientData.tfg < 45) rec.push('Ajustar dosis de Metformina (máx 1000mg/día).');
  }
  if (patientData.tfg < 60 || patientData.diagnostico.includes('DM')) rec.push('Estatina de alta intensidad.');
  if (patientData.tfg < 20) rec.push('Remitir a nefrología para preparación de TRR.');
  if (rec.length) { content.innerHTML = rec.map(r=>`<p><i class="fas fa-angle-right text-primary mr-2"></i>${r}</p>`).join(''); wrapper.classList.remove('hidden'); } else wrapper.classList.add('hidden');
}

// --- Laboratorios (config y UI manual) ---
const labsConfig = {
  hba1c:{ label:'HbA1c (%)', normal:{min:0,max:5.7}, alert:{min:7,max:100}},
  ldl:{ label:'Colesterol LDL (mg/dL)', normal:{min:0,max:100}, alert:{min:130,max:1000}},
  hdl:{ label:'Colesterol HDL (mg/dL)', normal:{min:40,max:100}, alert:{min:0,max:35}},
  trigliceridos:{ label:'Triglicéridos (mg/dL)', normal:{min:0,max:150}, alert:{min:200,max:2000}},
  rac:{ label:'RAC (mg/g)', normal:{min:0,max:30}, alert:{min:300,max:10000}},
  glicemia:{ label:'Glicemia (mg/dL)', normal:{min:70,max:100}, alert:{min:126,max:500}},
  pth:{ label:'PTH (pg/mL)', normal:{min:15,max:65}, alert:{min:100,max:1000}},
  albumina:{ label:'Albúmina (g/dL)', normal:{min:3.5,max:5.2}, alert:{min:0,max:3}},
  potasio:{ label:'Potasio (mEq/L)', normal:{min:3.5,max:5.0}, alert:{min:5.5,max:7}},
  sodio:{ label:'Sodio (mEq/L)', normal:{min:135,max:145}, alert:{min:0,max:130}},
  fosforo:{ label:'Fósforo (mg/dL)', normal:{min:2.5,max:4.5}, alert:{min:5.5,max:10}},
  acido_urico:{ label:'Ácido Úrico (mg/dL)', normal:{min:2.4,max:6.0}, alert:{min:7,max:15}},
  calcio:{ label:'Calcio (mg/dL)', normal:{min:8.5,max:10.5}, alert:{min:0,max:8}},
  hemoglobina:{ label:'Hemoglobina (g/dL)', normal:{min:12,max:16}, alert:{min:0,max:10}},
  ferritina:{ label:'Ferritina (ng/mL)', normal:{min:30,max:300}, alert:{min:0,max:15}},
  bun:{ label:'BUN (mg/dL)', normal:{min:7,max:20}, alert:{min:50,max:200}},
  creatinina:{ label:'Creatinina (mg/dL)', normal:{min:0.4,max:1.4}, alert:{min:2,max:20}}
};

function getLabStatus(id, value) {
  if (!labsConfig[id] || value === undefined || value === null || value === '') return '';
  const v = parseFloat(value); if (isNaN(v)) return '';
  const { normal, alert } = labsConfig[id];
  if (v >= normal.min && v <= normal.max) return 'normal';
  if (v >= alert.min && v <= alert.max) return 'alert';
  return 'warning';
}

function renderLabInputs() {
  const grid = document.querySelector('.lab-grid'); if (!grid) return;
  grid.innerHTML = '';
  Object.entries(labsConfig).forEach(([key, cfg]) => {
    const card = document.createElement('div'); card.className = 'lab-card lab-entry'; card.dataset.labName = key;
    card.innerHTML = `
      <label class="text-xs font-semibold text-gray-700 mb-1 block">${cfg.label}</label>
      <div class="flex items-center gap-2 mb-2">
        <input type="number" step="0.01" placeholder="Valor" class="input-field lab-value text-sm">
        <div class="enhanced-tooltip"><i class="fas fa-info-circle text-gray-400"></i>
          <div class="tooltip-content">
            <h4 class="font-medium mb-1">Rangos:</h4>
            <p class="text-xs">Normal: ${cfg.normal.min} - ${cfg.normal.max}</p>
            <p class="text-xs">Alerta: ${cfg.alert.min > cfg.alert.max ? '< ' + cfg.alert.min : '> ' + cfg.alert.max}</p>
          </div>
        </div>
      </div>
      <input type="date" class="input-field lab-date text-sm">
    `;
    grid.appendChild(card);
    const valueInput = card.querySelector('.lab-value');
    valueInput.addEventListener('input', () => {
      const val = parseFloat(valueInput.value);
      if (!isNaN(val)) {
        const status = getLabStatus(key, val);
        valueInput.style.backgroundColor = status === 'normal' ? '#dcfce7' : status === 'warning' ? '#fef3c7' : status === 'alert' ? '#fee2e2' : '';
        updateAllCalculations();
      }
    });
  });
}

function renderLoadedLabs() {
  const cont = $('#loaded-labs-container'); if (!cont) return;
  cont.innerHTML = '';
  if (patientData.laboratorios.length) cont.innerHTML = '<h3 class="font-medium text-sm mb-2">Laboratorios Registrados:</h3>';
  patientData.laboratorios.forEach((lab, i) => {
    const cfg = labsConfig[lab.id] || { label: lab.id }; const status = getLabStatus(lab.id, lab.valor);
    const statusClass = status ? status : '';
    cont.insertAdjacentHTML('beforeend', `
      <div class="bg-gray-50 p-2 rounded-lg flex items-center justify-between mb-2 card-slide-in">
        <div>
          <span class="font-semibold text-sm">${cfg.label}</span>: 
          <span class="lab-value-pill ${statusClass}">${lab.valor}</span>
          <span class="text-xs text-gray-500 ml-2">(${lab.fecha || 'Sin fecha'})</span>
        </div>
        <button type="button" class="remove-lab-btn text-red-400 hover:text-red-600" data-index="${i}" aria-label="Eliminar laboratorio"><i class="fas fa-times-circle"></i></button>
      </div>`);
  });
}

function syncManualLabInputsIntoState() {
  document.querySelectorAll('.lab-entry').forEach(row => {
    const id = row.dataset.labName; const value = row.querySelector('.lab-value').value; const fecha = row.querySelector('.lab-date').value;
    const idx = patientData.laboratorios.findIndex(l => l.id === id);
    if (value) {
      const entry = { id, valor: parseFloat(value), fecha: fecha || new Date().toISOString().split('T')[0], nombreCompleto: labsConfig[id].label };
      if (idx > -1) patientData.laboratorios[idx] = entry; else patientData.laboratorios.push(entry);
    } else if (idx > -1) patientData.laboratorios.splice(idx, 1);
  });
}

// --- Procesamiento desde IA / Archivo ---
function processLabResults(labData) {
  try {
    if (!labData) return;
    if (labData.nombre_paciente) $('#nombre') && ($('#nombre').value = labData.nombre_paciente);
    if (labData.sexo_paciente) $('#sexo') && ($('#sexo').value = labData.sexo_paciente);
    if (labData.edad_paciente) $('#edad') && ($('#edad').value = labData.edad_paciente);
    const reportDate = labData.fecha_informe || new Date().toISOString().split('T')[0];
    if (Array.isArray(labData.resultados)) {
      labData.resultados.forEach(lab => {
        const nombre = (lab.nombre || '').toLowerCase();
        let key = null;
        if (/creatinina/.test(nombre)) key = 'creatinina';
        else if (nombre.includes('glicosilada')) key = 'hba1c';
        else if (nombre.includes(' ldl')) key = 'ldl';
        else if (nombre.includes('hdl')) key = 'hdl';
        else if (nombre.includes('triglicer')) key = 'trigliceridos';
        else if (nombre.includes('microalbuminuria') || nombre.includes('relacion micro')) key = 'rac';
        else if (nombre.includes('glucosa')) key = 'glicemia';
        else if (nombre.includes('pth')) key = 'pth';
        else if (nombre.includes('albumina')) key = 'albumina';
        else if (nombre.includes('sodio')) key = 'sodio';
        else if (nombre.includes('potasio')) key = 'potasio';
        else if (nombre.includes('fosforo')) key = 'fosforo';
        else if (nombre.includes('acido urico')) key = 'acido_urico';
        else if (nombre.includes('calcio')) key = 'calcio';
        else if (/hemoglobina(?!.*glicosilada)/.test(nombre)) key = 'hemoglobina';
        else if (nombre.includes('ferritina')) key = 'ferritina';
        else if (nombre.includes('bun') || nombre.includes('nitrogeno ureico')) key = 'bun';
        if (!key) return;
        let valor = parseFloat(lab.resultado);
        if (isNaN(valor) && lab.resultado) { const m = lab.resultado.toString().match(/([\d.,]+)/); if (m) valor = parseFloat(m[1].replace(',', '.')); }
        if (isNaN(valor)) return;
        const existing = patientData.laboratorios.find(l => l.id === key);
        const entry = { id: key, valor, fecha: reportDate, nombreCompleto: labsConfig[key]?.label || key };
        if (existing) Object.assign(existing, entry); else patientData.laboratorios.push(entry);
      });
    }
    renderLoadedLabs();
    updateAllCalculations();
    showAlert('Éxito', 'Resultados de laboratorio importados', 'success');
  } catch (e) { console.error(e); showAlert('Error', 'No se pudieron procesar los resultados.', 'error'); }
}

async function parseLabReportWithAI(text) {
  $('#file-loader')?.classList.remove('hidden');
  try {
    const resp = await callBackend('parse_lab_report', { text });
    processLabResults(resp);
  } catch (err) {
    console.warn('Fallo backend parse_lab_report, intentando Gemini...', err);
    try { await parseLabReportWithGemini(text); } catch (gErr) { console.error(gErr); showAlert('Error de Análisis', 'No se pudo procesar el archivo.', 'error'); }
  } finally { $('#file-loader')?.classList.add('hidden'); }
}

async function parseLabReportWithGemini(text) {
  const resp = await fetch(`${BACKEND_URL}/parse_document`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ text, use_ai:true }) });
  if (!resp.ok) throw new Error('Gemini backend error');
  const result = await resp.json();
  const raw = result.candidates?.[0]?.content?.parts?.[0]?.text || '';
  const match = raw.match(/```json\s*([\s\S]*?)```|({[\s\S]*})/);
  if (!match) throw new Error('JSON no encontrado en respuesta IA');
  const jsonText = match[1] || match[2];
  const labData = JSON.parse(jsonText);
  processLabResults(labData);
}

// --- Reporte ---
async function generateReportWithAI(data) {
  const placeholder = $('#report-placeholder'); const loader = $('#report-loader'); const container = $('#report-output-container');
  placeholder?.classList.add('hidden'); loader?.classList.remove('hidden'); container?.classList.add('hidden');
  try {
    const report = await callBackend('generate_report', data);
    renderReport(report.html_content || report);
  } catch (err) {
    try { await generateReportWithGemini(data); } catch (g) { console.error(g); showAlert('Error', 'No se pudo generar el informe.', 'error'); loader?.classList.add('hidden'); placeholder?.classList.remove('hidden'); }
  }
}

async function generateReportWithGemini(data) {
  const prompt = `Genera informe clínico estructurado en Markdown basado en los siguientes datos JSON. Analiza riesgo, metas terapéuticas y plan farmacológico.\n\n${JSON.stringify(data)}`;
  const resp = await fetch(`${BACKEND_URL}/generate_report`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ patient_data: data, prompt_template: prompt }) });
  if (!resp.ok) throw new Error('Gemini error');
  const result = await resp.json();
  const text = result.candidates?.[0]?.content?.parts?.[0]?.text || 'Informe no disponible.';
  renderReport(text);
}

function renderReport(text) {
  let html = text;
  if (!text.startsWith('<')) { // Markdown simple a HTML básico
    html = text
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^\* (.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/gs, m => `<ul>${m}</ul>`).replace(/<\/ul>\s*<ul>/g,'');
  }
  $('#report-output')?.setAttribute('data-html','1');
  $('#report-output').innerHTML = html;
  $('#report-loader')?.classList.add('hidden');
  $('#report-output-container')?.classList.remove('hidden');
  if (window.Swal) Swal.fire({ position:'top-end', icon:'success', title:'Informe generado', timer:1200, showConfirmButton:false });
}

// --- Actualización global de cálculos ---
function updateAllCalculations() {
  const form = $('#clinical-form'); if (!form) return;
  const data = new FormData(form); const formObj = Object.fromEntries(data.entries());
  Object.assign(patientData, formObj);
  patientData.diagnostico = data.getAll('diagnostico');
  // Medicamentos
  patientData.medicamentos = $$('#medicamentos-container .grid').map(row => ({
    nombre: row.querySelector('[name="med-nombre"]').value,
    dosis: row.querySelector('[name="med-dosis"]').value,
    frecuencia: row.querySelector('[name="med-frecuencia"]').value
  })).filter(m => m.nombre);
  // PA
  patientData.pa_values = $$('#pa-container .grid').map(row => {
    const sys = row.querySelector('.pa-sys').value; const dia = row.querySelector('.pa-dia').value; return (sys && dia) ? `${sys}/${dia}` : null; }).filter(Boolean);
  // Laboratorios manuales -> estado
  syncManualLabInputsIntoState();
  // Calcular TFG
  patientData.tfg = calculateTFG(patientData.creatinina, patientData.edad, patientData.sexo, patientData.peso);
  if ($('#tfg-display')) $('#tfg-display').value = patientData.tfg ? `${patientData.tfg} mL/min` : '';
  // Ajuste ERC/predialisis
  const ercCheckbox = $('#erc-checkbox'); const predialysis = $('#predialysis-section');
  if (ercCheckbox && predialysis) {
    if (patientData.tfg) {
      if (patientData.tfg <= 60) { ercCheckbox.checked = true; ercCheckbox.disabled = true; } else ercCheckbox.disabled = false;
      predialysis.classList.toggle('hidden', patientData.tfg > 20);
    } else { ercCheckbox.disabled = false; predialysis.classList.add('hidden'); }
  }
  updateRiskPanel(); updateGoalsPreview(); generateMedicationRecommendations();
}

// --- Fragilidad ---
function setupFragility() {
  const modal = $('#fragility-modal'); if (!modal) return;
  const checks = modal.querySelectorAll('#fried-criteria input');
  checks.forEach(cb => cb.addEventListener('change', () => {
    const count = Array.from(checks).filter(i => i.checked).length;
    const statusEl = $('#frailty-status'); const marker = $('#frailty-marker');
    let status = 'No Frágil'; let pos = '0%';
    if (count >= 3) { status = 'Frágil'; pos = '100%'; patientData.fragil = true; }
    else if (count > 0) { status = 'Pre-Frágil'; pos = '50%'; patientData.fragil = false; }
    else patientData.fragil = false;
    if (statusEl) statusEl.textContent = status; if (marker) marker.style.left = pos; updateAllCalculations();
  }));
}

// --- Medicamentos UI ---
function addMedicamento(nombre = '', dosis = '', frecuencia = '') {
  const cont = $('#medicamentos-container'); if (!cont) return;
  const div = document.createElement('div'); div.className = 'grid grid-cols-12 gap-2 items-center';
  div.innerHTML = `
    <input type="text" name="med-nombre" placeholder="Nombre" class="input-field col-span-5" value="${nombre}">
    <input type="text" name="med-dosis" placeholder="Dosis" class="input-field col-span-3" value="${dosis}">
    <input type="text" name="med-frecuencia" placeholder="Frecuencia" class="input-field col-span-3" value="${frecuencia}">
    <button type="button" class="remove-med-btn text-red-500 hover:text-red-700 col-span-1" aria-label="Eliminar medicamento"><i class="fas fa-trash"></i></button>`;
  cont.appendChild(div);
  div.querySelector('.remove-med-btn').addEventListener('click', () => { div.remove(); updateAllCalculations(); });
  ['input','change'].forEach(evt => div.addEventListener(evt, updateAllCalculations));
}

function setupMedicationShortcuts() {
  $$('#add-medicamento-btn').forEach(btn => btn.addEventListener('click', () => { addMedicamento(); }));
  $$('.quick-med-btn').forEach(btn => btn.addEventListener('click', () => { addMedicamento(btn.dataset.med, btn.dataset.dosis, btn.dataset.freq); updateAllCalculations(); }));
}

// --- Presión Arterial ---
function addPaReading(sys = '', dia = '') {
  const cont = $('#pa-container'); if (!cont) return;
  const div = document.createElement('div'); div.className = 'grid grid-cols-12 gap-2 items-center';
  div.innerHTML = `
    <input type="number" placeholder="Sistólica" class="input-field col-span-5 pa-sys" value="${sys}">
    <span class="text-center col-span-1">/</span>
    <input type="number" placeholder="Diastólica" class="input-field col-span-5 pa-dia" value="${dia}">
    <button type="button" class="remove-pa-btn text-red-500 hover:text-red-700 col-span-1" aria-label="Eliminar medición"><i class="fas fa-trash"></i></button>`;
  cont.appendChild(div);
  const sysI = div.querySelector('.pa-sys'); const diaI = div.querySelector('.pa-dia');
  const colorize = () => {
    const s = parseInt(sysI.value); const d = parseInt(diaI.value);
    sysI.style.backgroundColor = (isNaN(s)) ? '' : (s < 120 ? '#dcfce7' : s < 130 ? '#fef3c7' : '#fee2e2');
    diaI.style.backgroundColor = (isNaN(d)) ? '' : (d < 80 ? '#dcfce7' : d < 90 ? '#fef3c7' : '#fee2e2');
    updateAllCalculations();
  };
  ['input','change'].forEach(evt => { sysI.addEventListener(evt,colorize); diaI.addEventListener(evt,colorize); });
  div.querySelector('.remove-pa-btn').addEventListener('click', () => { div.remove(); updateAllCalculations(); });
}

// --- File Upload (Lab Reports) ---
function setupLabFileUpload() {
  const dropArea = $('#lab-upload-container'); const labFile = $('#lab-file-upload');
  if (!dropArea || !labFile) return;
  ['dragenter','dragover','dragleave','drop'].forEach(ev => dropArea.addEventListener(ev, e => { e.preventDefault(); e.stopPropagation(); }));
  ['dragenter','dragover'].forEach(ev => dropArea.addEventListener(ev, () => dropArea.classList.add('highlight')));
  ['dragleave','drop'].forEach(ev => dropArea.addEventListener(ev, () => dropArea.classList.remove('highlight')));
  dropArea.addEventListener('drop', e => { labFile.files = e.dataTransfer.files; labFile.dispatchEvent(new Event('change',{bubbles:true})); });
  labFile.addEventListener('change', e => {
    const files = Array.from(e.target.files); if (!files.length) return;
    files.forEach(file => {
      const reader = new FileReader();
      if (file.type === 'application/pdf') {
        reader.onload = async (ev) => {
          if (!window.pdfjsLib) { showAlert('PDF', 'Librería pdfjsLib no cargada.', 'error'); return; }
            try {
              const pdf = await pdfjsLib.getDocument(new Uint8Array(ev.target.result)).promise;
              let txt = '';
              for (let p=1; p<=pdf.numPages; p++) {
                const page = await pdf.getPage(p); const tc = await page.getTextContent();
                txt += tc.items.map(it => it.str).join(' ') + '\n';
              }
              parseLabReportWithAI(txt);
            } catch (err) { console.error(err); showAlert('Error PDF','No se pudo leer el PDF','error'); }
        };
        reader.readAsArrayBuffer(file);
      } else {
        reader.onload = ev => parseLabReportWithAI(ev.target.result);
        reader.readAsText(file);
      }
    });
    e.target.value = '';
  });
}

// --- Manual / Upload method toggle ---
function setupLabMethodToggle() {
  $$("input[name='lab-input-method']").forEach(r => r.addEventListener('change', () => {
    ['manual','upload','api'].forEach(v => { const el = document.getElementById(`${v}-labs-container`); el && el.classList.add('hidden'); });
    const val = document.querySelector("input[name='lab-input-method']:checked")?.value; if (val) { $(`#${val}-labs-container`)?.classList.remove('hidden'); }
  }));
}

// --- Form & Submit ---
function setupForm() {
  const form = $('#clinical-form'); if (!form) return;
  form.addEventListener('submit', e => { e.preventDefault(); updateAllCalculations(); generateReportWithAI(patientData); });
}

// --- Botones Reporte ---
function setupReportButtons() {
  $('#copy-report-btn')?.addEventListener('click', () => {
    navigator.clipboard.writeText($('#report-output')?.innerText || '').then(()=>showAlert('Éxito','Informe copiado.','success')).catch(()=>showAlert('Error','No se pudo copiar.','error'));
  });
  $('#print-report-btn')?.addEventListener('click', () => {
    const content = $('#report-output')?.innerHTML || ''; const w = window.open('', '_blank');
    if (!w) return; w.document.write('<html><head><title>Informe ERC Insight</title><style>body{font-family:sans-serif;padding:20px;} h1,h2,h3{color:#1e293b;} .alert-mace{background:#fffbeb;border-left:4px solid #f59e0b;padding:1rem;margin:1rem 0;}</style></head><body>');
    w.document.write(`<h1 style="text-align:center;color:#2563eb;">ERC Insight</h1><p style="text-align:center;color:#64748b;">Generado: ${new Date().toLocaleDateString()}</p>`);
    w.document.write(content); w.document.write('</body></html>'); w.document.close(); setTimeout(()=>w.print(), 400);
  });
  $('#save-report-btn')?.addEventListener('click', () => {
    const reportContent = $('#report-output')?.innerHTML || '';
    callBackend('save_report', { patient_id: patientData.numero_documento || 'sin_id', patient_name: patientData.nombre, report_content: reportContent, report_data: patientData })
      .then(()=>showAlert('Guardado','Informe guardado.','success'))
      .catch(err => { console.error(err); showAlert('Error','No se pudo guardar.','error'); });
  });
}

// --- Relleno form desde resultados (uso externo) ---
window.fillFormFromLabResults = function(results) {
  if (!results || !results.results) return;
  const mapping = { creatinina:'creatinina', hemoglobina:'hemoglobina', albumina:'albumina', calcio:'calcio', fosforo:'fosforo', pth:'pth' };
  Object.entries(mapping).forEach(([labKey, formId]) => {
    const el = document.getElementById(formId); if (!el) return;
    const val = results.results[labKey]; if (val !== undefined && val !== null) { el.value = val; el.dispatchEvent(new Event('change')); }
  });
  if (results.patient_data) {
    const pMap = { edad:'edad', sexo:'sexo', peso:'peso' };
    Object.entries(pMap).forEach(([k,v]) => { const el = document.getElementById(v); if (el && results.patient_data[k] !== undefined) { el.value = results.patient_data[k]; el.dispatchEvent(new Event('change')); }});
  }
  updateAllCalculations();
};

// --- Init principal ---
function init() {
  if (!document.getElementById('clinical-form')) return;
  // Listeners básicos
  $('#peso')?.addEventListener('input', calculateIMC); $('#talla')?.addEventListener('input', calculateIMC);
  renderLabInputs(); setupLabMethodToggle(); setupLabFileUpload(); setupFragility(); setupMedicationShortcuts(); setupForm(); setupReportButtons();
  addMedicamento(); addPaReading(); // entradas iniciales
  updateAllCalculations();
  ensureCheckboxInteractions();
}

document.addEventListener('DOMContentLoaded', init);

})();