from fastapi import FastAPI, Request
from pydantic import BaseModel
from src.RAG_embeddings import load_and_chunk_json, search, generate_answer
from sentence_transformers import SentenceTransformer
import numpy as np

app = FastAPI()

# Load data and model once at startup
# if id doesn't work check the path of the file it might need to be changed
chunks, metadata = load_and_chunk_json(r"data\morocco_constitution_clean.json", chunk_size=300)
model_name = "sentence-transformers/all-mpnet-base-v2"
model = SentenceTransformer(model_name)
embeddings = model.encode(chunks, show_progress_bar=True)
import faiss
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