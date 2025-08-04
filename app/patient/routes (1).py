from flask import render_template, redirect, url_for, flash, request, jsonify
from app.patient import bp
from app.logic.patient_eval import calcular_tfg, determinar_etapa_erc
from app.utils.helpers import calcular_pa_promedio

@bp.route('/')
def index():
    """Muestra la lista de pacientes (placeholder)."""
    return render_template('patient/index.html', title='Gestión de Pacientes')

@bp.route('/new', methods=['GET', 'POST'])
def new():
    """Formulario para crear un nuevo paciente."""
    if request.method == 'POST':
        # Procesar datos del formulario
        # En una implementación real, estos datos se guardarían en una base de datos
        patient_data = {
            'nombre': request.form.get('nombre'),
            'edad': int(request.form.get('edad', 0)),
            'sexo': request.form.get('sexo'),
            'peso': float(request.form.get('peso', 0)),
            'creatinina': float(request.form.get('creatinina', 0)),
            'hta': request.form.get('hta') == 'on',
            'dm2': request.form.get('dm2') == 'on'
        }
        
        # Cálculos preliminares
        tfg = calcular_tfg(
            patient_data['edad'],
            patient_data['peso'],
            patient_data['creatinina'],
            patient_data['sexo']
        )
        
        patient_data['tfg'] = tfg
        patient_data['etapa_erc'] = determinar_etapa_erc(tfg)
        
        # En una aplicación real, aquí se guardarían los datos
        # Por ahora, redirigimos a una página de visualización simulada
        flash(f'Paciente {patient_data["nombre"]} creado correctamente.', 'success')
        return redirect(url_for('patient.view', patient_id=1))  # ID simulado
        
    return render_template('patient/form.html', title='Nuevo Paciente')

@bp.route('/<int:patient_id>')
def view(patient_id):
    """Vista detallada de un paciente."""
    # En una aplicación real, aquí se obtendrían los datos del paciente desde la BD
    # Por ahora, usamos datos de prueba
    patient_data = {
        'id': patient_id,
        'nombre': 'Juan Pérez',
        'edad': 65,
        'sexo': 'm',
        'peso': 75,
        'creatinina': 1.2,
        'tfg': 58.3,
        'etapa_erc': 'g3a',
        'hta': True,
        'dm2': False
    }
    
    return render_template('patient/view.html', title='Detalles del Paciente', patient=patient_data)

@bp.route('/api/tfg', methods=['POST'])
def calculate_tfg():
    """API para calcular TFG basado en parámetros enviados."""
    data = request.json
    
    try:
        tfg = calcular_tfg(
            int(data.get('edad', 0)),
            float(data.get('peso', 0)),
            float(data.get('creatinina', 1.0)),
            data.get('sexo', 'm')
        )
        
        etapa_erc = determinar_etapa_erc(tfg)
        
        return jsonify({
            'success': True,
            'tfg': tfg,
            'etapa_erc': etapa_erc
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
