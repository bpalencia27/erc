# app/api/report_cache.py
import redis
import json
from datetime import timedelta
from flask import current_app

class ReportCache:
    def __init__(self):
        self.redis_client = self._get_redis_client()
    
    def _get_redis_client(self):
        """Obtiene cliente Redis con fallback a memoria"""
        try:
            redis_url = current_app.config.get('REDIS_URL', 'redis://localhost:6379')
            return redis.from_url(redis_url, decode_responses=True)
        except:
            # Fallback a cache en memoria
            return None
    
    def get_report(self, report_id: str):
        """Obtiene informe cacheado"""
        if not self.redis_client:
            return None
        
        try:
            data = self.redis_client.get(f"report:{report_id}")
            return json.loads(data) if data else None
        except:
            return None
    
    def cache_report(self, report_id: str, report_data: dict, ttl: int = 3600):
        """Cachea informe por 1 hora por defecto"""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.setex(
                f"report:{report_id}",
                ttl,
                json.dumps(report_data)
            )
        except:
            pass

# Actualizar en routes.py
@api_bp.route('/generate_report', methods=['POST'])
def generate_report():
    cache = ReportCache()
    
    # Verificar cache primero
    cache_key = generate_cache_key(request.json)
    cached = cache.get_report(cache_key)
    if cached:
        return jsonify(cached)
    
    # Generar informe...
    result = generate_report_logic(request.json)
    
    # Cachear resultado
    cache.cache_report(cache_key, result)
    
    return jsonify(result)