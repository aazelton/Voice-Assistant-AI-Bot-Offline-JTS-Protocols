#!/usr/bin/env python3
"""
Voice JTS Assistant - Combines voice interface with JTS knowledge base
Uses local voice processing + remote knowledge base queries
"""

import os
import sys
import time
import json
import subprocess
import speech_recognition as sr
from openai import OpenAI
import google.generativeai as genai
import tempfile
import shlex

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import API keys
try:
    from config.api_keys import OPENAI_API_KEY, GEMINI_API_KEY
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
    os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY
except ImportError:
    print("⚠️  API keys not found, using environment variables")

def init_speech_recognition():
    """Initialize speech recognition"""
    try:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        print("🎤 Initializing speech recognition...")
        
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("✅ Microphone initialized")
        print("🎤 Adjusting for ambient noise...")
        
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)
        
        print("✅ Speech recognition ready")
        return recognizer, microphone
        
    except Exception as e:
        print(f"❌ Speech recognition failed: {e}")
        return None, None

def convert_medical_abbreviations(text):
    """Convert medical abbreviations for better TTS pronunciation"""
    replacements = {
        'mg': 'milligrams',
        'kg': 'kilograms',
        'mcg': 'micrograms',
        'ml': 'milliliters',
        'iv': 'intravenous',
        'im': 'intramuscular',
        'rsi': 'rapid sequence intubation',
        'txa': 'tranexamic acid',
        'prn': 'as needed',
        'q': 'every',
        'bid': 'twice daily',
        'tid': 'three times daily',
        'qd': 'once daily'
    }
    
    for abbrev, full in replacements.items():
        text = text.replace(f' {abbrev} ', f' {full} ')
        text = text.replace(f'{abbrev} ', f'{full} ')
        text = text.replace(f' {abbrev}', f' {full}')
    
    return text

def speak_response(text):
    """Speak the response using OpenAI TTS with fallback"""
    try:
        # Convert medical abbreviations for better pronunciation
        text_for_tts = convert_medical_abbreviations(text)
        
        # Try OpenAI TTS first (better quality)
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            client = OpenAI(api_key=api_key)
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                response = client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=text_for_tts
                )
                response.write_to_file(f.name)
                
                # Play on Mac
                subprocess.run(['afplay', f.name], check=True)
                os.unlink(f.name)
                print("🔊 Natural voice played successfully")
                return
        
        # Fallback to gTTS
        from gtts import gTTS
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tts = gTTS(text=text_for_tts, lang='en', slow=False)
            tts.save(f.name)
            subprocess.run(['afplay', f.name], check=True)
            os.unlink(f.name)
            print("🔊 Voice played successfully")
            
    except Exception as e:
        print(f"❌ TTS failed: {e}")
        print(f"📝 Response: {text}")

def listen_for_speech(recognizer, microphone, timeout=20):
    """Listen for speech input"""
    try:
        with microphone as source:
            print("🎤 Listening... (speak now)")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=30)
            
        text = recognizer.recognize_google(audio)
        print(f"👤 You said: '{text}'")
        return text.lower()
        
    except sr.WaitTimeoutError:
        print("❌ No speech detected within timeout")
        return None
    except sr.UnknownValueError:
        print("❌ Could not understand audio - try speaking louder")
        return None
    except sr.RequestError as e:
        print(f"❌ Speech recognition error: {e}")
        return None

def extract_weight_and_drug(text):
    """Extract weight and drug from text"""
    import re
    
    # Weight patterns
    weight_patterns = [
        r'(\d+)\s*kg',
        r'(\d+)\s*kilograms',
        r'(\d+)\s*kilos',
        r'patient\s+weighs\s+(\d+)',
        r'(\d+)\s*kg\s+patient',
        r'patient\s+(\d+)\s*kg'
    ]
    
    # Drug patterns
    drugs = {
        'ketamine': 'ketamine',
        'ket': 'ketamine',
        'rocuronium': 'rocuronium',
        'roc': 'rocuronium',
        'rock': 'rocuronium',
        'succinylcholine': 'succinylcholine',
        'succ': 'succinylcholine',
        'fentanyl': 'fentanyl',
        'fent': 'fentanyl',
        'morphine': 'morphine',
        'midazolam': 'midazolam',
        'midaz': 'midazolam',
        'propofol': 'propofol',
        'etomidate': 'etomidate',
        'tranexamic acid': 'tranexamic acid',
        'txa': 'tranexamic acid',
        'calcium': 'calcium gluconate',
        'furosemide': 'furosemide',
        'lasix': 'furosemide'
    }
    
    weight = None
    drug = None
    
    # Extract weight
    for pattern in weight_patterns:
        match = re.search(pattern, text.lower())
        if match:
            weight = float(match.group(1))
            break
    
    # Extract drug
    text_lower = text.lower()
    for drug_key, drug_name in drugs.items():
        if drug_key in text_lower:
            drug = drug_name
            break
    
    return weight, drug

def query_jts_knowledge_base(question, vm_ip="10.128.0.2", vm_user="akaclinicalco"):
    """Query the JTS knowledge base on the VM via SSH"""
    try:
        # Create a temporary file for the question
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(question)
            temp_file = f.name
        
        # SSH command to query the knowledge base
        ssh_cmd = f"ssh {vm_user}@{vm_ip} 'cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols && source venv/bin/activate && echo \"{question}\" | python3 scripts/ask_balanced.py'"
        
        print(f"🔍 Querying JTS knowledge base...")
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        # Clean up temp file
        os.unlink(temp_file)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"❌ SSH error: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ SSH timeout")
        return None
    except Exception as e:
        print(f"❌ SSH error: {e}")
        return None

