# 🏥 ERC Insight - Sistema de Análisis Renal con IA

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![AI](https://img.shields.io/badge/AI-Google%20Gemini-orange.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Sistema inteligente para análisis de enfermedad renal crónica con inteligencia artificial**

[🌟 Demo en Vivo](https://erc-insight.onrender.com) | [📖 Documentación](docs/) | [🚀 Instalación](#instalación)

</div>

## 📋 Descripción

ERC Insight es una aplicación web avanzada que utiliza inteligencia artificial para asistir en el análisis y seguimiento de pacientes con enfermedad renal crónica (ERC). Combina análisis de laboratorios, evaluación de riesgo cardiovascular y generación automática de informes médicos.

### ✨ Características Principales

- 🤖 **IA Integrada**: Análisis inteligente con Google Gemini
- 📊 **Análisis de Laboratorios**: Procesamiento automático de resultados
- 🫀 **Evaluación Cardiovascular**: Clasificación de riesgo completa
- 📋 **Informes Automáticos**: Generación de reportes médicos
- 📱 **Interfaz Moderna**: Diseño responsive y accesible
- 🔒 **Seguro**: Configuración robusta de seguridad
- ☁️ **Cloud Ready**: Optimizado para Render.com

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.9+
- Git
- Cuenta en Google AI Studio (para API key)

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/erc-insight.git
cd erc-insight
```

### 2. Configurar Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
```bash
cp .env.example .env
```

Edita `.env` con tus valores:
```env
SECRET_KEY=tu-clave-secreta-aqui
GEMINI_API_KEY=tu-api-key-de-gemini
DATABASE_URL=sqlite:///erc_insight.db
```

### 5. Ejecutar la Aplicación
```bash
python run.py
```

Visita: http://localhost:5000

## 🏗️ Arquitectura

```
ERC Insight/
├── app/
│   ├── __init__.py          # Factory de la aplicación
│   ├── api/                 # Endpoints de API
│   │   ├── routes.py        # Rutas principales
│   │   ├── gemini_client.py # Cliente de Google AI
│   │   └── report_generator.py # Generador de informes
│   ├── logic/               # Lógica de negocio
│   │   ├── patient_eval.py  # Evaluación de pacientes
│   │   └── advanced_patient_eval.py # Análisis avanzado
│   ├── models/              # Modelos de datos
│   ├── parsers/             # Procesadores de archivos
│   ├── static/              # Assets frontend
│   │   ├── css/            # Estilos
│   │   └── js/             # JavaScript
│   └── templates/           # Templates HTML
├── config.py               # Configuración centralizada
├── wsgi.py                # Punto de entrada WSGI
├── requirements.txt       # Dependencias Python
└── render.yaml           # Configuración Render.com
```

## 📚 Uso

### Análisis de Paciente

1. **Ingreso de Datos**: Completa el formulario con datos del paciente
2. **Carga de Laboratorios**: Sube archivos PDF o introduce valores manualmente
3. **Análisis IA**: El sistema procesa y analiza automáticamente
4. **Reporte**: Obtén un informe médico completo

### API Endpoints

```python
# Análisis de riesgo
POST /api/risk/classify
{
    "edad": 65,
    "sexo": "m",
    "creatinina": 1.5,
    "peso": 70
}

# Generación de informe
POST /api/generate_report
{
    "patientData": {...},
    "labResults": {...}
}
```

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Requerido |
|----------|-------------|-----------|
| `SECRET_KEY` | Clave secreta de Flask | ✅ |
| `GEMINI_API_KEY` | API Key de Google Gemini | ✅ |
| `DATABASE_URL` | URL de base de datos | ✅ |
| `FLASK_ENV` | Entorno (development/production) | ⚠️ |
| `SENTRY_DSN` | DSN de Sentry para monitoreo | ❌ |

### Configuración de Base de Datos

#### SQLite (Desarrollo)
```env
DATABASE_URL=sqlite:///erc_insight.db
```

#### PostgreSQL (Producción)
```env
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

## 🌐 Despliegue en Render.com

### Automático con render.yaml

1. **Fork el repositorio**
2. **Conecta GitHub a Render**
3. **Selecciona "Blueprint"**
4. **Configura variables de entorno**:
   - `GEMINI_API_KEY`: Tu API key de Google AI

### Manual

1. Crea un Web Service en Render
2. Configuración:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:application`
   - **Python Version**: `3.9.13`

## 🧪 Testing

### Ejecutar Tests
```bash
# Tests completos
pytest

# Tests con cobertura
pytest --cov=app

# Tests específicos
pytest tests/test_patient_eval.py
```

### Verificar Despliegue
```bash
python check_deployment.py
```

## 🤝 Contribución

1. **Fork** el repositorio
2. **Crea** una branch (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. **Push** a la branch (`git push origin feature/nueva-funcionalidad`)
5. **Crea** un Pull Request

### Estándares de Código

- **PEP 8** para Python
- **JSDoc** para JavaScript
- **Tests** para nuevas funcionalidades
- **Documentación** actualizada

## 📊 Performance

- ⚡ **Tiempo de respuesta**: < 2s para análisis básico
- 🔄 **Concurrencia**: Soporta 100+ usuarios simultáneos
- 💾 **Memoria**: Uso optimizado < 512MB
- 🌐 **CDN Ready**: Assets optimizados para CDN

## 🔐 Seguridad

- ✅ **CSRF Protection**: Habilitado por defecto
- ✅ **SQL Injection**: Protección con SQLAlchemy
- ✅ **XSS Protection**: Headers de seguridad
- ✅ **HTTPS**: Forzado en producción
- ✅ **Input Validation**: Validación robusta

## 🐛 Solución de Problemas

### Error: ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### Error: GEMINI_API_KEY no configurado
1. Obtén tu API key en [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Configúrala en `.env` o variables de entorno

### Error de Base de Datos
```bash
# Desarrollo
export DATABASE_URL=sqlite:///erc_insight.db

# Producción
# Configurar en variables de entorno de Render
```

## 📈 Roadmap

- [ ] 🔐 Sistema de autenticación completo
- [ ] 📊 Dashboard de analytics
- [ ] 🔄 Integración con sistemas hospitalarios
- [ ] 📱 Progressive Web App (PWA)
- [ ] 🌍 Internacionalización (i18n)
- [ ] 🤖 Modelos de ML personalizados

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 👥 Equipo

- **Desarrollador Principal**: [Tu Nombre](https://github.com/tu-usuario)
- **Colaboradores**: Ver [Contributors](https://github.com/tu-usuario/erc-insight/contributors)

## 🙏 Agradecimientos

- [Google AI](https://ai.google.dev/) por la API de Gemini
- [Flask Community](https://flask.palletsprojects.com/) por el framework
- [Render](https://render.com/) por el hosting gratuito

---

<div align="center">
  <sub>Construido con ❤️ para mejorar la atención médica</sub>
</div>
