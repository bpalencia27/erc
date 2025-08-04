#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de ping para mantener activa la aplicación en Render.com
Este script puede ejecutarse desde un servicio externo como cron-job.org o UptimeRobot
para enviar pings periódicos a la aplicación y evitar que entre en hibernación.
"""

import argparse
import logging
import requests
import time
from datetime import datetime

def setup_logging():
    """Configura el logging para este script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("keep_alive.log")
        ]
    )
    return logging.getLogger("keep_alive")

def ping_app(url, timeout=10):
    """Envía un ping a la aplicación y verifica la respuesta"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            logger.info(f"✅ Ping exitoso a {url} - Tiempo de respuesta: {elapsed:.2f}s")
            return True
        else:
            logger.warning(f"⚠️ Ping a {url} retornó código {response.status_code} - Tiempo: {elapsed:.2f}s")
            return False
    except requests.RequestException as e:
        logger.error(f"❌ Error al enviar ping a {url}: {e}")
        return False

def keep_alive(url, interval=10, max_retries=3, timeout=10):
    """Envía pings periódicos a la aplicación"""
    logger.info(f"Iniciando servicio de keep-alive para {url}")
    logger.info(f"Intervalo entre pings: {interval} minutos")
    
    while True:
        success = False
        retries = 0
        
        while not success and retries < max_retries:
            success = ping_app(url, timeout)
            if not success:
                retries += 1
                logger.warning(f"Reintento {retries}/{max_retries} en 30 segundos...")
                time.sleep(30)
        
        if not success:
            logger.error(f"❌ No se pudo conectar a {url} después de {max_retries} intentos")
        
        # Registrar timestamp del próximo ping
        next_ping = datetime.now().timestamp() + (interval * 60)
        next_ping_time = datetime.fromtimestamp(next_ping).strftime('%H:%M:%S')
        logger.info(f"Próximo ping programado para las {next_ping_time}")
        
        # Esperar hasta el próximo intervalo
        time.sleep(interval * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script para mantener activa una aplicación en Render.com")
    parser.add_argument("url", help="URL de la aplicación a mantener activa")
    parser.add_argument("--interval", type=int, default=10, help="Intervalo entre pings en minutos (default: 10)")
    parser.add_argument("--retries", type=int, default=3, help="Número máximo de reintentos (default: 3)")
    parser.add_argument("--timeout", type=int, default=10, help="Tiempo de espera para cada ping en segundos (default: 10)")
    
    args = parser.parse_args()
    logger = setup_logging()
    
    try:
        keep_alive(args.url, args.interval, args.retries, args.timeout)
    except KeyboardInterrupt:
        logger.info("Servicio de keep-alive detenido manualmente")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
