from flask import (
    Blueprint,
    render_template, request,
    current_app, jsonify, flash, redirect, url_for
)
bp = Blueprint('upload', __name__)
import os
from werkzeug.utils import secure_filename
from . import bp
from app.parsers.pdf_extractor import extract_data_from_pdf
from app.parsers.txt_extractor import extract_data_from_txt
from app.parsers.lab_parser import parse_lab_results

ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload', methods=['GET'])
def upload_form():
    return render_template('upload/pdf_uploader.html')

@bp.route('/process', methods=['POST'])
def process_document():
    if 'file' not in request.files:
        flash('No se encontrÃ³ ningÃºn archivo', 'error')
        return redirect(url_for('upload.upload_form'))

    file = request.files['file']

    if file.filename == '':
        flash('No se seleccionÃ³ ningÃºn archivo', 'error')
        return redirect(url_for('upload.upload_form'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.static_folder, 'uploads', filename)
        file.save(file_path)

        if filename.endswith('.pdf'):
            raw_data = extract_data_from_pdf(file_path)
        elif filename.endswith('.txt'):
            raw_data = extract_data_from_txt(file_path)
        else:
            flash('Tipo de archivo no soportado', 'error')
            return redirect(url_for('upload.upload_form'))

        lab_results = parse_lab_results(raw_data)

        return jsonify({
            'success': True,
            'file_path': file_path,
            'results': lab_results
        })

    flash('Tipo de archivo no permitido', 'error')
    return redirect(url_for('upload.upload_form'))
