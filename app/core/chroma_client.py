import os
from chromadb import Client, HttpClient
from chromadb.config import Settings

def get_chroma_client():
    """
    Devuelve el cliente Chroma adecuado según entorno:
    - LOCAL_MODE=1 → Usa HttpClient en localhost:8000
    - Otro caso → Usa Client embebido (modo producción o tests)
    """
    if os.getenv("LOCAL_MODE") == "1":
        print("🔌 Usando HttpClient (modo local)")
        return HttpClient(host="localhost", port=8000)
    
    print("💾 Usando Chroma embebido (modo producción)")
    return Client(Settings(
        persist_directory="chroma_db",  # Asegúrate de que este volumen exista en producción
        anonymized_telemetry=False
    ))
