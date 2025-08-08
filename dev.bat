@echo off
echo 🚀 Iniciando ERC Insight en modo desarrollo...

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Verificar dependencias
echo 🔍 Verificando dependencias...
python -c "import flask, flask_cors, werkzeug, dotenv; print('✅ Dependencias OK')" || goto :error

REM Cargar variables de entorno y ejecutar
echo 🌐 Iniciando servidor de desarrollo...
set FLASK_ENV=development
set FLASK_DEBUG=1
python run.py

goto :end

:error
echo ❌ Error: Ejecuta primero 'python setup.py' para instalar dependencias
pause

:end
