#!/usr/bin/env python3
"""
Voice JTS Assistant - Local Version
Combines voice interface with local JTS knowledge base (if available)
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

def calculate_dose(drug, weight_kg, indication="general"):
    """Calculate drug dose based on weight and indication"""
    
    dosing_protocols = {
        'ketamine': {
            'rsi': {'dose': 2.0, 'unit': 'mg/kg', 'max': 200},
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

def get_jts_protocol_info(drug, indication):
    """Get JTS protocol information for drugs"""
    
    jts_protocols = {
        'ketamine': {
            'rsi': {
                'dose': '2 mg/kg IV',
                'onset': '30-60 seconds',
                'duration': '10-20 minutes',
                'cautions': 'Hypertension, increased ICP, hallucinations',
                'contraindications': 'Known hypersensitivity, severe hypertension'
            },
            'pain': {
                'dose': '0.3 mg/kg IV',
                'onset': '1-2 minutes',
                'duration': '15-30 minutes',
                'cautions': 'Psychotomimetic effects, hypertension'
            }
        },
        'rocuronium': {
            'rsi': {
                'dose': '1.2 mg/kg IV',
                'onset': '60-90 seconds',
                'duration': '30-60 minutes',
                'cautions': 'Prolonged paralysis, monitor with train-of-four',
                'reversal': 'Sugammadex 16 mg/kg'
            }
        },
        'tranexamic acid': {
            'trauma': {
                'dose': '1 g IV over 10 minutes',
                'repeat': '1 g IV over 8 hours',
                'timing': 'Within 3 hours of injury',
                'cautions': 'Thromboembolic risk, renal impairment',
                'indications': 'Significant hemorrhage, shock'
            }
        },
        'fentanyl': {
            'pain': {
                'dose': '1 mcg/kg IV',
                'onset': '1-2 minutes',
                'duration': '30-60 minutes',
                'cautions': 'Respiratory depression, chest wall rigidity',
                'antidote': 'Naloxone'
            }
        }
    }
    
    if drug in jts_protocols and indication in jts_protocols[drug]:
        return jts_protocols[drug][indication]
    return None

def get_ai_enhanced_response(question, weight=None, drug=None, calculated_dose=None, jts_info=None, conversation_history=None):
    """Get AI-enhanced response combining dose calculation and JTS knowledge"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return get_fallback_response(question, weight, drug, calculated_dose, jts_info)
        
        client = OpenAI(api_key=api_key)
        
        # Build context information
        context_info = []
        if weight:
            context_info.append(f"Patient weight: {weight} kg")
        if drug:
            context_info.append(f"Drug: {drug}")
        if calculated_dose:
            dose, unit, indication = calculated_dose
            if '/kg' in unit:
                total_dose = dose * weight
                context_info.append(f"Calculated dose: {total_dose:.1f} {unit.replace('/kg', '')} ({dose} {unit})")
            else:
                context_info.append(f"Calculated dose: {dose:.1f} {unit}")
        if jts_info:
            context_info.append(f"JTS Protocol: {json.dumps(jts_info, indent=2)}")
        
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
        return get_fallback_response(question, weight, drug, calculated_dose, jts_info)

def get_fallback_response(question, weight=None, drug=None, calculated_dose=None, jts_info=None):
    """Fallback response when AI is unavailable"""
    if weight and drug and calculated_dose:
        dose, unit, indication = calculated_dose
        if '/kg' in unit:
            total_dose = dose * weight
            return f"{drug.title()}: {total_dose:.1f} {unit.replace('/kg', '')} ({dose} {unit}) for {indication}"
        else:
            return f"{drug.title()}: {dose:.1f} {unit} for {indication}"
    elif weight and drug:
        return f"Patient: {weight} kg, Drug: {drug}. Please specify indication (RSI, pain, etc.)"
    elif jts_info:
        return f"JTS Protocol for {drug}: {jts_info.get('dose', 'Dose not specified')}"
    else:
        return "I need more information. Please specify patient weight and medication."

def main():
    """Main voice assistant loop"""
    print("🎤 VOICE JTS ASSISTANT (LOCAL)")
    print("=" * 50)
    print("Voice + Local JTS Knowledge Base")
    print("📋 Note: For full JTS database, connect to VM")
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
            
            # Calculate dose if we have weight and drug
            calculated_dose = None
            if final_weight and final_drug:
                calculated_dose = calculate_dose(final_drug, final_weight, question)
                if calculated_dose:
                    dose, unit, indication = calculated_dose
                    if '/kg' in unit:
                        total_dose = dose * final_weight
                        print(f"💊 Calculated: {total_dose:.1f} {unit.replace('/kg', '')} for {indication}")
                    else:
                        print(f"💊 Calculated: {dose:.1f} {unit} for {indication}")
            
            # Get JTS protocol information
            jts_info = None
            if final_drug and final_indication:
                jts_info = get_jts_protocol_info(final_drug, final_indication)
                if jts_info:
                    print("📋 JTS protocol data available")
            
            # Generate response combining dose calculation and JTS knowledge
            response = get_ai_enhanced_response(
                question, 
                final_weight, 
                final_drug, 
                calculated_dose,
                jts_info,
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