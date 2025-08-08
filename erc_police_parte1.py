#!/usr/bin/env python3
"""
🚨 ERC POLICE WATCHDOG - PARTE 1: IMPORTS, CONFIGURACIÓN Y ESTRUCTURA PRINCIPAL
================================================================================

Sistema "policía" para monitoreo en tiempo real de la aplicación médica ERC Insight.
Vigila integridad, enforce reglas médicas estrictas, maneja errores y genera alertas.

AUTOR: ERC Insight Development Team
VERSIÓN: 1.0.0 
"""

import sqlite3
import hashlib
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any

"""
FECHA: Agosto 2025
LICENCIA: Uso exclusivo para ERC Insight Flask Application
"""

# ═══════════════════════════════════════════════════════════════════════════════
# IMPORTS Y LIBRERÍAS CORE
# ═══════════════════════════════════════════════════════════════════════════════

# Sistema base
import os
import sys
import json
import time
import logging
import threading
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from functools import wraps
import traceback
import hashlib
import socket
import uuid

# Programación de tareas
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    print("⚠️ APScheduler no disponible - usando threading básico")

# Monitoreo de sistema
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil no disponible - métricas básicas de sistema")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ requests no disponible - health checks deshabilitados")

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("⚠️ watchdog no disponible - monitoreo de archivos básico")

# Alertas y notificaciones
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import urllib.parse
import urllib.request

# Testing y validación
try:
    import pytest
    import unittest
    from unittest.mock import patch, MagicMock
    TESTING_AVAILABLE = True
except ImportError:
    TESTING_AVAILABLE = False
    print("⚠️ pytest/unittest no disponible - tests deshabilitados")

import tempfile
import shutil

# Logging estructurado
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    print("⚠️ structlog no disponible - logging básico")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN GLOBAL DEL WATCHDOG
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ERCPoliceConfig:
    """Configuración centralizada del sistema policía"""
    
    # Paths y directorios
    app_root: str = r"c:\Users\brandon\Desktop\ERC"
    log_dir: str = r"c:\Users\brandon\Desktop\ERC\logs"
    config_file: str = r"c:\Users\brandon\Desktop\ERC\erc_police_config.json"
    
    # Intervalos de monitoreo (en segundos)
    health_check_interval: int = 30
    medical_rules_check_interval: int = 60
    file_integrity_check_interval: int = 120
    performance_check_interval: int = 45
    
    # Configuración de alertas
    enable_email_alerts: bool = True
    enable_desktop_alerts: bool = True
    enable_slack_alerts: bool = False
    enable_discord_alerts: bool = False
    
    # Límites de rendimiento
    max_cpu_usage: float = 85.0
    max_memory_usage: float = 90.0
    max_response_time: float = 5.0
    min_disk_space_gb: float = 2.0
    
    # URLs para health checks
    app_url: str = "http://localhost:5000"
    api_endpoints: List[str] = field(default_factory=lambda: [
        "/api/health",
        "/api/generate_report", 
        "/api/parse_document",
        "/patient/api/tfg"
    ])
    
    # Email configuration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_user: str = "erc.insight.alerts@gmail.com"
    email_password: str = "your_app_password_here"
    alert_recipients: List[str] = field(default_factory=lambda: [
        "admin@ercinsight.com",
        "dev@ercinsight.com"
    ])
    
    # Webhooks
    slack_webhook_url: str = ""
    discord_webhook_url: str = ""
    
    # Archivos críticos a monitorear
    critical_files: List[str] = field(default_factory=lambda: [
        "app/logic/patient_eval.py",
        "app/logic/advanced_patient_eval.py", 
        "app/api/routes.py",
        "app/models/patient.py",
        "run.py",
        "wsgi.py",
        "config.py"
    ])
    
    # Reglas médicas críticas 
    medical_rules: Dict[str, Any] = field(default_factory=lambda: {
        "tfg_ranges": {
            "g1": {"min": 90, "max": float('inf')},
            "g2": {"min": 60, "max": 89},
            "g3a": {"min": 45, "max": 59},
            "g3b": {"min": 30, "max": 44},
            "g4": {"min": 15, "max": 29},
            "g5": {"min": 0, "max": 14}
        },
        "cockcroft_gault_formula": "(140-edad)*peso*factor_sexo/(72*creatinina)",
        "mandatory_fields": ["edad", "peso", "creatinina", "sexo"],
        "cardiovascular_risk_levels": ["bajo", "moderado", "alto", "muy_alto"],
        "therapeutic_goals_weights": {
            "glicemia": {"erc123_dm2": 4, "erc4_dm2": 5, "erc123_nodm2": 5, "erc4_nodm2": 10},
            "presion_arterial": {"erc123_dm2": 20, "erc4_dm2": 30, "erc123_nodm2": 25, "erc4_nodm2": 40},
            "rac": {"erc123_dm2": 20, "erc4_dm2": 15, "erc123_nodm2": 25, "erc4_nodm2": 10}
        },
        "tfg_validation": {
            "min_valid": 0,
            "max_valid": 200,
            "critical_threshold": 15  # G5 threshold
        }
    })

