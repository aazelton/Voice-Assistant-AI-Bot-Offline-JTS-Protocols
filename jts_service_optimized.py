#!/usr/bin/env python3
# Optimized JTS REST API Service - Minimal Resource Usage
import flask
from flask import Flask, request, jsonify
import sys
import os
import time
import json
import faiss
from sentence_transformers import SentenceTransformer

# Add the project path
sys.path.append('/home/akaclinicalco/Voice-Assistant-AI-Bot-Offline-JTS-Protocols')

app = Flask(__name__)

# Global variables for loaded models
model = None
index = None
metadata = None

def load_models():
    global model, index, metadata
    if model is None:
        print("Loading optimized sentence transformer...")
        # Use smaller model for better performance
        model = SentenceTransformer('paraphrase-MiniLM-L3-v2')  # Smaller than L6
        print("Loading FAISS index...")
        index = faiss.read_index('/home/akaclinicalco/Voice-Assistant-AI-Bot-Offline-JTS-Protocols/embeds/faiss.idx')
        print("Loading metadata...")
        with open('/home/akaclinicalco/Voice-Assistant-AI-Bot-Offline-JTS-Protocols/embeds/meta.json', 'r') as f:
            metadata = json.load(f)
        print("All models loaded successfully!")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "models_loaded": model is not None})

@app.route('/query', methods=['POST'])
def query():
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # Load models if not already loaded
        if model is None:
            load_models()
        
        # Search for relevant context (reduced from 3 to 2 for efficiency)
        question_embedding = model.encode([question])
        distances, indices = index.search(question_embedding, 2)  # Reduced from 3
        
        # Get relevant chunks
        relevant_chunks = []
        for idx in indices[0]:
            if idx < len(metadata):
                relevant_chunks.append(metadata[idx])
        
        if relevant_chunks:
            # Return the first chunk as response
            chunk = relevant_chunks[0]
            if isinstance(chunk, dict):
                if 'text' in chunk:
                    response_text = chunk['text']
                elif 'content' in chunk:
                    response_text = chunk['content']
                else:
                    response_text = str(chunk)
            else:
                response_text = str(chunk)
            
            return jsonify({
                "question": question,
                "response": response_text,
                "chunks_found": len(relevant_chunks)
            })
        else:
            return jsonify({
                "question": question,
                "response": "No relevant JTS protocol found for this query.",
                "chunks_found": 0
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/load', methods=['POST'])
def load():
    try:
        load_models()
        return jsonify({"status": "Models loaded successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting optimized JTS REST API service...")
    load_models()
    # Use threaded=False for single-threaded operation (reduces resource usage)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=False) 