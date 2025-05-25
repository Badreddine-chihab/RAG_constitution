import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import openai

#Load and Chunk the Legal Text 
def load_and_chunk_json(filepath, chunk_size=300):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chunks = []
    metadata = []
    
    # Process each title (e.g., "Title 1", "Title 2")
    for title_key, title_content in data.items():
        title_name = title_content.get("name", f"Title {title_content.get('number', '')}")
        
        # Process each article within the title
        for art_num, article in title_content["articles"].items():
            content = article["content"]
            article_ref = f"{title_name} - Article {article['number']}"
            
            # Clean and normalize the content
            content = ' '.join(content.split())  # Remove extra whitespace
            
            # Split into sentences or logical chunks
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            
            # Create chunks preserving sentence boundaries
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
            
            # Add the last chunk for this article
            if current_chunk:
                chunks.append('. '.join(current_chunk) + '.')
                metadata.append({
                    "source": article_ref,
                    "article_id": f"{title_key}_{art_num}",
                    "chunk_type": "sentence_group"
                })
    
    return chunks, metadata

#Create Embeddings with Different Models
def generate_embeddings(texts, model_name):
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings

# Store Vectors in FAISS 
def build_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

#Semantic Search
def search(query, model, index, texts, metadata, top_k=5):
    query_vec = model.encode([query])
    D, I = index.search(np.array(query_vec), top_k)
    results = [(texts[i], metadata[i]) for i in I[0]]
    return results

# RAG-style Answer Generation 
def generate_answer(query, results, api_key):
    openai.api_key = api_key
    context = "\n".join([f"[{meta['source']}]: {txt}" for txt, meta in results])
    prompt = f"Réponds à la question suivante basée sur le texte suivant:\n{context}\n\nQuestion: {query}\nRéponse:"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]



if __name__ == "__main__":
    # Load and chunk data
    chunks, metadata = load_and_chunk_json(r"data\morocco_constitution_clean.json", chunk_size=300)

    # Evaluate different models
    models = ["sentence-transformers/all-MiniLM-L6-v2", "sentence-transformers/all-mpnet-base-v2", "nlpaueb/legal-bert-base-uncased"]
    chosen_model_name = models[1]  # Change to test others

    # Generate embeddings
    print(f"Using model: {chosen_model_name}")
    model = SentenceTransformer(chosen_model_name)
    embeddings = generate_embeddings(chunks, chosen_model_name)

    # Build FAISS index
    faiss_index = build_faiss_index(np.array(embeddings))

    #  query
    query = "What color is the emblem of the state ?"
    results = search(query, model, faiss_index, chunks, metadata, top_k=5)

    for i, (text, meta) in enumerate(results):
        print(f"\nResult {i+1} - Source: {meta['source']}\n{text}")

    openai_api_key = "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"
    answer = generate_answer(query, results, openai_api_key)
    print("\n🧠 Réponse Générée:\n", answer)

