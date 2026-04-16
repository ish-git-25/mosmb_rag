from app.error_handler import extract_error_codes, get_error_from_chroma_fast

def parse_log_events(log_text):

    events = []

    lines = log_text.split("\n")

    for line in lines:

        line = line.strip()
        if not line:
            continue

        codes = extract_error_codes(line)

        events.append({
            "raw": line,
            "codes": codes
        })

    return events

def infer_root_cause(events):

    codes = []
    for e in events:
        if e["codes"]:
            codes.extend(e["codes"])

    # frequency based root cause
    from collections import Counter
    freq = Counter(codes)

    most_common = freq.most_common(1)

    return most_common[0][0] if most_common else None

def build_log_context(events):

    context = []

    for e in events:
        if e["error"]:

            context.append({
                "code": e["error"]["error_codes"][0],
                "desc": e["error"]["error_string"],
                "solution": e["error"]["solution"]   # 🔥 FULL SOLUTION (not [:2])
            })

    return context

def generate_log_answer(log_text):

    # STEP 1 — parse events
    events_raw = parse_log_events(log_text)

    events = []

    for e in events_raw:

        error_data = None

        if e["codes"]:
            for code in e["codes"]:
                result = get_error_from_chroma_fast(code)
                if result:
                    error_data = result
                    break

        events.append({
            "log": e["raw"],
            "codes": e["codes"],
            "error": error_data
        })

    # STEP 2 — ROOT CAUSE
    root_code = infer_root_cause(events)

    root_error = None
    if root_code:
        root_error = get_error_from_chroma_fast(root_code)

    # STEP 3 — CLEAN TIMELINE (REMOVE NOISE)
    timeline = []
    step_id = 1

    for e in events:

        # skip useless info logs
        if not e["error"] and not e["codes"]:
            continue

        if e["error"]:
            line = e["error"]["error_string"]
        else:
            continue

        timeline.append(f"{step_id}. {line}")
        step_id += 1

    # STEP 4 — CONTEXT (REMOVE LIMIT INSIDE THAT FUNCTION TOO)
    context = build_log_context(events)   # make sure NO [:5] inside it

    # STEP 5 — FINAL SOLUTION (FILTER EMPTY + DEDUP)
    seen = set()
    final_steps = []

    for c in context:
        for step in c["solution"]:
            step = step.strip()

            # remove garbage / empty steps
            if not step or len(step) < 5:
                continue

            if step not in seen:
                seen.add(step)
                final_steps.append(step)

    # STEP 6 — CLEAN STRUCTURED OUTPUT (NO RAW STRING BUILDING)
    output_lines = []

    # Root Cause
    output_lines.append("Root Cause:")
    if root_error:
        output_lines.append(root_error["error_string"])
    else:
        output_lines.append("Unable to determine exact root cause")

    # Failure Flow
    output_lines.append("\nFailure Flow:")
    output_lines.extend(timeline)

    # Final Solution
    output_lines.append("\nFinal Solution:")
    for i, step in enumerate(final_steps, 1):
        output_lines.append(f"{i}. {step}")

    return "\n".join(output_lines)

def summarize_logs(log_text):

    # Step 1: extract important lines
    lines = log_text.split("\n")

    important = []

    for l in lines:
        if any(tag in l for tag in ["ERROR", "WARN", "FAIL"]):
            important.append(l.strip())

    important = important[:50]  # limit noise

    context = "\n".join(important)

    prompt = f"""
You are a system debugging expert.

Analyze the following logs

Summarize the following logs into key technical failures.

Rules:
- DO NOT include instructions
- DO NOT ask questions
- ONLY extract failures
- Keep it short and technical

Logs:
{context}

Output format:

Summary:
...

Root Cause:
...
"""

    return generate_answer(prompt)