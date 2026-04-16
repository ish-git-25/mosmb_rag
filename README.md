# MoSMB RAG Support System

## Overview

This project is a Retrieval-Augmented Generation (RAG) based backend system designed for MoSMB technical support.

It supports three types of queries:

- **Documentation Queries** → Retrieves structured answers with citations  
- **Error Code Queries** → Returns exact solutions from error database  
- **Log Analysis Queries** → Analyzes multi-line logs to identify root cause, failure flow, and resolution  

Additional capabilities:
- Multi-turn conversation memory (last 5 interactions)
- Step-level follow-up explanations
- Source attribution for documentation answers

---

## Project Structure
mosmb_rag/
│
├── app/
│ ├── init.py
│ ├── main.py # FastAPI entry point
│ ├── rag_pipeline.py # Core pipeline logic
│ ├── retrieval.py # Vector + BM25 + hybrid retrieval
│ ├── error_handler.py # Error detection & resolution
│ ├── log_handler.py # Log parsing + reasoning
│ ├── memory.py # Conversation memory (sliding window)
│ ├── prompts.py # Prompt templates
│ ├── model.py # LLM + embeddings loading
│ ├── database.py # ChromaDB + BM25 setup
│ ├── utils.py # Cleaning, formatting utilities
│
├── data/
│ ├── mosmb_final_chunks.json # Processed documentation chunks
│ ├── chroma_db/ # Persistent vector database
│
├── test.py # Testing script for pipeline
├── requirements.txt # Python dependencies
├── README.md # Project documentation
├── .env # Environment variables (HF_TOKEN)
├── .gitignore # Ignore secrets and cache

## Setup Instructions

### 1. Clone Repository


git clone <your_repo_url>
cd mosmb_rag


---

### 2. Install Dependencies


pip install -r requirements.txt


---

### 3. Configure Environment Variables

Create a `.env` file in the root directory:


HF_TOKEN=your_huggingface_token_here


---

## Running the System

### Run API Server


uvicorn app.main:app --host 0.0.0.0 --port 8000


---

### Test API (example)


curl -X POST http://localhost:8000/query

-H "Content-Type: application/json"
-d '{"q":"How to configure kerberos?"}'


---

### Run Local Tests


python test.py


---

## Query Types Supported

### 1. Documentation Query
Example:

How to configure kerberos?


---

### 2. Error Query
Example:

I am facing EC02010016 error


---

### 3. Log Query
Example:

[MO_ERROR]:[EC02010016]: Failed getpwnam


---

## System Architecture (High-Level)

1. Query → Intent Detection  
2. Route to:
   - Retrieval pipeline (docs)
   - Error DB lookup
   - Log analysis engine  
3. Context building  
4. LLM generation (controlled)  
5. Output formatting + sources  

---

## Notes

- LLM runs locally using HuggingFace models
- ChromaDB is used for vector storage
- BM25 is used for keyword-based retrieval
- Hybrid retrieval improves accuracy
- Memory stores last 5 interactions (sliding window)

---

## Security

- HuggingFace token is stored in `.env`
- `.env` is excluded via `.gitignore`
- No secrets are hardcoded

---