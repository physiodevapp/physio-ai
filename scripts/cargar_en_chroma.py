import json
from app.core.chroma_client import get_chroma_client

from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

def cargar_datos_en_chroma():
    ruta_json = Path(__file__).resolve().parent.parent / "app" / "data" / "resultado_por_subgrupos.json"
    
    with open(ruta_json, encoding="utf-8") as f:
        datos = json.load(f)

    client = get_chroma_client()
    coleccion = client.get_or_create_collection("subgrupos_fisioterapia")

    def inferir_region(texto):
        texto = texto.lower()
        if "cervical" in texto or "cefalea" in texto:
            return "cuello"
        elif "hombro" in texto:
            return "hombro"
        elif "cadera" in texto:
            return "cadera"
        else:
            return "general"

    for i, item in enumerate(datos):
        coleccion.add(
            documents=[item["texto"]],
            embeddings=[item["embedding"]],
            ids=[f"subgrupo_{i+1}"],
            metadatas=[{"region": inferir_region(item["texto"])}]
        )

    print("✅ Datos cargados correctamente en chroma.")
