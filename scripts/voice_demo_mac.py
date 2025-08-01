#!/usr/bin/env python3
"""
Voice Demo - Mac Optimized
Uses afplay for better Mac audio compatibility
"""

import speech_recognition as sr
import subprocess
import time
import os

def init_speech_recognition():
    """Initialize speech recognition"""
    print("🎤 Initializing speech recognition...")
    
    try:
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 3000
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 2.0
        
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
        # Use gTTS for better quality
        from gtts import gTTS
        import tempfile
        
        tts = gTTS(text=text, lang='en', slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            tts.save(f.name)
            temp_file = f.name
        
        # Use afplay (Mac's built-in audio player) instead of mpg123
        try:
            subprocess.run(["afplay", temp_file], check=True, capture_output=True)
            print("🔊 Audio played successfully")
        except subprocess.CalledProcessError:
            # Fallback to mpg123 if afplay fails
            try:
                subprocess.run(["mpg123", temp_file], check=True, capture_output=True)
                print("🔊 Audio played successfully (mpg123)")
            except subprocess.CalledProcessError:
                print("🔊 Audio output failed, but text response shown")
        
        # Clean up
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"❌ TTS failed: {e}")
        print(f"Text: {text}")

def listen_for_speech(recognizer, microphone, timeout=15):
    """Listen for speech input"""
    try:
        with microphone as source:
            print("🎤 Listening... (speak now)")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=25)
            
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

def get_demo_response(question):
    """Get demo response for testing"""
    question_lower = question.lower()
    
    # Simple demo responses
    if 'hello' in question_lower or 'hi' in question_lower:
        return "Hello! I'm your voice-enabled clinical assistant. How can I help you today?"
    
    elif 'ketamine' in question_lower:
        if 'rsi' in question_lower:
            return "For RSI, ketamine is typically 1 to 2 milligrams per kilogram IV. Have your airway equipment ready."
        else:
            return "Ketamine can be used for pain control at 0.1 to 0.5 milligrams per kilogram IV."
    
    elif 'txa' in question_lower or 'tranexamic' in question_lower:
        return "TXA is 1 gram IV bolus, then 1 gram over 8 hours. Best given within 3 hours of injury."
    
    elif 'fentanyl' in question_lower:
        return "Fentanyl is 1 to 2 micrograms per kilogram IV. Start low and titrate up as needed."
    
    elif 'thank' in question_lower:
        return "You're welcome! I'm here to help with clinical questions."
    
    elif 'bye' in question_lower or 'goodbye' in question_lower:
        return "Goodbye! Take care and stay safe."
    
    else:
        return "I heard your question about " + question + ". This is a demo mode - in the full system, I would search the clinical database for specific answers."

def main():
    print("🎤 VOICE-ENABLED CLINICAL ASSISTANT DEMO (MAC)")
    print("=" * 55)
    print("This is a voice demo - no knowledge base required")
    print("Optimized for Mac audio compatibility")
    print()
    
    # Initialize speech recognition
    recognizer, microphone = init_speech_recognition()
    if not recognizer or not microphone:
        print("❌ Speech recognition failed - cannot continue")
        return
    
    print("✅ Ready! Ask clinical questions by voice.")
    print("💡 Try: 'Hello', 'Ketamine RSI dose', 'TXA protocol', 'Goodbye'")
    print()
    
    # Welcome message
    speak_response("Hello! I'm your voice-enabled clinical assistant. How can I help you today?")
    
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
            
            # Get demo response
            response = get_demo_response(question)
            
            end_time = time.time()
            
            # Display and speak response
            print(f"🤖 Me ({end_time - start_time:.1f}s): {response}")
            speak_response(response)
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Take care!")
            break
        except Exception as e:
            print(f"❌ Oops, something went wrong: {e}")
            continue

if __name__ == "__main__":
    main() 