import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

from extraer_embeddings import extraer_texto_completo, dividir_por_subgrupos, generar_embeddings, guardar_resultado
from cargar_en_chroma import cargar_datos_en_chroma

def run_pipeline():
    print("📄 Extrayendo texto del PDF...")
    texto_total = extraer_texto_completo("app/data/Clasificacion_dolor_cervical_fisioterapia.pdf")

    print("🧠 Dividiendo por subgrupos...")
    fragmentos = dividir_por_subgrupos(texto_total)

    print("🔢 Generando embeddings...")
    embeddings = generar_embeddings(fragmentos)

    print("💾 Guardando resultados en JSON...")
    guardar_resultado(fragmentos, embeddings)

    print("📤 Cargando en ChromaDB...")
    cargar_datos_en_chroma()

    print("✅ Embeddings procesados y cargados con éxito.")

if __name__ == "__main__":
    run_pipeline()
