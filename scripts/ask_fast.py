import json
import numpy as np
import faiss
import sys
import os
from sentence_transformers import SentenceTransformer
from llama_cpp import Llama

# Use hardcoded paths
MODEL_PATH = "models/mistral.Q4_K_M.gguf"
EMBEDDINGS_PATH = "embeds/faiss.idx"
METADATA_PATH = "embeds/meta.json"
DOCS_PATH = "embeds/docs.txt"

print("Loading model with ultra-fast settings...")
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=256,  # Very small context
    n_batch=1,  # Minimal batch
    n_threads=2,  # Fewer threads
    verbose=False
)

print("Loading embeddings...")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index(EMBEDDINGS_PATH)
metadata = json.load(open(METADATA_PATH))
docs = open(DOCS_PATH).readlines()

print("Ready! Ask medical questions about JTS protocols.")

def answer(question):
    print("Searching...")
    q_embed = embed_model.encode([question])
    D, I = index.search(np.array(q_embed), 1)  # Get only top 1 match
    
    context = docs[I[0][0]]
    
    # Medical-focused prompt with strict guidelines
    prompt = f"""You are a medical assistant answering questions about Joint Trauma System (JTS) protocols. 

CONTEXT: {context}

QUESTION: {question}

INSTRUCTIONS:
- Answer ONLY based on the provided context
- Be specific with drug names, doses, and procedures
- If the context doesn't contain the answer, say "Not found in JTS protocols"
- Keep answers under 50 words
- Use medical terminology

ANSWER:"""

    try:
        output = llm(
            prompt, 
            max_tokens=50,  # Very short response
            temperature=0.0,  # No randomness
            stop=["\n", "QUESTION:", "CONTEXT:"]
        )
        return output["choices"][0]["text"].strip()
    except Exception as e:
        return f"Error: {e}"

while True:
    try:
        q = input("Ask: ")
        if q.lower() in ['quit', 'exit', 'q']:
            break
        a = answer(q)
        print(f"Answer: {a}\n")
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Error: {e}")
        break 