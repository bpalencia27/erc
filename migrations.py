from flask_migrate import Migrate
from app import create_app, db
from app.models.patient import Patient
from app.models.lab_result import LabResult
from app.models.report import Report

app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    """Configura el contexto del shell de Flask."""
    return {
        'db': db, 
        'Patient': Patient, 
        'LabResult': LabResult, 
        'Report': Report
    }
