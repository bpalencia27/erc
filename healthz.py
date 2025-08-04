from flask import jsonify
from app import create_app

# Crear la aplicación Flask
app = create_app('production')

@app.route('/healthz')
def health_check():
    """Endpoint para health check de Render.com"""
    return jsonify({
        "status": "ok",
        "message": "ERC Insight está en funcionamiento"
    })

if __name__ == '__main__':
    app.run(debug=False)
