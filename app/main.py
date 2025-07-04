from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Literal

from core.consulta_semantica import buscar_subgrupos
from core.chatgpt_utils import enriquecer_con_chatgpt, enriquecer_con_historial_chatgpt, contar_tokens

from core.limite_tokens import puede_consumir_tokens
from core.redis_cache import get_cached_response, set_cached_response, store_in_cache_if_valid, generate_cache_key

import time
import json

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Middleware CORS (Netlify o local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConsultaRequest(BaseModel):
    message: str
    enriquecer: Optional[bool] = False
    umbral: Optional[float] = 0.6
    max: Optional[int] = 3
    longitud: Optional[int] = None
    historial: Optional[List[Dict[str, str]]] = None  # 🧠 nuevo campo opcional
    model: Optional[Literal[
       "gpt-3.5-turbo-0125",
       "o4-mini-2025-04-16"
    ]] = "gpt-3.5-turbo-0125"

@app.post("/consulta")
def consulta_endpoint(data: ConsultaRequest):
    resultados = buscar_subgrupos(
        consulta=data.message,
        region="cuello",
        umbral=data.umbral,
        max_resultados=data.max,
    )

    # 🧠 CASO 1: No hay resultados, pero hay historial e IA activada → usa el historial
    if not resultados and data.enriquecer and data.historial:
        cache_key = generate_cache_key(data.message, "sin-contexto")
        cached = get_cached_response(cache_key)

        if cached:
            try:
                cached_data = json.loads(cached)
                razonamiento = cached_data["respuesta"]
            except (json.JSONDecodeError, KeyError):
                razonamiento = cached  # fallback por si hay caché vieja o corrupta

            return {
                "response": "No se encontraron resultados relevantes.",
                "ia": cached_data["respuesta"],
                "historial": data.historial,
            }

        resultado_api = enriquecer_con_historial_chatgpt(
            historial=data.historial,
            modelo=data.model,
            pregunta=data.message,
            contexto="No se encontraron datos relevantes del subgrupo.",
            longitud=data.longitud,
        )
        razonamiento = resultado_api["razonamiento"]
        nuevo_historial = resultado_api["historial"]
        respuesta = resultado_api["respuesta"]

        set_cached_response(
            cache_key,
            json.dumps({
                "response": razonamiento,
                "modelo": data.model,
                "timestamp": time.time(),
                "tokens": {
                    "input": respuesta.usage.prompt_tokens,
                    "output": respuesta.usage.completion_tokens
                }
            }),
            ttl_seconds=600
        )

        return {
            "response": "No se encontraron resultados relevantes.",
            "ia": razonamiento,
            "historial": nuevo_historial,
        }


    # ❌ CASO 2: No hay resultados, no hay historial, IA está activa → responde sin IA
    if not resultados:
        return {"response": "No se encontraron resultados relevantes."}

    # ✅ CASO 3: Hay resultados → genera resumen y evalúa IA
    resumen = "\n\n".join([
        f"🔹 Similitud: {r['similitud']}\n📄 {r['texto'][:100]}..."
        for r in resultados
    ])

    if data.enriquecer:
        tokens_estimados = contar_tokens(data.message, data.model) + contar_tokens(resultados[0]["texto"], data.model)

        if not puede_consumir_tokens(tokens_estimados):
            return {
                "response": resumen,
                "ia": "⚠️ Se ha alcanzado el límite de uso. Inténtalo más tarde.",
                "historial": data.historial,
            }

        cache_key = generate_cache_key(data.message, resultados[0]['texto'])
        cached = get_cached_response(cache_key)

        if cached:
            try:
                cached_data = json.loads(cached)
                razonamiento = cached_data["respuesta"]
            except (json.JSONDecodeError, KeyError):
                razonamiento = cached  # fallback por si hay caché vieja o corrupta

            return {
                "response": resumen,
                "ia": razonamiento,
                "historial": data.historial if data.historial else None,
            }

        # ➕ Enriquecimiento según si hay historial o no
        if data.historial:
            resultado_api = enriquecer_con_historial_chatgpt(
                historial=data.historial,
                modelo=data.model,
                pregunta=data.message,
                contexto=resultados[0]["texto"],
                longitud=data.longitud,
            )
            razonamiento = resultado_api["razonamiento"]
            nuevo_historial = resultado_api["historial"]
            respuesta = resultado_api["respuesta"]

            store_in_cache_if_valid(cache_key, razonamiento, respuesta, data.model)

            return {
                "response": resumen,
                "ia": razonamiento,
                "historial": nuevo_historial
            }
        else:
            resultado_api = enriquecer_con_chatgpt(
                modelo=data.model,
                pregunta=data.message,
                contexto=resultados[0]["texto"],
                longitud=data.longitud,
            )
            razonamiento = resultado_api["razonamiento"]
            respuesta = resultado_api["respuesta"]

            store_in_cache_if_valid(cache_key, razonamiento, respuesta, data.model)

            return {
                "response": resumen,
                "ia": razonamiento,
            }

    # 🟨 CASO 4: IA no activada, solo devolver resumen
    return {"response": resumen}
