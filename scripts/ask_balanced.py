#!/usr/bin/env python3
"""
Balanced Q&A Script - Fast but usable medical responses
Optimized for speed while maintaining response quality
"""

import os
import sys
import json
import time
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_model():
    """Load the LLM with balanced settings"""
    try:
        from llama_cpp import Llama
        
        # Balanced settings - fast but usable
        model_path = "models/mistral.Q4_K_M.gguf"
        
        print("Loading model with balanced settings...")
        llm = Llama(
            model_path=model_path,
            n_ctx=1024,          # Increased context
            n_batch=32,          # Balanced batch size
            n_threads=4,         # Moderate threading
            n_gpu_layers=0,      # CPU only for compatibility
            verbose=False,
            max_tokens=150,      # Reasonable response length
            temperature=0.3,     # Some creativity but focused
            top_p=0.9,           # Nucleus sampling
            repeat_penalty=1.1   # Prevent repetition
        )
        print("✅ Model loaded successfully")
        return llm
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return None

def load_embeddings():
    """Load FAISS index and metadata"""
    try:
        import faiss
        from sentence_transformers import SentenceTransformer
        
        # Load the embedding model
        print("Loading embeddings...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load FAISS index
        index_path = "embeds/faiss.idx"
        meta_path = "embeds/meta.json"
        
        if not os.path.exists(index_path):
            print("❌ FAISS index not found")
            return None, None, None
            
        index = faiss.read_index(index_path)
        
        # Load metadata
        with open(meta_path, 'r') as f:
            metadata = json.load(f)
            
        print(f"✅ Loaded {index.ntotal} embeddings")
        return model, index, metadata
        
    except Exception as e:
        print(f"❌ Embeddings loading failed: {e}")
        return None, None, None

def search_context(question, model, index, metadata, top_k=3):
    """Search for relevant context"""
    try:
        # Encode the question
        question_embedding = model.encode([question])
        
        # Search the index
        distances, indices = index.search(question_embedding, top_k)
        
        # Get relevant chunks - fix the metadata access
        relevant_chunks = []
        for idx in indices[0]:
            if idx < len(metadata.get('chunks', [])):
                relevant_chunks.append(metadata['chunks'][idx])
        
        return relevant_chunks
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return []

def generate_response(question, context_chunks, llm):
    """Generate medical response"""
    try:
        # Create context from chunks
        context = "\n".join(context_chunks[:2])  # Use top 2 chunks
        
        # Medical prompt template
        prompt = f"""You are a clinical decision support assistant. Answer the following medical question based on Joint Trauma System (JTS) Clinical Practice Guidelines.

Context from JTS guidelines:
{context}

Question: {question}

Instructions:
- Provide a concise, evidence-based answer
- Include specific dosages when applicable
- Reference JTS guidelines when possible
- Keep answer under 100 words
- Use medical terminology appropriately
- If information is not in the context, say so clearly

Answer:"""
        
        # Generate response
        response = llm(
            prompt,
            max_tokens=150,
            temperature=0.3,
            top_p=0.9,
            stop=["Question:", "\n\n"]
        )
        
        return response['choices'][0]['text'].strip()
        
    except Exception as e:
        print(f"❌ Response generation failed: {e}")
        return "I'm sorry, I couldn't generate a response at this time."

def main():
    print("🚀 TRAUMA ASSISTANT - BALANCED Q&A")
    print("=" * 50)
    print("Loading components...")
    
    # Load model
    llm = load_model()
    if not llm:
        print("❌ Failed to load model")
        return
    
    # Load embeddings
    model, index, metadata = load_embeddings()
    if not model or not index or not metadata:
        print("❌ Failed to load embeddings")
        return
    
    print("✅ Ready! Ask medical questions about JTS protocols.")
    print()
    
    while True:
        try:
            # Get question
            question = input("Ask: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
                
            if not question:
                continue
            
            print("Searching...")
            start_time = time.time()
            
            # Search for context
            context_chunks = search_context(question, model, index, metadata)
            
            if not context_chunks:
                print("❌ No relevant context found")
                continue
            
            # Generate response
            response = generate_response(question, context_chunks, llm)
            
            end_time = time.time()
            
            print(f"Answer ({end_time - start_time:.1f}s): {response}")
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

if __name__ == "__main__":
    main() 