# Configuración global
POLICE_CONFIG = ERCPoliceConfig()

# ═══════════════════════════════════════════════════════════════════════════════
# SISTEMA DE LOGGING ESTRUCTURADO  
# ═══════════════════════════════════════════════════════════════════════════════

def setup_police_logging():
    """Configura el sistema de logging avanzado para el watchdog"""
    
    # Crear directorio de logs si no existe
    Path(POLICE_CONFIG.log_dir).mkdir(parents=True, exist_ok=True)
    
    # Configurar structlog si está disponible
    if STRUCTLOG_AVAILABLE:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    
    # Logger principal
    logger = logging.getLogger("erc_police")
    logger.setLevel(logging.DEBUG)
    
    # Limpiar handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Handler para archivo principal
    main_handler = logging.FileHandler(
        Path(POLICE_CONFIG.log_dir) / "erc_police.log",
        encoding='utf-8'
    )
    main_handler.setLevel(logging.DEBUG)
    
    # Handler para errores críticos
    error_handler = logging.FileHandler(
        Path(POLICE_CONFIG.log_dir) / "erc_police_errors.log", 
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Formatter estructurado
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    main_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(main_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger

# Logger global
POLICE_LOGGER = setup_police_logging()

# ═══════════════════════════════════════════════════════════════════════════════
# DECORADORES DE MONITOREO Y VALIDACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

def police_monitor(operation_name: str):
    """Decorador para monitorear operaciones críticas del watchdog"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            operation_id = str(uuid.uuid4())[:8]
            
            POLICE_LOGGER.info(
                f"🚨 POLICE OPERATION START: {operation_name} (ID: {operation_id})"
            )
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                POLICE_LOGGER.info(
                    f"✅ POLICE OPERATION SUCCESS: {operation_name} "
                    f"(ID: {operation_id}, Time: {round(execution_time, 3)}s)"
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                POLICE_LOGGER.error(
                    f"❌ POLICE OPERATION FAILED: {operation_name} "
                    f"(ID: {operation_id}, Error: {str(e)}, Time: {round(execution_time, 3)}s)"
                )
                
                # Disparar alerta crítica si el watchdog está disponible
                if hasattr(ERCPoliceWatchdog, 'instance') and ERCPoliceWatchdog.instance:
                    ERCPoliceWatchdog.instance.send_critical_alert(
                        f"POLICE OPERATION FAILED: {operation_name}",
                        f"Error: {str(e)}\nOperation ID: {operation_id}\nTime: {execution_time:.3f}s"
                    )
                
                raise
                
        return wrapper
    return decorator

def medical_validation(rule_name: str):
    """Decorador para validar reglas médicas críticas"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            validation_id = str(uuid.uuid4())[:8]
            
            POLICE_LOGGER.info(
                f"🏥 MEDICAL VALIDATION START: {rule_name} (ID: {validation_id})"
            )
            
            try:
                result = func(*args, **kwargs)
                
                # Validar resultado si es un cálculo médico
                if rule_name.startswith("tfg_") and isinstance(result, (int, float)):
                    tfg_config = POLICE_CONFIG.medical_rules["tfg_validation"]
                    if result < tfg_config["min_valid"] or result > tfg_config["max_valid"]:
                        raise ValueError(f"TFG calculado fuera de rango válido: {result}")
                
                POLICE_LOGGER.info(
                    f"✅ MEDICAL VALIDATION PASSED: {rule_name} "
                    f"(ID: {validation_id}, Result: {result})"
                )
                
                return result
                
            except Exception as e:
                POLICE_LOGGER.error(
                    f"🚨 MEDICAL VALIDATION FAILED: {rule_name} "
                    f"(ID: {validation_id}, Error: {str(e)})"
                )
                
                # Alerta crítica médica
                if hasattr(ERCPoliceWatchdog, 'instance') and ERCPoliceWatchdog.instance:
                    ERCPoliceWatchdog.instance.send_critical_alert(
                        f"MEDICAL RULE VIOLATION: {rule_name}",
                        f"Validation failed: {str(e)}\nValidation ID: {validation_id}"
                    )
                
                raise
                
        return wrapper
    return decorator

# ═══════════════════════════════════════════════════════════════════════════════
# CLASE PRINCIPAL DEL SISTEMA WATCHDOG
# ═══════════════════════════════════════════════════════════════════════════════

class ERCPoliceWatchdog:
    """
    Sistema principal de monitoreo autónomo para ERC Insight.
    
    Responsabilidades:
    - Monitoreo continuo de salud de la aplicación
    - Enforcement de reglas médicas críticas  
    - Detección proactiva de errores y anomalías
    - Sistema de alertas multi-canal
    - Validación de integridad de archivos
    - Monitoreo de rendimiento
    """
    
    instance = None  # Singleton para acceso global
    
    def __init__(self, config: ERCPoliceConfig = None):
        """Inicializa el sistema watchdog"""
        ERCPoliceWatchdog.instance = self
        self.config = config or POLICE_CONFIG
        self.is_running = False
        self.scheduler = None
        self.file_observer = None
        self.system_stats = {}
        self.alert_counts = {"info": 0, "warning": 0, "critical": 0}
        self.last_health_check = None
        self.startup_time = datetime.now()
        
        # Thread locks para operaciones concurrentes
        self.stats_lock = threading.Lock()
        self.alert_lock = threading.Lock()
        
        # Base de datos SQLite para logging
        self.db_path = Path(self.config.log_dir) / "erc_police.db"
        self._init_database()
        
        POLICE_LOGGER.info(
            f"🚨 ERC Police Watchdog initialized at {self.startup_time.isoformat()}"
        )

    def _init_database(self):
        """Inicializa la base de datos SQLite para logging"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabla de eventos del sistema
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS police_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        operation TEXT,
                        message TEXT,
                        details TEXT,
                        resolved BOOLEAN DEFAULT FALSE
                    )
                """)
                
                # Tabla de métricas de sistema
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        cpu_usage REAL,
                        memory_usage REAL,
                        disk_usage REAL,
                        response_time REAL,
                        active_connections INTEGER
                    )
                """)
                
                # Tabla de validaciones médicas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS medical_validations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        rule_name TEXT NOT NULL,
                        input_data TEXT,
                        result TEXT,
                        status TEXT NOT NULL,
                        error_message TEXT
                    )
                """)
                
                conn.commit()
                POLICE_LOGGER.info("✅ Police database initialized successfully")
                
        except Exception as e:
            POLICE_LOGGER.error(f"❌ Failed to initialize database: {str(e)}")

    def send_critical_alert(self, title: str, message: str):
        """Envía una alerta crítica (método stub para implementar en PARTE 2)"""
        with self.alert_lock:
            self.alert_counts["critical"] += 1
            POLICE_LOGGER.error(f"🚨 CRITICAL ALERT: {title} - {message}")

    @police_monitor("startup_validation")
    def validate_system_integrity(self):
        """Valida la integridad del sistema al inicio"""
        POLICE_LOGGER.info("🔍 Starting system integrity validation...")
        
        # Validar estructura de directorios
        required_dirs = [
            Path(self.config.app_root),
            Path(self.config.app_root) / "app",
            Path(self.config.app_root) / "app" / "logic",
            Path(self.config.app_root) / "app" / "api",
            Path(self.config.log_dir)
        ]
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                raise FileNotFoundError(f"Required directory missing: {dir_path}")
        
        # Validar archivos críticos
        missing_files = []
        for file_path in self.config.critical_files:
            full_path = Path(self.config.app_root) / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            raise FileNotFoundError(f"Critical files missing: {missing_files}")
        
        POLICE_LOGGER.info("✅ System integrity validation completed")
        return True

