import os
import sys
import numpy as np
import faiss
import json
from sentence_transformers import SentenceTransformer

# Add the parent directory to the path so we can import config and utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *
from scripts.utils import extract_chunks_from_pdf, save_docs_text

# Verify that PDFS_DIR is defined
if 'PDFS_DIR' not in globals():
    print("Error: PDFS_DIR not found in config. Using default 'pdfs/' directory.")
    PDFS_DIR = "pdfs/"

print(f"Using PDFS_DIR: {PDFS_DIR}")
print(f"PDFS_DIR exists: {os.path.exists(PDFS_DIR)}")

model = SentenceTransformer('all-MiniLM-L6-v2')
all_chunks, metadata = [], []

for file in os.listdir(PDFS_DIR):
    if file.endswith(".pdf"):
        path = os.path.join(PDFS_DIR, file)
        chunks = extract_chunks_from_pdf(path)
        for chunk, page in chunks:
            all_chunks.append(chunk)
            metadata.append({"file": file, "page": page})
    elif file.endswith(".txt"):
        # Handle text files for testing
        path = os.path.join(PDFS_DIR, file)
        with open(path, 'r') as f:
            content = f.read()
            # Split into chunks
            chunk_size = 512
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i+chunk_size]
                all_chunks.append(chunk)
                metadata.append({"file": file, "page": i//chunk_size + 1})

embeds = model.encode(all_chunks)
index = faiss.IndexFlatL2(embeds.shape[1])
index.add(np.array(embeds))

os.makedirs(EMBEDS_DIR, exist_ok=True)
faiss.write_index(index, EMBEDDINGS_PATH)

with open(METADATA_PATH, "w") as f:
    json.dump(metadata, f)

save_docs_text(all_chunks, DOCS_PATH)
