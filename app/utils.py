import re

def clean_output(text):

    # 🔥 EXISTING LOGIC (UNCHANGED)
    garbage_phrases = [
        "Best regards",
        "I hope this helps",
        "Please let me know",
        "I will be happy to help",
        "Thank you"
    ]

    for g in garbage_phrases:
        text = text.replace(g, "")

    # 🔥 NEW — REMOVE PROMPT GARBAGE (ADDED)
    garbage_patterns = [
        r'please provide.*',
        r'your response.*',
        r'\*\*your response\*\*',
        r'based on the context.*',
        r'please follow.*',
        r'provide your response.*',
        r'here is the answer.*',
        r'answer:.*',
        r'response:.*',
        r'\*\*Response\*\*',
        r'Since the query type is \'general\', I\'ll provide a short direct answer.',
        r'\*\*Your Response\*\*',
        r'\*\*your answer\*\*',
        r'\*\*Your Answer\*\*',
        r'\*\*Answer\*\*',
        r'\*\*answer\*\*',
        r'\*\*Response\*\*',
        r'\*\*response\*\*',
        r'info:',
        r'\*\*END OF ANSWER\*\*',
        r'if I need any further assistance!',
        r'\(info\)',
        r'\*\*Output\*\*',
        r'\*\*output\*\*',
        r'Use simple language'
    ]

    for pattern in garbage_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # 🔥 NEW — REMOVE CODE BLOCKS (VERY IMPORTANT)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

    # 🔥 EXISTING LOGIC (UNCHANGED)
    lines = text.split("\n")
    seen = set()
    cleaned_lines = []

    for line in lines:
        line = line.strip()
        if line and line not in seen:
            cleaned_lines.append(line)
            seen.add(line)

    return "\n".join(cleaned_lines)

import re

def format_steps_output(text):

    lines = text.split("\n")

    cleaned = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # ❌ remove markdown headings / bold lines
        if "**" in line or "step-by-step" in line.lower():
            continue

        # ❌ remove existing numbering (1. , 2. , etc.)
        line = re.sub(r'^\d+\.\s*', '', line)

        # ❌ remove bullet points
        line = re.sub(r'^[-•]\s*', '', line)

        # keep only meaningful lines
        if len(line) > 20:
            cleaned.append(line)

    # ✅ rebuild clean numbered steps
    steps = []
    for i, line in enumerate(cleaned[:6], 1):
        steps.append(f"{i}. {line}")

    return "\n".join(steps)

import re

def clean_log_output(text):

    # remove code blocks safely
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

    # remove inline ```
    text = text.replace("```", "")

    # 🔥 KEEP ONLY STRUCTURED PART
    pattern = r"(Root Cause:.*?Final Solution:.*)"

    match = re.search(pattern, text, re.DOTALL)

    if match:
        text = match.group(1)

    # 🔥 CLEAN EXTRA LINES AFTER FINAL SOLUTION
    if "Final Solution:" in text:
        parts = text.split("Final Solution:")
        tail = parts[1].split("\n\n")[0]
        text = parts[0] + "Final Solution:" + tail

    return text.strip()
