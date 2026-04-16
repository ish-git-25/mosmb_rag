from app.database import collection, docs, bm25
from app.model import embedding_model, reranker
from app.model import reranker

def vector_search(query):

    query_embedding = embedding_model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=10,
        where={"type": "doc"},
        include=['documents', 'metadatas']   # 🔥 ADD THIS
    )

    retrieved_docs = []

    for doc_text, metadata in zip(
        results["documents"][0],
        results["metadatas"][0]
    ):
        retrieved_docs.append({
            "text": doc_text,
            "source": metadata.get("source", "")
        })

    return retrieved_docs

def bm25_search(query):

    tokenized_query = query.split()

    scores = bm25.get_scores(tokenized_query)

    top_n_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )[:10]

    return [
        {
            "text": docs[i]["text"],
            "source": docs[i]["url"]
        }
        for i in top_n_indices
    ]


def hybrid_retrieval(query):

    vec_docs = vector_search(query)
    bm_docs = bm25_search(query)

    seen = set()
    combined = []

    for doc in vec_docs + bm_docs:

        key = doc["text"].strip().lower()

        if key not in seen:
            seen.add(key)
            combined.append(doc)

    return combined[:20]

def rerank(query, docs):

    pairs = [[query, doc["text"]] for doc in docs]

    scores = reranker.predict(pairs)

    ranked = sorted(
        zip(scores, docs),
        reverse=True
    )

    filtered = []

    for score, doc in ranked:
        if score > 0.3:
            filtered.append(doc)

    if len(filtered) < 3:
        filtered = [doc for _, doc in ranked[:5]]

    return filtered[:5]

def clean_context(docs):

    seen = set()
    cleaned = []

    for doc in docs:

        # 🔥 HANDLE BOTH CASES (IMPORTANT FIX)
        if isinstance(doc, str):
            text = doc.strip()
            source = ""
        else:
            text = doc.get("text", "").strip()
            source = doc.get("source", "")

        # remove junk
        if len(text) < 50:
            continue

        key = text.lower()

        if key not in seen:
            seen.add(key)

            cleaned.append({
                "text": text,
                "source": source
            })

    return cleaned[:5]  