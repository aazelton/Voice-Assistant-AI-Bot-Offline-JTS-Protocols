#!/usr/bin/env python3
"""
Voice-Enabled Clinical Assistant - Remote Knowledge Base
Uses voice on Mac, connects to VM's knowledge base
"""

import speech_recognition as sr
import subprocess
import time
import os
import requests
import json

def init_speech_recognition():
    """Initialize speech recognition"""
    print("🎤 Initializing speech recognition...")
    
    try:
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 3000
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 1.5
        
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

def listen_for_speech(recognizer, microphone, timeout=15):
    """Listen for speech input"""
    try:
        with microphone as source:
            print("🎤 Listening... (speak now)")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=20)
            
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

def query_vm_knowledge_base(question, vm_ip="your-vm-ip"):
    """Query the VM's knowledge base remotely"""
    try:
        # This would require setting up a simple API on the VM
        # For now, we'll use SSH to run the query
        import subprocess
        
        # Write question to a temporary file and use that for SSH
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(question)
            temp_file = f.name
        
        # SSH command to run the query on VM using the temp file
        ssh_cmd = f"ssh akaclinicalco@{vm_ip} 'cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols && cat {temp_file} | python3 scripts/ask_direct.py'"
        
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Extract the response from the output
            lines = result.stdout.split('\n')
            for line in lines:
                if line.startswith('🤖 Me') or 'Answer:' in line:
                    return line.split(':', 1)[1].strip()
            return "Response received from VM"
        else:
            return f"Error querying VM: {result.stderr}"
            
    except Exception as e:
        return f"Failed to connect to VM: {e}"

def get_fallback_response(question):
    """Get fallback response if VM is not available"""
    question_lower = question.lower()
    
    # Simple fallback responses
    if 'ketamine' in question_lower:
        if 'rsi' in question_lower:
            return "For RSI, ketamine is typically 1 to 2 milligrams per kilogram IV. Have your airway equipment ready."
        else:
            return "Ketamine can be used for pain control at 0.1 to 0.5 milligrams per kilogram IV."
    
    elif 'txa' in question_lower or 'tranexamic' in question_lower:
        return "TXA is 1 gram IV bolus, then 1 gram over 8 hours. Best given within 3 hours of injury."
    
    elif 'fentanyl' in question_lower:
        return "Fentanyl is 1 to 2 micrograms per kilogram IV. Start low and titrate up as needed."
    
    else:
        return f"I heard your question about {question}. This is fallback mode - the full knowledge base is on the VM."

def main():
    print("🎤 VOICE-ENABLED CLINICAL ASSISTANT (REMOTE)")
    print("=" * 55)
    print("Voice on Mac + Knowledge Base on VM")
    print()
    
    # Get VM IP
    vm_ip = input("Enter your VM IP address (or press Enter for fallback mode): ").strip()
    if not vm_ip:
        vm_ip = None
        print("⚠️  Running in fallback mode (no VM connection)")
    else:
        print(f"✅ Will connect to VM at {vm_ip}")
    
    # Initialize speech recognition
    recognizer, microphone = init_speech_recognition()
    if not recognizer or not microphone:
        print("❌ Speech recognition failed - cannot continue")
        return
    
    print("✅ Ready! Ask clinical questions by voice.")
    print("💡 Try: 'Ketamine RSI dose', 'TXA protocol', 'Goodbye'")
    print()
    
    # Welcome message
    if vm_ip:
        speak_response("Hello! I'm your voice-enabled clinical assistant. Connected to the full knowledge base.")
    else:
        speak_response("Hello! I'm your voice-enabled clinical assistant. Running in fallback mode.")
    
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
            
            # Get response
            if vm_ip:
                response = query_vm_knowledge_base(question, vm_ip)
            else:
                response = get_fallback_response(question)
            
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