from app.rag_pipeline import rag_pipeline

def run_test_block(title, queries):
    print("\n" + "="*60)
    print(f"🔥 {title}")
    print("="*60)

    for i, q in enumerate(queries, 1):
        print(f"\n[{i}] Q:", q)
        try:
            result = rag_pipeline(q)

            if isinstance(result, dict):
                print("A:", result["answer"])
                if result.get("sources"):
                    print("Sources:", result["sources"])
            else:
                print("A:", result)

        except Exception as e:
            print("❌ ERROR:", str(e))


# 🔹 1. DOC TESTS
run_test_block("DOC TESTS", [
    "How to configure kerberos?",
    "What ACLs are supported",
    "Kerberos ticket generation failed"
])


# 🔹 2. ERROR TESTS
run_test_block("ERROR TESTS", [
    "I am facing EC02010016 error",
    "Kerberos failure EC02010016 how to fix?",
    "EC02010016 root cause"
])


# 🔹 3. LOG TESTS (CRITICAL)
run_test_block("LOG TESTS", [

    # simple
    "[MO_ERROR]:[EC02010016]: Failed getpwnam",

    # medium
    """[2026-03-23]:[MO_ERROR]:[EC02010016]: Failed getpwnam
    [MO_WARN]:[EC0202011F]: Failed to map user""",

    # complex (your main case)
    """[2026-03-04 16:18:58.951]:[MO_WARN]:[AUTH]:[EC0602010C]: Can not authorize
    [MO_ERROR]:[RPC]:[EC10010103]: bind failed
    [MO_ERROR]:[SMBCORE]:[EC0201014A]: Failed session key
    [MO_ERROR]:[RPC]:[EC10010105]: FAILED TO RECOMPUTE SESSION KEY"""
])


# 🔹 4. MEMORY TESTS
print("\n" + "="*60)
print("🔥 MEMORY TESTS")
print("="*60)

sequence = [
    "How to configure kerberos?",
    "Explain step 2",
    "Why is this required?",
    "What happens if I skip it?",
    "Explain step 1 again"
]

for q in sequence:
    print("\nQ:", q)
    print("A:", rag_pipeline(q))