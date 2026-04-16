import chromadb
import json
from rank_bm25 import BM25Okapi

client = chromadb.PersistentClient(
    path="./data/chroma_db"
)

collection = client.get_or_create_collection(
    name="mosmb_docs_upt_01"
)

with open("./data/mosmb_final_chunks.json") as f:
    docs = json.load(f)

corpus = [d["text"] for d in docs]
tokenized_corpus = [doc.split() for doc in corpus]
bm25 = BM25Okapi(tokenized_corpus)