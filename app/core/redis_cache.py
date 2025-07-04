import os
import time
import hashlib
from typing import Optional

import json

import hashlib

try:
    from redis import Redis
    REDIS_URL = os.getenv("REDIS_URL")
    REDIS_TOKEN = os.getenv("REDIS_TOKEN")
    redis_client = Redis.from_url(REDIS_URL, password=REDIS_TOKEN, decode_responses=True)
    redis_available = True
except Exception:
    print("⚠️ Redis no disponible. Usando fallback local.")
    redis_available = False
    redis_client = None
    local_cache = {}

def _make_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()

def get_cached_response(key: str) -> Optional[str]:
    hashed_key = _make_key(key)
    if redis_available:
        return redis_client.get(hashed_key)
    else:
        item = local_cache.get(hashed_key)
        if item:
            value, expiry = item
            if time.time() < expiry:
                return value
            else:
                del local_cache[hashed_key]  # remove expired
        return None

def set_cached_response(key: str, value: str, ttl_seconds: int = 60):
    hashed_key = _make_key(key)
    if redis_available:
        redis_client.setex(hashed_key, ttl_seconds, value)
    else:
        expiry = time.time() + ttl_seconds
        local_cache[hashed_key] = (value, expiry)

def store_in_cache_if_valid(cache_key, razonamiento, respuesta, modelo, ttl=600):
    if respuesta is None:
        return False
    set_cached_response(
        cache_key,
        json.dumps({
            "response": razonamiento,
            "modelo": modelo,
            "timestamp": time.time(),
            "tokens": {
                "input": respuesta.usage.prompt_tokens,
                "output": respuesta.usage.completion_tokens
            }
        }),
        ttl_seconds=ttl
    )
    return True

def generate_cache_key(*parts: str) -> str:
    """
    Genera una clave de caché segura a partir de cualquier número de partes de texto.
    """
    raw_key = "||".join(parts)  # separador seguro entre partes
    return hashlib.sha256(raw_key.encode()).hexdigest()

