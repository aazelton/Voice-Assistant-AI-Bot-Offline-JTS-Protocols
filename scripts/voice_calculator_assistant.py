#!/usr/bin/env python3
"""
Smart Voice Calculator Assistant
Automatically calculates drug dosages based on patient weight
"""

import speech_recognition as sr
import subprocess
import time
import os
import re
from openai import OpenAI
import google.generativeai as genai

# Load API keys from config
try:
    import sys
    sys.path.append('config')
    from api_keys import OPENAI_API_KEY, GEMINI_API_KEY
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
    os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY
except ImportError:
    pass  # Use environment variables if config not available

def init_speech_recognition():
    """Initialize speech recognition with extended timing"""
    print("🎤 Initializing speech recognition...")
    
    try:
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 3000
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 2.5  # Much longer pause threshold
        
        microphone = sr.Microphone()
        print("✅ Microphone initialized")
        
        # Adjust for ambient noise
        with microphone as source:
            print("🎤 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
        
        print("✅ Speech recognition ready")
        return recognizer, microphone
        
    except Exception as e:
        print(f"❌ Speech recognition failed: {e}")
        return None, None

def speak_response(text):
    """Convert text to speech using Mac-optimized approach"""
    try:
        from gtts import gTTS
        import tempfile
        
        tts = gTTS(text=text, lang='en', slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            tts.save(f.name)
            temp_file = f.name
        
        # Use afplay (Mac's built-in audio player)
        try:
            subprocess.run(["afplay", temp_file], check=True, capture_output=True)
            print("🔊 Audio played successfully")
        except subprocess.CalledProcessError:
            print("🔊 Audio output failed, but text response shown")
        
        # Clean up
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"❌ TTS failed: {e}")
        print(f"Text: {text}")

def listen_for_speech(recognizer, microphone, timeout=20):
    """Listen for speech input with extended timing"""
    try:
        with microphone as source:
            print("🎤 Listening... (speak now)")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=30)
            
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

def extract_weight_and_drug(text):
    """Extract patient weight and drug from speech"""
    text_lower = text.lower()
    
    # Extract weight (look for numbers followed by kg, kilograms, etc.)
    weight_patterns = [
        r'(\d+)\s*(?:kg|kilos?|kilograms?)',
        r'(\d+)\s*(?:pounds?|lbs?)',
        r'weighs?\s*(\d+)',
        r'(\d+)\s*(?:kg|kilos?|kilograms?)\s*patient',
        r'patient\s*(\d+)\s*(?:kg|kilos?|kilograms?)'
    ]
    
    weight = None
    for pattern in weight_patterns:
        match = re.search(pattern, text_lower)
        if match:
            weight = int(match.group(1))
            break
    
    # Extract drug name
    drugs = {
        'ketamine': 'ketamine',
        'ket': 'ketamine',
        'rocuronium': 'rocuronium',
        'rocur': 'rocuronium',
        'roc': 'rocuronium',
        'succinylcholine': 'succinylcholine',
        'succ': 'succinylcholine',
        'succs': 'succinylcholine',
        'fentanyl': 'fentanyl',
        'fent': 'fentanyl',
        'morphine': 'morphine',
        'morph': 'morphine',
        'midazolam': 'midazolam',
        'versed': 'midazolam',
        'propofol': 'propofol',
        'prop': 'propofol',
        'etomidate': 'etomidate',
        'etom': 'etomidate',
        'txa': 'tranexamic acid',
        'tranexamic': 'tranexamic acid',
        'tranexamic acid': 'tranexamic acid'
    }
    
    drug = None
    for drug_key, drug_name in drugs.items():
        if drug_key in text_lower:
            drug = drug_name
            break
    
    return weight, drug

def calculate_dose(drug, weight_kg, indication="general"):
    """Calculate drug dose based on weight and indication"""
    
    # Standard dosing protocols
    dosing_protocols = {
        'ketamine': {
            'rsi': {'dose': 1.5, 'unit': 'mg/kg', 'max': 200},
            'pain': {'dose': 0.3, 'unit': 'mg/kg', 'max': 50},
            'sedation': {'dose': 1.0, 'unit': 'mg/kg', 'max': 100}
        },
        'rocuronium': {
            'rsi': {'dose': 1.2, 'unit': 'mg/kg', 'max': 120},
            'general': {'dose': 0.6, 'unit': 'mg/kg', 'max': 60}
        },
        'succinylcholine': {
            'rsi': {'dose': 1.5, 'unit': 'mg/kg', 'max': 150}
        },
        'fentanyl': {
            'pain': {'dose': 1.0, 'unit': 'mcg/kg', 'max': 100},
            'rsi': {'dose': 2.0, 'unit': 'mcg/kg', 'max': 200}
        },
        'morphine': {
            'pain': {'dose': 0.1, 'unit': 'mg/kg', 'max': 10}
        },
        'midazolam': {
            'sedation': {'dose': 0.05, 'unit': 'mg/kg', 'max': 5},
            'rsi': {'dose': 0.1, 'unit': 'mg/kg', 'max': 10}
        },
        'propofol': {
            'induction': {'dose': 2.0, 'unit': 'mg/kg', 'max': 200},
            'sedation': {'dose': 0.5, 'unit': 'mg/kg', 'max': 50}
        },
        'etomidate': {
            'rsi': {'dose': 0.3, 'unit': 'mg/kg', 'max': 30}
        },
        'tranexamic acid': {
            'trauma': {'dose': 1000, 'unit': 'mg', 'fixed': True}  # Fixed dose
        }
    }
    
    if drug not in dosing_protocols:
        return None, "Drug not found in protocols"
    
    # Determine indication from context
    if 'rsi' in indication.lower() or 'rapid sequence' in indication.lower():
        indication = 'rsi'
    elif 'pain' in indication.lower():
        indication = 'pain'
    elif 'sedation' in indication.lower():
        indication = 'sedation'
    elif 'induction' in indication.lower():
        indication = 'induction'
    elif 'trauma' in indication.lower():
        indication = 'trauma'
    else:
        # Use first available indication
        indication = list(dosing_protocols[drug].keys())[0]
    
    if indication not in dosing_protocols[drug]:
        indication = list(dosing_protocols[drug].keys())[0]
    
    protocol = dosing_protocols[drug][indication]
    
    if protocol.get('fixed', False):
        # Fixed dose (like TXA)
        total_dose = protocol['dose']
        unit = protocol['unit']
    else:
        # Weight-based dose
        dose_per_kg = protocol['dose']
        total_dose = dose_per_kg * weight_kg
        unit = protocol['unit']
        
        # Apply maximum dose if specified
        if 'max' in protocol and total_dose > protocol['max']:
            total_dose = protocol['max']
    
    return total_dose, unit, indication

