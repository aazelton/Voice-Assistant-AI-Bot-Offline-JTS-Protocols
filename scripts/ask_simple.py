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

print("Loading model with optimized settings...")
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=512,  # Smaller context window
    n_batch=8,  # Smaller batch size
    n_threads=4,  # Limit threads
    verbose=False
)

print("Loading embeddings...")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index(EMBEDDINGS_PATH)
metadata = json.load(open(METADATA_PATH))
docs = open(DOCS_PATH).readlines()

print("Ready! Ask questions about your JTS protocols.")

def answer(question):
    print("Searching for relevant information...")
    q_embed = embed_model.encode([question])
    D, I = index.search(np.array(q_embed), 2)  # Get top 2 matches
    
    print("Found relevant chunks, generating answer...")
    context = "\n".join([docs[i] for i in I[0]])
    prompt = f"Based on this medical information:\n{context}\n\nQuestion: {question}\nAnswer:"
    
    try:
        output = llm(
            prompt, 
            max_tokens=100,  # Shorter response
            temperature=0.1,  # More focused
            stop=["\n\n", "Question:", "Answer:"]
        )
        return output["choices"][0]["text"].strip()
    except Exception as e:
        return f"Error generating answer: {e}"

while True:
    try:
        q = input("Ask: ")
        if q.lower() in ['quit', 'exit', 'q']:
            break
        a = answer(q)
        print(f"\nAnswer: {a}\n")
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Error: {e}")
        break 