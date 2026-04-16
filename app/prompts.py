def classify_query_type(query):

    q = query.lower()

    if "how" in q or "configure" in q or "install" in q:
        return "how_to"

    if "error" in q or "failed" in q or "not working" in q:
        return "troubleshoot"

    if "what" in q or "where" in q:
        return "info"

    if "step" in q or "explain" in q:
        return "followup"

    return "general"

def build_doc_prompt(context, query):
    query_type = classify_query_type(query)

    return f"""
You are a MoSMB technical documentation assistant.

Your job:
Provide a clear, structured answer based ONLY on the given context.

STRICT RULES:
- Do NOT hallucinate
- Do NOT assume issues
- Do NOT add extra commentary
- Do NOT ask questions
- ONLY use relevant information
- IGNORE irrelevant lines from context

FORMAT RULE (MANDATORY):
- If the question is "how to" → output ONLY numbered steps
- Minimum 3 steps if applicable
- DO NOT add headings
- DO NOT number steps (system will format)
- Each step must be clear and actionable
- No paragraphs

QUERY TYPE: {query_type}

CONTEXT:
{context}

USER QUERY:
{query}

INSTRUCTIONS:

If QUERY TYPE = how_to:
→ Return ONLY actionable steps

If QUERY TYPE = troubleshoot:
→ Return:
Root Cause:
...

Solution:
- Step 1
- Step 2

If QUERY TYPE = info:
→ Return short direct answer (2–4 lines)

If QUERY TYPE = followup:
→ Explain ONLY the requested step clearly

OUTPUT:
"""