def get_ai_enhanced_response(question, weight=None, drug=None, calculated_dose=None):
    """Get AI-enhanced response with dose calculations"""
    try:
        # Load API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return get_fallback_response(question, weight, drug, calculated_dose)
        
        client = OpenAI(api_key=api_key)
        
        # Create enhanced prompt with dose information
        if calculated_dose:
            dose_info = f"""
            Patient weight: {weight} kg
            Drug: {drug}
            Calculated dose: {calculated_dose[0]} {calculated_dose[1]}
            Indication: {calculated_dose[2]}
            """
        else:
            dose_info = f"Patient weight: {weight} kg, Drug: {drug}" if weight and drug else ""
        
        system_prompt = f"""You are a clinical assistant providing drug dosing guidance. 
        
        {dose_info}
        
        Provide clear, concise clinical guidance including:
        1. The calculated dose and how to administer it
        2. Any important considerations or contraindications
        3. Monitoring requirements
        4. Alternative options if applicable
        
        Be conversational and helpful."""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            max_tokens=400,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return get_fallback_response(question, weight, drug, calculated_dose)

def get_fallback_response(question, weight=None, drug=None, calculated_dose=None):
    """Fallback response without AI"""
    if calculated_dose:
        dose, unit, indication = calculated_dose
        # Fix the unit display - remove /kg from total dose
        display_unit = unit.replace('/kg', '') if '/kg' in unit else unit
        return f"For {drug} {indication} in a {weight} kg patient: {dose:.1f} {display_unit}. Administer IV push over 30-60 seconds. Monitor vital signs and airway."
    else:
        return f"I heard your question about {question}. Please specify the patient weight and drug for dose calculation."

def main():
    print("🎤 SMART VOICE CALCULATOR ASSISTANT")
    print("=" * 50)
    print("Automatic Drug Dose Calculations")
    print()
    
    # Choose AI provider
    print("Choose AI provider:")
    print("1. ChatGPT (requires OPENAI_API_KEY)")
    print("2. Local calculations only")
    
    choice = input("Enter choice (1-2): ").strip()
    use_ai = choice == "1" and os.getenv('OPENAI_API_KEY')
    
    if choice == "1":
        if os.getenv('OPENAI_API_KEY'):
            print("✅ OpenAI API key found - ChatGPT integration enabled!")
        else:
            print("⚠️  OPENAI_API_KEY not set. Using local calculations only.")
            use_ai = False
    
    # Initialize speech recognition
    recognizer, microphone = init_speech_recognition()
    if not recognizer or not microphone:
        print("❌ Speech recognition failed - cannot continue")
        return
    
    print("✅ Ready! Ask for drug doses by voice.")
    print("💡 Try: 'Ketamine RSI for 80 kg patient', 'TXA for trauma', 'Goodbye'")
    print()
    
    # Welcome message
    if use_ai:
        speak_response("Hello! I'm your AI-enhanced dose calculator. I'll calculate drug doses and provide clinical guidance.")
    else:
        speak_response("Hello! I'm your dose calculator. I'll calculate drug doses based on patient weight.")
    
    while True:
        try:
            # Listen for speech
            question = listen_for_speech(recognizer, microphone)
            if not question:
                print("Please try speaking again...")
                continue
            
            if question.lower() in ['quit', 'exit', 'q', 'bye', 'stop', 'goodbye']:
                speak_response("Goodbye! Take care and stay safe.")
                break
                
            print("🧠 Processing...")
            start_time = time.time()
            
            # Extract weight and drug
            weight, drug = extract_weight_and_drug(question)
            
            if weight and drug:
                print(f"📊 Extracted: {weight} kg patient, {drug}")
                
                # Calculate dose
                calculated_dose = calculate_dose(drug, weight, question)
                
                if calculated_dose and calculated_dose[0]:
                    dose, unit, indication = calculated_dose
                    print(f"💊 Calculated: {dose} {unit} for {indication}")
                    
                    # Get response
                    if use_ai:
                        response = get_ai_enhanced_response(question, weight, drug, calculated_dose)
                    else:
                        response = get_fallback_response(question, weight, drug, calculated_dose)
                else:
                    response = f"Could not calculate dose for {drug}. Please check the drug name and indication."
            else:
                if not weight:
                    response = "I couldn't understand the patient weight. Please say something like '80 kg patient' or 'patient weighs 80 kilograms'."
                elif not drug:
                    response = "I couldn't understand the drug name. Please specify the medication clearly."
                else:
                    response = "I couldn't understand the weight or drug. Please try again with clear pronunciation."
            
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