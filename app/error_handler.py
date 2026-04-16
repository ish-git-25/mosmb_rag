from app.database import collection
from app.model import tokenizer, llm
from app.utils import format_steps_output
from app.llm import generate_answer

def detect_intent(query):

    import re

    q = query.lower()

    # 1. Detect error codes (handles EC02010016, 02010016, logs)
    codes = re.findall(r'(?:EC)?([0-9]{8})', query.upper())
    codes = list(set(codes))

    if codes:
        return {
            "type": "error",
            "codes": codes
        }

    # 2. Detect log pattern
    if "[" in query and "]" in query and ("error" in q or "warn" in q):
        return {
            "type": "log",
            "codes": None
        }

    # 3. Detect semantic error queries (no code but error intent)
    if "error" in q or "failed" in q or "issue" in q:
        return {
            "type": "error_semantic",
            "codes": None
        }

    # 4. Default → documentation query
    return {
        "type": "doc",
        "codes": None
    }

import re

def extract_error_codes(text):

    # Step 1: normalize
    text = text.upper()

    # Step 2: extract all possible patterns
    patterns = [
        r'\b[0-9A-F]{8}\b',          # 02010016
        r'\bEC[0-9A-F]{8}\b',       # EC02010016
        r'\[EC[0-9A-F]{8}\]',       # [EC02010016]
        r'\[[0-9A-F]{8}\]'          # [02010016]
    ]

    matches = []

    for pattern in patterns:
        found = re.findall(pattern, text)
        matches.extend(found)

    # Step 3: clean results → always return pure 8-digit code
    cleaned = []

    for m in matches:
        code = re.sub(r'[^0-9A-F]', '', m)  # remove EC, [, ]
        if len(code) >= 8:
            cleaned.append(code[-8:])  # last 8 digits

    return list(set(cleaned)) if cleaned else None

def process_log_input(log_text):

    log_text_lower = log_text.lower()

    # ✅ USE ROBUST ERROR EXTRACTION (FIXED)
    codes = extract_error_codes(log_text)

    # 2. Extract severity-based lines (IMPORTANT)
    important_lines = []

    for line in log_text.split("\n"):
        if any(tag in line.upper() for tag in ["ERROR", "WARN"]):
            important_lines.append(line.strip())

    # 3. Extract keywords (signals)
    signals = []

    if "ldap" in log_text_lower:
        signals.append("LDAP failure")

    if "kerberos" in log_text_lower:
        signals.append("Kerberos issue")

    if "gssapi" in log_text_lower:
        signals.append("GSSAPI error")

    if "auth" in log_text_lower:
        signals.append("Authentication issue")

    # 4. Build structured query (ONLY for fallback use)
    structured_query = ""

    if signals:
        structured_query += "Issues detected: " + ", ".join(signals) + ". "

    if codes:
        structured_query += "Error codes: " + ", ".join(codes) + ". "

    structured_query += "Provide root cause and solution."

    # ⚠️ IMPORTANT CHANGE
    return log_text, codes, important_lines

def get_error_from_chroma_fast(code):

    result = collection.get(ids=[f"error_{code}"])

    if not result["ids"]:
        return None

    doc = result["documents"][0]
    meta = result["metadatas"][0]

    return {
        "error_codes": meta["error_codes"],
        "error_string": doc.split("Description:")[1].split("Solution:")[0].strip(),
        "category": meta["category"],
        "solution": doc.split("Solution:")[1].strip().split("\n"),
    }

def solve_error(query, codes):

    for code in codes:

        error = get_error_from_chroma_fast(code)

        if error:

            return {
                "type": "error",
                "data": error,
                "query": query
            }

    return None

def solve_log(query):

    structured_query, codes, important_lines = process_log_input(query)

    # 🔥 PRIORITY 1 → error codes inside logs
    if codes:
        result = solve_error(query, codes)
        if result:
            return result

    # 🔥 fallback → treat as semantic issue
    return {
        "type": "log",
        "query": structured_query,
        "signals": important_lines
    }

def generate_error_answer(error_obj):

    error = error_obj["data"]
    query = error_obj["query"]

    steps = [s.strip() for s in error["solution"] if s.strip()]

    context = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])

    prompt = f"""
You are a MoSMB support system.

STRICT RULES (NON-NEGOTIABLE):
- You MUST use ONLY the given solution steps
- You MUST NOT add any new steps
- You MUST NOT remove any step
- You MUST NOT add placeholders like "refer documentation"
- You MUST NOT ask user anything
- You MUST NOT add explanations unless explicitly asked

User Query:
{query}

Error Code: {", ".join(error['error_codes'])}
Description: {error['error_string']}

Official Steps:
{context}

TASK:
Return the SAME steps cleanly.

OUTPUT FORMAT:
1. step
2. step
3. step
"""

    answer = generate_answer(prompt)

    return format_steps_output(answer)
