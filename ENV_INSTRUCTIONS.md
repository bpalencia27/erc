# Variables de entorno para ERC Insight

Este archivo detalla las variables de entorno necesarias para ejecutar la aplicación ERC Insight, tanto en desarrollo local como en producción.

## Variables de entorno requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta para proteger sesiones | `clave-aleatoria-segura` |
| `DATABASE_URL` | URL de conexión a la base de datos | `postgresql://usuario:contraseña@host:puerto/nombre_db` |
| `GEMINI_API_KEY` | Clave API para Google Gemini | `su-clave-api-de-gemini` |
| `FLASK_APP` | Punto de entrada de la aplicación | `wsgi.py` |
| `FLASK_ENV` | Entorno (development, production) | `production` |

## Configuración en Render.com

En Render.com, las variables de entorno se configuran en la interfaz web o a través del archivo `render.yaml`.

Para `SECRET_KEY`, utiliza la opción de generar un valor aleatorio:
```yaml
- key: SECRET_KEY
  generateValue: true
```

Para la conexión a la base de datos, utiliza:
```yaml
- key: DATABASE_URL
  fromDatabase:
    name: erc-database
    property: connectionString
```

Para la clave API de Gemini, marca la opción como "no sincronizar" para proteger la clave:
```yaml
- key: GEMINI_API_KEY
  sync: false
```

## Seguridad

IMPORTANTE: Nunca incluyas el archivo `.env` en el control de versiones. Está configurado para ser ignorado en `.gitignore`.

Para desarrollo local, crea un archivo `.env` con estas variables. Para producción, configúralas en el proveedor de hosting (como Render.com).
