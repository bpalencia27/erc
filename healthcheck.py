#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Healthcheck para ERC Insight
Este script realiza una verificación del estado de la aplicación
"""

import os
import requests
from datetime import datetime
import logging
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("healthcheck.log")
    ]
)
logger = logging.getLogger("healthcheck")

def check_api_health(url, timeout=5):
    """Verifica el estado de la API"""
    try:
        health_url = f"{url.rstrip('/')}/api/health"
        logger.info(f"Verificando estado de la API en: {health_url}")
        
        response = requests.get(health_url, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                logger.info(f"✅ API operativa: {data.get('message', 'Sin mensaje')}")
                return True
            else:
                logger.warning(f"⚠️ API responde con estado inválido: {data}")
                return False
        else:
            logger.error(f"❌ Error de API: Status code {response.status_code}")
            return False
    except requests.RequestException as e:
        logger.error(f"❌ Error de conexión: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Verificador de estado para ERC Insight")
    parser.add_argument("url", nargs="?", default="http://localhost:5000", 
                        help="URL de la aplicación (default: http://localhost:5000)")
    args = parser.parse_args()
    
    logger.info(f"=== Iniciando verificación de estado para ERC Insight ===")
    success = check_api_health(args.url)
    
    if success:
        logger.info("✅ Verificación completada con éxito")
        sys.exit(0)
    else:
        logger.error("❌ Verificación fallida")
        sys.exit(1)
