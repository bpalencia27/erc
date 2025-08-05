# ERC Insight

Sistema de gestión y seguimiento de pacientes con Enfermedad Renal Crónica (ERC)

## Descripción

ERC Insight es una aplicación web diseñada para ayudar a los profesionales de la salud en el seguimiento y manejo de pacientes con enfermedad renal crónica. El sistema permite:

- Calcular automáticamente la Tasa de Filtración Glomerular (TFG) y estadificar la ERC
- Gestionar pacientes y sus resultados de laboratorio
- Generar informes clínicos inteligentes con la ayuda de IA
- Establecer alertas para exámenes de laboratorio vencidos
- Visualizar tendencias en los valores de laboratorio

## Tecnologías utilizadas

- Python 3.9+
- Flask (Framework web)
- SQLAlchemy (ORM)
- Google Gemini API (Generación de informes con IA)
- Bootstrap 5 (Interfaz de usuario)

## Estructura del proyecto

```
erc_insight/
├── app/                    # Aplicación principal
│   ├── __init__.py         # Inicialización de la aplicación
│   ├── api/                # Endpoints de API
│   ├── logic/              # Lógica de negocio
│   ├── models/             # Modelos de datos
│   ├── static/             # Archivos estáticos
│   └── templates/          # Plantillas HTML
├── config/                 # Configuración
│   └── lab_validity.json   # Configuración de validez de pruebas
├── logs/                   # Logs de la aplicación
├── tests/                  # Pruebas unitarias
├── .env.example            # Ejemplo de variables de entorno
├── requirements.txt        # Dependencias
└── wsgi.py                 # Punto de entrada para WSGI
```

## Instalación

1. Clonar el repositorio:
   ```
   git clone https://github.com/yourusername/erc_insight.git
   cd erc_insight
   ```

2. Crear un entorno virtual:
   ```
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno:
   ```
   cp .env.example .env
   # Editar .env con las configuraciones correctas
   ```

5. Ejecutar la aplicación:
   ```
   flask run
   ```

## Uso

Acceder a la aplicación en `http://localhost:5000`

## Cálculo de TFG

La aplicación utiliza la fórmula CKD-EPI para calcular la Tasa de Filtración Glomerular:

- Para mujeres:
  - Si creatinina ≤ 0.7: TFG = 144 × (Cr/0.7)^-0.329 × 0.993^edad
  - Si creatinina > 0.7: TFG = 144 × (Cr/0.7)^-1.209 × 0.993^edad

- Para hombres:
  - Si creatinina ≤ 0.9: TFG = 141 × (Cr/0.9)^-0.411 × 0.993^edad
  - Si creatinina > 0.9: TFG = 141 × (Cr/0.9)^-1.209 × 0.993^edad

## Licencia

Este proyecto está licenciado bajo la licencia MIT.
