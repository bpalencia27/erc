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

- Python 3.9.13
- Flask 2.3+
- PostgreSQL (para producción)
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
   GEMINI_API_KEY=tu-api-key-de-gemini
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

## Despliegue en Render.com (Plan Gratuito)

Este proyecto está optimizado para despliegue en Render.com utilizando el plan gratuito. Para instrucciones detalladas, consulta:

1. `RENDER_FREE_DEPLOYMENT.md` - Guía paso a paso para despliegue con plan gratuito
2. `pre_deploy_check.py` - Script para verificar que todo esté listo para el despliegue
3. `keep_alive.py` - Script para mantener la aplicación activa (evitar hibernación)

### Pasos rápidos para despliegue

1. Asegúrate de que tu código esté en GitHub
2. Crea una cuenta en Render.com
3. Crea un servicio web conectado a tu repositorio
4. Configura una base de datos PostgreSQL
5. Configura las variables de entorno
6. Despliega la aplicación

Para más detalles, ejecuta:
```
python pre_deploy_check.py
```

## Variables de Entorno

Consulta el archivo `.env.example` y `ENV_INSTRUCTIONS.md` para detalles sobre las variables de entorno necesarias.

## Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT.
