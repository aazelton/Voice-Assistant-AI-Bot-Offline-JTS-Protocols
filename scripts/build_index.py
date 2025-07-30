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

# Check if there are any files to process
pdf_files = [f for f in os.listdir(PDFS_DIR) if f.endswith('.pdf')]
txt_files = [f for f in os.listdir(PDFS_DIR) if f.endswith('.txt')]

print(f"Found {len(pdf_files)} PDF files: {pdf_files}")
print(f"Found {len(txt_files)} TXT files: {txt_files}")

if not pdf_files and not txt_files:
    print("No PDF or TXT files found in PDFS_DIR. Please add some files and try again.")
    sys.exit(1)

model = SentenceTransformer('all-MiniLM-L6-v2')
all_chunks, metadata = [], []

for file in os.listdir(PDFS_DIR):
    if file.endswith(".pdf"):
        path = os.path.join(PDFS_DIR, file)
        print(f"Processing PDF: {file}")
        try:
    chunks = extract_chunks_from_pdf(path)
    for chunk, page in chunks:
        all_chunks.append(chunk)
        metadata.append({"file": file, "page": page})
        except Exception as e:
            print(f"Error processing {file}: {e}")
    elif file.endswith(".txt"):
        # Handle text files for testing
        path = os.path.join(PDFS_DIR, file)
        print(f"Processing TXT: {file}")
        try:
            with open(path, 'r') as f:
                content = f.read()
                # Split into chunks
                chunk_size = 512
                for i in range(0, len(content), chunk_size):
                    chunk = content[i:i+chunk_size]
                    all_chunks.append(chunk)
                    metadata.append({"file": file, "page": i//chunk_size + 1})
        except Exception as e:
            print(f"Error processing {file}: {e}")

print(f"Total chunks extracted: {len(all_chunks)}")

if not all_chunks:
    print("No text chunks were extracted. Please check your PDF/TXT files.")
    sys.exit(1)

print("Encoding chunks...")
embeds = model.encode(all_chunks)
print(f"Embeddings shape: {embeds.shape}")

if embeds.shape[0] == 0:
    print("No embeddings were created. Please check your input files.")
    sys.exit(1)

index = faiss.IndexFlatL2(embeds.shape[1])
index.add(np.array(embeds))

os.makedirs(EMBEDS_DIR, exist_ok=True)
faiss.write_index(index, EMBEDDINGS_PATH)

with open(METADATA_PATH, "w") as f:
    json.dump(metadata, f)

save_docs_text(all_chunks, DOCS_PATH)

print(f"Successfully created index with {len(all_chunks)} chunks")
print(f"Index saved to: {EMBEDDINGS_PATH}")
print(f"Metadata saved to: {METADATA_PATH}")
print(f"Docs saved to: {DOCS_PATH}")
