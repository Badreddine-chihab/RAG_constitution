import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import openai
from dotenv import load_dotenv
import re

#Load and Chunk the Legal Text 
def load_and_chunk_json(filepath, chunk_size=500, overlap=100):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chunks = []
    metadata = []
    
    for title_key, title_content in data.items():
        title_name = title_content.get("name", f"Title {title_content.get('number', '')}")
        
        for art_num, article in title_content["articles"].items():
            content = article["content"]
            article_ref = f"{title_name} - Article {article['number']}"
            
            # Improved cleaning
            content = ' '.join(content.split())
            content = re.sub(r'\s+([.,;:])', r'\1', content)
            
            # Split into sentences while preserving legal references
            sentences = []
            temp_sentence = ""
            for char in content:
                temp_sentence += char
                if char in ['.', '!', '?']:
                    # Check if this might be part of a legal reference (e.g., Art. 12)
                    if len(temp_sentence) > 3 and not temp_sentence[-3:].lower().startswith('art'):
                        sentences.append(temp_sentence.strip())
                        temp_sentence = ""
            
            if temp_sentence:
                sentences.append(temp_sentence.strip())
            
            # Create chunks with overlap
            current_chunk = []
            current_length = 0
            prev_sentences = []
            
            for i, sentence in enumerate(sentences):
                if current_length + len(sentence) > chunk_size and current_chunk:
                    chunks.append(' '.join(current_chunk))
                    metadata.append({
                        "source": article_ref,
                        "article_id": f"{title_key}_{art_num}",
                        "chunk_type": "paragraph",
                        "full_article": content  # Store full article for context
                    })
                    
                    # Keep last few sentences for overlap
                    prev_sentences = current_chunk[-3:] if len(current_chunk) > 3 else current_chunk.copy()
                    current_chunk = prev_sentences.copy()
                    current_length = sum(len(s) for s in current_chunk)
                
                current_chunk.append(sentence)
                current_length += len(sentence)
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                metadata.append({
                    "source": article_ref,
                    "article_id": f"{title_key}_{art_num}",
                    "chunk_type": "paragraph",
                    "full_article": content
                })
    
    return chunks, metadata

# Improved Embeddings with model caching
MODEL_CACHE = {}

def generate_embeddings(texts, model_name):
    if model_name not in MODEL_CACHE:
        MODEL_CACHE[model_name] = SentenceTransformer(model_name)
    
    model = MODEL_CACHE[model_name]
    
    # Normalize texts for better embeddings
    normalized_texts = [re.sub(r'\s+', ' ', text.lower().strip()) for text in texts]
    embeddings = model.encode(normalized_texts, show_progress_bar=True, batch_size=32)
    return embeddings

