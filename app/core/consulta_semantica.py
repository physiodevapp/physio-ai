from chromadb import HttpClient
import argparse

def buscar_subgrupos(
    consulta, 
    region=None, 
    umbral=0.6, 
    max_resultados=3,
):
    client = HttpClient(host="localhost", port=8000)
    coleccion = client.get_collection("subgrupos_fisioterapia")

    filtro = {"region": region} if region else None

    resultado = coleccion.query(
        query_texts=[consulta],
        n_results=max_resultados,
        where=filtro
    )

    resultados_utiles = []
    for i, (id, texto, metadata, distancia) in enumerate(zip(
        resultado["ids"][0],
        resultado["documents"][0],
        resultado["metadatas"][0],
        resultado["distances"][0]
    )):
        similitud = 1 - distancia
        if similitud < umbral:
            continue

        resultados_utiles.append({
            "id": id,
            "region": metadata.get("region", "desconocida"),
            "similitud": round(similitud, 4),
            "texto": texto
        })

    return resultados_utiles

# Si se ejecuta como script desde terminal
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Buscar subgrupos clínicos por similitud semántica.")
    parser.add_argument("consulta", type=str, help="Consulta clínica o síntomas del paciente.")
    parser.add_argument("--region", type=str, default=None, help="Región anatómica (opcional, ej: cuello, hombro).")
    parser.add_argument("--umbral", type=float, default=0.6, help="Similitud mínima (0.0 a 1.0)")
    parser.add_argument("--max_resultados", type=int, default=10, help="Número máximo de resultados")
    parser.add_argument("--limite_caracteres", type=int, default=100, help="Máximo de caracteres (usa -1 para todo el texto)")

    args = parser.parse_args()
    resultados = buscar_subgrupos(args.consulta, args.region, args.umbral, args.max_resultados)

    print(f"\n🔍 Consulta: {args.consulta}")
    print(f"📍 Región: {args.region or 'todas'}")
    print(f"📏 Umbral de similitud: {args.umbral}\n")

    if not resultados:
        print("⚠️  No se encontraron resultados relevantes.")
    else:
        for i, r in enumerate(resultados, start=1):
            if args.limite_caracteres == -1:
                resumen = r["texto"]
            elif len(r["texto"]) > args.limite_caracteres and args.limite_caracteres > 0:
                resumen = r["texto"][:args.limite_caracteres] + "..."
            else:
                resumen = r["texto"]

            resumen = resumen.replace("\n", " ")
            print(f"🔸 Resultado {i}:")
            print(f"   📌 ID: {r['id']}")
            print(f"   🏷️  Región: {r['region']}")
            print(f"   📏 Similitud: {r['similitud']}")
            print(f"   📄 Texto: {resumen}\n")
