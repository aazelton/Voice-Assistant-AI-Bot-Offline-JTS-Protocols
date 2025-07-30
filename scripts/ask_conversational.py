#!/usr/bin/env python3
"""
Conversational Clinical Assistant - Human-like medical guidance
Feels like talking to a knowledgeable colleague
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

def get_conversational_response(question, clinical_info, apis, conversation_history=None):
    """Get conversational response from cloud APIs"""
    try:
        # Prepare context from clinical info
        context = " ".join(clinical_info[:2]) if clinical_info else "No specific clinical data available."
        
        # Create conversation history
        history = ""
        if conversation_history:
            recent = conversation_history[-3:]  # Last 3 exchanges
            for msg in recent:
                history += f"User: {msg.get('question', '')}\nAssistant: {msg.get('response', '')}\n"
        
        # Create conversational prompt
        prompt = f"""You are a friendly, experienced trauma nurse practitioner who's been in the field for 15+ years. You're talking to a colleague who needs quick clinical guidance. Be conversational, confident, and practical.

Use the JTS Clinical Practice Guidelines as your knowledge base, but respond like you're having a casual conversation with a fellow healthcare provider.

Context from JTS guidelines: {context}

{history}User: {question}

Respond as if you're a knowledgeable colleague giving advice. Be conversational, use "you" and "I", and include practical tips. Keep it concise but friendly."""

        # Try Gemini first, then OpenAI
        if 'gemini' in apis:
            print("🧠 Thinking...")
            response = apis['gemini'].generate_content(prompt)
            return response.text.strip()
        elif 'openai' in apis:
            print("🧠 Thinking...")
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a friendly, experienced trauma nurse practitioner. Be conversational and practical."},
                    {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
                ],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        
        return "I'd love to help, but I'm having trouble accessing my resources right now."
        
    except Exception as e:
        print(f"❌ Conversational response failed: {e}")
        return "Sorry, I'm having a moment here. Let me try a different approach."

def get_fast_conversational_response(question, clinical_info, conversation_history=None):
    """Get fast conversational response for simple queries"""
    try:
        question_lower = question.lower()
        weight = extract_weight(question)
        
        # Handle medication queries with conversational tone
        if 'ketamine' in question_lower:
            if 'rsi' in question_lower or 'induction' in question_lower:
                base_dosage = "1-2 mg/kg IV"
                if weight:
                    calculated_dose = calculate_dosage(base_dosage, weight)
                    return f"Perfect! For your {weight}kg patient, I'd go with {calculated_dose} of ketamine for RSI. That's the standard 1-2 mg/kg range - works like a charm for most cases."
                else:
                    return f"Standard ketamine for RSI is {base_dosage}. Works great for most patients - just make sure you have your airway equipment ready!"
            elif 'pain' in question_lower:
                base_dosage = "0.1-0.5 mg/kg IV"
                if weight:
                    calculated_dose = calculate_dosage(base_dosage, weight)
                    return f"For pain control, I'd start with {calculated_dose} for your {weight}kg patient. That's the 0.1-0.5 mg/kg range - much gentler than RSI doses."
                else:
                    return f"For pain, ketamine is {base_dosage}. Much lower than RSI doses - patients usually tolerate it really well."
        
        elif 'txa' in question_lower or 'tranexamic' in question_lower:
            if 'im' in question_lower:
                return "Actually, TXA isn't great IM - it can be painful and absorption is unpredictable. Stick with 1g IV bolus, then 1g over 8h. Works much better that way."
            else:
                return "TXA is straightforward - 1g IV bolus, then 1g over 8h. Great for trauma bleeding, especially if you can give it within 3 hours of injury."
        
        elif 'fentanyl' in question_lower:
            base_dosage = "1-2 mcg/kg IV"
            if weight:
                calculated_dose = calculate_dosage(base_dosage, weight)
                return f"Fentanyl for your {weight}kg patient would be {calculated_dose}. That's the 1-2 mcg/kg range - potent stuff, so start low and titrate up."
            else:
                return f"Fentanyl is {base_dosage}. Pretty potent, so I always start on the lower end and work up. Patients respond differently to it."
        
        # Return conversational clinical info if available
        if clinical_info:
            combined_text = " ".join(clinical_info)
            sentences = combined_text.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in question_lower.split()):
                    return f"Based on the protocols, {sentence.strip()[:150]}. That's what I'd go with in this situation."
        
        return "I'm not finding specific info for that, but I'd be happy to help you think through it. What's the clinical scenario you're dealing with?"
        
    except Exception as e:
        print(f"❌ Fast response failed: {e}")
        return "Sorry, I'm having trouble with that one. Let me know if you need help with something else!"

def should_use_conversational_api(question, clinical_info):
    """Determine if we should use conversational API vs fast response"""
    question_lower = question.lower()
    
    # Use fast response for:
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
    
    # Use conversational API for:
    # - Complex questions
    # - Protocol explanations
    # - Conversational queries
    conversational_patterns = [
        r'\b(how|why|what|explain|describe)\b',
        r'\b(protocol|guideline|management)\b',
        r'\b(assessment|treatment|monitoring)\b',
        r'\b(patient|case|scenario)\b',
        r'\b(help|advice|think)\b'
    ]
    
    for pattern in conversational_patterns:
        if re.search(pattern, question_lower):
            return True
    
    # Default to conversational if no clear pattern
    return True

def main():
    print("👨‍⚕️  CONVERSATIONAL CLINICAL ASSISTANT")
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
        print("⚠️  No cloud APIs available - using fast responses only")
    
    print("✅ Ready! Let's talk clinical scenarios.")
    print("💡 Ask me anything - dosages, protocols, or just bounce ideas off me")
    print("💡 Example: 'ketamine RSI 80kg' or 'what do you think about this burn case?'")
    print()
    
    conversation_history = []
    
    while True:
        try:
            question = input("👨‍⚕️  You: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q', 'bye']:
                print("👋 Take care! Let me know if you need anything else.")
                break
                
            if not question:
                continue
            
            print("🔍 Looking that up...")
            start_time = time.time()
            
            # Search for clinical info
            clinical_info = search_clinical_info(question, model, index, metadata)
            
            # Determine response method
            use_conversational = should_use_conversational_api(question, clinical_info) and apis
            
            if use_conversational:
                response = get_conversational_response(question, clinical_info, apis, conversation_history)
                method = "Conversational"
            else:
                response = get_fast_conversational_response(question, clinical_info, conversation_history)
                method = "Fast"
            
            end_time = time.time()
            
            print(f"👨‍⚕️  Me ({end_time - start_time:.1f}s): {response}")
            print()
            
            # Store conversation
            conversation_history.append({"question": question, "response": response})
            if len(conversation_history) > 5:
                conversation_history.pop(0)
            
        except KeyboardInterrupt:
            print("\n👋 Take care! Let me know if you need anything else.")
            break
        except Exception as e:
            print(f"❌ Oops, something went wrong: {e}")
            continue

if __name__ == "__main__":
    main() 