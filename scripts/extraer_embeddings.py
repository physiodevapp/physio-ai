import fitz
import re
import json
from sentence_transformers import SentenceTransformer

# Cargar modelo
modelo = SentenceTransformer('all-MiniLM-L6-v2')

# Extraer texto completo
def extraer_texto_completo(ruta_pdf):
    with fitz.open(ruta_pdf) as doc:
        return "\n".join([pagina.get_text() for pagina in doc])

# Dividir por subgrupos clínicos
def dividir_por_subgrupos(texto):
    bloques = re.split(r"(Subgrupo\s+\d+:.*?)\n", texto, flags=re.DOTALL)
    fragmentos = []
    for i in range(1, len(bloques), 2):
        titulo = bloques[i].strip()
        contenido = bloques[i + 1].strip() if (i + 1) < len(bloques) else ""
        fragmentos.append(f"{titulo}\n{contenido}")
    return fragmentos

# Generar embeddings
def generar_embeddings(fragmentos):
    return modelo.encode(fragmentos, show_progress_bar=True)

# Guardar resultados
def guardar_resultado(fragmentos, embeddings):
    datos = [{"texto": t, "embedding": e.tolist()} for t, e in zip(fragmentos, embeddings)]
    with open("resultado_por_subgrupos.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

# Ejecución
if __name__ == "__main__":
    pdf = "Clasificacion_dolor_cervical_fisioterapia.pdf"
    texto_total = extraer_texto_completo(pdf)
    fragmentos = dividir_por_subgrupos(texto_total)
    embeddings = generar_embeddings(fragmentos)
    guardar_resultado(fragmentos, embeddings)
