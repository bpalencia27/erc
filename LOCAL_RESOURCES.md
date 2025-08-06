# Archivos de Recursos Locales

Para cumplir con las reglas internas del proyecto que prohíben el uso de CDNs y referencias externas, es necesario agregar los siguientes archivos localmente:

## Archivos CSS
- `app/static/css/tailwind.min.css` - Descargado de [Tailwind CSS](https://tailwindcss.com/docs/installation) 
- `app/static/css/fonts.css` - Archivo con las fuentes Inter incrustadas
- `app/static/css/fontawesome.min.css` - Font Awesome 6.4.0 descargado

## Archivos JavaScript
- `app/static/js/pdf.min.js` - PDF.js versión 2.11.338
- `app/static/js/chart.js` - Chart.js 
- `app/static/js/chartjs-adapter-date-fns.js` - Adaptador de fechas para Chart.js

## Imágenes
- `app/static/img/cardiaia-logo.svg` - Logo de CardiaIA (crear un SVG simple)

## Instrucciones para agregar estos archivos

1. Crear los directorios necesarios si no existen:
   ```
   mkdir -p app/static/css
   mkdir -p app/static/js
   mkdir -p app/static/img
   ```

2. Descargar los archivos CSS y JavaScript necesarios desde sus fuentes oficiales y guardarlos en los directorios correspondientes.

3. Crear una versión simple del logo en SVG y guardarla como `app/static/img/cardiaia-logo.svg`.

## Nota Importante

Estos archivos deben ser agregados **localmente** sin hacer referencias a URLs externas en ningún momento. Todos los recursos deben estar contenidos dentro del repositorio para cumplir con las políticas de seguridad internas.
