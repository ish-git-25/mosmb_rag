memory = {
    "last_query": None,
    "last_answer": None,
    "last_context": None,
    "last_steps": None,

    # 🔥 NEW (DO NOT TOUCH OLD)
    "history": [],
    "max_size": 5
}

def update_history(query, answer, context):

    memory["history"].append({
        "query": query,
        "answer": answer,
        "context": context
    })

    # 🔥 sliding window
    if len(memory["history"]) > memory["max_size"]:
        memory["history"] = memory["history"][-memory["max_size"]:]

def enrich_query(query):

    q = query.lower()

    triggers = ["this", "that", "it", "those", "step", "explain", "why"]

    if not any(t in q for t in triggers):
        return query

    if not memory["history"]:
        return query

    last = memory["history"][-1]

    enriched = f"""
Previous Query:
{last['query']}

Previous Answer:
{last['answer']}

Current Query:
{query}
"""

    return enriched