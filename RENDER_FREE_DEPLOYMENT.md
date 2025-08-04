# Despliegue de ERC Insight en Render.com (Plan Gratuito)

Este documento proporciona instrucciones detalladas para desplegar ERC Insight en Render.com utilizando **exclusivamente el plan gratuito**.

## Contenido
1. [Preparación del Repositorio](#preparación-del-repositorio)
2. [Registro en Render.com](#registro-en-rendercom)
3. [Despliegue del Servicio Web](#despliegue-del-servicio-web)
4. [Configuración de Base de Datos](#configuración-de-base-de-datos)
5. [Configuración de Variables de Entorno](#configuración-de-variables-de-entorno)
6. [Verificación del Despliegue](#verificación-del-despliegue)
7. [Mantenimiento de la Aplicación Activa](#mantenimiento-de-la-aplicación-activa)
8. [Solución de Problemas](#solución-de-problemas)

## Preparación del Repositorio

Antes de desplegar, ejecuta el script de verificación pre-despliegue para asegurarte de que todo está correctamente configurado:

```bash
python pre_deploy_check.py
```

Si el script reporta algún problema, soluciónalo antes de continuar.

## Registro en Render.com

1. Crea una cuenta en [Render.com](https://render.com/)
2. Verifica tu correo electrónico y accede a tu dashboard

## Despliegue del Servicio Web

### Opción 1: Despliegue Manual

1. En tu dashboard de Render, haz clic en "New" y selecciona "Web Service"
2. Conecta tu repositorio de GitHub (deberás autorizar a Render para acceder a tus repositorios)
3. Configura los siguientes parámetros:
   - **Name**: erc-insight (o el nombre que prefieras)
   - **Environment**: Python
   - **Region**: Selecciona la más cercana a tus usuarios
   - **Branch**: main (o la rama principal de tu repositorio)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app --log-file -`
   - **Plan**: Free

### Opción 2: Despliegue con render.yaml

Si has actualizado el archivo render.yaml para usar el plan gratuito:

1. En tu dashboard de Render, haz clic en "New" y selecciona "Blueprint"
2. Selecciona tu repositorio de GitHub
3. Render detectará automáticamente el archivo render.yaml y configurará los servicios
4. Revisa la configuración y haz clic en "Apply"

## Configuración de Base de Datos

1. En tu dashboard de Render, haz clic en "New" y selecciona "PostgreSQL"
2. Configura los siguientes parámetros:
   - **Name**: erc-database (o el nombre que prefieras)
   - **Database**: erc_database
   - **User**: (se generará automáticamente)
   - **Region**: Selecciona la misma región que tu servicio web
   - **Plan**: Free
3. Haz clic en "Create Database"
4. Cuando se complete la creación, copia la "Internal Database URL"

## Configuración de Variables de Entorno

1. Ve a tu servicio web en el dashboard de Render
2. Haz clic en "Environment" en el menú lateral
3. Agrega las siguientes variables:
   - `DATABASE_URL`: (Pega la URL interna de tu base de datos PostgreSQL)
   - `SECRET_KEY`: (Genera una clave secreta aleatoria)
   - `GEMINI_API_KEY`: (Tu clave API de Google Gemini)
   - `FLASK_APP`: wsgi.py
   - `FLASK_ENV`: production
4. Haz clic en "Save Changes"

## Verificación del Despliegue

1. Espera a que el despliegue se complete (esto puede tomar varios minutos)
2. Haz clic en la URL proporcionada por Render para acceder a tu aplicación
3. Verifica que la aplicación se cargue correctamente
4. Prueba las funcionalidades principales

## Mantenimiento de la Aplicación Activa

En el plan gratuito de Render, los servicios web se suspenden después de 15 minutos de inactividad. Para mantener la aplicación activa:

### Opción 1: Uso de servicios de monitoreo externos

Configura un servicio gratuito como [UptimeRobot](https://uptimerobot.com/) o [Cron-job.org](https://cron-job.org/) para hacer ping a tu aplicación cada 10-12 minutos.

### Opción 2: Script de keep-alive personalizado

Puedes ejecutar el script `keep_alive.py` en un servidor externo (como una Raspberry Pi o una VPS):

```bash
python keep_alive.py https://tu-app.onrender.com --interval 10
```

## Solución de Problemas

### Error de Base de Datos

Si encuentras errores relacionados con la base de datos:

1. Ve a la pestaña "Logs" del servicio web
2. Busca errores específicos relacionados con la base de datos
3. Verifica que la variable `DATABASE_URL` esté configurada correctamente
4. Asegúrate de que la URL comience con `postgresql://` (no `postgres://`)

### Error de Aplicación

Si la aplicación no se inicia:

1. Ve a la pestaña "Logs" del servicio web
2. Busca errores específicos relacionados con la aplicación
3. Verifica que todas las variables de entorno estén configuradas correctamente

### Problemas con Google Gemini API

Si las funcionalidades de IA no funcionan:

1. Verifica que la variable `GEMINI_API_KEY` esté configurada correctamente
2. Asegúrate de que la clave API tenga los permisos adecuados
3. Verifica los registros para errores específicos de la API

## Limitaciones del Plan Gratuito

Es importante conocer las limitaciones del plan gratuito de Render.com:

- **Hibernación**: Los servicios web gratuitos se suspenden después de 15 minutos de inactividad
- **Rendimiento**: Menor capacidad de procesamiento y memoria RAM
- **Base de datos**: Las bases de datos PostgreSQL gratuitas tienen un límite de 1GB de almacenamiento
- **Eliminación**: Las bases de datos gratuitas se eliminan después de 90 días si no se actualizan a un plan pago
- **Ancho de banda**: Limitado a 100GB por mes

## Transición a Plan Pago

Si decides actualizar a un plan pago en el futuro, puedes hacerlo directamente desde el dashboard de Render sin necesidad de reconfigurar tu aplicación.
