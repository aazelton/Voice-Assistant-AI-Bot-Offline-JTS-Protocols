import json
import numpy as np
import subprocess
import faiss
import sys
import os
from sentence_transformers import SentenceTransformer
from llama_cpp import Llama

# Use hardcoded paths to avoid config import issues
MODEL_PATH = "models/mistral.Q4_K_M.gguf"
EMBEDDINGS_PATH = "embeds/faiss.idx"
METADATA_PATH = "embeds/meta.json"
DOCS_PATH = "embeds/docs.txt"

print(f"Using MODEL_PATH: {MODEL_PATH}")
print(f"Using EMBEDDINGS_PATH: {EMBEDDINGS_PATH}")

# Check if files exist
if not os.path.exists(MODEL_PATH):
    print(f"Error: Model file not found at {MODEL_PATH}")
    sys.exit(1)

if not os.path.exists(EMBEDDINGS_PATH):
    print(f"Error: Embeddings file not found at {EMBEDDINGS_PATH}")
    sys.exit(1)

print("Loading model...")
llm = Llama(model_path=MODEL_PATH)

print("Loading embeddings...")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index(EMBEDDINGS_PATH)
metadata = json.load(open(METADATA_PATH))
docs = open(DOCS_PATH).readlines()

print("Ready! Ask questions about your JTS protocols.")

def answer(question):
    q_embed = embed_model.encode([question])
    D, I = index.search(np.array(q_embed), 3)
    context = "\n\n".join([docs[i] for i in I[0]])
    prompt = f"[CONTEXT START]\n{context}\n[CONTEXT END]\n\nQuestion: {question}\nAnswer:"
    output = llm(prompt, max_tokens=150, stop=["\n"])["choices"][0]["text"].strip()
    return output

while True:
    try:
        q = input("Ask: ")
        a = answer(q)
        print(f"\nAnswer: {a}")
        try:
            subprocess.run(["espeak-ng", a], capture_output=True, timeout=10)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("(Text-to-speech not available)")
    except KeyboardInterrupt:
        break