# Improved FAISS index with normalization
def build_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    
    # Normalize vectors for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Use more efficient index type
    quantizer = faiss.IndexFlatL2(dimension)
    index = faiss.IndexIVFFlat(quantizer, dimension, min(100, len(embeddings)//4))
    index.train(embeddings)
    index.add(embeddings)
    return index

# Enhanced search with query expansion
def search(query, model, index, texts, metadata, top_k=5):
    # Basic query preprocessing
    query = query.lower().strip()
    
    # Simple query expansion for legal terms 
    #ici le plus le mieux pour faciliter au model la recherche malgre les synonymes
    legal_synonyms = {
        "religion": ["faith", "belief", "religious"],
        "state": ["country", "nation", "government"],
        "right": ["entitlement", "privilege", "freedom"],
        "citizen": ["national", "resident", "inhabitant"],
        "equality": ["fairness", "equity", "justice"],
        "law": ["legislation", "statute", "regulation"],
        "constitution": ["charter", "fundamental law", "basic law"],
        "monarchy": ["kingdom", "royalty", "crown"],
        "sovereignty": ["independence", "autonomy", "self-governance"],
        "government": ["administration", "executive", "authority"],
        "parliament": ["legislature", "assembly", "congress"],
        "rights": ["entitlements", "privileges", "freedoms"],
        "freedom": ["liberty", "autonomy", "independence"],
        "justice": ["fairness", "equity", "lawfulness"],
        "elections": ["voting", "polls", "referendum"],
        "democracy": ["republic", "popular rule", "self-governance"],
        "human rights": ["civil rights", "fundamental rights", "basic freedoms"],
        "social rights": ["welfare rights", "economic rights", "cultural rights"],
        "economic rights": ["property rights", "labor rights", "social security"],
        "cultural rights": ["cultural freedoms", "heritage rights", "identity rights"],
        "environmental rights": ["ecological rights", "sustainability rights", "nature rights"],
        "education": ["learning", "knowledge", "instruction"],
        "health": ["well-being", "medical care", "healthcare"],
        "privacy": ["personal space", "data protection", "confidentiality"],
        "freedom of speech": ["free expression", "speech rights", "expression freedoms"],
        "freedom of assembly": ["gathering rights", "assembly freedoms", "protest rights"],
        "freedom of association": ["group rights", "association freedoms", "collective rights"],
        "freedom of movement": ["travel rights", "mobility freedoms", "migration rights"],
        "freedom of religion": ["religious freedoms", "faith rights", "belief rights"],#etc
    }
    
    expanded_query = query
    for term, synonyms in legal_synonyms.items():
        if term in query:
            expanded_query += " " + " ".join(synonyms)
    
    # Get embeddings for both original and expanded query
    query_vec = model.encode([query, expanded_query])
    query_vec = np.mean(query_vec, axis=0, keepdims=True)
    
    # Search with higher recall
    D, I = index.search(query_vec, top_k*2)
    
    # Re-rank results using more sophisticated similarity
    results = []
    for i in I[0]:
        text = texts[i]
        meta = metadata[i]
        
        # Compute more sophisticated similarity score
        text_vec = model.encode([text])
        similarity = cosine_similarity(query_vec, text_vec)[0][0]
        
        results.append({
            "text": text,
            "metadata": meta,
            "score": similarity
        })
    
    # Sort by combined score
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

# Improved RAG answer generation
def generate_answer(query, results, api_key):
    openai.api_key = api_key
    
    # Build better context
    context_parts = []
    for i, result in enumerate(results):
        context_parts.append(
            f"SOURCE: {result['metadata']['source']}\n"
            f"CONTENT: {result['text']}\n"
            f"FULL_ARTICLE_CONTEXT: {result['metadata']['full_article'][:1000]}...\n"
        )
    
    context = "\n---\n".join(context_parts)
    
    # Better prompt engineering
    prompt = (
        "You are a legal expert analyzing Morocco's constitution. "
        "Answer the question precisely based on the provided legal texts. "
        "If the answer isn't found in the texts, say so.\n\n"
        "CONTEXT:\n{context}\n\n"
        "QUESTION: {query}\n\n"
        "Provide a detailed answer with exact legal references when possible. "
        "Structure your answer as:\n"
        "1. Direct answer\n"
        "2. Legal basis (quote exact articles)\n"
        "3. Explanation in simple terms\n"
        "ANSWER:"
    ).format(context=context, query=query)
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use more capable model
            messages=[
                {"role": "system", "content": "You are a legal assistant specializing in Moroccan constitutional law."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error generating answer: {str(e)}"



if __name__ == "__main__":
    # Load and chunk data
    chunks, metadata = load_and_chunk_json(
        r"D:\WORK\IDSCC3\NLProject\backend\data\morocco_constitution_clean.json",
        chunk_size=500,
        overlap=100
    )

    # Evaluate different models
    chosen_model_name = "nlpaueb/legal-bert-base-uncased"

    # Generate embeddings
    print(f"Using model: {chosen_model_name}")
    model = SentenceTransformer(chosen_model_name)
    embeddings = generate_embeddings(chunks, chosen_model_name)

    # Build FAISS index
    faiss_index = build_faiss_index(np.array(embeddings))

    #  query
    query = "What color is the emblem of the state ?"
    results = search(query, model, faiss_index, chunks, metadata, top_k=5)

    print("\nTop Results:")
    for i, result in enumerate(results):
        print(f"\nResult {i+1} - Score: {result['score']:.3f}")
        print(f"Source: {result['metadata']['source']}")
        print(f"Content: {result['text'][:200]}...")

    openai_api_key = "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"
    answer = generate_answer(query, results, openai_api_key)
    print("\n🧠 Réponse Générée:\n", answer)
