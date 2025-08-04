#!/usr/bin/env python
"""
Script para generar un archivo .env vacío para Render.com
Este script crea un archivo .env vacío que se utilizará durante
el despliegue en Render.com. Las variables reales se configurarán
en el panel de control de Render.
"""

import os
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def create_empty_env():
    """Crea un archivo .env vacío con comentarios"""
    env_content = """# Este es un archivo .env vacío para despliegue en Render.com
# Las variables reales se configuran en el panel de Render.com

# FLASK_APP=wsgi.py
# FLASK_ENV=production
# SECRET_KEY=se-generará-automáticamente-en-render
# DATABASE_URL=se-configurará-automáticamente-en-render
# GEMINI_API_KEY=debe-configurarse-manualmente-en-render
"""

    with open('.env', 'w') as f:
        f.write(env_content)
    
    logger.info("✅ Archivo .env vacío creado con éxito")
    logger.info("ℹ️ Las variables reales se configurarán en el panel de Render.com")

if __name__ == "__main__":
    if os.path.exists('.env'):
        logger.warning("⚠️ Ya existe un archivo .env")
        overwrite = input("¿Desea sobrescribirlo? (s/n): ").lower()
        if overwrite == 's' or overwrite == 'si' or overwrite == 'yes':
            create_empty_env()
        else:
            logger.info("❌ Operación cancelada")
    else:
        create_empty_env()
