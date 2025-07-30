#!/usr/bin/env python3
"""
Smart Clinical Assistant - Intelligent responses with math
GPT-like reasoning without slow model loading
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

def extract_weight(question):
    """Extract patient weight from question"""
    weight_patterns = [
        r'(\d+)\s*kg',
        r'(\d+)\s*kilo',
        r'(\d+)\s*pound',
        r'(\d+)\s*lb',
        r'(\d+)\s*kg\s*pt',
        r'(\d+)\s*kg\s*patient'
    ]
    
    for pattern in weight_patterns:
        match = re.search(pattern, question.lower())
        if match:
            weight = float(match.group(1))
            # Convert pounds to kg if needed
            if 'pound' in question.lower() or 'lb' in question.lower():
                weight = weight * 0.453592
            return weight
    return None

def extract_dosage_info(text):
    """Extract dosage information from text"""
    dosage_patterns = [
        r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(?:mg|g|mcg|units?)\s*(?:per\s*)?(?:kg|kg\/hr|hr|min|dose)',
        r'(\d+(?:\.\d+)?)\s*(?:mg|g|mcg|units?)\s*(?:per\s*)?(?:kg|kg\/hr|hr|min|dose)',
        r'(\d+(?:\.\d+)?)\s*(?:mg|g|mcg|units?)\s*(?:IV|IM|PO|SC)',
        r'(\d+(?:\.\d+)?)\s*(?:mg|g|mcg|units?)\/(?:kg|hr|min)',
    ]
    
    dosages = []
    for pattern in dosage_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        dosages.extend(matches)
    
    return dosages

def calculate_dosage(base_dosage, weight):
    """Calculate actual dosage based on weight"""
    try:
        # Extract numbers from dosage string
        numbers = re.findall(r'\d+(?:\.\d+)?', base_dosage)
        if len(numbers) >= 2:
            min_dose = float(numbers[0])
            max_dose = float(numbers[1])
            
            min_total = min_dose * weight
            max_total = max_dose * weight
            
            # Round to reasonable precision
            min_total = round(min_total, 1)
            max_total = round(max_total, 1)
            
            return f"{min_total}-{max_total}mg"
        elif len(numbers) == 1:
            dose = float(numbers[0]) * weight
            dose = round(dose, 1)
            return f"{dose}mg"
    except:
        pass
    return base_dosage

def generate_smart_response(question, clinical_info):
    """Generate intelligent response with math"""
    try:
        # Extract patient weight
        weight = extract_weight(question)
        
        # Combine all relevant info
        combined_text = " ".join(clinical_info)
        
        # Look for specific keywords
        question_lower = question.lower()
        
        # Ketamine patterns
        if 'ketamine' in question_lower:
            if 'rsi' in question_lower or 'induction' in question_lower:
                base_dosage = "1-2 mg/kg IV"
                if weight:
                    calculated_dose = calculate_dosage(base_dosage, weight)
                    return f"Ketamine RSI: {base_dosage} = {calculated_dose} for {weight}kg patient"
                else:
                    return f"Ketamine RSI: {base_dosage}"
            elif 'pain' in question_lower:
                base_dosage = "0.1-0.5 mg/kg IV"
                if weight:
                    calculated_dose = calculate_dosage(base_dosage, weight)
                    return f"Ketamine pain: {base_dosage} = {calculated_dose} for {weight}kg patient"
                else:
                    return f"Ketamine pain: {base_dosage}"
            else:
                base_dosage = "1-2 mg/kg IV"
                if weight:
                    calculated_dose = calculate_dosage(base_dosage, weight)
                    return f"Ketamine: {base_dosage} = {calculated_dose} for {weight}kg patient"
                else:
                    return f"Ketamine: {base_dosage}"
        
        # TXA patterns
        elif 'txa' in question_lower or 'tranexamic' in question_lower:
            if 'im' in question_lower:
                return "TXA: Not recommended IM. Use 1g IV bolus, then 1g over 8h"
            else:
                return "TXA: 1g IV bolus, then 1g over 8h"
        
        # Fentanyl patterns
        elif 'fentanyl' in question_lower:
            base_dosage = "1-2 mcg/kg IV"
            if weight:
                calculated_dose = calculate_dosage(base_dosage, weight)
                return f"Fentanyl: {base_dosage} = {calculated_dose} for {weight}kg patient"
            else:
                return f"Fentanyl: {base_dosage}"
        
        # Morphine patterns
        elif 'morphine' in question_lower:
            base_dosage = "0.1-0.2 mg/kg IV"
            if weight:
                calculated_dose = calculate_dosage(base_dosage, weight)
                return f"Morphine: {base_dosage} = {calculated_dose} for {weight}kg patient"
            else:
                return f"Morphine: {base_dosage}"
        
        # General dosage extraction
        dosages = extract_dosage_info(combined_text)
        if dosages:
            dosage_text = ", ".join(dosages[:2])
            if weight:
                return f"Dosage: {dosage_text} (calculate for {weight}kg patient)"
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
    print("🧠 SMART CLINICAL ASSISTANT")
    print("=" * 40)
    print("Loading intelligent clinical database...")
    
    # Load components
    model, index, metadata = load_embeddings()
    if not model or not index or not metadata:
        return
    
    print("✅ Ready! Intelligent clinical guidance.")
    print("💡 Ask: 'ketamine RSI 80kg' or 'fentanyl pain 70kg'")
    print()
    
    while True:
        try:
            question = input("🧠 Q: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not question:
                continue
            
            print("🔍 Searching...")
            start_time = time.time()
            
            # Search for clinical info
            clinical_info = search_clinical_info(question, model, index, metadata)
            
            # Generate smart response
            response = generate_smart_response(question, clinical_info)
            
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