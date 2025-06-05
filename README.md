# 🇲🇦 Moroccan Constitution QA - RAG App
#### This is an end of semester project
This project is a Retrieval-Augmented Generation (RAG) API built using FastAPI. It allows users to query the Moroccan Constitution using semantic search powered by SentenceTransformers and OpenAI's GPT.

---

## 🧠 Features

- Load and chunk articles from the Moroccan Constitution
- Perform semantic search using FAISS and sentence-transformers
- Generate contextual answers using OPENROUTER API (free)
- FastAPI backend for easy interaction
- frontend interface with streamlit 

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Badreddine-Chihab/RAG_constitution.git
cd RAG_constitution
```

```bash
pip install -r requirements.txt
```

Add Your OpenAI Key
Create a .env file in the root folder


### 2.RUN THE API
```bash
 python -m uvicorn src.rag_api:app --host 0.0.0.0 --port 8000 --reload
```
Check if API is up at: http://127.0.0.1:8000/health

### 3.🖥️ Run the Frontend (Streamlit)
If your Streamlit app is in streamlit_app.py, run:
in the root run 
```bash
 python -m streamlit run interface/streamlit_app/last.py
```









