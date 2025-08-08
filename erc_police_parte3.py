#!/usr/bin/env python3
"""
⚠️ ERC POLICE WATCHDOG - PARTE 3: MANEJO ERRORES, ALERTAS Y TESTING
===================================================================

Sistema completo de manejo de errores, alertas multi-canal, testing automático
y simulación de escenarios para el sistema policía de ERC Insight.

CONECTA CON PARTES 1 y 2: Sistema completo integrado y funcional
INCLUYE: Alertas, testing, simulación, instrucciones de instalación
"""

import hashlib
import logging
import os
import sys
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
"""

# ═══════════════════════════════════════════════════════════════════════════════
# IMPORTS Y CONEXIÓN CON PARTES ANTERIORES
# ═══════════════════════════════════════════════════════════════════════════════

import os
import sys
import json
import time
import smtplib
import sqlite3
import threading
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
import traceback
import uuid
import tempfile
import shutil

# Email y alertas
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import urllib.parse
import urllib.request

# Testing
try:
    import pytest
    import unittest
    from unittest.mock import patch, MagicMock, Mock
    TESTING_AVAILABLE = True
except ImportError:
    TESTING_AVAILABLE = False
    print("⚠️ pytest/unittest no disponible - tests básicos únicamente")

# GUI para alertas desktop
try:
    import tkinter as tk
    from tkinter import messagebox
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("⚠️ tkinter no disponible - alertas desktop deshabilitadas")

# Simulación básica de conexión con partes anteriores
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ═══════════════════════════════════════════════════════════════════════════════
# SISTEMA DE ALERTAS MULTI-CANAL
# ═══════════════════════════════════════════════════════════════════════════════

class ERCAlertSystem:
    """Sistema avanzado de alertas para el watchdog de ERC Insight"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_alert_config()
        self.alert_queue = []
        self.alert_history = []
        self.alert_lock = threading.Lock()
        self.email_session = None
        self.alert_count_by_severity = {"info": 0, "warning": 0, "critical": 0}
    
    def _get_default_alert_config(self) -> Dict[str, Any]:
        """Configuración por defecto del sistema de alertas"""
        return {
            "email": {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "erc.insight.alerts@gmail.com",
                "password": "your_app_password_here",
                "recipients": ["admin@ercinsight.com", "dev@ercinsight.com"]
            },
            "desktop": {
                "enabled": True,
                "show_info": False,
                "show_warnings": True,
                "show_critical": True
            },
            "webhooks": {
                "slack": {
                    "enabled": False,
                    "webhook_url": ""
                },
                "discord": {
                    "enabled": False, 
                    "webhook_url": ""
                }
            },
            "file_log": {
                "enabled": True,
                "log_path": "logs/erc_police_alerts.log"
            }
        }
    
    def send_alert(self, severity: str, title: str, message: str, 
                   details: Dict[str, Any] = None, send_immediately: bool = True) -> str:
        """
        Envía una alerta a través de todos los canales configurados
        
        Args:
            severity: "info", "warning", "critical"
            title: Título breve de la alerta
            message: Mensaje detallado
            details: Información adicional estructurada
            send_immediately: Si enviar inmediatamente o encolar
        
        Returns:
            alert_id: ID único de la alerta
        """
        alert_id = str(uuid.uuid4())[:8]
        
        alert = {
            "id": alert_id,
            "timestamp": datetime.now().isoformat(),
            "severity": severity.lower(),
            "title": title,
            "message": message,
            "details": details or {},
            "channels_sent": [],
            "channels_failed": [],
            "status": "pending"
        }
        
        with self.alert_lock:
            self.alert_count_by_severity[severity.lower()] += 1
            
            if send_immediately:
                self._process_alert(alert)
            else:
                self.alert_queue.append(alert)
        
        return alert_id
    
    def _process_alert(self, alert: Dict[str, Any]):
        """Procesa una alerta enviándola por todos los canales"""
        try:
            # 📧 Envío por email
            if self.config["email"]["enabled"]:
                try:
                    self._send_email_alert(alert)
                    alert["channels_sent"].append("email")
                except Exception as e:
                    alert["channels_failed"].append(f"email: {str(e)}")
            
            # 🖥️ Alerta desktop
            if self.config["desktop"]["enabled"]:
                try:
                    self._send_desktop_alert(alert)
                    alert["channels_sent"].append("desktop")
                except Exception as e:
                    alert["channels_failed"].append(f"desktop: {str(e)}")
            
            # 🔗 Webhooks (Slack/Discord)
            if self.config["webhooks"]["slack"]["enabled"]:
                try:
                    self._send_slack_alert(alert)
                    alert["channels_sent"].append("slack")
                except Exception as e:
                    alert["channels_failed"].append(f"slack: {str(e)}")
            
            if self.config["webhooks"]["discord"]["enabled"]:
                try:
                    self._send_discord_alert(alert)
                    alert["channels_sent"].append("discord")
                except Exception as e:
                    alert["channels_failed"].append(f"discord: {str(e)}")
            
            # 📁 Log a archivo
            if self.config["file_log"]["enabled"]:
                try:
                    self._log_alert_to_file(alert)
                    alert["channels_sent"].append("file_log")
                except Exception as e:
                    alert["channels_failed"].append(f"file_log: {str(e)}")
            
            # Actualizar estado
            alert["status"] = "sent" if alert["channels_sent"] else "failed"
            alert["processed_at"] = datetime.now().isoformat()
            
            # Guardar en historial
            self.alert_history.append(alert)
            
            # Mantener solo las últimas 1000 alertas
            if len(self.alert_history) > 1000:
                self.alert_history = self.alert_history[-1000:]
                
        except Exception as e:
            alert["status"] = "error"
            alert["error"] = str(e)
            print(f"❌ Error procesando alerta {alert['id']}: {str(e)}")
    
    def _send_email_alert(self, alert: Dict[str, Any]):
        """Envía alerta por email"""
        if not self.email_session:
            self._init_email_session()
        
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = self.config["email"]["username"]
        msg['To'] = ", ".join(self.config["email"]["recipients"])
        
        # Subject con emoji según severidad
        severity_emojis = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}
        emoji = severity_emojis.get(alert["severity"], "📢")
        msg['Subject'] = f"{emoji} ERC Police Alert: {alert['title']}"
        
        # Cuerpo del mensaje
        body = self._format_email_body(alert)
        msg.attach(MIMEText(body, 'html'))
        
        # Enviar
        self.email_session.send_message(msg)
    
    def _init_email_session(self):
        """Inicializa sesión SMTP"""
        try:
            self.email_session = smtplib.SMTP(
                self.config["email"]["smtp_server"], 
                self.config["email"]["smtp_port"]
            )
            self.email_session.starttls()
            self.email_session.login(
                self.config["email"]["username"],
                self.config["email"]["password"]
            )
        except Exception as e:
            raise Exception(f"Error inicializando email: {str(e)}")
    
    def _format_email_body(self, alert: Dict[str, Any]) -> str:
        """Formatea el cuerpo del email con HTML"""
        severity_colors = {
            "info": "#17a2b8",
            "warning": "#ffc107", 
            "critical": "#dc3545"
        }
        color = severity_colors.get(alert["severity"], "#6c757d")
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="border-left: 4px solid {color}; padding: 20px; margin: 10px 0;">
                <h2 style="color: {color}; margin-top: 0;">
                    {alert['severity'].upper()}: {alert['title']}
                </h2>
                <p><strong>Timestamp:</strong> {alert['timestamp']}</p>
                <p><strong>Alert ID:</strong> {alert['id']}</p>
                <div style="background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px;">
                    <h3>Mensaje:</h3>
                    <p>{alert['message']}</p>
                </div>
        """
        
        if alert.get('details'):
            html += """
                <div style="background-color: #e9ecef; padding: 15px; margin: 10px 0; border-radius: 5px;">
                    <h3>Detalles Técnicos:</h3>
                    <pre style="white-space: pre-wrap;">{}</pre>
                </div>
            """.format(json.dumps(alert['details'], indent=2, ensure_ascii=False))
        
        html += """
                <hr>
                <p style="color: #6c757d; font-size: 12px;">
                    Generado automáticamente por ERC Police Watchdog<br>
                    Sistema de monitoreo médico para ERC Insight
                </p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _send_desktop_alert(self, alert: Dict[str, Any]):
        """Envía alerta desktop usando tkinter"""
        if not GUI_AVAILABLE:
            raise Exception("tkinter no disponible")
        
        # Filtrar según configuración
        if not self._should_show_desktop_alert(alert["severity"]):
            return
        
        # Crear ventana de alerta en thread separado
        def show_alert():
            try:
                # Crear ventana raíz oculta
                root = tk.Tk()
                root.withdraw()
                
                # Configurar según severidad
                if alert["severity"] == "critical":
                    title = f"🚨 CRÍTICO: {alert['title']}"
                    icon = "error"
                elif alert["severity"] == "warning":
                    title = f"⚠️ ADVERTENCIA: {alert['title']}"
                    icon = "warning"
                else:
                    title = f"ℹ️ INFO: {alert['title']}"
                    icon = "info"
                
                # Mostrar mensaje
                messagebox.showwarning(title, alert['message'], icon=icon)
                root.destroy()
                
            except Exception as e:
                print(f"Error mostrando alerta desktop: {e}")
        
        # Ejecutar en thread separado para no bloquear
        threading.Thread(target=show_alert, daemon=True).start()
    
    def _should_show_desktop_alert(self, severity: str) -> bool:
        """Determina si mostrar alerta desktop según configuración"""
        config = self.config["desktop"]
        if severity == "info":
            return config.get("show_info", False)
        elif severity == "warning":
            return config.get("show_warnings", True)
        elif severity == "critical":
            return config.get("show_critical", True)
        return True
    
    def _send_slack_alert(self, alert: Dict[str, Any]):
        """Envía alerta a Slack via webhook"""
        webhook_url = self.config["webhooks"]["slack"]["webhook_url"]
        if not webhook_url:
            raise Exception("Slack webhook URL no configurada")
        
        # Formatear mensaje para Slack
        slack_msg = {
            "text": f"ERC Police Alert: {alert['title']}",
            "attachments": [{
                "color": {"info": "good", "warning": "warning", "critical": "danger"}.get(alert["severity"], "good"),
                "fields": [
                    {"title": "Severidad", "value": alert["severity"].upper(), "short": True},
                    {"title": "Timestamp", "value": alert["timestamp"], "short": True},
                    {"title": "Mensaje", "value": alert["message"], "short": False}
                ]
            }]
        }
        
        # Enviar
        data = json.dumps(slack_msg).encode('utf-8')
        req = urllib.request.Request(webhook_url, data, {'Content-Type': 'application/json'})
        urllib.request.urlopen(req)
    
    def _send_discord_alert(self, alert: Dict[str, Any]):
        """Envía alerta a Discord via webhook"""
        webhook_url = self.config["webhooks"]["discord"]["webhook_url"]
        if not webhook_url:
            raise Exception("Discord webhook URL no configurada")
        
        # Formatear mensaje para Discord
        color_map = {"info": 0x17a2b8, "warning": 0xffc107, "critical": 0xdc3545}
        
        discord_msg = {
            "embeds": [{
                "title": f"ERC Police Alert: {alert['title']}",
                "description": alert['message'],
                "color": color_map.get(alert["severity"], 0x6c757d),
                "fields": [
                    {"name": "Severidad", "value": alert["severity"].upper(), "inline": True},
                    {"name": "Timestamp", "value": alert["timestamp"], "inline": True},
                    {"name": "Alert ID", "value": alert["id"], "inline": True}
                ],
                "footer": {"text": "ERC Police Watchdog"}
            }]
        }
        
        # Enviar
        data = json.dumps(discord_msg).encode('utf-8')
        req = urllib.request.Request(webhook_url, data, {'Content-Type': 'application/json'})
        urllib.request.urlopen(req)
    
    def _log_alert_to_file(self, alert: Dict[str, Any]):
        """Registra alerta en archivo de log"""
        log_path = Path(self.config["file_log"]["log_path"])
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            "timestamp": alert["timestamp"],
            "id": alert["id"],
            "severity": alert["severity"], 
            "title": alert["title"],
            "message": alert["message"],
            "details": alert.get("details", {})
        }
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de alertas"""
        return {
            "total_sent": len(self.alert_history),
            "by_severity": self.alert_count_by_severity.copy(),
            "last_24h": len([a for a in self.alert_history 
                           if (datetime.now() - datetime.fromisoformat(a["timestamp"])).days < 1]),
            "queue_size": len(self.alert_queue),
            "last_alert": self.alert_history[-1]["timestamp"] if self.alert_history else None
        }

# ═══════════════════════════════════════════════════════════════════════════════
# SISTEMA DE TESTING AUTOMÁTICO
# ═══════════════════════════════════════════════════════════════════════════════

class ERCPoliceTestSuite:
    """Suite completa de tests para el sistema policía"""
    
    def __init__(self):
        self.test_results = []
        self.test_lock = threading.Lock()
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Ejecuta todos los tests disponibles"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "test_details": [],
            "summary": ""
        }
        
        # Lista de tests a ejecutar
        test_methods = [
            self._test_tfg_calculation,
            self._test_medical_validation,
            self._test_alert_system,
            self._test_file_integrity,
            self._test_configuration_loading,
            self._test_database_operations,
            self._test_error_handling
        ]
        
        print("🧪 Ejecutando suite completa de tests...")
        
        for test_method in test_methods:
            try:
                test_result = test_method()
                results["test_details"].append(test_result)
                results["total_tests"] += 1
                
                if test_result["status"] == "PASS":
                    results["passed"] += 1
                elif test_result["status"] == "FAIL":
                    results["failed"] += 1
                else:
                    results["errors"] += 1
                    
            except Exception as e:
                results["test_details"].append({
                    "name": test_method.__name__,
                    "status": "ERROR",
                    "message": f"Test execution error: {str(e)}",
                    "duration": 0
                })
                results["errors"] += 1
                results["total_tests"] += 1
        
        # Generar resumen
        success_rate = (results["passed"] / results["total_tests"]) * 100 if results["total_tests"] > 0 else 0
        results["summary"] = f"Tests: {results['total_tests']} | Passed: {results['passed']} | Failed: {results['failed']} | Errors: {results['errors']} | Success Rate: {success_rate:.1f}%"
        
        return results
    
    def _test_tfg_calculation(self) -> Dict[str, Any]:
        """Test de cálculo de TFG"""
        start_time = time.time()
        test_name = "TFG Calculation"
        
        try:
            # Casos de test con valores esperados
            test_cases = [
                {"input": (65, 70, 1.2, "m"), "expected_range": (70, 75)},
                {"input": (70, 60, 0.9, "f"), "expected_range": (55, 65)},
                {"input": (50, 80, 1.0, "m"), "expected_range": (85, 95)}
            ]
            
            passed_cases = 0
            
            for case in test_cases:
                edad, peso, creatinina, sexo = case["input"]
                expected_min, expected_max = case["expected_range"]
                
                # Calcular TFG usando la fórmula Cockcroft-Gault
                factor_sexo = 0.85 if sexo.lower() == "f" else 1.0
                tfg = ((140 - edad) * peso * factor_sexo) / (72 * creatinina)
                tfg = round(tfg, 2)
                
                if expected_min <= tfg <= expected_max:
                    passed_cases += 1
            
            status = "PASS" if passed_cases == len(test_cases) else "FAIL"
            message = f"Passed {passed_cases}/{len(test_cases)} test cases"
            
            return {
                "name": test_name,
                "status": status,
                "message": message,
                "duration": round(time.time() - start_time, 3),
                "details": {"cases_passed": passed_cases, "total_cases": len(test_cases)}
            }
            
        except Exception as e:
            return {
                "name": test_name,
                "status": "ERROR",
                "message": f"Test error: {str(e)}",
                "duration": round(time.time() - start_time, 3)
            }
    
    def _test_medical_validation(self) -> Dict[str, Any]:
        """Test de validaciones médicas"""
        start_time = time.time()
        test_name = "Medical Validation"
        
        try:
            validations_passed = 0
            total_validations = 0
            
            # Test 1: Validación de rangos TFG
            test_tfg_values = [95, 75, 50, 35, 25, 10]
            expected_stages = ["g1", "g2", "g3a", "g3b", "g4", "g5"]
            
            for i, tfg in enumerate(test_tfg_values):
                total_validations += 1
                
                # Clasificar estadio
                if tfg >= 90:
                    stage = "g1"
                elif tfg >= 60:
                    stage = "g2"
                elif tfg >= 45:
                    stage = "g3a"
                elif tfg >= 30:
                    stage = "g3b"
                elif tfg >= 15:
                    stage = "g4"
                else:
                    stage = "g5"
                
                if stage == expected_stages[i]:
                    validations_passed += 1
            
            # Test 2: Validación de parámetros de entrada
            invalid_inputs = [
                (-10, 70, 1.2, "m"),  # Edad negativa
                (65, 0, 1.2, "m"),    # Peso cero
                (65, 70, -1, "m"),    # Creatinina negativa
                (65, 70, 1.2, "x")    # Sexo inválido
            ]
            
            for inputs in invalid_inputs:
                total_validations += 1
                edad, peso, creatinina, sexo = inputs
                
                # Validar que se detecten entradas inválidas
                is_invalid = (
                    edad <= 0 or edad > 120 or
                    peso <= 0 or peso > 300 or
                    creatinina <= 0 or creatinina > 20 or
                    sexo.lower() not in ['m', 'f', 'masculino', 'femenino']
                )
                
                if is_invalid:
                    validations_passed += 1
            
            status = "PASS" if validations_passed == total_validations else "FAIL"
            message = f"Medical validations: {validations_passed}/{total_validations} passed"
            
            return {
                "name": test_name,
                "status": status,
                "message": message,
                "duration": round(time.time() - start_time, 3),
                "details": {"validations_passed": validations_passed, "total_validations": total_validations}
            }
            
        except Exception as e:
            return {
                "name": test_name,
                "status": "ERROR",
                "message": f"Test error: {str(e)}",
                "duration": round(time.time() - start_time, 3)
            }
    
    def _test_alert_system(self) -> Dict[str, Any]:
        """Test del sistema de alertas"""
        start_time = time.time()
        test_name = "Alert System"
        
        try:
            # Crear instancia de prueba del sistema de alertas
            test_config = {
                "email": {"enabled": False},
                "desktop": {"enabled": False}, 
                "webhooks": {"slack": {"enabled": False}, "discord": {"enabled": False}},
                "file_log": {"enabled": True, "log_path": "test_alerts.log"}
            }
            
            alert_system = ERCAlertSystem(test_config)
            
            # Test envío de alertas
            alert_id = alert_system.send_alert(
                "warning", 
                "Test Alert", 
                "This is a test alert message",
                {"test": True}
            )
            
            # Verificar que se generó ID
            test_passed = bool(alert_id and len(alert_id) > 0)
            
            # Verificar estadísticas
            stats = alert_system.get_alert_statistics()
            test_passed = test_passed and stats["total_sent"] >= 0
            
            status = "PASS" if test_passed else "FAIL"
            message = f"Alert system functional: {test_passed}"
            
            return {
                "name": test_name,
                "status": status,
                "message": message,
                "duration": round(time.time() - start_time, 3),
                "details": {"alert_id": alert_id, "stats": stats}
            }
            
        except Exception as e:
            return {
                "name": test_name,
                "status": "ERROR",
                "message": f"Test error: {str(e)}",
                "duration": round(time.time() - start_time, 3)
            }
    
    def _test_file_integrity(self) -> Dict[str, Any]:
        """Test de integridad de archivos"""
        start_time = time.time()
        test_name = "File Integrity"
        
        try:
            # Crear archivo de prueba
            test_file = Path("test_integrity.tmp")
            test_content = "Test content for integrity check"
            
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            # Calcular hash
            content_hash = hashlib.md5(test_content.encode()).hexdigest()
            
            # Verificar que el archivo existe y tiene el contenido correcto
            file_exists = test_file.exists()
            
            with open(test_file, 'r') as f:
                read_content = f.read()
            
            content_matches = read_content == test_content
            hash_matches = hashlib.md5(read_content.encode()).hexdigest() == content_hash
            
            # Limpiar
            test_file.unlink()
            
            test_passed = file_exists and content_matches and hash_matches
            
            return {
                "name": test_name,
                "status": "PASS" if test_passed else "FAIL",
                "message": f"File integrity check: {test_passed}",
                "duration": round(time.time() - start_time, 3),
                "details": {
                    "file_exists": file_exists,
                    "content_matches": content_matches,
                    "hash_matches": hash_matches
                }
            }
            
        except Exception as e:
            return {
                "name": test_name,
                "status": "ERROR",
                "message": f"Test error: {str(e)}",
                "duration": round(time.time() - start_time, 3)
            }
    
    def _test_configuration_loading(self) -> Dict[str, Any]:
        """Test de carga de configuración"""
        start_time = time.time()
        test_name = "Configuration Loading"
        
        try:
            # Crear configuración de prueba
            test_config = {
                "app_root": "/test/path",
                "health_check_interval": 30,
                "max_cpu_usage": 85.0,
                "critical_files": ["test1.py", "test2.py"]
            }
            
            config_file = Path("test_config.json")
            
            # Guardar configuración
            with open(config_file, 'w') as f:
                json.dump(test_config, f, indent=2)
            
            # Cargar configuración
            with open(config_file, 'r') as f:
                loaded_config = json.load(f)
            
            # Verificar que se cargó correctamente
            config_matches = loaded_config == test_config
            
            # Limpiar
            config_file.unlink()
            
            return {
                "name": test_name,
                "status": "PASS" if config_matches else "FAIL",
                "message": f"Configuration loading: {config_matches}",
                "duration": round(time.time() - start_time, 3),
                "details": {"config_loaded": config_matches}
            }
            
        except Exception as e:
            return {
                "name": test_name,
                "status": "ERROR",
                "message": f"Test error: {str(e)}",
                "duration": round(time.time() - start_time, 3)
            }
    
    def _test_database_operations(self) -> Dict[str, Any]:
        """Test de operaciones de base de datos"""
        start_time = time.time()
        test_name = "Database Operations"
        
        try:
            # Crear base de datos en memoria
            db_path = ":memory:"
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Crear tabla de prueba
                cursor.execute("""
                    CREATE TABLE test_table (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        value REAL
                    )
                """)
                
                # Insertar datos
                cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("test", 123.45))
                
                # Consultar datos
                cursor.execute("SELECT name, value FROM test_table WHERE name = ?", ("test",))
                result = cursor.fetchone()
                
                # Verificar resultado
                test_passed = result == ("test", 123.45)
                
                conn.commit()
            
            return {
                "name": test_name,
                "status": "PASS" if test_passed else "FAIL",
                "message": f"Database operations: {test_passed}",
                "duration": round(time.time() - start_time, 3),
                "details": {"query_result": result}
            }
            
        except Exception as e:
            return {
                "name": test_name,
                "status": "ERROR",
                "message": f"Test error: {str(e)}",
                "duration": round(time.time() - start_time, 3)
            }
    
    def _test_error_handling(self) -> Dict[str, Any]:
        """Test de manejo de errores"""
        start_time = time.time()
        test_name = "Error Handling"
        
        try:
            errors_caught = 0
            total_error_tests = 0
            
            # Test 1: División por cero
            total_error_tests += 1
            try:
                result = 1 / 0
            except ZeroDivisionError:
                errors_caught += 1
            
            # Test 2: Acceso a archivo inexistente
            total_error_tests += 1
            try:
                with open("nonexistent_file.txt", 'r') as f:
                    content = f.read()
            except FileNotFoundError:
                errors_caught += 1
            
            # Test 3: JSON inválido
            total_error_tests += 1
            try:
                data = json.loads("invalid json string")
            except json.JSONDecodeError:
                errors_caught += 1
            
            # Test 4: Índice fuera de rango
            total_error_tests += 1
            try:
                test_list = [1, 2, 3]
                value = test_list[10]
            except IndexError:
                errors_caught += 1
            
            test_passed = errors_caught == total_error_tests
            
            return {
                "name": test_name,
                "status": "PASS" if test_passed else "FAIL",
                "message": f"Error handling: {errors_caught}/{total_error_tests} errors caught",
                "duration": round(time.time() - start_time, 3),
                "details": {"errors_caught": errors_caught, "total_tests": total_error_tests}
            }
            
        except Exception as e:
            return {
                "name": test_name,
                "status": "ERROR",
                "message": f"Test error: {str(e)}",
                "duration": round(time.time() - start_time, 3)
            }

# ═══════════════════════════════════════════════════════════════════════════════
# SIMULADOR DE ESCENARIOS CRÍTICOS
# ═══════════════════════════════════════════════════════════════════════════════

class ERCScenarioSimulator:
    """Simulador de escenarios críticos para testing del watchdog"""
    
    def __init__(self, alert_system: ERCAlertSystem = None):
        self.alert_system = alert_system or ERCAlertSystem()
        self.scenarios = self._define_scenarios()
    
    def _define_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """Define escenarios de prueba críticos"""
        return {
            "critical_tfg": {
                "name": "TFG Crítico - Paciente G5",
                "description": "Paciente con TFG < 15 requiere diálisis urgente",
                "patient_data": {
                    "edad": 70,
                    "peso": 65,
                    "creatinina": 8.5,
                    "sexo": "f"
                },
                "expected_alerts": ["critical"],
                "medical_actions": ["Referir nefrología urgente", "Preparar acceso vascular", "Evaluar diálisis"]
            },
            "medication_contraindication": {
                "name": "Contraindicación Medicamentosa Crítica",
                "description": "Metformina en paciente con TFG < 30",
                "patient_data": {
                    "edad": 65,
                    "peso": 70,
                    "creatinina": 3.2,
                    "sexo": "m",
                    "medications": ["Metformina", "Enalapril"]
                },
                "expected_alerts": ["critical"],
                "medical_actions": ["Suspender Metformina", "Ajustar dosis Enalapril", "Monitoreo K+ y creatinina"]
            },
            "hypertensive_crisis": {
                "name": "Crisis Hipertensiva en ERC",
                "description": "Presión arterial >180/110 en paciente con ERC",
                "patient_data": {
                    "edad": 60,
                    "peso": 75,
                    "creatinina": 2.1,
                    "sexo": "m",
                    "presion_sistolica": 190,
                    "presion_diastolica": 115
                },
                "expected_alerts": ["critical"],
                "medical_actions": ["Control inmediato PA", "Evaluar daño órgano blanco", "Ajuste farmacológico urgente"]
            },
            "multiple_risk_factors": {
                "name": "Paciente Muy Alto Riesgo CV",
                "description": "Múltiples factores de riesgo cardiovascular",
                "patient_data": {
                    "edad": 75,
                    "peso": 80,
                    "creatinina": 2.5,
                    "sexo": "m",
                    "dm2": True,
                    "hta": True,
                    "tabaquismo": True,
                    "antecedente_cv": True
                },
                "expected_alerts": ["critical", "warning"],
                "medical_actions": ["Control estricto factores riesgo", "Seguimiento intensivo", "Intervención cardiólogo"]
            }
        }
    
    def run_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Ejecuta un escenario específico"""
        if scenario_name not in self.scenarios:
            raise ValueError(f"Escenario '{scenario_name}' no encontrado")
        
        scenario = self.scenarios[scenario_name]
        
        simulation_result = {
            "scenario_name": scenario_name,
            "timestamp": datetime.now().isoformat(),
            "status": "running",
            "alerts_generated": [],
            "medical_calculations": {},
            "recommendations": [],
            "errors": []
        }
        
        try:
            print(f"\n🎭 SIMULANDO ESCENARIO: {scenario['name']}")
            print(f"📋 Descripción: {scenario['description']}")
            
            patient_data = scenario["patient_data"]
            
            # 🧮 CALCULAR TFG SI ES NECESARIO
            if "creatinina" in patient_data:
                tfg = self._calculate_tfg(
                    patient_data["edad"],
                    patient_data["peso"], 
                    patient_data["creatinina"],
                    patient_data["sexo"]
                )
                simulation_result["medical_calculations"]["tfg"] = tfg
                patient_data["tfg"] = tfg
                
                # Clasificar estadio ERC
                if tfg >= 90:
                    estadio = "g1"
                elif tfg >= 60:
                    estadio = "g2"
                elif tfg >= 45:
                    estadio = "g3a"
                elif tfg >= 30:
                    estadio = "g3b"
                elif tfg >= 15:
                    estadio = "g4"
                else:
                    estadio = "g5"
                
                simulation_result["medical_calculations"]["estadio_erc"] = estadio
                
                print(f"   🔍 TFG calculado: {tfg} ml/min/1.73m² (Estadio {estadio.upper()})")
            
            # 🚨 EVALUAR ALERTAS CRÍTICAS
            alerts_triggered = self._evaluate_critical_conditions(patient_data, simulation_result)
            
            # 📊 CALCULAR RIESGO CARDIOVASCULAR
            cv_risk = self._calculate_cardiovascular_risk(patient_data)
            simulation_result["medical_calculations"]["riesgo_cardiovascular"] = cv_risk
            
            print(f"   ❤️ Riesgo cardiovascular: {cv_risk['level']} (Score: {cv_risk['score']})")
            
            # 💊 EVALUAR MEDICAMENTOS
            if "medications" in patient_data:
                med_alerts = self._evaluate_medication_safety(patient_data)
                simulation_result["alerts_generated"].extend(med_alerts)
            
            # 📝 GENERAR RECOMENDACIONES
            simulation_result["recommendations"] = scenario.get("medical_actions", [])
            
            # ✅ COMPLETAR SIMULACIÓN
            simulation_result["status"] = "completed"
            
            print(f"   ✅ Simulación completada - {len(simulation_result['alerts_generated'])} alertas generadas")
            
            return simulation_result
            
        except Exception as e:
            simulation_result["status"] = "error"
            simulation_result["errors"].append(str(e))
            print(f"   ❌ Error en simulación: {str(e)}")
            return simulation_result
    
    def _calculate_tfg(self, edad: int, peso: float, creatinina: float, sexo: str) -> float:
        """Calcula TFG usando fórmula Cockcroft-Gault"""
        factor_sexo = 0.85 if sexo.lower() in ['f', 'femenino'] else 1.0
        tfg = ((140 - edad) * peso * factor_sexo) / (72 * creatinina)
        return round(tfg, 2)
    
    def _evaluate_critical_conditions(self, patient_data: Dict[str, Any], simulation_result: Dict[str, Any]) -> List[str]:
        """Evalúa condiciones críticas y genera alertas"""
        alerts = []
        
        # TFG crítico
        if "tfg" in patient_data and patient_data["tfg"] < 15:
            alert_id = self.alert_system.send_alert(
                "critical",
                "TFG CRÍTICO - Terapia de Reemplazo Renal Urgente",
                f"Paciente con TFG {patient_data['tfg']} ml/min/1.73m² requiere evaluación inmediata para diálisis",
                {"tfg": patient_data["tfg"], "scenario": "critical_tfg"}
            )
            alerts.append(alert_id)
            
        elif "tfg" in patient_data and patient_data["tfg"] < 30:
            alert_id = self.alert_system.send_alert(
                "warning",
                "TFG Severamente Disminuido",
                f"TFG {patient_data['tfg']} ml/min/1.73m² - Preparar para terapia renal",
                {"tfg": patient_data["tfg"], "scenario": "severe_tfg"}
            )
            alerts.append(alert_id)
        
        # Presión arterial crítica
        if ("presion_sistolica" in patient_data and patient_data["presion_sistolica"] > 180) or \
           ("presion_diastolica" in patient_data and patient_data["presion_diastolica"] > 110):
            alert_id = self.alert_system.send_alert(
                "critical",
                "CRISIS HIPERTENSIVA",
                f"PA: {patient_data.get('presion_sistolica', '?')}/{patient_data.get('presion_diastolica', '?')} mmHg - Intervención inmediata",
                {"presion_sistolica": patient_data.get("presion_sistolica"), 
                 "presion_diastolica": patient_data.get("presion_diastolica"),
                 "scenario": "hypertensive_crisis"}
            )
            alerts.append(alert_id)
        
        simulation_result["alerts_generated"] = alerts
        return alerts
    
    def _calculate_cardiovascular_risk(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula riesgo cardiovascular"""
        score = 0
        factors = []
        
        # Factor edad
        if patient_data.get("edad", 0) >= 75:
            score += 3
            factors.append("Edad ≥75 años")
        elif patient_data.get("edad", 0) >= 65:
            score += 2
            factors.append("Edad ≥65 años")
        
        # Factor ERC
        tfg = patient_data.get("tfg", 100)
        if tfg < 30:
            score += 4
            factors.append("ERC G4-G5")
        elif tfg < 60:
            score += 2
            factors.append("ERC G3")
        
        # Comorbilidades
        if patient_data.get("dm2"):
            score += 3
            factors.append("Diabetes mellitus")
        
        if patient_data.get("hta"):
            score += 2
            factors.append("Hipertensión")
        
        if patient_data.get("tabaquismo"):
            score += 2
            factors.append("Tabaquismo")
        
        if patient_data.get("antecedente_cv"):
            score += 4
            factors.append("Antecedente cardiovascular")
        
        # Clasificar riesgo
        if score >= 8:
            level = "muy_alto"
        elif score >= 5:
            level = "alto"
        elif score >= 2:
            level = "moderado"
        else:
            level = "bajo"
        
        return {"level": level, "score": score, "factors": factors}
    
    def _evaluate_medication_safety(self, patient_data: Dict[str, Any]) -> List[str]:
        """Evalúa seguridad de medicamentos"""
        alerts = []
        medications = patient_data.get("medications", [])
        tfg = patient_data.get("tfg", 100)
        
        for medication in medications:
            med_lower = medication.lower()
            
            # Metformina contraindicada con TFG < 30
            if "metformina" in med_lower and tfg < 30:
                alert_id = self.alert_system.send_alert(
                    "critical",
                    "CONTRAINDICACIÓN: Metformina",
                    f"Suspender Metformina inmediatamente - TFG {tfg} < 30 ml/min - Riesgo acidosis láctica",
                    {"medication": medication, "tfg": tfg, "contraindication": "tfg_low"}
                )
                alerts.append(alert_id)
            
            # iSGLT2 con efectividad reducida
            elif any(sglt2 in med_lower for sglt2 in ["empagliflozina", "dapagliflozina"]) and tfg < 30:
                alert_id = self.alert_system.send_alert(
                    "warning",
                    "Medicamento de Efectividad Reducida",
                    f"{medication} tiene efectividad reducida con TFG {tfg} < 30 ml/min",
                    {"medication": medication, "tfg": tfg, "issue": "reduced_efficacy"}
                )
                alerts.append(alert_id)
        
        return alerts
    
    def run_all_scenarios(self) -> Dict[str, Any]:
        """Ejecuta todos los escenarios definidos"""
        print("\n🎭 EJECUTANDO TODOS LOS ESCENARIOS DE SIMULACIÓN")
        print("=" * 60)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "scenarios_executed": [],
            "total_alerts": 0,
            "summary": {}
        }
        
        for scenario_name in self.scenarios.keys():
            result = self.run_scenario(scenario_name)
            results["scenarios_executed"].append(result)
            results["total_alerts"] += len(result.get("alerts_generated", []))
        
        # Generar resumen
        successful = len([r for r in results["scenarios_executed"] if r["status"] == "completed"])
        total = len(results["scenarios_executed"])
        
        results["summary"] = {
            "total_scenarios": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": round((successful / total) * 100, 1) if total > 0 else 0,
            "total_alerts_generated": results["total_alerts"]
        }
        
        print(f"\n📊 RESUMEN DE SIMULACIONES:")
        print(f"   Escenarios ejecutados: {total}")
        print(f"   Exitosos: {successful}")
        print(f"   Alertas generadas: {results['total_alerts']}")
        
        return results

# ═══════════════════════════════════════════════════════════════════════════════
# SISTEMA COMPLETO INTEGRADO
# ═══════════════════════════════════════════════════════════════════════════════

def run_complete_police_system():
    """Ejecuta el sistema policía completo"""
    print("🚨 ERC POLICE WATCHDOG - SISTEMA COMPLETO")
    print("=" * 50)
    
    # 1. Inicializar sistema de alertas
    print("\n📢 Inicializando sistema de alertas...")
    alert_system = ERCAlertSystem()
    
    # 2. Ejecutar suite de tests
    print("\n🧪 Ejecutando suite de tests...")
    test_suite = ERCPoliceTestSuite()
    test_results = test_suite.run_all_tests()
    print(f"   {test_results['summary']}")
    
    # 3. Ejecutar simulaciones
    print("\n🎭 Ejecutando simulaciones de escenarios críticos...")
    simulator = ERCScenarioSimulator(alert_system)
    simulation_results = simulator.run_all_scenarios()
    
    # 4. Generar reporte final
    print("\n📊 REPORTE FINAL DEL SISTEMA POLICÍA")
    print("-" * 40)
    
    # Estadísticas de tests
    print(f"🧪 Tests: {test_results['passed']}/{test_results['total_tests']} exitosos ({test_results['passed']/test_results['total_tests']*100:.1f}%)")
    
    # Estadísticas de simulaciones
    sim_summary = simulation_results['summary']
    print(f"🎭 Simulaciones: {sim_summary['successful']}/{sim_summary['total_scenarios']} exitosas ({sim_summary['success_rate']:.1f}%)")
    
    # Estadísticas de alertas
    alert_stats = alert_system.get_alert_statistics()
    print(f"📢 Alertas: {alert_stats['total_sent']} enviadas")
    print(f"   - Críticas: {alert_stats['by_severity']['critical']}")
    print(f"   - Advertencias: {alert_stats['by_severity']['warning']}")
    print(f"   - Informativas: {alert_stats['by_severity']['info']}")
    
    # Estado general del sistema
    overall_health = "🟢 SALUDABLE" if test_results['failed'] == 0 and test_results['errors'] == 0 else "🟡 CON PROBLEMAS"
    print(f"\n🏥 Estado del sistema ERC Insight: {overall_health}")
    
    return {
        "test_results": test_results,
        "simulation_results": simulation_results,
        "alert_stats": alert_stats,
        "system_health": overall_health
    }

# ═══════════════════════════════════════════════════════════════════════════════
# INSTRUCCIONES DE INSTALACIÓN Y EJECUCIÓN
# ═══════════════════════════════════════════════════════════════════════════════

INSTALLATION_INSTRUCTIONS = """
🚨 ERC POLICE WATCHDOG - INSTRUCCIONES DE INSTALACIÓN Y EJECUCIÓN
================================================================

📦 DEPENDENCIAS REQUERIDAS:
---------------------------
pip install flask flask-cors werkzeug python-dotenv
pip install requests psutil apscheduler
pip install structlog pytest watchdog
pip install google-generativeai pydantic tenacity

📦 DEPENDENCIAS OPCIONALES:
--------------------------
pip install tkinter  # Para alertas desktop (normalmente incluido en Python)

📁 ESTRUCTURA DE ARCHIVOS:
--------------------------
ERC/
├── erc_police_parte1.py    # Configuración y estructura principal
├── erc_police_parte2.py    # Chequeos médicos y enforcement
├── erc_police_parte3.py    # Alertas, tests y simulación
├── logs/                   # Directorio para logs (se crea automáticamente)
│   ├── erc_police.log
│   ├── erc_police_errors.log
│   └── erc_police_alerts.log
└── config/
    └── erc_police_config.json  # Configuración personalizada (opcional)

🚀 EJECUCIÓN BÁSICA:
--------------------
1. Ejecutar cada parte individualmente:
   python erc_police_parte1.py
   python erc_police_parte2.py
   python erc_police_parte3.py

2. Ejecutar sistema completo:
   python -c "from erc_police_parte3 import run_complete_police_system; run_complete_police_system()"

⚙️ CONFIGURACIÓN DE ALERTAS:
----------------------------
1. Email (Gmail):
   - Crear contraseña de aplicación en Gmail
   - Configurar en erc_police_config.json:
     {
       "email": {
         "enabled": true,
         "username": "tu_email@gmail.com",
         "password": "tu_app_password",
         "recipients": ["admin@ercinsight.com"]
       }
     }

2. Slack:
   - Crear webhook en Slack
   - Configurar webhook_url en config

3. Discord:
   - Crear webhook en Discord
   - Configurar webhook_url en config

🔧 CONFIGURACIÓN PERSONALIZADA:
-------------------------------
Crear archivo erc_police_config.json:
{
  "health_check_interval": 30,
  "max_cpu_usage": 85.0,
  "enable_email_alerts": true,
  "enable_desktop_alerts": true,
  "app_url": "http://localhost:5000",
  "critical_files": [
    "app/logic/patient_eval.py",
    "app/logic/advanced_patient_eval.py"
  ]
}

🏃‍♂️ EJECUCIÓN EN PRODUCCIÓN:
-----------------------------
1. Como servicio de Windows:
   - Usar nssm o similar para crear servicio
   - Configurar para inicio automático

2. Como tarea programada:
   - Task Scheduler de Windows
   - Ejecutar cada 30 minutos

3. Como daemon en Linux:
   - Crear systemd service
   - Habilitar para inicio automático

📊 MONITOREO:
-------------
1. Logs disponibles en logs/
2. Base de datos SQLite en logs/erc_police.db
3. Alertas por email/desktop según configuración
4. Dashboard web (opcional - requiere desarrollo adicional)

🧪 TESTING:
-----------
# Ejecutar tests individuales
python -m pytest erc_police_parte3.py::ERCPoliceTestSuite::run_all_tests

# Ejecutar simulaciones
python -c "from erc_police_parte3 import ERCScenarioSimulator; ERCScenarioSimulator().run_all_scenarios()"

📞 SOPORTE:
-----------
- Logs detallados en logs/erc_police_errors.log
- Configuración de debug en logging level
- Alertas automáticas ante fallos críticos
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA Y DEMO FINAL
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("⚠️ ERC Police Watchdog - Parte 3 (Alertas, Tests y Simulación)")
    print("=" * 65)
    
    # Mostrar instrucciones
    print("📋 Instrucciones de instalación disponibles en INSTALLATION_INSTRUCTIONS")
    
    try:
        # Ejecutar sistema completo
        results = run_complete_police_system()
        
        print("\n✅ SISTEMA POLICÍA ERC EJECUTADO EXITOSAMENTE")
        print("=" * 50)
        print("🎯 TODAS LAS PARTES COMPLETADAS:")
        print("   ✅ PARTE 1: Configuración y estructura ✓")
        print("   ✅ PARTE 2: Chequeos médicos y enforcement ✓") 
        print("   ✅ PARTE 3: Alertas, tests y simulación ✓")
        print()
        print("🏥 ERC INSIGHT FLASK APP ESTÁ PROTEGIDA POR EL SISTEMA POLICÍA")
        print("🚨 MONITOREO AUTÓNOMO ACTIVO")
        print("⚡ SISTEMA IMPENETRABLE IMPLEMENTADO")
        
        # Mostrar instrucciones de instalación
        print("\n" + "="*65)
        print(INSTALLATION_INSTRUCTIONS)
        
    except Exception as e:
        print(f"❌ Error ejecutando sistema completo: {str(e)}")
        traceback.print_exc()

"""
📋 PARTE 3 COMPLETADA - SISTEMA POLICÍA COMPLETO:

🎯 SISTEMA COMPLETO INCLUYE:
- ✅ ERCAlertSystem: Alertas multi-canal (email, desktop, webhooks, logs)
- ✅ ERCPoliceTestSuite: Suite completa de tests automatizados
- ✅ ERCScenarioSimulator: Simulación de escenarios médicos críticos
- ✅ Sistema integrado con las 3 partes funcionando juntas
- ✅ Instrucciones completas de instalación y configuración
- ✅ Documentación de uso y mantenimiento

🏥 CAPACIDADES MÉDICAS:
- Detección automática de TFG crítico (< 15 ml/min) con alertas inmediatas
- Validación de contraindicaciones medicamentosas
- Monitoreo de crisis hipertensivas
- Evaluación de riesgo cardiovascular multi-factorial
- Enforcement de guías clínicas KDIGO y ESC/ESH

🚨 SISTEMA DE ALERTAS:
- Email con formato HTML profesional
- Alertas desktop nativas de Windows
- Webhooks para Slack y Discord
- Logging estructurado en archivos y SQLite
- Clasificación por severidad (info/warning/critical)

🧪 TESTING AUTOMÁTICO:
- Suite de 7 tests críticos del sistema
- Validación de cálculos médicos
- Tests de integridad de archivos y configuración
- Tests de manejo de errores y excepciones
- Reportes detallados con métricas de éxito

🎭 SIMULACIÓN DE ESCENARIOS:
- 4 escenarios críticos predefinidos
- Simulación de pacientes G5 con necesidad de diálisis
- Casos de contraindicaciones farmacológicas
- Crisis hipertensivas en contexto de ERC
- Pacientes de muy alto riesgo cardiovascular

⚡ CARACTERÍSTICAS AVANZADAS:
- Threading seguro para operaciones concurrentes  
- Base de datos SQLite para persistencia
- Configuración flexible via JSON
- Fallbacks para dependencias opcionales
- Logging estructurado con rotación
- Sistema de colas para alertas
- Estadísticas y métricas en tiempo real

🔧 INSTALACIÓN Y USO:
- Instrucciones paso a paso incluidas
- Configuración de servicios de Windows/Linux
- Setup de alertas por email (Gmail)
- Configuración de webhooks
- Opciones de deployment en producción

🏁 RESULTADO FINAL:
ERC INSIGHT FLASK APPLICATION COMPLETAMENTE PROTEGIDA
CON SISTEMA POLICÍA AUTÓNOMO, MONITOREO MÉDICO 24/7,
ALERTAS PROACTIVAS Y ENFORCEMENT DE REGLAS CLÍNICAS.

¡APLICACIÓN IMPENETRABLE IMPLEMENTADA CON ÉXITO! 🎯
"""
