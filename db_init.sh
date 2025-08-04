#!/bin/bash
# Script para inicializar la base de datos en Render.com
# Este script se ejecuta como parte del proceso de despliegue

echo "Iniciando la configuración de la base de datos..."

# Aplicar migraciones
echo "Aplicando migraciones..."
python -m flask db upgrade

# Verificar si la base de datos está vacía
# Si lo está, inicializar con datos básicos
echo "Verificando si se necesita inicializar la base de datos..."
python -c "
from app import create_app, db
from app.models.patient import Patient

app = create_app('production')
with app.app_context():
    # Verificar si hay pacientes en la base de datos
    if Patient.query.count() == 0:
        print('Base de datos vacía, inicializando datos básicos...')
        # Aquí puedes agregar código para inicializar datos básicos
    else:
        print('Base de datos ya inicializada, omitiendo inicialización.')
"

echo "Configuración de la base de datos completada."
