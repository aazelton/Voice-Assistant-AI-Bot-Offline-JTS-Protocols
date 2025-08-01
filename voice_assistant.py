#!/usr/bin/env python3
"""
Voice Assistant AI Bot
Raspberry Pi 4 + Gemini Voice Integration
"""

import asyncio
import json
import logging
import numpy as np
import os
import pyaudio
import queue
import speech_recognition as sr
import subprocess
import threading
import time
from typing import Optional, Dict, Any

import faiss
from sentence_transformers import SentenceTransformer
from llama_cpp import Llama

# Local imports
from config import *
from scripts.utils import extract_chunks_from_pdf

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VoiceAssistant:
    """Main voice assistant class integrating all components."""
    
    def __init__(self):
        """Initialize the voice assistant with all components."""
        self.running = False
        self.conversation_history = []
        self.audio_queue = queue.Queue()
        
        # Initialize components
        self._init_audio()
        self._init_speech_recognition()
        self._init_llm()
        self._init_embeddings()
        self._init_tts()
        
        logger.info("Voice Assistant initialized successfully")
    
    def _init_audio(self):
        """Initialize audio components."""
        self.audio = pyaudio.PyAudio()
        self.audio_stream = None
        
        # Find the best audio input device
        self.input_device = self._find_best_audio_device()
        logger.info(f"Using audio input device: {self.input_device}")
    
    def _init_speech_recognition(self):
        """Initialize speech recognition components."""
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Configure microphone
        self.microphone = sr.Microphone(
            device_index=self.input_device,
            sample_rate=AUDIO_SAMPLE_RATE,
            chunk_size=AUDIO_CHUNK_SIZE
        )
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        logger.info("Speech recognition initialized")
    
    def _init_llm(self):
        """Initialize the local LLM."""
        try:
            self.llm = Llama(
                model_path=MODEL_PATH,
                n_ctx=LLM_CONTEXT_WINDOW,
                n_threads=4,  # Optimized for Raspberry Pi 4
                n_batch=512
            )
            logger.info(f"LLM loaded from {MODEL_PATH}")
        except Exception as e:
            logger.error(f"Failed to load LLM: {e}")
            raise
    
    def _init_embeddings(self):
        """Initialize embedding model and FAISS index."""
        try:
            self.embed_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.index = faiss.read_index(EMBEDDINGS_PATH)
            
            with open(METADATA_PATH, 'r') as f:
                self.metadata = json.load(f)
            
            with open(DOCS_PATH, 'r') as f:
                self.docs = f.readlines()
            
            logger.info("Embeddings and knowledge base loaded")
        except Exception as e:
            logger.error(f"Failed to load embeddings: {e}")
            raise
    
    def _init_tts(self):
        """Initialize text-to-speech components."""
        self.tts_engine = TTS_ENGINE
        logger.info(f"TTS engine set to: {self.tts_engine}")
    
    def _find_best_audio_device(self) -> Optional[int]:
        """Find the best available audio input device."""
        try:
            # Try to find USB microphone first
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                max_channels = device_info.get('maxInputChannels', 0)
                device_name = device_info.get('name', '')
                if (isinstance(max_channels, (int, float)) and max_channels > 0 and 
                    isinstance(device_name, str) and 'USB' in device_name.upper()):
                    return i
            
            # Fallback to default device
            return sr.Microphone.list_microphone_names().index(
                sr.Microphone.list_microphone_names()[0]
            )
        except Exception as e:
            logger.warning(f"Could not find optimal audio device: {e}")
            return None
    
    def listen_for_wake_word(self) -> bool:
        """Listen for wake word activation."""
        try:
            with self.microphone as source:
                logger.info("Listening for wake word...")
                audio = self.recognizer.listen(
                    source,
                    timeout=SPEECH_RECOGNITION_TIMEOUT,
                    phrase_time_limit=SPEECH_RECOGNITION_PHRASE_TIME_LIMIT
                )
                
                # Try to recognize the wake word
                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    if WAKE_WORD.lower() in text:
                        logger.info(f"Wake word detected: {text}")
                        return True
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    logger.warning(f"Speech recognition service error: {e}")
                
                return False
                
        except sr.WaitTimeoutError:
            return False
        except Exception as e:
            logger.error(f"Error in wake word detection: {e}")
            return False
    
    def listen_for_query(self) -> Optional[str]:
        """Listen for user query after wake word."""
        try:
            with self.microphone as source:
                logger.info("Listening for query...")
                audio = self.recognizer.listen(
                    source,
                    timeout=SPEECH_RECOGNITION_TIMEOUT,
                    phrase_time_limit=SPEECH_RECOGNITION_PHRASE_TIME_LIMIT
                )
                
                try:
                    text = self.recognizer.recognize_google(audio)
                    logger.info(f"Query recognized: {text}")
                    return text
                except sr.UnknownValueError:
                    logger.info("Could not understand audio")
                    return None
                except sr.RequestError as e:
                    logger.warning(f"Speech recognition service error: {e}")
                    return None
                    
        except sr.WaitTimeoutError:
            logger.info("No speech detected within timeout")
            return None
        except Exception as e:
            logger.error(f"Error in query recognition: {e}")
            return None
    
    def search_knowledge_base(self, query: str) -> str:
        """Search the knowledge base for relevant context."""
        try:
            # Generate query embedding
            query_embed = self.embed_model.encode([query])
            
            # Search FAISS index
            D, I = self.index.search(
                np.array(query_embed), 
                VECTOR_SEARCH_TOP_K
            )
            
            # Filter by similarity threshold
            relevant_docs = []
            for i, distance in zip(I[0], D[0]):
                if distance < VECTOR_SEARCH_THRESHOLD:
                    relevant_docs.append(self.docs[i].strip())
            
            if relevant_docs:
                context = "\n\n".join(relevant_docs)
                logger.info(f"Found {len(relevant_docs)} relevant documents")
                return context
            else:
                logger.warning("No relevant documents found")
                return ""
                
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return ""
    
    def generate_response(self, query: str, context: str = "") -> str:
        """Generate response using the local LLM."""
        try:
            # Build prompt with context
            if context:
                prompt = f"""You are an experienced trauma provider giving quick, direct advice. Be concise but conversational. Give actionable answers in 1-2 sentences.

[CONTEXT START]
{context}
[CONTEXT END]

Question: {query}

Answer with direct, actionable advice:"""
            else:
                prompt = f"""You are an experienced trauma provider giving quick, direct advice. Be concise but conversational.

Question: {query}

Answer with direct, actionable advice:"""
            
            # Generate response
            response = self.llm(
                prompt,
                max_tokens=100,  # Shorter responses for voice
                temperature=0.3,  # More focused
                top_p=0.9,
                stop=["\n\n", "Question:", "Context:", "Answer:"]
            )
            
            answer = response["choices"][0]["text"].strip()
            logger.info(f"Generated response: {answer}")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while processing your question."
    
    def speak_response(self, text: str):
        """Convert text to speech and play audio."""
        try:
            if self.tts_engine == "gemini" and GEMINI_VOICE_API_KEY:
                self._speak_with_gemini(text)
            elif self.tts_engine == "espeak":
                self._speak_with_espeak(text)
            elif self.tts_engine == "pyttsx3":
                self._speak_with_pyttsx3(text)
            elif self.tts_engine == "gtts":
                self._speak_with_gtts(text)
            else:
                # Fallback to espeak
                self._speak_with_espeak(text)
                
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            # Emergency fallback
            self._speak_with_espeak(text)
    
    def _speak_with_gemini(self, text: str):
        """Use Gemini Voice API for TTS."""
        try:
            import google.generativeai as genai
            
            # Configure Gemini
            genai.configure(api_key=GEMINI_VOICE_API_KEY)
            model = genai.GenerativeModel(GEMINI_VOICE_MODEL)
            
            # Generate speech
            response = model.generate_content(
                text,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="audio/mpeg"
                )
            )
            
            # Save and play audio
            audio_file = os.path.join(CACHE_DIR, "response.mp3")
            with open(audio_file, "wb") as f:
                f.write(response.candidates[0].content.parts[0].inline_data.data)
            
            # Play audio
            subprocess.run(["mpg123", audio_file], check=True)
            
        except Exception as e:
            logger.error(f"Gemini Voice error: {e}")
            raise
    
    def _speak_with_espeak(self, text: str):
        """Use eSpeak-ng for TTS."""
        try:
            subprocess.run([
                "espeak-ng",
                "-v", TTS_VOICE,
                "-s", str(TTS_RATE),
                "-a", str(int(TTS_VOLUME * 200)),
                text
            ], check=True)
        except Exception as e:
            logger.error(f"eSpeak error: {e}")
            raise
    
    def _speak_with_pyttsx3(self, text: str):
        """Use pyttsx3 for TTS."""
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            engine.setProperty('rate', TTS_RATE)
            engine.setProperty('volume', TTS_VOLUME)
            
            # Set voice
            voices = engine.getProperty('voices')
            for voice in voices:
                if TTS_VOICE in voice.id:
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.say(text)
            engine.runAndWait()
            
        except Exception as e:
            logger.error(f"pyttsx3 error: {e}")
            raise
    
    def _speak_with_gtts(self, text: str):
        """Use Google Text-to-Speech for TTS."""
        try:
            from gtts import gTTS
            import tempfile
            
            # Generate speech
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                tts.save(f.name)
                temp_file = f.name
            
            # Play audio
            subprocess.run(["mpg123", temp_file], check=True)
            
            # Clean up
            os.unlink(temp_file)
            
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            raise
    
    def process_query(self, query: str) -> str:
        """Process a complete query through the pipeline."""
        try:
            # Search knowledge base
            context = self.search_knowledge_base(query)
            
            # Generate response
            response = self.generate_response(query, context)
            
            # Add to conversation history
            self.conversation_history.append({
                "query": query,
                "response": response,
                "timestamp": time.time()
            })
            
            # Keep only recent history
            if len(self.conversation_history) > MAX_CONVERSATION_HISTORY:
                self.conversation_history.pop(0)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return "I apologize, but I encountered an error while processing your request."
    
    def run(self):
        """Main run loop for the voice assistant."""
        self.running = True
        logger.info("Voice Assistant started. Say 'Hey Assistant' to begin.")
        
        try:
            while self.running:
                # Listen for wake word
                if self.listen_for_wake_word():
                    # Acknowledge wake word
                    self.speak_response("Yes, I'm listening.")
                    
                    # Listen for query
                    query = self.listen_for_query()
                    if query:
                        # Process query
                        response = self.process_query(query)
                        
                        # Speak response
                        self.speak_response(response)
                    else:
                        self.speak_response("I didn't catch that. Please try again.")
                
                # Small delay to prevent CPU overuse
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("Voice Assistant stopped by user")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        self.running = False
        
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        logger.info("Voice Assistant cleaned up")

def main():
    """Main entry point."""
    try:
        assistant = VoiceAssistant()
        assistant.run()
    except Exception as e:
        logger.error(f"Failed to start Voice Assistant: {e}")
        raise

if __name__ == "__main__":
    main() 