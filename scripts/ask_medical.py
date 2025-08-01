#!/usr/bin/env python3
"""
Medical Q&A Script - Optimized for clinical decision support
Enhanced prompt engineering for specific medical responses
"""

import os
import sys
import json
import time
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_model():
    """Load the LLM with medical-optimized settings"""
    try:
        from llama_cpp import Llama
        
        model_path = "models/mistral.Q4_K_M.gguf"
        
        print("Loading medical model...")
        llm = Llama(
            model_path=model_path,
            n_ctx=2048,          # Larger context for medical info
            n_batch=64,          # Efficient batch processing
            n_threads=4,         # Moderate threading
            n_gpu_layers=0,      # CPU only
            verbose=False,
            max_tokens=200,      # Longer responses for medical details
            temperature=0.2,     # Low temperature for consistency
            top_p=0.9,           # Nucleus sampling
            repeat_penalty=1.1   # Prevent repetition
        )
        print("✅ Medical model loaded")
        return llm
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return None

def load_embeddings():
    """Load FAISS index and metadata"""
    try:
        import faiss
        from sentence_transformers import SentenceTransformer
        
        print("Loading medical embeddings...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        index_path = "embeds/faiss.idx"
        meta_path = "embeds/meta.json"
        
        if not os.path.exists(index_path):
            print("❌ FAISS index not found")
            return None, None, None
            
        index = faiss.read_index(index_path)
        
        with open(meta_path, 'r') as f:
            metadata = json.load(f)
            
        print(f"✅ Loaded {index.ntotal} medical embeddings")
        return model, index, metadata
        
    except Exception as e:
        print(f"❌ Embeddings loading failed: {e}")
        return None, None, None

def search_context(question, model, index, metadata, top_k=5):
    """Search for relevant medical context"""
    try:
        # Enhance question with medical terms
        enhanced_question = f"medical trauma {question} dosage protocol"
        question_embedding = model.encode([enhanced_question])
        
        # Search with more results
        distances, indices = index.search(question_embedding, top_k)
        
        relevant_chunks = []
        for idx in indices[0]:
            if idx < len(metadata['chunks']):
                chunk = metadata['chunks'][idx]
                # Filter for medical relevance
                if any(term in chunk.lower() for term in ['mg', 'kg', 'dose', 'protocol', 'trauma', 'medical']):
                    relevant_chunks.append(chunk)
        
        return relevant_chunks[:3]  # Return top 3 relevant chunks
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return []

def generate_medical_response(question, context_chunks, llm):
    """Generate specific medical response"""
    try:
        # Create comprehensive context
        context = "\n".join(context_chunks)
        
        # Enhanced medical prompt
        prompt = f"""You are a trauma medicine expert providing clinical decision support based on Joint Trauma System (JTS) Clinical Practice Guidelines.

RELEVANT JTS GUIDELINES:
{context}

CLINICAL QUESTION: {question}

INSTRUCTIONS:
- Provide SPECIFIC medical information including dosages, routes, and protocols
- If dosing information is available, include exact amounts (mg/kg, mg, etc.)
- Mention the specific JTS guideline if referenced
- If information is incomplete, state what specific details are missing
- Use medical terminology appropriately
- Keep response under 150 words but be comprehensive

MEDICAL RESPONSE:"""
        
        # Generate with medical focus
        response = llm(
            prompt,
            max_tokens=200,
            temperature=0.2,
            top_p=0.9,
            stop=["CLINICAL QUESTION:", "INSTRUCTIONS:", "\n\n\n"]
        )
        
        answer = response['choices'][0]['text'].strip()
        
        # Post-process for medical clarity
        if "not found" in answer.lower() or "not in" in answer.lower():
            answer = f"INFORMATION STATUS: {answer}\n\nRECOMMENDATION: Consult current JTS Clinical Practice Guidelines for the most up-to-date protocols."
        
        return answer
        
    except Exception as e:
        print(f"❌ Response generation failed: {e}")
        return "ERROR: Unable to generate medical response. Please try rephrasing your question."

def main():
    print("🏥 TRAUMA MEDICINE ASSISTANT")
    print("=" * 50)
    print("Loading medical decision support system...")
    
    # Load components
    llm = load_model()
    if not llm:
        return
    
    model, index, metadata = load_embeddings()
    if not model or not index or not metadata:
        return
    
    print("✅ Ready for clinical questions!")
    print("💡 Ask about: dosages, protocols, procedures, medications")
    print()
    
    while True:
        try:
            question = input("🏥 CLINICAL QUESTION: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not question:
                continue
            
            print("🔍 Searching JTS guidelines...")
            start_time = time.time()
            
            # Search for context
            context_chunks = search_context(question, model, index, metadata)
            
            if not context_chunks:
                print("❌ No relevant JTS guidelines found")
                print("💡 Try: 'ketamine dosage trauma' or 'pain management protocol'")
                continue
            
            # Generate response
            response = generate_medical_response(question, context_chunks, llm)
            
            end_time = time.time()
            
            print(f"📋 MEDICAL RESPONSE ({end_time - start_time:.1f}s):")
            print(f"{response}")
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

if __name__ == "__main__":
    main() 