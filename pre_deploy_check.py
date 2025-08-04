#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de verificación pre-despliegue para ERC Insight
Este script realiza comprobaciones críticas para asegurar que la aplicación
está lista para el despliegue en entornos cloud como Render.com
"""

import os
import sys
import logging
from pathlib import Path
import importlib.util

def setup_logging():
    """Configura el logging para este script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger("pre_deploy_check")

def check_file_exists(filepath, critical=True):
    """Verifica si un archivo existe"""
    exists = os.path.isfile(filepath)
    if exists:
        logger.info(f"✅ Archivo encontrado: {filepath}")
    else:
        if critical:
            logger.error(f"❌ Archivo crítico no encontrado: {filepath}")
        else:
            logger.warning(f"⚠️ Archivo no encontrado: {filepath}")
    return exists

def check_directory_exists(dirpath, critical=True):
    """Verifica si un directorio existe"""
    exists = os.path.isdir(dirpath)
    if exists:
        logger.info(f"✅ Directorio encontrado: {dirpath}")
    else:
        if critical:
            logger.error(f"❌ Directorio crítico no encontrado: {dirpath}")
        else:
            logger.warning(f"⚠️ Directorio no encontrado: {dirpath}")
    return exists

def check_env_vars():
    """Verifica variables de entorno importantes"""
    critical_vars = ["FLASK_APP", "SECRET_KEY"]
    optional_vars = ["DATABASE_URL", "GEMINI_API_KEY"]
    
    all_critical_present = True
    for var in critical_vars:
        if var in os.environ:
            logger.info(f"✅ Variable de entorno {var} configurada")
        else:
            logger.error(f"❌ Variable de entorno crítica {var} no configurada")
            all_critical_present = False
    
    optional_present = 0
    for var in optional_vars:
        if var in os.environ:
            logger.info(f"✅ Variable de entorno {var} configurada")
            optional_present += 1
        else:
            logger.warning(f"⚠️ Variable de entorno {var} no configurada")
    
    return all_critical_present, optional_present == len(optional_vars)

def check_database_config():
    """Verifica la configuración de la base de datos"""
    # Verificar si podemos importar el módulo config
    if not os.path.exists("config.py"):
        logger.error("❌ No se encuentra config.py")
        return False
    
    try:
        spec = importlib.util.spec_from_file_location("config", "config.py")
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        
        # Verificar clase ProductionConfig
        if not hasattr(config_module, "ProductionConfig"):
            logger.error("❌ No se encuentra ProductionConfig en config.py")
            return False
        
        # Verificar la configuración de base de datos
        prod_config = config_module.ProductionConfig
        db_url = prod_config.SQLALCHEMY_DATABASE_URI if hasattr(prod_config, "SQLALCHEMY_DATABASE_URI") else None
        
        if db_url and db_url.startswith("postgresql://"):
            logger.info("✅ Configuración de base de datos PostgreSQL encontrada")
            return True
        else:
            logger.warning("⚠️ No se detecta configuración PostgreSQL en ProductionConfig")
            return False
    except Exception as e:
        logger.error(f"❌ Error al verificar config.py: {e}")
        return False

def check_gunicorn_wsgi():
    """Verifica configuración de Gunicorn y WSGI"""
    wsgi_exists = check_file_exists("wsgi.py")
    procfile_exists = check_file_exists("Procfile", False)
    
    # Verificar contenido de wsgi.py
    if wsgi_exists:
        with open("wsgi.py", "r") as f:
            content = f.read()
            if "app = create_app('production')" in content:
                logger.info("✅ Configuración correcta en wsgi.py")
            else:
                logger.warning("⚠️ wsgi.py puede no estar usando la configuración de producción")
    
    # Verificar contenido de Procfile si existe
    if procfile_exists:
        with open("Procfile", "r") as f:
            content = f.read()
            if "gunicorn" in content and "wsgi:app" in content:
                logger.info("✅ Configuración correcta en Procfile")
            else:
                logger.warning("⚠️ Procfile puede tener una configuración incorrecta")
    
    return wsgi_exists

