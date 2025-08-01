#!/usr/bin/env python3
"""
Voice-Enabled Clinical Assistant - Force Voice Mode
Debugging version to ensure voice is working
"""

import os
import sys
import json
import time
import re
import subprocess
import speech_recognition as sr
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

def init_speech_recognition():
    """Initialize speech recognition with debugging"""
    print("🎤 Initializing speech recognition...")
    
    try:
        # Test PyAudio
        import pyaudio
        print("✅ PyAudio imported successfully")
        
        # List audio devices
        p = pyaudio.PyAudio()
        print(f"📻 Found {p.get_device_count()} audio devices:")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            print(f"  Device {i}: {info['name']} (inputs: {info['maxInputChannels']})")
        p.terminate()
        
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 3000  # Lower threshold
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.8
        
        # Use default microphone
        microphone = sr.Microphone()
        print("✅ Microphone initialized")
        
        # Adjust for ambient noise
        with microphone as source:
            print("🎤 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
        
        print("✅ Speech recognition ready")
        return recognizer, microphone
        
    except ImportError as e:
        print(f"❌ PyAudio not installed: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Speech recognition failed: {e}")
        return None, None

def speak_response(text, tts_engine="espeak"):
    """Convert text to speech"""
    try:
        if tts_engine == "espeak":
            # Use eSpeak-ng for TTS
            subprocess.run([
                "espeak-ng",
                "-v", "en-us",
                "-s", "150",
                "-a", "200",
                text
            ], check=True)
        elif tts_engine == "gtts":
            # Use Google TTS
            from gtts import gTTS
            import tempfile
            
            tts = gTTS(text=text, lang='en', slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                tts.save(f.name)
                temp_file = f.name
            
            subprocess.run(["mpg123", temp_file], check=True)
            os.unlink(temp_file)
        else:
            print(f"Text: {text}")
            
    except Exception as e:
        print(f"❌ TTS failed: {e}")
        print(f"Text: {text}")

def listen_for_speech(recognizer, microphone, timeout=10):
    """Listen for speech input with better error handling"""
    try:
        with microphone as source:
            print("🎤 Listening... (speak now)")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            try:
                text = recognizer.recognize_google(audio)
                print(f"👤 You said: '{text}'")
                return text
            except sr.UnknownValueError:
                print("❌ Could not understand audio - try speaking louder")
                return None
            except sr.RequestError as e:
                print(f"❌ Speech recognition service error: {e}")
                return None
                
    except sr.WaitTimeoutError:
        print("⏰ No speech detected within timeout")
        return None
    except Exception as e:
        print(f"❌ Listening error: {e}")
        return None

def get_fast_direct_response(question, clinical_info, conversation_history=None):
    """Get fast, direct response for simple queries"""
    try:
        question_lower = question.lower()
        
        # Extract weight
        weight_match = re.search(r'(\d+(?:\.\d+)?)\s*kg', question_lower)
        weight = float(weight_match.group(1)) if weight_match else None
        
        # Handle medication queries with direct tone
        if 'ketamine' in question_lower:
            if 'rsi' in question_lower or 'induction' in question_lower:
                base_dosage = "1-2 mg/kg IV"
                if weight:
                    min_dose = 1 * weight
                    max_dose = 2 * weight
                    return f"Ketamine RSI: {min_dose:.1f}-{max_dose:.1f}mg for your {weight}kg patient."
                else:
                    return f"Ketamine RSI: {base_dosage}. Have airway equipment ready."
            elif 'pain' in question_lower:
                base_dosage = "0.1-0.5 mg/kg IV"
                if weight:
                    min_dose = 0.1 * weight
                    max_dose = 0.5 * weight
                    return f"Ketamine pain: {min_dose:.1f}-{max_dose:.1f}mg for your {weight}kg patient."
                else:
                    return f"Ketamine pain: {base_dosage}. Much gentler than RSI doses."
        
        elif 'txa' in question_lower or 'tranexamic' in question_lower:
            if 'im' in question_lower:
                return "TXA: Avoid IM - use 1g IV bolus, then 1g over 8h."
            else:
                return "TXA: 1g IV bolus, then 1g over 8h. Best within 3h of injury."
        
        elif 'fentanyl' in question_lower:
            base_dosage = "1-2 mcg/kg IV"
            if weight:
                min_dose = 1 * weight
                max_dose = 2 * weight
                return f"Fentanyl: {min_dose:.1f}-{max_dose:.1f}mcg for your {weight}kg patient. Start low, titrate up."
            else:
                return f"Fentanyl: {base_dosage}. Start low, titrate up."
        
        elif 'rocuronium' in question_lower or 'roc' in question_lower:
            base_dosage = "1 mg/kg IV"
            if weight:
                dose = 1 * weight
                return f"Rocuronium: {dose:.1f}mg for your {weight}kg patient. Have airway ready."
            else:
                return f"Rocuronium: {base_dosage}. Have airway management ready."
        
        elif 'side effects' in question_lower or 'lookout' in question_lower:
            if 'ketamine' in question_lower:
                return "Ketamine: Watch for emergence reactions, BP changes, and increased secretions. Have suction ready."
            elif 'txa' in question_lower:
                return "TXA: Monitor for thrombosis, seizures, and allergic reactions."
            elif 'fentanyl' in question_lower:
                return "Fentanyl: Watch for respiratory depression, hypotension, and chest wall rigidity."
        
        # Return direct clinical info if available
        if clinical_info:
            combined_text = " ".join(clinical_info)
            sentences = combined_text.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in question_lower.split()):
                    return f"Protocol: {sentence.strip()[:100]}."
        
        return "I don't have specific info for that. What's the clinical scenario?"
        
    except Exception as e:
        print(f"❌ Fast response failed: {e}")
        return "Sorry, I'm having trouble with that one."

def main():
    print("🎤 VOICE-ENABLED CLINICAL ASSISTANT (FORCE VOICE)")
    print("=" * 50)
    print("Loading components...")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed - using system environment")
    
    # Load components
    model, index, metadata = load_embeddings()
    if not model or not index or not metadata:
        return
    
    apis = load_cloud_apis()
    if not apis:
        print("⚠️  No cloud APIs available - using fast responses only")
    
    # Initialize speech recognition
    recognizer, microphone = init_speech_recognition()
    if not recognizer or not microphone:
        print("❌ Speech recognition failed - cannot continue in force voice mode")
        return
    
    print("✅ Ready! Ask clinical questions by voice.")
    print("💡 Say 'quit' to exit")
    print()
    
    conversation_history = []
    tts_engine = "espeak"
    
    while True:
        try:
            # Force voice input
            question = listen_for_speech(recognizer, microphone)
            if not question:
                print("Please try speaking again...")
                continue
            
            if question.lower() in ['quit', 'exit', 'q', 'bye', 'stop']:
                speak_response("Goodbye! Take care.", tts_engine)
                break
                
            print("🔍 Looking that up...")
            start_time = time.time()
            
            # Search for clinical info
            clinical_info = search_clinical_info(question, model, index, metadata)
            
            # Get response (simplified for voice)
            response = get_fast_direct_response(question, clinical_info, conversation_history)
            
            end_time = time.time()
            
            # Display and speak response
            print(f"🤖 Me ({end_time - start_time:.1f}s): {response}")
            speak_response(response, tts_engine)
            print()
            
            # Store conversation
            conversation_history.append({"question": question, "response": response})
            if len(conversation_history) > 3:
                conversation_history.pop(0)
            
        except KeyboardInterrupt:
            print("\n👋 Take care!")
            break
        except Exception as e:
            print(f"❌ Oops, something went wrong: {e}")
            continue

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

if __name__ == "__main__":
    main() 