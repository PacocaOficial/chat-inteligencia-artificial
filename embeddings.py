"""
    Dividir contexto da IA em blocos para melhorar desenpenho.
    Esse método ainda não é utilizado
"""
import os
import json
from sentence_transformers import SentenceTransformer
import faiss

MODEL_PATH = "all-MiniLM-L6-v2"
INDEX_PATH = "base_faiss/index.index"

model = SentenceTransformer(MODEL_PATH)

def dividir_em_blocos(texto, tamanho=500):
    return [texto[i:i+tamanho] for i in range(0, len(texto), tamanho)]

# Gerar e salvar índice FAISS
def criar_ou_carregar_indice():
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
        with open("base_faiss/trechos.json", "r", encoding="utf-8") as f:
            trechos = json.load(f)
    else:
        with open("historia.txt", "r", encoding="utf-8") as f:
            historia = f.read()

        trechos = dividir_em_blocos(historia)
        embeddings = model.encode(trechos)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        faiss.write_index(index, INDEX_PATH)

        os.makedirs("base_faiss", exist_ok=True)
        with open("base_faiss/trechos.json", "w", encoding="utf-8") as f:
            json.dump(trechos, f, ensure_ascii=False)

    return index, trechos

index, trechos_salvos = criar_ou_carregar_indice()

# Buscar trechos mais relevantes
def buscar_trechos_relevantes(pergunta, k=3):
    pergunta_emb = model.encode([pergunta])
    _, indices = index.search(pergunta_emb, k)
    return "\n".join([trechos_salvos[i] for i in indices[0]])