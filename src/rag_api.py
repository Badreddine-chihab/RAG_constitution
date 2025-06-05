from fastapi import FastAPI
from pydantic import BaseModel
from src.RAG_embeddings import (
    load_and_chunk_json,
    search,
    generate_answer,
    generate_embeddings,
    build_faiss_index
)
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv
import os
from pathlib import Path

api_key ="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" #routerapi because opeinai key is not free this one is used for deepseek
print("Api runnnig :",api_key)
app = FastAPI()


# Load data and model at startup
chunks, metadata = load_and_chunk_json("data/morocco_constitution_clean.json")
model_name = "sentence-transformers/all-mpnet-base-v2"
model = SentenceTransformer(model_name)
embeddings = generate_embeddings(chunks, model_name)
embeddings_np = np.array(embeddings)
faiss_index = build_faiss_index(embeddings_np)

# Define input schema for POST request
class QueryRequest(BaseModel):
    question: str

# Health check route
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running"}

# POST /query: accepts JSON {"question": "..."}
@app.post("/query")
def query_post(req: QueryRequest):
    if not req.question.strip():
        return {"answer": "⚠️ Veuillez poser une question.", "article": ""}

    results = search(req.question, model, faiss_index, chunks, metadata, top_k=4)
    if not results:
        return {"answer": "⚠️ Aucune information trouvée.", "article": ""}

    answer = generate_answer(req.question, results, api_key)
    article_refs = [f"{meta['source']}: {txt}" for txt, meta in results]
    article = "\n".join(article_refs)

    return {"answer": answer, "article": article}

# GET /query?question=...
@app.get("/query")
def query_get(question: str = ""):
    if not question.strip():
        return {"answer": "⚠️ Veuillez poser une question.", "article": ""}
    
    results = search(question, model, faiss_index, chunks, metadata, top_k=4)
    if not results:
        return {"answer": "⚠️ Aucune information trouvée.", "article": ""}
    
    answer = generate_answer(question, results, api_key)
    article_refs = [f"{meta['source']}: {txt}" for txt, meta in results]
    article = "\n".join(article_refs)

    return {"answer": answer, "article": article}
# This code is a FastAPI application that provides an API for querying a Moroccan Constitution dataset using RAG (Retrieval-Augmented Generation) techniques.