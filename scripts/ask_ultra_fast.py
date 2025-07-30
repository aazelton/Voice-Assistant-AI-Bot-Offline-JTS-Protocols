#!/usr/bin/env python3
"""
Ultra-Fast Clinical Q&A - Optimized for rapid decision support
Minimal context, maximum speed, concise medical answers
"""

import os
import sys
import json
import time
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_model():
    """Load LLM with ultra-fast settings"""
    try:
        from llama_cpp import Llama
        
        model_path = "models/mistral.Q4_K_M.gguf"
        
        print("Loading ultra-fast model...")
        llm = Llama(
            model_path=model_path,
            n_ctx=512,           # Minimal context
            n_batch=1,           # Single batch for speed
            n_threads=2,         # Fewer threads
            n_gpu_layers=0,      # CPU only
            verbose=False,
            max_tokens=50,       # Very short responses
            temperature=0.0,     # Deterministic
            top_p=0.8,           # Focused sampling
            repeat_penalty=1.0   # No repetition penalty
        )
        print("✅ Ultra-fast model loaded")
        return llm
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

def search_context(question, model, index, metadata, top_k=2):
    """Fast search for minimal context"""
    try:
        question_embedding = model.encode([question])
        distances, indices = index.search(question_embedding, top_k)
        
        relevant_chunks = []
        if isinstance(metadata, list):
            for idx in indices[0]:
                if idx < len(metadata):
                    chunk = metadata[idx]
                    if isinstance(chunk, dict):
                        text = chunk.get('text', str(chunk))
                    else:
                        text = str(chunk)
                    relevant_chunks.append(text)
        elif isinstance(metadata, dict) and 'chunks' in metadata:
            for idx in indices[0]:
                if idx < len(metadata['chunks']):
                    chunk = metadata['chunks'][idx]
                    if isinstance(chunk, dict):
                        text = chunk.get('text', str(chunk))
                    else:
                        text = str(chunk)
                    relevant_chunks.append(text)
        
        return relevant_chunks[:1]  # Only use top 1 chunk for speed
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return []

def generate_fast_response(question, context_chunks, llm):
    """Generate ultra-fast, concise response"""
    try:
        # Use only first chunk, limit to 100 chars
        context = ""
        if context_chunks:
            context = str(context_chunks[0])[:100]
        
        # Ultra-minimal prompt
        prompt = f"""Q: {question}
Context: {context}
A:"""
        
        # Generate with minimal settings
        response = llm(
            prompt,
            max_tokens=30,       # Very short
            temperature=0.0,     # Deterministic
            top_p=0.8,
            stop=["\n", "Q:"]
        )
        
        answer = response['choices'][0]['text'].strip()
        
        # Post-process for medical clarity
        if not answer or len(answer) < 5:
            return "No specific JTS protocol found."
        
        return answer
        
    except Exception as e:
        print(f"❌ Response failed: {e}")
        return "Error"

def main():
    print("⚡ ULTRA-FAST CLINICAL ASSISTANT")
    print("=" * 40)
    print("Loading for rapid decision support...")
    
    # Load components
    llm = load_model()
    if not llm:
        return
    
    model, index, metadata = load_embeddings()
    if not model or not index or not metadata:
        return
    
    print("✅ Ready! Ask for rapid clinical guidance.")
    print("💡 Format: 'ketamine dose RSI' or 'tranexamic acid trauma'")
    print()
    
    while True:
        try:
            question = input("⚡ Q: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not question:
                continue
            
            print("🔍 Searching...")
            start_time = time.time()
            
            # Search for context
            context_chunks = search_context(question, model, index, metadata)
            
            # Generate response
            response = generate_fast_response(question, context_chunks, llm)
            
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