# ═══════════════════════════════════════════════════════════════════════════════
# UTILIDADES DE CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

def load_config_from_file(config_path: str) -> ERCPoliceConfig:
    """Carga configuración desde archivo JSON"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        
        # Fusionar con configuración por defecto
        default_config = ERCPoliceConfig()
        for key, value in config_dict.items():
            if hasattr(default_config, key):
                setattr(default_config, key, value)
        
        return default_config
        
    except FileNotFoundError:
        POLICE_LOGGER.warning(f"Config file not found: {config_path}, using defaults")
        return ERCPoliceConfig()
    except Exception as e:
        POLICE_LOGGER.error(f"Error loading config: {str(e)}, using defaults")
        return ERCPoliceConfig()

def save_config_to_file(config: ERCPoliceConfig, config_path: str):
    """Guarda configuración a archivo JSON"""
    try:
        config_dict = {}
        for key, value in config.__dict__.items():
            if not key.startswith('_'):
                config_dict[key] = value
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        POLICE_LOGGER.info(f"Configuration saved to {config_path}")
        
    except Exception as e:
        POLICE_LOGGER.error(f"Error saving config: {str(e)}")

# ═══════════════════════════════════════════════════════════════════════════════
# INICIALIZACIÓN Y PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════════════════

def initialize_police_watchdog(config_file: str = None) -> ERCPoliceWatchdog:
    """Inicializa el sistema watchdog"""
    
    # Cargar configuración
    if config_file and Path(config_file).exists():
        config = load_config_from_file(config_file)
    else:
        config = POLICE_CONFIG
    
    # Crear instancia del watchdog
    watchdog = ERCPoliceWatchdog(config)
    
    # Validar sistema
    watchdog.validate_system_integrity()
    
    return watchdog

if __name__ == "__main__":
    print("🚨 ERC Police Watchdog - Parte 1 (Configuración y Estructura)")
    print("=" * 65)
    
    try:
        # Inicializar watchdog
        watchdog = initialize_police_watchdog()
        
        print("✅ Sistema watchdog inicializado correctamente")
        print(f"📁 Directorio base: {watchdog.config.app_root}")
        print(f"📋 Archivos críticos: {len(watchdog.config.critical_files)} monitoreados")
        print(f"🏥 Reglas médicas: {len(watchdog.config.medical_rules)} configuradas")
        
        # Test de decoradores
        @medical_validation("tfg_calculation_test")
        def test_tfg_calculation(edad: int, peso: float, creatinina: float, sexo: str) -> float:
            """Función de test para cálculo de TFG"""
            if creatinina <= 0:
                creatinina = 1.0
            if edad <= 0 or peso <= 0:
                return 0.0
            
            factor_sexo = 0.85 if sexo.lower() == "f" else 1.0
            tfg = ((140 - edad) * peso * factor_sexo) / (72 * creatinina)
            return round(tfg, 2)
        
        # Test del sistema de validación
        print("\n🧪 Ejecutando test de validación médica...")
        test_result = test_tfg_calculation(65, 70, 1.2, "m")
        print(f"✅ TFG calculado: {test_result} ml/min/1.73m²")
        
        print("\n🎯 PARTE 1 COMPLETADA - Lista para PARTE 2")
        
    except Exception as e:
        print(f"❌ Error durante inicialización: {str(e)}")
        traceback.print_exc()

"""
📋 PARTE 1 COMPLETADA - INSTRUCCIONES PARA ENSAMBLAJE:

