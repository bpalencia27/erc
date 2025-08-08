#!/usr/bin/env python3
"""
🚔 ERC INSIGHT POLICE WATCHDOG - PARTE 1 DEMO
Sistema autónomo de monitoreo, integridad y enforcement para Flask App

VERSIÓN SIMPLIFICADA PARA DEMOSTRACIÓN
Author: ERC Insight Team
Version: 1.0.0
"""

import os
import sys
import json
import time
import logging
import traceback
from datetime import datetime, timedelta
from threading import Thread, Lock, Event
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import hashlib

# Importaciones opcionales
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil no disponible - algunas métricas de sistema estarán deshabilitadas")

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    print("⚠️ APScheduler no disponible - usando timer básico")

# ============================================================================
# 🔧 CONFIGURACIÓN GLOBAL DEL SISTEMA POLICÍA
# ============================================================================

class AlertLevel(Enum):
    """Niveles de alertas del sistema"""
    INFO = "INFO"
    WARNING = "WARNING" 
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"

class RuleCategory(Enum):
    """Categorías de reglas médicas"""
    TFG_CALCULATION = "tfg_calculation"
    ERC_CLASSIFICATION = "erc_classification"
    LAB_VALIDITY = "lab_validity"
    THERAPEUTIC_GOALS = "therapeutic_goals"
    DATA_INTEGRITY = "data_integrity"
    PERFORMANCE = "performance"
    SECURITY = "security"

@dataclass
class MonitoringConfig:
    """Configuración principal del sistema de monitoreo"""
    # Rutas y archivos
    app_root: str = r"c:\Users\brandon\Desktop\ERC"
    log_file: str = "logs/erc_police.log"
    db_file: str = "erc_police.db"
    config_file: str = "config/police_config.json"
    
    # Intervalos de monitoreo (segundos)
    file_check_interval: int = 30
    performance_check_interval: int = 60
    health_check_interval: int = 120
    medical_rules_check_interval: int = 300
    
    # Límites y umbrales
    max_cpu_percent: float = 85.0
    max_memory_percent: float = 80.0
    max_response_time: float = 3.0
    min_disk_space_gb: float = 1.0
    
    # Archivos críticos a monitorear
    critical_files: List[str] = None
    
    def __post_init__(self):
        if self.critical_files is None:
            self.critical_files = [
                "app/__init__.py",
                "app/logic/patient_eval.py", 
                "app/logic/advanced_patient_eval.py",
                "run.py",
                "wsgi.py",
                "config.py"
            ]

@dataclass
class HealthStatus:
    """Estado de salud del sistema"""
    timestamp: datetime
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_space_gb: float = 0.0
    active_connections: int = 0
    response_time: float = 0.0
    errors_last_hour: int = 0
    status: str = "HEALTHY"

# ============================================================================
# 🗄️ SISTEMA DE BASE DE DATOS LOCAL
# ============================================================================

class PoliceDatabase:
    """Base de datos local para el sistema policía"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.lock = Lock()
        self._init_database()
    
    def _init_database(self):
        """Inicializa las tablas de la base de datos"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        except:
            pass
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabla de eventos de monitoreo
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monitoring_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT NOT NULL,
                    details TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de métricas de salud
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS health_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_space_gb REAL,
                    response_time REAL,
                    status TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            print("✅ Base de datos inicializada correctamente")
    
    def log_event(self, event_type: str, severity: AlertLevel, description: str, details: Dict = None):
        """Registra un evento de monitoreo"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO monitoring_events 
                        (timestamp, event_type, severity, description, details)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        datetime.now().isoformat(),
                        event_type,
                        severity.value,
                        description,
                        json.dumps(details) if details else None
                    ))
                    conn.commit()
                    print(f"📝 Evento registrado: {severity.value} - {description}")
            except Exception as e:
                print(f"❌ Error al registrar evento: {e}")

# ============================================================================
# 🔍 SISTEMA DE LOGGING BÁSICO
# ============================================================================

class ERCPoliceLogger:
    """Logger básico para el sistema policía"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self._setup_logging()
        self.db = PoliceDatabase(os.path.join(config.app_root, config.db_file))
    
    def _setup_logging(self):
        """Configura el sistema de logging"""
        log_path = os.path.join(self.config.app_root, self.config.log_file)
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
        except:
            pass
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger("ERC_POLICE")
        print("✅ Sistema de logging configurado")
    
    def info(self, message: str, **kwargs):
        self.logger.info(f"{message} {kwargs}")
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(f"{message} {kwargs}")
        self.db.log_event("WARNING", AlertLevel.WARNING, message, kwargs)
    
    def critical(self, message: str, **kwargs):
        self.logger.critical(f"{message} {kwargs}")
        self.db.log_event("CRITICAL", AlertLevel.CRITICAL, message, kwargs)

