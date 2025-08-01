#!/usr/bin/env python3
"""
Voice JTS Assistant - VM Direct Version
Designed to run directly on VM with full JTS database access
"""

import os
import sys
import time
import json
import subprocess
import speech_recognition as sr
from openai import OpenAI
import tempfile

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
            recognizer.pause_threshold = 2.5
            recognizer.energy_threshold = 300
        
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
    """Speak the response using available TTS"""
    try:
        text_for_tts = convert_medical_abbreviations(text)
        
        # Try OpenAI TTS first
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
                
                # Play audio (works on VM with mpg123)
                subprocess.run(['mpg123', f.name], check=True)
                os.unlink(f.name)
                print("🔊 Natural voice played successfully")
                return
        
        # Fallback to espeak-ng (available on VM)
        subprocess.run(['espeak-ng', text_for_tts], check=True)
        print("🔊 Voice played successfully")
            
    except Exception as e:
        print(f"❌ TTS failed: {e}")
        print(f"📝 Response: {text}")

def listen_for_speech(recognizer, microphone, timeout=30):
    """Listen for speech input"""
    try:
        with microphone as source:
            print("🎤 Listening... (speak now)")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=45)
            
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

def query_jts_database(question):
    """Query the full JTS database directly"""
    try:
        print("🔍 Querying full JTS database...")
        
        # Use the ask_balanced.py script directly
        cmd = f"echo '{question}' | python3 scripts/ask_balanced.py"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"❌ JTS query error: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ JTS query timeout")
        return None
    except Exception as e:
        print(f"❌ JTS query error: {e}")
        return None

def get_ai_enhanced_response(question, jts_response=None, conversation_history=None):
    """Get AI-enhanced response with full JTS knowledge"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jts_response or "Need OpenAI API key for enhanced responses"
        
        client = OpenAI(api_key=api_key)
        
        # Build context with JTS response
        context_str = f"JTS Database Response: {jts_response[:500]}..." if jts_response else "No JTS data available"
        
        SYSTEM_PROMPT = f"""You are a calm, experienced paramedic assisting another paramedic in the field. Your job is to provide direct, calculated answers using the full JTS database.

Context: {context_str}

CRITICAL RULES:
- Answer ONLY what was asked - no extra information
- Use JTS database information when available
- Calculate total doses when weight is provided
- NO cautions, contraindications, or warnings unless specifically asked
- Keep responses under 50 words
- Use simple bullet points
- Convert mg/kg to total mg for the patient

Format responses as:
- Drug: X mg (total dose)
- Route: IV/IM"""

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        if conversation_history:
            messages.extend(conversation_history[-4:])
        
        messages.append({"role": "user", "content": question})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=150,
            temperature=0.1
        )
        
        assistant_reply = response.choices[0].message.content
        
        if conversation_history is not None:
            conversation_history.append({"role": "user", "content": question})
            conversation_history.append({"role": "assistant", "content": assistant_reply})
            
            if len(conversation_history) > 6:
                conversation_history = conversation_history[-6:]
        
        return assistant_reply
        
    except Exception as e:
        print(f"❌ AI error: {e}")
        return jts_response or "Error processing response"

def main():
    """Main voice assistant loop"""
    print("🎤 VOICE JTS ASSISTANT (VM DIRECT)")
    print("=" * 50)
    print("Voice + Full JTS Database on VM")
    print("🎤 Initializing speech recognition...")
    
    # Initialize speech recognition
    recognizer, microphone = init_speech_recognition()
    if not recognizer or not microphone:
        print("❌ Failed to initialize speech recognition")
        return
    
    # Initialize conversation tracking
    conversation_history = []
    
    print("✅ Ready! Ask for clinical guidance using full JTS database.")
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
            
            # Query full JTS database
            jts_response = query_jts_database(question)
            
            # Generate AI-enhanced response
            response = get_ai_enhanced_response(question, jts_response, conversation_history)
            
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