from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
from sentence_transformers import SentenceTransformer
from sentence_transformers import CrossEncoder
from dotenv import load_dotenv
import os

load_dotenv()

hf_token = os.getenv("HF_TOKEN")

model_id = "meta-llama/Meta-Llama-3-8B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

llm = AutoModelForCausalLM.from_pretrained(
    model_id,
    token=hf_token,
    device_map="auto",
    quantization_config=quantization_config,
    torch_dtype=torch.float16
)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')