def get_ai_enhanced_response(question, weight=None, drug=None, jts_response=None, conversation_history=None):
    """Get AI-enhanced response combining dose calculation and JTS knowledge"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return get_fallback_response(question, weight, drug, jts_response)
        
        client = OpenAI(api_key=api_key)
        
        # Build context information
        context_info = []
        if weight:
            context_info.append(f"Patient weight: {weight} kg")
        if drug:
            context_info.append(f"Drug: {drug}")
        if jts_response:
            context_info.append(f"JTS Protocol: {jts_response[:200]}...")
        
        context_str = "\n".join(context_info) if context_info else "No specific context"
        
        SYSTEM_PROMPT = f"""You are a calm, experienced paramedic assisting another paramedic in the field. Your job is to provide accurate, brief, and helpful advice in a stressful prehospital environment.

Context: {context_str}

IMPORTANT RULES:
- Be concise and tactical - time is critical
- Use bullet points for medication responses
- If weight and drug are provided, calculate the total dose
- If JTS protocol info is available, reference it
- Keep responses under 100 words
- Use tactical language appropriate for emergency medicine
- If information is incomplete, ask for what's missing

Format medication responses as:
- Drug: X mg (Y mg/kg)
- Route: IV/IM
- Caution: [key warnings]"""

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history if available
        if conversation_history:
            messages.extend(conversation_history[-4:])  # Last 2 exchanges
        
        messages.append({"role": "user", "content": question})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=150,
            temperature=0.1
        )
        
        assistant_reply = response.choices[0].message.content
        
        # Update conversation history
        if conversation_history is not None:
            conversation_history.append({"role": "user", "content": question})
            conversation_history.append({"role": "assistant", "content": assistant_reply})
            
            # Keep only last 6 messages to prevent memory bloat
            if len(conversation_history) > 6:
                conversation_history = conversation_history[-6:]
        
        return assistant_reply
        
    except Exception as e:
        print(f"❌ AI error: {e}")
        return get_fallback_response(question, weight, drug, jts_response)

def get_fallback_response(question, weight=None, drug=None, jts_response=None):
    """Fallback response when AI is unavailable"""
    if weight and drug:
        return f"Patient: {weight} kg, Drug: {drug}. Please consult JTS protocols for dosing."
    elif jts_response:
        return f"JTS Protocol: {jts_response[:100]}..."
    else:
        return "I need more information. Please specify patient weight and medication."

def main():
    """Main voice assistant loop"""
    print("🎤 VOICE JTS ASSISTANT")
    print("=" * 50)
    print("Voice + JTS Knowledge Base Integration")
    print("🎤 Initializing speech recognition...")
    
    # Initialize speech recognition
    recognizer, microphone = init_speech_recognition()
    if not recognizer or not microphone:
        print("❌ Failed to initialize speech recognition")
        return
    
    # Initialize conversation tracking
    conversation_history = []
    
    # Context memory for multi-turn conversations
    context = {
        'weight': None,
        'drug': None,
        'indication': None,
        'last_question': None
    }
    
    print("✅ Ready! Ask for drug doses or clinical guidance.")
    print("💡 Try: 'Ketamine RSI for 80 kg patient', 'TXA protocol', 'Goodbye'")
    
    while True:
        try:
            # Listen for speech
            question = listen_for_speech(recognizer, microphone)
            if not question:
                print("Please try speaking again...")
                continue
            
            if 'goodbye' in question or 'exit' in question or 'quit' in question:
                print("👋 Take care!")
                break
                
            print("🧠 Processing...")
            start_time = time.time()
            
            # Extract weight and drug from current question
            weight, drug = extract_weight_and_drug(question)
            
            # Update context with new information
            if weight:
                context['weight'] = weight
                print(f"💾 Remembered weight: {weight} kg")
            if drug:
                context['drug'] = drug
                print(f"💾 Remembered drug: {drug}")
            
            # Determine indication from question
            question_lower = question.lower()
            if 'rsi' in question_lower or 'rapid sequence' in question_lower:
                context['indication'] = 'rsi'
            elif 'pain' in question_lower:
                context['indication'] = 'pain'
            elif 'trauma' in question_lower:
                context['indication'] = 'trauma'
            elif 'sedation' in question_lower:
                context['indication'] = 'sedation'
            
            context['last_question'] = question
            
            # Show current context
            if context['weight']:
                print(f"📋 Current context: {context['weight']} kg patient")
            
            # Use context to fill in missing information
            final_weight = weight or context['weight']
            final_drug = drug or context['drug']
            final_indication = context['indication']
            
            # Query JTS knowledge base for clinical guidance
            jts_response = None
            if 'protocol' in question.lower() or 'guideline' in question.lower() or final_drug:
                print("🔍 Querying JTS knowledge base...")
                jts_response = query_jts_knowledge_base(question)
                if jts_response:
                    print("✅ JTS data retrieved")
                else:
                    print("⚠️  JTS query failed, using local knowledge")
            
            # Generate response combining local dose calculation and JTS knowledge
            response = get_ai_enhanced_response(
                question, 
                final_weight, 
                final_drug, 
                jts_response, 
                conversation_history
            )
            
            processing_time = time.time() - start_time
            print(f"🤖 Me ({processing_time:.1f}s): {response}")
            
            # Speak response
            speak_response(response)
            
        except KeyboardInterrupt:
            print("\n👋 Take care!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            speak_response("Sorry, I encountered an error. Please try again.")

if __name__ == "__main__":
    main() 