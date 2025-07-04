from openai import OpenAI
import os
from typing import Optional
import tiktoken

client = OpenAI(api_key=os.getenv("PHYSIO_KEY"))

system_prompt = (
    "Eres un asistente experto en razonamiento clínico en fisioterapia. "
    "Tu tarea es interpretar la siguiente información clínica de un subgrupo de pacientes "
    "y ayudar al usuario a entenderla mejor, ofreciendo sugerencias clínicas claras y concisas. "
    "Evita lenguaje técnico excesivo. Sé didáctico y enfocado."
)

def contar_tokens(texto: str, modelo: str) -> int:
    """Devuelve el número de tokens de un texto dado para un modelo específico."""
    encoding = tiktoken.encoding_for_model(modelo)
    return len(encoding.encode(texto))

def enriquecer_con_chatgpt(
    modelo: str,
    pregunta: str, 
    contexto: str, 
    longitud: Optional[int] = None,
) -> str:
    try:
        user_prompt = (
            f"Consulta del usuario: {pregunta}\n\n"
            f"Información relevante del subgrupo:\n{contexto}\n\n"
            "Por favor, ofrece una explicación clínica basada en esta información."
        )

        mensajes = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Calcula los tokens ya utilizados
        tokens_usados = sum(
            contar_tokens(m["content"], modelo) 
            for m in mensajes
            if isinstance(m, dict) and "content" in m
        )

        if longitud is None:
            max_tokens = 500
        elif longitud == -1:
            max_tokens = max(100, 4096 - tokens_usados)
        else:
            max_tokens = longitud

        respuesta = client.chat.completions.create(
            model=modelo,
            messages=mensajes,
            temperature=0.3,  # o 0.2
            max_tokens=max_tokens, # 🔒 Limita la longitud de la respuesta
        )
        
        return {
            "razonamiento": respuesta.choices[0].message.content.strip(),
            "respuesta": respuesta
        }
    except Exception as e:
        return {
            "razonamiento": f"⚠️ Error al enriquecer con IA: {e}",
            "respuesta": None
        }
    

def enriquecer_con_historial_chatgpt(
    historial: list[dict],
    modelo: str,
    pregunta: str, 
    contexto: str, 
    longitud: Optional[int] = None,
) -> tuple[str, list[dict]]:
    try:
        user_prompt = (
            f"Consulta del usuario: {pregunta}\n\n"
            f"Información relevante del subgrupo:\n{contexto}\n\n"
            "Por favor, ofrece una explicación clínica basada en esta información."
        )

        # Prepara mensajes con historial + nuevo mensaje
        mensajes = [{"role": "system", "content": system_prompt}] + historial
        mensajes.append({"role": "user", "content": user_prompt})

        # Calcular tokens ya utilizados
        tokens_usados = sum(
            contar_tokens(m["content"], modelo) 
            for m in mensajes
            if isinstance(m, dict) and "content" in m
        )

        if longitud is None:
            max_tokens = 500
        elif longitud == -1:
            max_tokens = max(100, 4096 - tokens_usados)
        else:
            max_tokens = longitud  # asumimos que el usuario ya lo pasó como tokens

        respuesta = client.chat.completions.create(
            model=modelo,
            messages=mensajes,
            temperature=0.3,
            max_tokens=max_tokens,
        )

        content = respuesta.choices[0].message.content.strip()
        mensajes.append({
            "role": "assistant", 
            "content": content
        })

        return {
            "razonamiento": content,
            "historial": mensajes,
            "respuesta": respuesta
        }

    except Exception as e:
        return {
            "razonamiento": f"⚠️ Error al enriquecer con historial: {e}",
            "respuesta": None,
            "historial": historial  # devuelves el historial sin modificar
        }
