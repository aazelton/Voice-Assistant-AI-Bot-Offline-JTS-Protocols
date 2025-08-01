#!/usr/bin/env python3
"""
Simple Voice Test - Test speech recognition and TTS
"""

import speech_recognition as sr
import subprocess
import time

def test_speech_recognition():
    """Test speech recognition"""
    print("🎤 Testing Speech Recognition...")
    
    try:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        # Adjust for ambient noise
        with microphone as source:
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("✅ Speech recognition initialized")
        print("Say something when prompted...")
        
        with microphone as source:
            print("🎤 Listening... (say 'test' or anything)")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            try:
                text = recognizer.recognize_google(audio)
                print(f"✅ Heard: '{text}'")
                return text
            except sr.UnknownValueError:
                print("❌ Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"❌ Speech recognition service error: {e}")
                return None
                
    except Exception as e:
        print(f"❌ Speech recognition failed: {e}")
        return None

def test_tts():
    """Test text-to-speech"""
    print("\n🔊 Testing Text-to-Speech...")
    
    test_text = "Hello, this is a test of the text to speech system."
    
    try:
        # Test eSpeak
        print("Testing eSpeak...")
        subprocess.run([
            "espeak-ng",
            "-v", "en-us",
            "-s", "150",
            test_text
        ], check=True)
        print("✅ eSpeak TTS working")
        return True
        
    except Exception as e:
        print(f"❌ eSpeak failed: {e}")
        
        try:
            # Test gTTS as fallback
            print("Testing gTTS...")
            from gtts import gTTS
            import tempfile
            import os
            
            tts = gTTS(text=test_text, lang='en', slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                tts.save(f.name)
                temp_file = f.name
            
            subprocess.run(["mpg123", temp_file], check=True)
            os.unlink(temp_file)
            print("✅ gTTS working")
            return True
            
        except Exception as e2:
            print(f"❌ gTTS also failed: {e2}")
            return False

def main():
    print("🎤 VOICE SYSTEM TEST")
    print("=" * 30)
    
    # Test TTS first (easier)
    tts_working = test_tts()
    
    # Test speech recognition
    speech_working = test_speech_recognition()
    
    print("\n" + "=" * 30)
    print("TEST RESULTS:")
    print(f"Text-to-Speech: {'✅ Working' if tts_working else '❌ Failed'}")
    print(f"Speech Recognition: {'✅ Working' if speech_working else '❌ Failed'}")
    
    if tts_working and speech_working:
        print("\n🎉 Voice system is ready!")
        print("You can now run: python3 scripts/ask_voice.py")
    else:
        print("\n⚠️  Some voice components need attention")
        if not tts_working:
            print("- Install TTS: sudo apt install espeak-ng mpg123")
        if not speech_working:
            print("- Check microphone permissions and internet connection")

if __name__ == "__main__":
    main() 