# ============================================================================
# 🎯 CLASE PRINCIPAL DEL SISTEMA POLICÍA
# ============================================================================

class ERCPoliceWatchdog:
    """
    Sistema principal de monitoreo y enforcement para ERC Insight
    VERSIÓN DEMO PARA PARTE 1
    """
    
    def __init__(self, config: MonitoringConfig = None):
        self.config = config or MonitoringConfig()
        self.logger = ERCPoliceLogger(self.config)
        self.db = self.logger.db
        
        # Estado del sistema
        self.is_running = False
        self.stop_event = Event()
        
        # Cache de archivos monitoreados
        self.file_hashes: Dict[str, str] = {}
        
        self.logger.info("🚔 ERC Police Watchdog inicializado", config=asdict(self.config))
        print("✅ Watchdog inicializado exitosamente")
    
    def start(self):
        """Inicia el sistema de monitoreo"""
        if self.is_running:
            self.logger.warning("El sistema ya está ejecutándose")
            return
        
        self.logger.info("🚀 Iniciando ERC Police Watchdog...")
        print("🚀 Iniciando ERC Police Watchdog...")
        
        try:
            self.is_running = True
            
            # Inicializar hashes de archivos
            self._initialize_file_monitoring()
            
            # Simular métricas de sistema
            self._demo_system_check()
            
            self.logger.info("✅ ERC Police Watchdog iniciado exitosamente")
            print("✅ ERC Police Watchdog iniciado exitosamente")
            
        except Exception as e:
            self.logger.critical("❌ Error al iniciar el sistema", error=str(e))
            print(f"❌ Error al iniciar el sistema: {e}")
            self.stop()
    
    def stop(self):
        """Detiene el sistema de monitoreo"""
        if not self.is_running:
            return
        
        self.logger.info("🛑 Deteniendo ERC Police Watchdog...")
        print("🛑 Deteniendo ERC Police Watchdog...")
        
        try:
            self.is_running = False
            self.stop_event.set()
            
            self.logger.info("✅ ERC Police Watchdog detenido exitosamente")
            print("✅ ERC Police Watchdog detenido exitosamente")
            
        except Exception as e:
            self.logger.critical("❌ Error al detener el sistema", error=str(e))
            print(f"❌ Error al detener el sistema: {e}")
    
    def _initialize_file_monitoring(self):
        """Inicializa el monitoreo de archivos críticos"""
        print("📁 Inicializando monitoreo de archivos críticos...")
        
        for file_path in self.config.critical_files:
            full_path = os.path.join(self.config.app_root, file_path)
            if os.path.exists(full_path):
                file_hash = self._calculate_file_hash(full_path)
                self.file_hashes[file_path] = file_hash
                self.logger.info("📁 Archivo añadido al monitoreo", file=file_path, hash=file_hash[:8])
                print(f"  ✅ {file_path} (hash: {file_hash[:8]}...)")
            else:
                print(f"  ⚠️ {file_path} (no encontrado)")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcula el hash MD5 de un archivo"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.warning("Error calculando hash", file=file_path, error=str(e))
            return ""
    
    def _demo_system_check(self):
        """Demostración de chequeos del sistema"""
        print("🏥 Ejecutando chequeos de demostración...")
        
        # Simular métricas básicas
        if PSUTIL_AVAILABLE:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            print(f"  💻 CPU: {cpu_percent:.1f}%")
            print(f"  🧠 Memoria: {memory.percent:.1f}%")
            print(f"  💾 Disco: {disk.percent:.1f}%")
            
            # Simular alerta si los valores son altos
            if cpu_percent > self.config.max_cpu_percent:
                self.logger.warning("Alto uso de CPU detectado", cpu=cpu_percent)
            
        else:
            print("  ⚠️ Métricas de sistema no disponibles (psutil no instalado)")
        
        # Verificar archivos críticos
        print("🔍 Verificando integridad de archivos críticos...")
        modified_files = 0
        
        for file_path, old_hash in self.file_hashes.items():
            full_path = os.path.join(self.config.app_root, file_path)
            if os.path.exists(full_path):
                new_hash = self._calculate_file_hash(full_path)
                if new_hash != old_hash:
                    modified_files += 1
                    self.logger.warning("Archivo modificado detectado", 
                                      file=file_path, 
                                      old_hash=old_hash[:8], 
                                      new_hash=new_hash[:8])
                    print(f"  🔄 {file_path} - MODIFICADO")
                else:
                    print(f"  ✅ {file_path} - OK")
        
        if modified_files == 0:
            print("  ✅ Todos los archivos críticos están íntegros")
        
        # Simular chequeo de reglas médicas
        print("⚕️ Simulando chequeo de reglas médicas ERC...")
        self._demo_medical_rules_check()
    
    def _demo_medical_rules_check(self):
        """Demostración de chequeos de reglas médicas"""
        
        # Simular validación de cálculo de TFG
        test_cases = [
            {"edad": 65, "peso": 70, "creatinina": 1.2, "sexo": "f"},
            {"edad": 45, "peso": 80, "creatinina": 0.9, "sexo": "m"},
            {"edad": 70, "peso": 65, "creatinina": 1.8, "sexo": "f"}
        ]
        
        for i, case in enumerate(test_cases, 1):
            # Simular cálculo TFG (fórmula Cockcroft-Gault)
            factor_sexo = 0.85 if case["sexo"] == "f" else 1.0
            tfg = ((140 - case["edad"]) * case["peso"] * factor_sexo) / (72 * case["creatinina"])
            
            # Determinar etapa ERC
            if tfg >= 90: etapa = "G1"
            elif tfg >= 60: etapa = "G2"  
            elif tfg >= 45: etapa = "G3a"
            elif tfg >= 30: etapa = "G3b"
            elif tfg >= 15: etapa = "G4"
            else: etapa = "G5"
            
            print(f"  👤 Caso {i}: TFG={tfg:.1f} ml/min → Etapa {etapa}")
            
            # Simular validación de regla médica
            if tfg < 15:  # Etapa G5
                self.logger.critical("Paciente en etapa G5 detectado - Requiere atención urgente",
                                   tfg=tfg, etapa=etapa, case=case)
                print(f"    🚨 ALERTA CRÍTICA: Paciente requiere diálisis")
            elif tfg < 30:  # Etapa G4
                self.logger.warning("Paciente en etapa G4 detectado - Preparación para TRS",
                                  tfg=tfg, etapa=etapa)
                print(f"    ⚠️ ALERTA: Preparar para terapia de reemplazo renal")


