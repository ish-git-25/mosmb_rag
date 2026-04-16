from app.retrieval import *
from app.error_handler import *
from app.log_handler import *
from app.memory import *
from app.prompts import *
from app.llm import *
from app.utils import *
from app.error_handler import detect_intent
from app.log_handler import generate_log_answer

def rag_pipeline(query):

    original_query = query
    query = enrich_query(query)

    # FOLLOW-UP
    if any(k in query.lower() for k in ["step", "this", "that", "explain", "why"]):
        import re
        match = re.search(r'step\s*(\d+)', query.lower())

        if match and memory["last_steps"]:
            step_num = int(match.group(1))

            if step_num <= len(memory["last_steps"]):
                step_text = memory["last_steps"][step_num - 1]

                prompt = f"""
Explain this step clearly:

{step_text}

Rules:
- Be concise
- No extra info
"""
                return generate_answer(prompt)

    # LOG FLOW
    if "[" in query and "]" in query and ("ERROR" in query or "WARN" in query):
        answer = generate_log_answer(query)

        memory["last_steps"] = answer.split("\n")
        update_history(original_query, answer, "log")

        return answer

    # ERROR FLOW
    intent = detect_intent(query)

    if intent["type"] == "error":
        result = solve_error(query, intent["codes"])

        if result:
            answer = generate_error_answer(result)
            update_history(original_query, answer, "error")
            return answer

    # DOC FLOW
    docs = hybrid_retrieval(query)
    ranked_docs = rerank(query, docs)
    final_docs = clean_context(ranked_docs)

    context = ""
    sources = []

    for doc in final_docs:
        context += doc["text"] + "\n\n"
        if doc.get("source"):
            sources.append(doc["source"])

    prompt = build_doc_prompt(context, query)

    answer = generate_answer(prompt)
    answer = clean_output(answer)

    if "how" in query.lower():
        final_output = format_steps_output(answer)
    else:
        final_output = answer

    memory["last_steps"] = final_output.split("\n")
    update_history(original_query, final_output, context)

    return {
        "answer": final_output,
        "sources": list(set(sources))[:3]
    }