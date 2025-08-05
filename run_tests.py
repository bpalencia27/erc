#!/usr/bin/env python
"""
Script para ejecutar pruebas sin necesidad de un archivo .env
"""
import os
import sys
import unittest

# Configurar variables de entorno para pruebas
os.environ['SECRET_KEY'] = 'clave-pruebas-12345'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['FLASK_ENV'] = 'testing'
os.environ['PYTEST_CURRENT_TEST'] = 'true'  # Esto evitará que se cargue .env

# Ejecutar pruebas
if __name__ == '__main__':
    tests = unittest.defaultTestLoader.discover('tests')
    result = unittest.TextTestRunner().run(tests)
    sys.exit(not result.wasSuccessful())
