#!/usr/bin/env python3
"""
Cloud-Enhanced Clinical Assistant - Fast lookup + Cloud APIs (Gemini/GPT)
Uses cloud APIs for conversational flow when available
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

def load_cloud_apis():
    """Load cloud API clients"""
    apis = {}
    
    # Try to load Gemini
    try:
        import google.generativeai as genai
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            apis['gemini'] = model
            print("✅ Gemini API loaded")
        else:
            print("⚠️  GEMINI_API_KEY not found")
    except Exception as e:
        print(f"⚠️  Gemini API failed: {e}")
    
    # Try to load OpenAI GPT
    try:
        import openai
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            openai.api_key = openai_key
            apis['openai'] = openai
            print("✅ OpenAI API loaded")
        else:
            print("⚠️  OPENAI_API_KEY not found")
    except Exception as e:
        print(f"⚠️  OpenAI API failed: {e}")
    
    return apis

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

def get_fast_response(question, clinical_info, conversation_history=None):
    """Get fast response from lookup system"""
    try:
        question_lower = question.lower()
        weight = extract_weight(question)
        
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
        
        # Return relevant clinical info if available
        if clinical_info:
            combined_text = " ".join(clinical_info)
            sentences = combined_text.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in question_lower.split()):
                    return sentence.strip()[:150]
        
        return None  # No fast response available
        
    except Exception as e:
        print(f"❌ Fast response failed: {e}")
        return None

def get_gemini_response(question, clinical_info, gemini_model, conversation_history=None):
    """Get response from Gemini API"""
    try:
        # Prepare context
        context = " ".join(clinical_info[:2]) if clinical_info else "No specific clinical data available."
        
        # Create conversation history
        history = ""
        if conversation_history:
            recent = conversation_history[-3:]
            for msg in recent:
                history += f"User: {msg.get('question', '')}\nAssistant: {msg.get('response', '')}\n"
        
        # Create prompt
        prompt = f"""You are a clinical decision support assistant for trauma care. Use the JTS Clinical Practice Guidelines to provide accurate, concise medical advice.

Context from JTS guidelines: {context}

{history}User: {question}

Provide a clear, concise response based on the JTS guidelines. Focus on practical clinical guidance."""

        # Generate response
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"❌ Gemini response failed: {e}")
        return "I'm having trouble processing that request right now."

def get_openai_response(question, clinical_info, openai_client, conversation_history=None):
    """Get response from OpenAI API"""
    try:
        # Prepare context
        context = " ".join(clinical_info[:2]) if clinical_info else "No specific clinical data available."
        
        # Create conversation history
        messages = [
            {"role": "system", "content": "You are a clinical decision support assistant for trauma care. Use the JTS Clinical Practice Guidelines to provide accurate, concise medical advice."},
            {"role": "user", "content": f"Context from JTS guidelines: {context}\n\nUser question: {question}"}
        ]
        
        # Add recent conversation history
        if conversation_history:
            recent = conversation_history[-3:]
            for msg in recent:
                messages.append({"role": "user", "content": msg.get('question', '')})
                messages.append({"role": "assistant", "content": msg.get('response', '')})
        
        # Generate response
        client = openai.OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"❌ OpenAI response failed: {e}")
        return "I'm having trouble processing that request right now."

def should_use_cloud_api(question, clinical_info):
    """Determine if we should use cloud API vs fast lookup"""
    question_lower = question.lower()
    
    # Use fast lookup for:
    # - Simple medication queries
    # - Dosage calculations
    # - Short questions
    fast_patterns = [
        r'\b(ketamine|txa|fentanyl|morphine)\b',
        r'\b\d+\s*kg\b',
        r'\b(dose|dosage|mg|mcg)\b',
        r'^\w+\s+\w+$'  # Very short questions
    ]
    
    for pattern in fast_patterns:
        if re.search(pattern, question_lower):
            return False
    
    # Use cloud API for:
    # - Complex questions
    # - Protocol explanations
    # - Conversational queries
    api_patterns = [
        r'\b(how|why|what|explain|describe)\b',
        r'\b(protocol|guideline|management)\b',
        r'\b(assessment|treatment|monitoring)\b',
        r'\b(patient|case|scenario)\b'
    ]
    
    for pattern in api_patterns:
        if re.search(pattern, question_lower):
            return True
    
    # Default to fast lookup if no clear pattern
    return False

def main():
    print("☁️  CLOUD-ENHANCED CLINICAL ASSISTANT")
    print("=" * 45)
    print("Loading components...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Load components
    model, index, metadata = load_embeddings()
    if not model or not index or not metadata:
        return
    
    apis = load_cloud_apis()
    if not apis:
        print("⚠️  No cloud APIs available - using fast lookup only")
    
    print("✅ Ready! Cloud-enhanced clinical guidance.")
    print("💡 Fast lookup for dosages, Cloud APIs for complex questions")
    print("💡 Ask: 'ketamine RSI 80kg' or 'explain snake bite protocol'")
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
            
            print("🔍 Searching...")
            start_time = time.time()
            
            # Search for clinical info
            clinical_info = search_clinical_info(question, model, index, metadata)
            
            # Determine response method
            use_api = should_use_cloud_api(question, clinical_info) and apis
            
            if use_api:
                # Try Gemini first, then OpenAI
                if 'gemini' in apis:
                    print("☁️  Using Gemini API...")
                    response = get_gemini_response(question, clinical_info, apis['gemini'], conversation_history)
                    api_used = "Gemini"
                elif 'openai' in apis:
                    print("☁️  Using OpenAI API...")
                    response = get_openai_response(question, clinical_info, apis['openai'], conversation_history)
                    api_used = "OpenAI"
                else:
                    response = "No cloud APIs available."
                    api_used = "None"
            else:
                print("⚡ Using fast lookup...")
                response = get_fast_response(question, clinical_info, conversation_history)
                if not response:
                    # Fallback to cloud API if available
                    if apis:
                        if 'gemini' in apis:
                            print("☁️  Falling back to Gemini...")
                            response = get_gemini_response(question, clinical_info, apis['gemini'], conversation_history)
                            api_used = "Gemini"
                        elif 'openai' in apis:
                            print("☁️  Falling back to OpenAI...")
                            response = get_openai_response(question, clinical_info, apis['openai'], conversation_history)
                            api_used = "OpenAI"
                    else:
                        response = "I don't have specific information for that query."
                        api_used = "None"
                else:
                    api_used = "Fast"
            
            end_time = time.time()
            
            print(f"📋 A ({end_time - start_time:.1f}s) [{api_used}]: {response}")
            print()
            
            # Store conversation
            conversation_history.append({"question": question, "response": response})
            if len(conversation_history) > 5:
                conversation_history.pop(0)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

if __name__ == "__main__":
    main() 