#!/usr/bin/env python3
"""
AI Voice Assistant - ChatGPT/Gemini Integration
Uses AI for faster, more intelligent responses with local knowledge base
"""

import speech_recognition as sr
import subprocess
import time
import os
import json
import requests
from openai import OpenAI
import google.generativeai as genai

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

def query_local_knowledge_base(question):
    """Query the local knowledge base"""
    try:
        # Use the existing ask_direct.py script
        result = subprocess.run(
            ["python3", "scripts/ask_direct.py"],
            input=question,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Extract the response
            lines = result.stdout.split('\n')
            for line in lines:
                if line.startswith('🤖 Me') or 'Answer:' in line:
                    return line.split(':', 1)[1].strip()
            return "Response from local knowledge base"
        else:
            return f"Error querying knowledge base: {result.stderr}"
            
    except Exception as e:
        return f"Failed to query knowledge base: {e}"

def query_chatgpt(question, context=""):
    """Query ChatGPT for enhanced response"""
    try:
        # Load API key from environment or config
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return "ChatGPT API key not found. Please set OPENAI_API_KEY environment variable."
        
        client = OpenAI(api_key=api_key)
        
        # Create system prompt with clinical context
        system_prompt = f"""You are a clinical assistant with access to trauma protocols. 
        Use this knowledge base information to answer: {context}
        
        Provide clear, concise clinical guidance. If the knowledge base doesn't have specific information, 
        provide general clinical guidance based on standard protocols."""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            max_tokens=300,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"ChatGPT error: {e}"

def query_gemini(question, context=""):
    """Query Gemini for enhanced response"""
    try:
        # Load API key from environment or config
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return "Gemini API key not found. Please set GEMINI_API_KEY environment variable."
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Create prompt with clinical context
        prompt = f"""You are a clinical assistant with access to trauma protocols. 
        Use this knowledge base information to answer: {context}
        
        Question: {question}
        
        Provide clear, concise clinical guidance. If the knowledge base doesn't have specific information, 
        provide general clinical guidance based on standard protocols."""
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Gemini error: {e}"

def get_ai_enhanced_response(question, ai_provider="chatgpt"):
    """Get AI-enhanced response using local knowledge base + AI"""
    print("🧠 Querying local knowledge base...")
    local_response = query_local_knowledge_base(question)
    
    print(f"🤖 Enhancing with {ai_provider.upper()}...")
    
    if ai_provider.lower() == "chatgpt":
        enhanced_response = query_chatgpt(question, local_response)
    elif ai_provider.lower() == "gemini":
        enhanced_response = query_gemini(question, local_response)
    else:
        enhanced_response = local_response
    
    return enhanced_response

def main():
    print("🎤 AI VOICE-ENABLED CLINICAL ASSISTANT")
    print("=" * 50)
    print("ChatGPT/Gemini + Local Knowledge Base")
    print()
    
    # Choose AI provider
    print("Choose AI provider:")
    print("1. ChatGPT (requires OPENAI_API_KEY)")
    print("2. Gemini (requires GEMINI_API_KEY)")
    print("3. Local knowledge base only")
    
    choice = input("Enter choice (1-3): ").strip()
    
    ai_provider = None
    if choice == "1":
        ai_provider = "chatgpt"
        if not os.getenv('OPENAI_API_KEY'):
            print("⚠️  OPENAI_API_KEY not set. Please set it in your environment.")
    elif choice == "2":
        ai_provider = "gemini"
        if not os.getenv('GEMINI_API_KEY'):
            print("⚠️  GEMINI_API_KEY not set. Please set it in your environment.")
    else:
        ai_provider = "local"
    
    # Initialize speech recognition
    recognizer, microphone = init_speech_recognition()
    if not recognizer or not microphone:
        print("❌ Speech recognition failed - cannot continue")
        return
    
    print("✅ Ready! Ask clinical questions by voice.")
    print("💡 Try: 'Ketamine RSI dose', 'TXA protocol', 'Goodbye'")
    print()
    
    # Welcome message
    if ai_provider != "local":
        speak_response(f"Hello! I'm your AI-enhanced clinical assistant using {ai_provider.upper()}. How can I help you?")
    else:
        speak_response("Hello! I'm your clinical assistant with local knowledge base. How can I help you?")
    
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
            if ai_provider != "local":
                response = get_ai_enhanced_response(question, ai_provider)
            else:
                response = query_local_knowledge_base(question)
            
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