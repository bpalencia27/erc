# Guía de Despliegue en Render.com

Esta guía proporciona instrucciones paso a paso para desplegar ERC Insight en Render.com.

## Prerrequisitos

1. Una cuenta en [Render.com](https://render.com/)
2. Tu código subido a un repositorio GitHub
3. Todas las verificaciones de `check_deployment.py` pasadas correctamente

## Pasos para el Despliegue

### 1. Preparación del Repositorio

Asegúrate de que tu repositorio contenga los siguientes archivos:

- `render.yaml` - Configuración de servicios de Render
- `requirements.txt` - Dependencias de Python
- `runtime.txt` - Versión de Python (python-3.9.13)
- `.env.example` - Ejemplo de variables de entorno (NO incluir .env con credenciales reales)

### 2. Conectar GitHub a Render

1. Inicia sesión en [Render Dashboard](https://dashboard.render.com/)
2. Haz clic en "New" y luego en "Blueprint"
3. Conecta tu cuenta de GitHub si aún no lo has hecho
4. Selecciona el repositorio que contiene ERC Insight

### 3. Configuración del Blueprint

1. Render detectará automáticamente el archivo `render.yaml`
2. Verifica los servicios que se crearán:
   - Servicio web para la aplicación
   - Base de datos PostgreSQL
3. Haz clic en "Apply" para crear los servicios

### 4. Configuración de Variables de Entorno

Después de que los servicios se hayan creado:

1. Ve al servicio web de ERC Insight
2. Navega a la pestaña "Environment"
3. Asegúrate de que estas variables estén configuradas:
   - `SECRET_KEY` (Render lo genera automáticamente)
   - `DATABASE_URL` (Render lo configura automáticamente)
   - `GEMINI_API_KEY` (Debes configurarlo manualmente)
   - `FLASK_APP` = wsgi.py
   - `FLASK_ENV` = production

### 5. Inicialización de la Base de Datos

Después del primer despliegue exitoso:

1. Ve a la pestaña "Shell" del servicio web
2. Ejecuta los siguientes comandos:
   ```
   flask init-db
   flask create-admin admin tu_contraseña tu_email@ejemplo.com
   ```

### 6. Verificación del Despliegue

1. Una vez completado el despliegue, haz clic en la URL proporcionada
2. Asegúrate de que la aplicación se cargue correctamente
3. Intenta iniciar sesión con las credenciales de administrador

### 7. Configuración del Dominio Personalizado (Opcional)

1. Ve a la pestaña "Settings" del servicio web
2. En la sección "Custom Domain", haz clic en "Add"
3. Sigue las instrucciones para configurar tu dominio personalizado

## Solución de Problemas

### Error de Base de Datos

Si encuentras errores relacionados con la base de datos:

1. Ve a la pestaña "Logs" del servicio web
2. Busca errores específicos relacionados con la base de datos
3. Verifica que la variable `DATABASE_URL` esté configurada correctamente

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

## Escalamiento

Render.com ofrece opciones para escalar tu aplicación:

1. Ve a la pestaña "Settings" del servicio web
2. En la sección "Instance Type", selecciona un plan más potente según sea necesario
3. Puedes configurar escalado automático en planes de nivel superior

## Mantenimiento

### Actualizaciones de Código

Para actualizar tu aplicación:

1. Realiza cambios en tu repositorio de GitHub
2. Render detectará automáticamente los cambios y desplegará la nueva versión

### Copia de Seguridad de la Base de Datos

Render.com realiza copias de seguridad automáticas de la base de datos. Para restaurar:

1. Ve al servicio de base de datos
2. Navega a la pestaña "Backups"
3. Selecciona la copia de seguridad que deseas restaurar

## Monitoreo

Render proporciona herramientas de monitoreo:

1. Ve a la pestaña "Metrics" del servicio web
2. Puedes ver el uso de CPU, memoria y ancho de banda
3. Configura alertas para ser notificado sobre problemas

---

Para obtener ayuda adicional, consulta la [documentación oficial de Render](https://render.com/docs) o contacta a su soporte.
