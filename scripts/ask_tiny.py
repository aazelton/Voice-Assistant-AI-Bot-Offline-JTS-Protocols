#!/usr/bin/env python3
"""
Tiny Model Clinical Q&A - Ultra-fast with smaller model
Uses TinyLlama or similar for rapid responses
"""

import os
import sys
import json
import time
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_tiny_model():
    """Load a smaller, faster model"""
    try:
        from llama_cpp import Llama
        
        # Try different small models in order of preference
        model_paths = [
            "models/tinyllama-1.1b-chat.Q4_K_M.gguf",  # ~600MB
            "models/mistral-7b-instruct-v0.2.Q2_K.gguf",  # ~2.7GB but faster
            "models/mistral.Q4_K_M.gguf"  # Fallback to current model
        ]
        
        for model_path in model_paths:
            if os.path.exists(model_path):
                print(f"Loading {os.path.basename(model_path)}...")
                llm = Llama(
                    model_path=model_path,
                    n_ctx=256,           # Very small context
                    n_batch=1,           # Single batch
                    n_threads=1,         # Single thread for speed
                    n_gpu_layers=0,      # CPU only
                    verbose=False,
                    max_tokens=25,       # Very short responses
                    temperature=0.0,     # Deterministic
                    top_p=0.7,           # Focused
                    repeat_penalty=1.0   # No penalty
                )
                print(f"✅ Loaded {os.path.basename(model_path)}")
                return llm
        
        print("❌ No small models found")
        return None
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return None

def load_embeddings():
    """Load FAISS index and metadata"""
    try:
        import faiss
        from sentence_transformers import SentenceTransformer
        
        print("Loading embeddings...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        index_path = "embeds/faiss.idx"
        meta_path = "embeds/meta.json"
        
        if not os.path.exists(index_path):
            print("❌ FAISS index not found")
            return None, None, None
            
        index = faiss.read_index(index_path)
        
        with open(meta_path, 'r') as f:
            metadata = json.load(f)
            
        print(f"✅ Loaded {index.ntotal} embeddings")
        return model, index, metadata
        
    except Exception as e:
        print(f"❌ Embeddings loading failed: {e}")
        return None, None, None

def search_context(question, model, index, metadata, top_k=1):
    """Minimal search for speed"""
    try:
        question_embedding = model.encode([question])
        distances, indices = index.search(question_embedding, top_k)
        
        if isinstance(metadata, list) and indices[0][0] < len(metadata):
            chunk = metadata[indices[0][0]]
            if isinstance(chunk, dict):
                return chunk.get('text', str(chunk))[:50]  # Very short
            return str(chunk)[:50]
        elif isinstance(metadata, dict) and 'chunks' in metadata and indices[0][0] < len(metadata['chunks']):
            chunk = metadata['chunks'][indices[0][0]]
            if isinstance(chunk, dict):
                return chunk.get('text', str(chunk))[:50]
            return str(chunk)[:50]
        
        return ""
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return ""

def generate_tiny_response(question, context, llm):
    """Generate ultra-fast response with tiny model"""
    try:
        # Minimal prompt
        prompt = f"Q: {question}\nA:"
        
        response = llm(
            prompt,
            max_tokens=20,       # Very short
            temperature=0.0,     # Deterministic
            stop=["\n", "Q:"]
        )
        
        answer = response['choices'][0]['text'].strip()
        
        if not answer:
            return "No protocol found"
        
        return answer
        
    except Exception as e:
        print(f"❌ Response failed: {e}")
        return "Error"

def main():
    print("🔬 TINY CLINICAL ASSISTANT")
    print("=" * 40)
    print("Loading for ultra-fast responses...")
    
    # Load components
    llm = load_tiny_model()
    if not llm:
        return
    
    model, index, metadata = load_embeddings()
    if not model or not index or not metadata:
        return
    
    print("✅ Ready! Ask for rapid clinical guidance.")
    print("💡 Keep questions short: 'ketamine dose' or 'TXA protocol'")
    print()
    
    while True:
        try:
            question = input("🔬 Q: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not question:
                continue
            
            print("🔍 Searching...")
            start_time = time.time()
            
            # Search for context
            context = search_context(question, model, index, metadata)
            
            # Generate response
            response = generate_tiny_response(question, context, llm)
            
            end_time = time.time()
            
            print(f"📋 A ({end_time - start_time:.1f}s): {response}")
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

if __name__ == "__main__":
    main() 