#!/usr/bin/env python3
"""
Quick Voice Calculator - Skip welcome message for immediate testing
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
    pass

def init_speech_recognition():
    """Initialize speech recognition with extended timing"""
    print("🎤 Initializing speech recognition...")
    
    try:
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 3000
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 2.5
        
        microphone = sr.Microphone()
        print("✅ Microphone initialized")
        
        with microphone as source:
            print("🎤 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
        
        print("✅ Speech recognition ready")
        return recognizer, microphone
        
    except Exception as e:
        print(f"❌ Speech recognition failed: {e}")
        return None, None

def convert_medical_abbreviations(text):
    """Convert medical abbreviations to full words for better TTS pronunciation"""
    abbreviations = {
        'mg': 'milligrams',
        'mcg': 'micrograms',
        'kg': 'kilograms',
        'ml': 'milliliters',
        'cc': 'cubic centimeters',
        'iv': 'intravenous',
        'im': 'intramuscular',
        'sc': 'subcutaneous',
        'po': 'by mouth',
        'pr': 'rectal',
        'rsi': 'rapid sequence intubation',
        'txa': 'tranexamic acid',
        'roc': 'rocuronium',
        'succ': 'succinylcholine',
        'fent': 'fentanyl',
        'morph': 'morphine',
        'versed': 'midazolam',
        'prop': 'propofol',
        'etom': 'etomidate',
        'ket': 'ketamine'
    }
    
    # Convert text to lowercase for matching, but preserve original case
    text_lower = text.lower()
    
    for abbr, full in abbreviations.items():
        # Replace whole words only (with word boundaries)
        pattern = r'\b' + re.escape(abbr) + r'\b'
        text = re.sub(pattern, full, text, flags=re.IGNORECASE)
    
    return text

def speak_response(text):
    """Convert text to speech using OpenAI TTS for natural voice"""
    try:
        # Convert medical abbreviations to full words
        tts_text = convert_medical_abbreviations(text)
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            # Fallback to gTTS if no OpenAI key
            from gtts import gTTS
            import tempfile
            
            tts = gTTS(text=tts_text, lang='en', slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                tts.save(f.name)
                temp_file = f.name
            
            try:
                subprocess.run(["afplay", temp_file], check=True, capture_output=True)
                print("🔊 Audio played successfully")
            except subprocess.CalledProcessError:
                print("🔊 Audio output failed, but text response shown")
            
            os.unlink(temp_file)
            return
        
        # Use OpenAI TTS for natural voice
        client = OpenAI(api_key=api_key)
        import tempfile
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",  # Natural, clear voice
            input=tts_text
        )
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            response.write_to_file(f.name)
            temp_file = f.name
        
        try:
            subprocess.run(["afplay", temp_file], check=True, capture_output=True)
            print("🔊 Natural voice played successfully")
        except subprocess.CalledProcessError:
            print("🔊 Audio output failed, but text response shown")
        
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
            'trauma': {'dose': 1000, 'unit': 'mg', 'fixed': True}
        }
    }
    
    if drug not in dosing_protocols:
        return None
    
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
        indication = list(dosing_protocols[drug].keys())[0]
    
    if indication not in dosing_protocols[drug]:
        indication = list(dosing_protocols[drug].keys())[0]
    
    protocol = dosing_protocols[drug][indication]
    
    if protocol.get('fixed', False):
        total_dose = protocol['dose']
        unit = protocol['unit']
    else:
        dose_per_kg = protocol['dose']
        total_dose = dose_per_kg * weight_kg
        unit = protocol['unit']
        
        if 'max' in protocol and total_dose > protocol['max']:
            total_dose = protocol['max']
    
    return total_dose, unit, indication

def get_ai_enhanced_response(question, weight=None, drug=None, calculated_dose=None, conversation_history=None):
    """Get AI-enhanced response with full conversation tracking"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return get_fallback_response(question, weight, drug, calculated_dose)
        
        client = OpenAI(api_key=api_key)
        
        if calculated_dose and weight:
            total_dose = calculated_dose[0] * weight
            dose_info = f"Patient: {weight} kg, {drug} {calculated_dose[2]}, Total dose: {total_dose:.1f} {calculated_dose[1].replace('/kg', '')}"
        elif weight and drug:
            dose_info = f"Patient: {weight} kg, Drug: {drug}"
        else:
            dose_info = ""
        
        SYSTEM_PROMPT = f"""You are a calm, experienced paramedic assisting another paramedic in the field. Your job is to provide accurate, brief, and helpful advice in a stressful prehospital environment.

Rules:
1. Be concise, tactical, and focused.
2. Use medic-style communication. Sound human, not robotic.
3. Never explain unless asked. Give clear actions.
4. Keep context from prior messages — you're following the same case.
5. Use short bullets, not paragraphs.
6. Provide meds, doses, route, and only critical cautions.
7. If something is unclear, ask a short clarifying question.
8. Match tone of a seasoned street medic. Think: calm, clipped radio report or verbal handoff.

{dose_info}

Example:
User: "Got a burn patient, I need to RSI — thinking ketamine and roc."
You: 
- Ketamine 2 mg/kg IV
- Rocuronium 1 mg/kg IV
- Watch for hypotension, may worsen

User: "He's hypotensive now."
You:
- Consider push-dose epi 10–20 mcg IV
- Repeat every 2–5 min PRN
- Check airway pressure and fluid status"""
        
        # Build conversation with history
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history if available
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current question
        messages.append({"role": "user", "content": question})
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=200,
            temperature=0.3
        )
        
        assistant_reply = response.choices[0].message.content
        
        # Update conversation history (limit to prevent memory issues)
        if conversation_history is not None:
            conversation_history.append({"role": "user", "content": question})
            conversation_history.append({"role": "assistant", "content": assistant_reply})
            
            # Keep only last 6 messages to prevent memory bloat
            if len(conversation_history) > 6:
                conversation_history = conversation_history[-6:]
        
        return assistant_reply
        
    except Exception as e:
        return get_fallback_response(question, weight, drug, calculated_dose)

