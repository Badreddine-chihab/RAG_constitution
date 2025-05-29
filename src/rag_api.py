from fastapi import FastAPI, Request
from pydantic import BaseModel
from src.RAG_embeddings import load_and_chunk_json, search, generate_answer
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

app = FastAPI()

# Load data and model once at startup
# if id doesn't work check the path of the file it might need to be changed
chunks, metadata = load_and_chunk_json(r"data\morocco_constitution_clean.json", chunk_size=300)
model_name = "sentence-transformers/all-mpnet-base-v2" #best model after tests 
model = SentenceTransformer(model_name)
embeddings = model.encode(chunks, show_progress_bar=True)

faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
faiss_index.add(np.array(embeddings))

class QueryRequest(BaseModel):
    question: str


@app.post("/query")
def query_endpoint(req: QueryRequest):
    results = search(req.question, model, faiss_index, chunks, metadata, top_k=5)
    print("DEBUG RESULTS:", results)
    answer = results[0][0] if results else "No answer found."
    article = results[0][1]['source'] if results else ""
    return {"answer": answer, "article": article}

@app.post("/")
def read_root() :
    return {"message": "Welcome to the RAG API. Use the /query endpoint to ask questions."}
# RAG API using FastAPI
# en general :
# This code sets up a FastAPI application that allows users to ask a RAG (Retrieval-Augmented Generation) system.
# It loads a JSON file (cleaned in extract_clean file), chunks the text, generates embeddings, and allows for semantic search and answer generation.
