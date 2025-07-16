#!/usr/bin/env python3
"""
Mac Setup script for Voice Assistant AI Bot
Development environment setup (without Raspberry Pi system dependencies)
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_mac_audio():
    """Check if Mac audio dependencies are available."""
    print("🔊 Checking Mac audio setup...")
    
    # Check if Homebrew is installed
    try:
        result = subprocess.run(["brew", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Homebrew is installed")
            
            # Install audio dependencies via Homebrew
            audio_deps = ["portaudio", "espeak", "mpg123"]
            for dep in audio_deps:
                try:
                    subprocess.run(["brew", "install", dep], check=True, capture_output=True)
                    print(f"✅ Installed {dep}")
                except subprocess.CalledProcessError:
                    print(f"⚠️  {dep} already installed or failed to install")
            
            return True
        else:
            print("❌ Homebrew not found")
            print("📝 Install Homebrew: https://brew.sh/")
            return False
    except FileNotFoundError:
        print("❌ Homebrew not found")
        print("📝 Install Homebrew: https://brew.sh/")
        return False

def create_virtual_environment():
    """Create and activate virtual environment."""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("🔄 Creating virtual environment...")
        if not run_command("python3 -m venv venv", "Creating virtual environment"):
            return False
    
    print("🔄 Virtual environment ready")
    return True

def install_python_dependencies():
    """Install Python dependencies for Mac."""
    # Upgrade pip first
    if not run_command("venv/bin/pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install dependencies in order of complexity
    dependencies = [
        # Core dependencies
        "numpy",
        "scipy",
        "pandas",
        
        # Audio processing
        "pyaudio",
        "speech_recognition",
        "sounddevice",
        "webrtcvad",
        
        # AI & ML
        "torch",
        "transformers",
        "sentence-transformers",
        "faiss-cpu",
        
        # Text processing
        "pdfplumber",
        
        # Voice synthesis
        "pyttsx3",
        "gTTS",
        "google-cloud-texttospeech",
        "google-generativeai",
        
        # System management
        "psutil",
        "configparser",
        "python-dotenv",
        "requests",
        
        # Utilities
        "pydub",
        "librosa",
    ]
    
    for dep in dependencies:
        if not run_command(f"venv/bin/pip install {dep}", f"Installing {dep}"):
            print(f"⚠️  Warning: Failed to install {dep}, continuing...")
    
    # Install llama-cpp-python separately
    print("🔄 Installing llama-cpp-python...")
    if not run_command("venv/bin/pip install llama-cpp-python", "Installing llama-cpp-python"):
        return False
    
    return True

def create_directories():
    """Create necessary directories."""
    directories = [
        "models",
        "pdfs", 
        "embeds",
        "logs",
        "cache",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def create_environment_file():
    """Create .env file with default configuration."""
    env_content = """# Voice Assistant Configuration (Mac Development)
# Edit these values according to your setup

# Model Configuration
MODEL_PATH=models/mistral.Q4_K_M.gguf
EMBEDDINGS_PATH=embeds/faiss.idx
METADATA_PATH=embeds/meta.json
DOCS_PATH=embeds/docs.txt

# Audio Configuration
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
AUDIO_CHUNK_SIZE=1024
AUDIO_FORMAT=16

# Speech Recognition
SPEECH_RECOGNITION_TIMEOUT=5.0
SPEECH_RECOGNITION_PHRASE_TIME_LIMIT=10.0
SPEECH_RECOGNITION_NON_SPEAKING_DURATION=0.5

# Wake Word Configuration
WAKE_WORD=Hey Assistant
WAKE_WORD_SENSITIVITY=0.5
WAKE_WORD_DETECTION_MODE=porcupine

# Gemini Voice Configuration
GEMINI_VOICE_API_KEY=your_gemini_api_key_here
GEMINI_VOICE_MODEL=gemini-1.5-flash
GEMINI_VOICE_VOICE_ID=medical-professional
GEMINI_VOICE_SPEED=1.0

# TTS Configuration
TTS_ENGINE=gemini
TTS_VOICE=en-us
TTS_RATE=150
TTS_VOLUME=1.0

# LLM Configuration
LLM_MAX_TOKENS=150
LLM_TEMPERATURE=0.7
LLM_TOP_P=0.9
LLM_CONTEXT_WINDOW=4096

# Vector Search Configuration
VECTOR_SEARCH_TOP_K=3
VECTOR_SEARCH_THRESHOLD=0.5

# System Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/voice_assistant.log
MAX_CONVERSATION_HISTORY=10

# Performance Configuration
CPU_GOVERNOR=performance
MAX_TEMPERATURE=80.0
MEMORY_LIMIT=6144

# Security Configuration
ENCRYPTION_KEY=your_encryption_key_here
API_KEY_FILE=.env

# Network Configuration
ONLINE_MODE=false
PROXY_URL=
TIMEOUT_SECONDS=30

# File Paths
PDFS_DIR=pdfs/
MODELS_DIR=models/
EMBEDS_DIR=embeds/
LOGS_DIR=logs/
CACHE_DIR=cache/
"""
    
    # Create both .env and env.example files
    with open(".env", "w") as f:
        f.write(env_content)
    
    with open("env.example", "w") as f:
        f.write(env_content)
    
    print("✅ Created .env file with default configuration")
    print("✅ Created env.example file as backup")
    print("📝 Please edit .env and add your Gemini API key")
    
    return True

def create_mac_startup_script():
    """Create startup script for Mac development."""
    startup_content = """#!/bin/bash
# Voice Assistant Startup Script (Mac Development)

# Change to the project directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the voice assistant
python voice_assistant.py
"""
    
    with open("start_voice_assistant_mac.sh", "w") as f:
        f.write(startup_content)
    
    # Make executable
    os.chmod("start_voice_assistant_mac.sh", 0o755)
    
    print("✅ Created Mac startup script: start_voice_assistant_mac.sh")
    return True

def main():
    """Main setup function for Mac development."""
    print("🚀 Setting up Voice Assistant AI Bot for Mac Development")
    print("=" * 60)
    
    # Check if running on Mac
    if sys.platform != "darwin":
        print("⚠️  Warning: This script is designed for macOS")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Check Mac audio setup
    if not check_mac_audio():
        print("❌ Failed to setup Mac audio dependencies")
        print("📝 Please install Homebrew and audio dependencies manually")
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("❌ Failed to create virtual environment")
        sys.exit(1)
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("❌ Failed to create directories")
        sys.exit(1)
    
    # Create configuration files
    if not create_environment_file():
        print("❌ Failed to create environment file")
        sys.exit(1)
    
    # Create startup script
    if not create_mac_startup_script():
        print("❌ Failed to create startup script")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Mac Development Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env and add your Gemini API key")
    print("2. Download your Mistral model to models/ directory")
    print("3. Place your PDF documents in pdfs/ directory")
    print("4. Run: python scripts/build_index.py")
    print("5. Run: ./start_voice_assistant_mac.sh")
    print("\n🔧 For Raspberry Pi deployment:")
    print("   git clone <repository-url> on Pi")
    print("   python3 setup.py on Pi")
    print("\n🎤 Say 'Hey Assistant' to begin using the voice assistant!")

if __name__ == "__main__":
    main() 