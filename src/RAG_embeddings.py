import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import openai
from dotenv import load_dotenv

load_dotenv()

# Load and chunk the JSON data
def load_and_chunk_json(filepath, chunk_size=500):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    chunks = []
    metadata = []

    for title_key, title_content in data.items():
        title_name = title_content.get("name", f"Title {title_content.get('number', '')}")
        for art_num, article in title_content["articles"].items():
            content = ' '.join(article["content"].split())
            article_ref = f"{title_name} - Article {article['number']}"
            sentences = [s.strip() for s in content.split('.') if s.strip()]

            current_chunk = []
            current_length = 0
            for sentence in sentences:
                if current_length + len(sentence) > chunk_size and current_chunk:
                    chunks.append('. '.join(current_chunk) + '.')
                    metadata.append({
                        "source": article_ref,
                        "article_id": f"{title_key}_{art_num}",
                        "chunk_type": "sentence_group"
                    })
                    current_chunk = []
                    current_length = 0

                current_chunk.append(sentence)
                current_length += len(sentence)

            if current_chunk:
                chunks.append('. '.join(current_chunk) + '.')
                metadata.append({
                    "source": article_ref,
                    "article_id": f"{title_key}_{art_num}",
                    "chunk_type": "sentence_group"
                })

    return chunks, metadata

# Generate sentence embeddings
def generate_embeddings(texts, model_name):
    model = SentenceTransformer(model_name)
    return model.encode(texts, show_progress_bar=True)

# Build FAISS index
def build_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

# Semantic search
def search(query, model, index, texts, metadata, top_k=5):
    query_vec = model.encode([query])
    D, I = index.search(np.array(query_vec), top_k)
    results = [(texts[i], metadata[i]) for i in I[0]]
    return results

# Generate answer using OpenRouter
def generate_answer(query, results, api_key):
    openai.api_key = api_key
    openai.api_base = "https://openrouter.ai/api/v1"

    context = "\n".join([f"[{meta['source']}]: {txt}" for txt, meta in results])
    prompt = f"""Tu es un assistant expert de la Constitution Marocaine.Si la réponse n'est pas présente dans la constitution ecris clairement que le document ne supporte pas cette question  .de facon professionelle ,  Utilise les extraits suivants pour répondre selon la langue utilisée dans la question :

{context}

Question: {query}
Réponse:"""

    response = openai.ChatCompletion.create(
        model="mistralai/mistral-7b-instruct",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response["choices"][0]["message"]["content"]

# Terminal test
if __name__ == "__main__":
    chunks, metadata = load_and_chunk_json(r"data\morocco_constitution_clean.json", chunk_size=300)

    model_name = "sentence-transformers/all-mpnet-base-v2"
    print(f"Using embedding model: {model_name}")
    model = SentenceTransformer(model_name)
    embeddings = generate_embeddings(chunks, model_name)

    faiss_index = build_faiss_index(np.array(embeddings))

    query = "Quels sont les droits fondamentaux garantis par la constitution ?"
    results = search(query, model, faiss_index, chunks, metadata, top_k=4)

    for i, (text, meta) in enumerate(results):
        print(f"\nResult {i+1} - Source: {meta['source']}\n{text}")

    api_key = os.getenv("API_KEY")
    answer = generate_answer(query, results, api_key)
    print("API running", )
    print("\n🧠 Réponse Générée:\n", answer)
