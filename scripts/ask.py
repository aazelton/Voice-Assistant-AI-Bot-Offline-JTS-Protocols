import json
import numpy as np
import subprocess
import faiss
from sentence_transformers import SentenceTransformer
from llama_cpp import Llama
from config import *

llm = Llama(model_path=MODEL_PATH)
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index(EMBEDDINGS_PATH)
metadata = json.load(open(METADATA_PATH))
docs = open(DOCS_PATH).readlines()

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
        subprocess.run(["espeak-ng", a])
    except KeyboardInterrupt:
        break