def get_fallback_response(question, weight=None, drug=None, calculated_dose=None):
    """Fallback response without AI"""
    if calculated_dose:
        dose, unit, indication = calculated_dose
        display_unit = unit.replace('/kg', '') if '/kg' in unit else unit
        return f"For {drug} {indication} in a {weight} kg patient: {dose:.1f} {display_unit}. Administer IV push over 30-60 seconds. Monitor vital signs and airway."
    else:
        return f"I heard your question about {question}. Please specify the patient weight and drug for dose calculation."

def main():
    print("🎤 SMART VOICE CALCULATOR ASSISTANT")
    print("=" * 50)
    print("ChatGPT Enhanced - Ready for Voice Input")
    print()
    
    # Initialize speech recognition
    recognizer, microphone = init_speech_recognition()
    if not recognizer or not microphone:
        print("❌ Speech recognition failed - cannot continue")
        return
    
    print("✅ Ready! Ask for drug doses by voice.")
    print("💡 Try: 'Ketamine RSI for 80 kg patient', 'TXA for trauma', 'Goodbye'")
    print()
    
    # Context memory for multi-turn conversations
    context = {
        'weight': None,
        'drug': None,
        'indication': None,
        'last_question': None
    }
    
    # Full conversation tracking
    conversation_history = []
    
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
            
            # Handle multiple drugs in one question
            if 'both' in question.lower() or 'and' in question.lower():
                # Extract multiple drugs
                all_drugs = []
                for drug_key in ['ketamine', 'rocuronium', 'succinylcholine', 'fentanyl', 'midazolam', 'propofol', 'etomidate', 'tranexamic acid']:
                    if drug_key in question.lower():
                        all_drugs.append(drug_key)
                
                if all_drugs and final_weight:
                    print(f"📊 Multi-drug request: {final_weight} kg patient, drugs: {', '.join(all_drugs)}")
                    
                    # Generate response for multiple drugs
                    response_parts = []
                    for drug_name in all_drugs:
                        calculated_dose = calculate_dose(drug_name, final_weight, question)
                        if calculated_dose and calculated_dose[0]:
                            dose, unit, indication = calculated_dose
                            # Calculate total dose for patient
                            if '/kg' in unit:
                                total_dose = dose * final_weight
                                display_unit = unit.replace('/kg', '')
                                response_parts.append(f"{drug_name.title()}: {total_dose:.1f} {display_unit} ({dose} {unit})")
                            else:
                                response_parts.append(f"{drug_name.title()}: {dose:.1f} {unit} {indication}")
                    
                    if response_parts:
                        response = "\n".join(response_parts)
                    else:
                        response = f"Could not calculate doses for {', '.join(all_drugs)}."
                else:
                    # Use AI for context-aware response even without dose calculation
                    response = get_ai_enhanced_response(question, final_weight, final_drug, None, conversation_history)
            
            elif final_weight and final_drug:
                print(f"📊 Context: {final_weight} kg patient, {final_drug}")
                
                # Calculate dose
                calculated_dose = calculate_dose(final_drug, final_weight, question)
                
                if calculated_dose and calculated_dose[0]:
                    dose, unit, indication = calculated_dose
                    # Calculate total dose for patient
                    if '/kg' in unit:
                        total_dose = dose * final_weight
                        display_unit = unit.replace('/kg', '')
                        print(f"💊 Calculated: {total_dose:.1f} {display_unit} for {indication}")
                    else:
                        total_dose = dose
                        display_unit = unit
                        print(f"💊 Calculated: {total_dose:.1f} {display_unit} for {indication}")
                    
                    # Get AI-enhanced response with conversation tracking
                    response = get_ai_enhanced_response(question, final_weight, final_drug, calculated_dose, conversation_history)
                else:
                    response = f"Could not calculate dose for {final_drug}. Please check the drug name and indication."
            else:
                # Use AI for all responses to maintain conversation context
                response = get_ai_enhanced_response(question, final_weight, final_drug, None, conversation_history)
            
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