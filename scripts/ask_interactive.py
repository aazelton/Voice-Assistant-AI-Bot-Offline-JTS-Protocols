#!/usr/bin/env python3
"""
Interactive Clinical Assistant - Multi-step protocol guidance
Handles complex topics with conversation flow
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

def search_clinical_info(question, model, index, metadata, top_k=5):
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
            if 'pound' in question.lower() or 'lb' in question.lower():
                weight = weight * 0.453592
            return weight
    return None

def calculate_dosage(base_dosage, weight):
    """Calculate actual dosage based on weight"""
    try:
        numbers = re.findall(r'\d+(?:\.\d+)?', base_dosage)
        if len(numbers) >= 2:
            min_dose = float(numbers[0])
            max_dose = float(numbers[1])
            
            min_total = min_dose * weight
            max_total = max_dose * weight
            
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

def get_protocol_topics(clinical_info):
    """Extract available protocol topics from clinical info"""
    topics = []
    combined_text = " ".join(clinical_info).lower()
    
    # Common protocol topics
    topic_patterns = [
        'assessment', 'diagnosis', 'treatment', 'management', 'monitoring',
        'antivenom', 'analgesia', 'airway', 'breathing', 'circulation',
        'wound care', 'antibiotics', 'tetanus', 'surgery', 'observation',
        'discharge', 'follow-up', 'complications', 'prevention'
    ]
    
    for topic in topic_patterns:
        if topic in combined_text:
            topics.append(topic)
    
    return topics

def get_current_topic(conversation_history):
    """Extract current topic from conversation history"""
    if not conversation_history:
        return None
    
    # Look for topic keywords in recent conversation
    recent_text = " ".join([msg.get("question", "").lower() + " " + msg.get("response", "").lower() 
                           for msg in conversation_history[-3:]])
    
    topics = {
        'snake': ['snake', 'envenomation', 'bite'],
        'burn': ['burn', 'thermal'],
        'trauma': ['trauma', 'injury', 'fracture'],
        'medication': ['ketamine', 'txa', 'fentanyl', 'morphine', 'medication']
    }
    
    for topic, keywords in topics.items():
        if any(keyword in recent_text for keyword in keywords):
            return topic
    
    return None

def generate_interactive_response(question, clinical_info, conversation_history=None):
    """Generate interactive response with protocol guidance"""
    try:
        question_lower = question.lower()
        weight = extract_weight(question)
        current_topic = get_current_topic(conversation_history or [])
        
        # Handle short responses with context
        if len(question.split()) <= 2 and current_topic:
            if current_topic == 'snake':
                if 'treatment' in question_lower:
                    return "Snake bite treatment: Immobilize limb, mark swelling progression, IV access, pain control, antivenom if indicated."
                elif 'assessment' in question_lower:
                    return "Snake bite assessment: Check airway, breathing, circulation. Look for fang marks, swelling, pain. Monitor for systemic symptoms (nausea, weakness, bleeding)."
                elif 'antivenom' in question_lower:
                    return "Snake bite antivenom: Administer based on severity. Monitor for allergic reactions. Keep patient for observation."
                elif 'monitoring' in question_lower:
                    return "Snake bite monitoring: Vital signs q15min, swelling progression, neuro status, coagulation studies, renal function."
                else:
                    return "Snake bite protocol. What do you need?\n- Assessment\n- Treatment\n- Antivenom\n- Monitoring"
            
            elif current_topic == 'burn':
                if 'treatment' in question_lower:
                    return "Burn treatment: Cool burn, remove jewelry, cover with clean dressing, pain control, fluid resuscitation if needed."
                elif 'assessment' in question_lower:
                    return "Burn assessment: Calculate TBSA, depth, location. Check for inhalation injury, associated trauma."
                elif 'fluid' in question_lower:
                    base_formula = "Parkland formula: 4ml × TBSA% × weight(kg) over 24h"
                    if weight:
                        return f"{base_formula}\nFor {weight}kg patient: Calculate based on TBSA%"
                    return base_formula
        
        # Handle complex topics that need protocol guidance
        if any(topic in question_lower for topic in ['snake', 'envenomation', 'bite']):
            topics = get_protocol_topics(clinical_info)
            if topics:
                return f"Snake bite protocol available. What specific aspect do you need?\nOptions: {', '.join(topics[:5])}\n\nAsk: 'snake bite assessment' or 'snake bite antivenom'"
            else:
                return "Snake bite protocol found. What do you need to know?\n- Assessment\n- Treatment\n- Antivenom\n- Monitoring\n\nAsk: 'snake bite treatment' or 'snake bite assessment'"
        
        # Handle specific snake bite topics
        if 'snake' in question_lower:
            if 'assessment' in question_lower:
                return "Snake bite assessment: Check airway, breathing, circulation. Look for fang marks, swelling, pain. Monitor for systemic symptoms (nausea, weakness, bleeding)."
            elif 'antivenom' in question_lower:
                return "Snake bite antivenom: Administer based on severity. Monitor for allergic reactions. Keep patient for observation."
            elif 'treatment' in question_lower:
                return "Snake bite treatment: Immobilize limb, mark swelling progression, IV access, pain control, antivenom if indicated."
            elif 'monitoring' in question_lower:
                return "Snake bite monitoring: Vital signs q15min, swelling progression, neuro status, coagulation studies, renal function."
        
        # Handle other complex topics
        if 'burn' in question_lower:
            if 'assessment' in question_lower:
                return "Burn assessment: Calculate TBSA, depth, location. Check for inhalation injury, associated trauma."
            elif 'fluid' in question_lower or 'resuscitation' in question_lower:
                base_formula = "Parkland formula: 4ml × TBSA% × weight(kg) over 24h"
                if weight:
                    return f"{base_formula}\nFor {weight}kg patient: Calculate based on TBSA%"
                return base_formula
        
        # Handle medication queries with weight calculations
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
        
        elif 'txa' in question_lower or 'tranexamic' in question_lower:
            if 'im' in question_lower:
                return "TXA: Not recommended IM. Use 1g IV bolus, then 1g over 8h"
            else:
                return "TXA: 1g IV bolus, then 1g over 8h"
        
        elif 'fentanyl' in question_lower:
            base_dosage = "1-2 mcg/kg IV"
            if weight:
                calculated_dose = calculate_dosage(base_dosage, weight)
                return f"Fentanyl: {base_dosage} = {calculated_dose} for {weight}kg patient"
            else:
                return f"Fentanyl: {base_dosage}"
        
        # General protocol guidance
        if any(word in question_lower for word in ['protocol', 'guideline', 'management']):
            topics = get_protocol_topics(clinical_info)
            if topics:
                return f"Protocol available. What specific aspect?\nOptions: {', '.join(topics[:5])}"
        
        # Fallback: return relevant clinical info
        if clinical_info:
            # Return first relevant sentence
            combined_text = " ".join(clinical_info)
            sentences = combined_text.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in question_lower.split()):
                    return sentence.strip()[:150]
        
        return "Protocol found. What specific information do you need? Try asking about assessment, treatment, or monitoring."
        
    except Exception as e:
        print(f"❌ Response generation failed: {e}")
        return "Error processing clinical information"

def main():
    print("💬 INTERACTIVE CLINICAL ASSISTANT")
    print("=" * 45)
    print("Loading clinical database...")
    
    # Load components
    model, index, metadata = load_embeddings()
    if not model or not index or not metadata:
        return
    
    print("✅ Ready! Interactive clinical guidance.")
    print("💡 Ask: 'snake bite' then follow prompts")
    print("💡 Or: 'ketamine RSI 80kg' for direct answers")
    print()
    
    conversation_history = []
    
    while True:
        try:
            question = input("💬 Q: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not question:
                continue
            
            print("🔍 Searching protocols...")
            start_time = time.time()
            
            # Search for clinical info
            clinical_info = search_clinical_info(question, model, index, metadata)
            
            # Generate interactive response
            response = generate_interactive_response(question, clinical_info, conversation_history)
            
            end_time = time.time()
            
            print(f"📋 A ({end_time - start_time:.1f}s): {response}")
            print()
            
            # Store conversation
            conversation_history.append({"question": question, "response": response})
            if len(conversation_history) > 5:  # Keep last 5 exchanges
                conversation_history.pop(0)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

if __name__ == "__main__":
    main() 