✅ INCLUYE:
- Imports completos con fallbacks para dependencias opcionales
- Configuración centralizada con dataclass ERCPoliceConfig  
- Sistema de logging estructurado con structlog opcional
- Decoradores de monitoreo (@police_monitor, @medical_validation)
- Clase principal ERCPoliceWatchdog con inicialización
- Base de datos SQLite para logging de eventos
- Validación de integridad del sistema
- Configuración de paths, intervalos, alertas y reglas médicas

🔗 CONECTA CON PARTE 2:
- La clase ERCPoliceWatchdog necesita métodos de chequeo médico
- Los decoradores están listos para usar en funciones de validación
- El sistema de logging está configurado para recibir eventos
- La configuración médica está lista para enforcement
- Base de datos preparada para almacenar eventos y métricas

📁 ARCHIVOS GENERADOS:
- erc_police_parte1.py (ESTRUCTURA PRINCIPAL)

🏥 REGLAS MÉDICAS INCLUIDAS:
- Rangos TFG por estadios G1-G5 según KDIGO
- Fórmula Cockcroft-Gault para validación
- Campos obligatorios para cálculos
- Niveles de riesgo cardiovascular  
- Pesos de metas terapéuticas por perfil de paciente
- Umbrales de validación para TFG

⚡ LISTO PARA PARTE 2: Funciones de chequeo y enforcement de reglas médicas
"""
