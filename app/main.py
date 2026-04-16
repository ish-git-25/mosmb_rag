from fastapi import FastAPI
from app.rag_pipeline import rag_pipeline

app = FastAPI()

@app.post("/query")
def query(q: str):
    return rag_pipeline(q)