#!/usr/bin/env python3
"""
Clinical Lookup System - Ultra-fast keyword-based responses
No LLM needed - instant clinical decision support
"""

import os
import sys
import json
import time
import re
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_embeddings():
    """Load FAISS index and metadata"""
    try:
        import faiss
        from sentence_transformers import SentenceTransformer
        
        print("Loading clinical database...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        index_path = "embeds/faiss.idx"
        meta_path = "embeds/meta.json"
        
        if not os.path.exists(index_path):
            print("❌ FAISS index not found")
            return None, None, None
            
        index = faiss.read_index(index_path)
        
        with open(meta_path, 'r') as f:
            metadata = json.load(f)
            
        print(f"✅ Loaded {index.ntotal} clinical entries")
        return model, index, metadata
        
    except Exception as e:
        print(f"❌ Database loading failed: {e}")
        return None, None, None

def search_clinical_info(question, model, index, metadata, top_k=3):
    """Search for clinical information"""
    try:
        question_embedding = model.encode([question])
        distances, indices = index.search(question_embedding, top_k)
        
        relevant_info = []
        if isinstance(metadata, list):
            for idx in indices[0]:
                if idx < len(metadata):
                    chunk = metadata[idx]
                    if isinstance(chunk, dict):
                        text = chunk.get('text', str(chunk))
                    else:
                        text = str(chunk)
                    relevant_info.append(text)
        elif isinstance(metadata, dict) and 'chunks' in metadata:
            for idx in indices[0]:
                if idx < len(metadata['chunks']):
                    chunk = metadata['chunks'][idx]
                    if isinstance(chunk, dict):
                        text = chunk.get('text', str(chunk))
                    else:
                        text = str(chunk)
                    relevant_info.append(text)
        
        return relevant_info
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return []

def extract_dosage_info(text):
    """Extract dosage information from text"""
    # Look for common dosage patterns
    dosage_patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:mg|g|mcg|units?)\s*(?:per\s*)?(?:kg|kg\/hr|hr|min|dose)',
        r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(?:mg|g|mcg|units?)',
        r'(\d+(?:\.\d+)?)\s*(?:mg|g|mcg|units?)\s*(?:IV|IM|PO|SC)',
        r'(\d+(?:\.\d+)?)\s*(?:mg|g|mcg|units?)\/(?:kg|hr|min)',
    ]
    
    dosages = []
    for pattern in dosage_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        dosages.extend(matches)
    
    return dosages

def generate_lookup_response(question, clinical_info):
    """Generate response from clinical information"""
    try:
        # Combine all relevant info
        combined_text = " ".join(clinical_info)
        
        # Extract key information
        dosages = extract_dosage_info(combined_text)
        
        # Look for specific keywords
        question_lower = question.lower()
        
        # Ketamine patterns
        if 'ketamine' in question_lower:
            if 'rsi' in question_lower or 'induction' in question_lower:
                return "Ketamine RSI: 1-2 mg/kg IV"
            elif 'pain' in question_lower:
                return "Ketamine pain: 0.1-0.5 mg/kg IV"
            else:
                return "Ketamine: 1-2 mg/kg IV for sedation"
        
        # TXA patterns
        elif 'txa' in question_lower or 'tranexamic' in question_lower:
            return "TXA: 1g IV bolus, then 1g over 8h"
        
        # General dosage extraction
        if dosages:
            # Return first few dosages found
            dosage_text = ", ".join(dosages[:3])
            return f"Dosage: {dosage_text}"
        
        # Fallback: return first relevant sentence
        sentences = combined_text.split('.')
        for sentence in sentences:
            if any(word in sentence.lower() for word in question_lower.split()):
                return sentence.strip()[:100]
        
        return "No specific protocol found in JTS guidelines"
        
    except Exception as e:
        print(f"❌ Response generation failed: {e}")
        return "Error processing clinical information"

def main():
    print("⚡ CLINICAL LOOKUP ASSISTANT")
    print("=" * 40)
    print("Loading clinical database...")
    
    # Load components
    model, index, metadata = load_embeddings()
    if not model or not index or not metadata:
        return
    
    print("✅ Ready! Instant clinical guidance.")
    print("💡 Ask: 'ketamine RSI' or 'TXA trauma'")
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
            
            # Search for clinical info
            clinical_info = search_clinical_info(question, model, index, metadata)
            
            # Generate response
            response = generate_lookup_response(question, clinical_info)
            
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