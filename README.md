# ERC Insight - Plataforma de Análisis Clínico con IA

## Descripción

ERC Insight es una plataforma web para el análisis clínico de pacientes con enfermedad renal crónica y otras condiciones relacionadas. Utiliza inteligencia artificial para procesar datos de pacientes y generar informes médicos detallados.

## Características Principales

- Cálculo automático de TFG y clasificación de ERC
- Extracción de datos desde archivos PDF y TXT
- Análisis de riesgo cardiovascular
- Programación inteligente de citas según etapa ERC
- Generación de informes médicos con IA (Google Gemini)
- Interfaz web intuitiva para carga de documentos

## Requisitos

- Python 3.9+
- Flask 2.3+
- Otras dependencias listadas en requirements.txt

## Instalación

1. Clonar el repositorio:
   ```
   git clone https://github.com/tu-usuario/erc-insight.git
   cd erc-insight
   ```

2. Crear y activar entorno virtual:
   ```
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno:
   Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:
   ```
   FLASK_APP=wsgi.py
   FLASK_ENV=development
   GOOGLE_AI_API_KEY=tu-api-key-de-gemini
   SECRET_KEY=tu-clave-secreta
   ```

## Ejecución

Para desarrollo:
```
python run.py
```

Para producción:
```
gunicorn -w 4 wsgi:app
```

## Estructura del Proyecto

- `app/`: Código principal de la aplicación
  - `main/`: Blueprint para las rutas principales
  - `patient/`: Blueprint para gestión de pacientes
  - `report/`: Blueprint para generación de informes
  - `upload/`: Blueprint para carga de documentos
  - `logic/`: Lógica de negocio
  - `parsers/`: Extractores de datos
  - `api/`: Integraciones con APIs externas
  - `static/`: Archivos estáticos
  - `templates/`: Plantillas HTML

## Despliegue en PythonAnywhere

Ver la documentación detallada en `docs/deployment.md`

## Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT.