def check_render_yaml():
    """Verifica la configuración de render.yaml"""
    if check_file_exists("render.yaml", False):
        with open("render.yaml", "r") as f:
            content = f.read()
            if "plan: free" in content:
                logger.info("✅ render.yaml configurado para plan gratuito")
                return True
            else:
                logger.warning("⚠️ render.yaml no está explícitamente configurado para plan gratuito")
                return False
    return False

def check_runtime_file():
    """Verifica la versión de Python en runtime.txt"""
    if check_file_exists("runtime.txt", False):
        with open("runtime.txt", "r") as f:
            content = f.read().strip()
            if content == "python-3.9.13":
                logger.info("✅ runtime.txt configurado correctamente para Python 3.9.13")
                return True
            else:
                logger.warning(f"⚠️ runtime.txt especifica versión: {content}, pero se recomienda python-3.9.13")
                return False
    return False

def check_static_dirs():
    """Verifica que existan los directorios estáticos necesarios"""
    app_dir = Path("app")
    
    uploads_dir = app_dir / "static" / "uploads"
    reports_dir = app_dir / "static" / "reports"
    
    uploads_exists = check_directory_exists(uploads_dir, False)
    reports_exists = check_directory_exists(reports_dir, False)
    
    if not uploads_exists:
        os.makedirs(uploads_dir, exist_ok=True)
        logger.info(f"✅ Se creó el directorio: {uploads_dir}")
    
    if not reports_exists:
        os.makedirs(reports_dir, exist_ok=True)
        logger.info(f"✅ Se creó el directorio: {reports_dir}")
    
    return True

def check_requirements():
    """Verifica que requirements.txt contenga las dependencias correctas"""
    if check_file_exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            content = f.read()
            missing = []
            for pkg in ["gunicorn", "psycopg2", "PyPDF2", "python-dotenv"]:
                if pkg not in content:
                    missing.append(pkg)
            
            if not missing:
                logger.info("✅ requirements.txt contiene todas las dependencias necesarias")
                return True
            else:
                logger.warning(f"⚠️ requirements.txt puede estar faltando: {', '.join(missing)}")
                return False
    return False

if __name__ == "__main__":
    logger = setup_logging()
    logger.info("=== Iniciando verificación pre-despliegue para ERC Insight ===")
    
    # Realizar todas las verificaciones
    critical_env, optional_env = check_env_vars()
    db_config_ok = check_database_config()
    wsgi_ok = check_gunicorn_wsgi()
    render_yaml_ok = check_render_yaml()
    runtime_ok = check_runtime_file()
    static_dirs_ok = check_static_dirs()
    requirements_ok = check_requirements()
    
    # Reportar resultados
    logger.info("\n=== Resultados de la verificación ===")
    logger.info(f"Variables críticas de entorno: {'✅' if critical_env else '❌'}")
    logger.info(f"Variables opcionales de entorno: {'✅' if optional_env else '⚠️'}")
    logger.info(f"Configuración de base de datos: {'✅' if db_config_ok else '⚠️'}")
    logger.info(f"Configuración WSGI: {'✅' if wsgi_ok else '❌'}")
    logger.info(f"Configuración render.yaml: {'✅' if render_yaml_ok else '⚠️'}")
    logger.info(f"Configuración runtime.txt: {'✅' if runtime_ok else '⚠️'}")
    logger.info(f"Directorios estáticos: {'✅' if static_dirs_ok else '⚠️'}")
    logger.info(f"Dependencias en requirements.txt: {'✅' if requirements_ok else '⚠️'}")
    
    # Determinar si todas las verificaciones críticas pasaron
    all_critical_passed = critical_env and wsgi_ok
    
    if all_critical_passed:
        logger.info("\n✅ Verificación completada con éxito")
        logger.info("   El sistema está listo para despliegue en Render.com")
        sys.exit(0)
    else:
        logger.error("\n❌ La verificación falló en aspectos críticos")
        logger.error("   Corrija los problemas antes de desplegar")
        sys.exit(1)
