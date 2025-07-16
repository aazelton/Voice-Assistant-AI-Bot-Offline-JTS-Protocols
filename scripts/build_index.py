import os
import numpy as np
import faiss
import json
from sentence_transformers import SentenceTransformer
from utils import extract_chunks_from_pdf, save_docs_text
from config import *

model = SentenceTransformer('all-MiniLM-L6-v2')
all_chunks, metadata = [], []

for file in os.listdir("../pdfs"):
    if not file.endswith(".pdf"): continue
    path = f"../pdfs/{file}"
    chunks = extract_chunks_from_pdf(path)
    for chunk, page in chunks:
        all_chunks.append(chunk)
        metadata.append({"file": file, "page": page})

embeds = model.encode(all_chunks)
index = faiss.IndexFlatL2(embeds.shape[1])
index.add(np.array(embeds))

os.makedirs("../embeds", exist_ok=True)
faiss.write_index(index, EMBEDDINGS_PATH)

with open(METADATA_PATH, "w") as f:
    json.dump(metadata, f)

save_docs_text(all_chunks, DOCS_PATH)