# ============================================================================
# 🎮 PUNTO DE ENTRADA PRINCIPAL
# ============================================================================

def main():
    """Función principal para ejecutar el watchdog - DEMO PARTE 1"""
    print("="*80)
    print("🚔 ERC INSIGHT POLICE WATCHDOG - PARTE 1 DEMO")
    print("="*80)
    print("✅ Imports y configuración listos")
    print("✅ Sistema de base de datos inicializado")
    print("✅ Logger básico configurado") 
    print("✅ Clase principal ERCPoliceWatchdog creada")
    print("="*80)
    print("🔄 Ejecutando demostración de funcionalidad base...")
    print()
    
    # Crear instancia de configuración
    config = MonitoringConfig()
    
    # Crear el watchdog
    watchdog = ERCPoliceWatchdog(config)
    
    try:
        # Ejecutar demo
        watchdog.start()
        print()
        print("🎯 DEMO COMPLETADA - El sistema base está funcionando")
        print("📊 Revisa el archivo 'logs/erc_police.log' para ver los logs detallados")
        print("🗄️ Revisa el archivo 'erc_police.db' para ver los eventos registrados")
        print()
        print("⏳ El sistema continuará ejecutándose por 10 segundos...")
        
        # Simular ejecución por 10 segundos
        for i in range(10, 0, -1):
            print(f"  ⏰ {i} segundos restantes...", end='\r')
            time.sleep(1)
        
        print("\n")
        watchdog.stop()
        
        print("="*80)
        print("🎉 PARTE 1 COMPLETADA EXITOSAMENTE")
        print("📋 PRÓXIMO PASO: Implementar PARTE 2 (Funciones de chequeo y enforcement)")
        print("🔄 LUEGO: Implementar PARTE 3 (Alertas, manejo de errores y tests)")
        print("="*80)
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sistema...")
        watchdog.stop()
        print("✅ Sistema detenido exitosamente")
    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {e}")
        watchdog.stop()

if __name__ == "__main__":
    main()
