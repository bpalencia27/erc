# ERC POLICE WATCHDOG - INSTRUCCIONES COMPLETAS DE INSTALACIÓN
# ============================================================

## 🚀 INSTALACIÓN RÁPIDA

### 1. Instalar dependencias principales:
```bash
pip install flask flask-cors werkzeug python-dotenv
pip install requests psutil apscheduler structlog
pip install pytest watchdog google-generativeai
pip install pydantic tenacity
```

### 2. Ejecutar sistema completo:
```bash
# Ejecutar cada parte individualmente
python erc_police_parte1.py
python erc_police_parte2.py  
python erc_police_parte3.py

# O ejecutar sistema integrado
python -c "from erc_police_parte3 import run_complete_police_system; run_complete_police_system()"
```

## ⚙️ CONFIGURACIÓN AVANZADA

### Crear archivo de configuración personalizada:
```json
{
  "app_root": "c:/Users/brandon/Desktop/ERC",
  "health_check_interval": 30,
  "max_cpu_usage": 85.0,
  "enable_email_alerts": true,
  "enable_desktop_alerts": true,
  "app_url": "http://localhost:5000",
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "erc.insight.alerts@gmail.com", 
    "password": "your_app_password_here",
    "recipients": ["admin@ercinsight.com"]
  }
}
```

## 🧪 EJECUTAR TESTS

### Tests automáticos:
```python
from erc_police_parte3 import ERCPoliceTestSuite
suite = ERCPoliceTestSuite()
results = suite.run_all_tests()
print(results['summary'])
```

### Simulaciones médicas:
```python
from erc_police_parte3 import ERCScenarioSimulator
simulator = ERCScenarioSimulator()
results = simulator.run_all_scenarios()
```

## 🏃‍♂️ EJECUCIÓN EN PRODUCCIÓN

### Como servicio de Windows:
1. Instalar NSSM: https://nssm.cc/download
2. Crear servicio:
```cmd
nssm install ERCPolice
nssm set ERCPolice Application python.exe
nssm set ERCPolice Parameters "c:/path/to/erc_police_parte3.py"
nssm set ERCPolice AppDirectory "c:/Users/brandon/Desktop/ERC"
nssm start ERCPolice
```

### Como tarea programada Windows:
1. Abrir Task Scheduler
2. Crear tarea básica
3. Configurar para ejecutar cada 30 minutos
4. Comando: `python c:/Users/brandon/Desktop/ERC/erc_police_parte3.py`

## 🔧 RESOLUCIÓN DE PROBLEMAS

### Error: Dependencias faltantes
```bash
# Instalar todas las dependencias opcionales
pip install tkinter psutil apscheduler
pip install structlog pytest watchdog
```

### Error: Permisos de archivo
```bash
# En Windows, ejecutar como administrador
# Verificar permisos de escritura en directorio logs/
```

### Error: Puerto ocupado
- Cambiar puerto en configuración app_url
- Verificar que Flask no esté corriendo en otro proceso

## 📊 MONITOREO Y LOGS

### Archivos de log:
- `logs/erc_police.log` - Log principal
- `logs/erc_police_errors.log` - Solo errores
- `logs/erc_police_alerts.log` - Historial de alertas
- `logs/erc_police.db` - Base de datos SQLite

### Ver estadísticas:
```python
from erc_police_parte3 import ERCAlertSystem
alerts = ERCAlertSystem()
stats = alerts.get_alert_statistics()
print(stats)
```

## 🎯 VERIFICACIÓN DE FUNCIONAMIENTO

### 1. Test básico del sistema:
```bash
python erc_police_parte1.py
# Debe mostrar: "✅ Sistema watchdog inicializado correctamente"
```

### 2. Test de validaciones médicas:
```bash  
python erc_police_parte2.py
# Debe mostrar cálculos TFG y validaciones exitosas
```

### 3. Test completo con alertas:
```bash
python erc_police_parte3.py
# Debe ejecutar todos los tests y simulaciones
```

## 📞 SOPORTE Y DEBUG

### Habilitar debug logging:
```python
import logging
logging.getLogger("erc_police").setLevel(logging.DEBUG)
```

### Verificar configuración:
```python
from erc_police_parte1 import POLICE_CONFIG
print(POLICE_CONFIG.__dict__)
```

### Test de conectividad Flask:
```bash
curl http://localhost:5000/api/health
```

¡Sistema ERC Police Watchdog listo para proteger tu aplicación! 🚨
