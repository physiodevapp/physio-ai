import os
import time
import redis

# Diferencia entre producción y desarrollo
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

TPM_LIMIT = 90000  # Tokens por minuto
VENTANA_TIEMPO = 60  # segundos

def puede_consumir_tokens(cantidad: int) -> bool:
    ahora = int(time.time())
    clave = f"tokens:{ahora // VENTANA_TIEMPO}"
    usados = int(redis_client.get(clave) or 0)
    
    if usados + cantidad > TPM_LIMIT:
        return False

    redis_client.incrby(clave, cantidad)
    redis_client.expire(clave, VENTANA_TIEMPO)
    return True
