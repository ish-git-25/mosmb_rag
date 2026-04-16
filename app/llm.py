from app.model import tokenizer, llm

def generate_answer(prompt):

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

    outputs = llm.generate(
        **inputs,
        max_new_tokens=200,
        do_sample=False,
        temperature=0.0,
        repetition_penalty=1.1,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id
    )

    generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]

    return tokenizer.decode(generated_tokens, skip_special_tokens=True)