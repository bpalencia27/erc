from flask import (
    render_template, request, 
    current_app, jsonify, flash, redirect, url_for
)
import os
from werkzeug.utils import secure_filename
from app.parsers.pdf_extractor import extract_data_from_pdf
from app.parsers.txt_extractor import extract_data_from_txt
from app.parsers.lab_parser import parse_lab_results
from app.upload import bp

ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/', methods=['GET'])
def upload_form():
    return render_template('upload/pdf_uploader.html')

@bp.route('/process', methods=['POST'])
def process_document():
    # Verificar si hay archivo en la solicitud
    if 'file' not in request.files:
        flash('No se encontró ningún archivo', 'error')
        return redirect(url_for('upload.upload_form'))
    
    file = request.files['file']
    
    # Verificar si se seleccionó un archivo
    if file.filename == '':
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('upload.upload_form'))
    
    # Verificar si el archivo es permitido
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.static_folder, 'uploads', filename)
        file.save(file_path)
        
        # Extraer datos según tipo de archivo
        if filename.endswith('.pdf'):
            raw_data = extract_data_from_pdf(file_path)
        elif filename.endswith('.txt'):
            raw_data = extract_data_from_txt(file_path)
        else:
            flash('Tipo de archivo no soportado', 'error')
            return redirect(url_for('upload.upload_form'))
        
        # Parsear los resultados de laboratorio
        lab_results = parse_lab_results(raw_data)
        
        # Retornar resultados en formato JSON
        return jsonify({
            'success': True,
            'file_path': file_path,
            'results': lab_results
        })
    
    flash('Tipo de archivo no permitido', 'error')
    return redirect(url_for('upload.upload_form'))
