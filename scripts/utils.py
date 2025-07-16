import os, json
import pdfplumber

def extract_chunks_from_pdf(file_path):
    chunks = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                for j in range(0, len(text), 512):
                    chunk = text[j:j+512]
                    chunks.append((chunk, i+1))
    return chunks

def save_docs_text(chunks, file_path):
    with open(file_path, "w") as f:
        for chunk in chunks:
            f.write(chunk + "\n")
