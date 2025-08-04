# Guía de Despliegue en Render.com (Plan Gratuito)

Esta guía te ayudará a desplegar ERC Insight en Render.com utilizando exclusivamente los recursos gratuitos disponibles.

## Requisitos previos

1. Una cuenta en Render.com
2. Tu repositorio de GitHub con el código de ERC Insight

## Limitaciones del plan gratuito

Es importante conocer las limitaciones del plan gratuito de Render.com:

- Servicios web: Los servicios gratuitos se suspenden después de 15 minutos de inactividad
- Base de datos: Las bases de datos PostgreSQL gratuitas tienen un límite de 1GB de almacenamiento
- Todos los servicios gratuitos tienen recursos computacionales limitados
- Las bases de datos gratuitas se eliminan después de 90 días

## Pasos para el despliegue

### 1. Servicio Web (Frontend y Backend)

1. Inicia sesión en tu cuenta de Render.com
2. Ve a tu dashboard y haz clic en "New" y luego "Web Service"
3. Conecta tu repositorio de GitHub
4. Configura el servicio con los siguientes parámetros:
   - **Name**: erc-insight (o el nombre que prefieras)
   - **Environment**: Python
   - **Branch**: main (o la rama principal de tu repositorio)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app --log-file -`
   - **Plan**: Free

### 2. Base de datos PostgreSQL

1. En tu dashboard de Render.com, haz clic en "New" y luego "PostgreSQL"
2. Configura la base de datos con los siguientes parámetros:
   - **Name**: erc-database (o el nombre que prefieras)
   - **Database**: erc_database
   - **User**: (se generará automáticamente)
   - **Plan**: Free

### 3. Configuración de variables de entorno

Después de crear los servicios, necesitas configurar las variables de entorno para tu servicio web:

1. Ve a tu servicio web en el dashboard de Render.com
2. Haz clic en "Environment" en el menú lateral
3. Agrega las siguientes variables de entorno:
   - `DATABASE_URL`: (Copia la Internal Database URL de tu base de datos PostgreSQL)
   - `SECRET_KEY`: (Genera una clave secreta, puedes usar un generador online)
   - `GEMINI_API_KEY`: (Tu clave API de Google Gemini)
   - `FLASK_APP`: wsgi.py
   - `FLASK_ENV`: production

### 4. Actualización y mantenimiento

Para mantener activo tu servicio en el plan gratuito:

1. Configura un servicio de ping (como UptimeRobot) para hacer peticiones a tu aplicación cada 10-12 minutos
2. Esto evitará que el servicio se suspenda por inactividad

## Monitoreo y solución de problemas

1. Puedes ver los logs de tu aplicación en la sección "Logs" de tu servicio web
2. Si encuentras problemas, revisa la sección "Events" para ver eventos relacionados con tu servicio

## Consideraciones para producción

Si tu aplicación comienza a recibir tráfico significativo o necesitas mayor confiabilidad:

1. Considera actualizar a un plan pago para obtener mejor rendimiento y disponibilidad
2. Implementa un CDN para servir archivos estáticos
3. Configura respaldos regulares de la base de datos

## Alternativas gratuitas a Render.com

Si necesitas opciones completamente gratuitas para producción, considera:

1. **PythonAnywhere**: Ofrece un plan gratuito con algunas limitaciones
2. **Heroku**: Aunque ya no tiene plan gratuito, tiene opciones económicas
3. **Railway**: Ofrece un crédito mensual gratuito
4. **Fly.io**: Tiene un plan gratuito con límites generosos
