#!/usr/bin/env python3
"""
Setup script for Voice Assistant AI Bot
Raspberry Pi 4 + Gemini Voice Integration
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

def install_system_dependencies():
    """Install system-level dependencies."""
    commands = [
        ("sudo apt-get update", "Updating package list"),
        ("sudo apt-get install -y python3-pip python3-venv", "Installing Python dependencies"),
        ("sudo apt-get install -y portaudio19-dev python3-pyaudio", "Installing audio dependencies"),
        ("sudo apt-get install -y espeak-ng", "Installing eSpeak-ng"),
        ("sudo apt-get install -y mpg123", "Installing MP3 player"),
        ("sudo apt-get install -y libatlas-base-dev", "Installing BLAS libraries"),
        ("sudo apt-get install -y libopenblas-dev", "Installing OpenBLAS"),
        ("sudo apt-get install -y liblapack-dev", "Installing LAPACK"),
        ("sudo apt-get install -y gfortran", "Installing Fortran compiler"),
        ("sudo apt-get install -y cmake", "Installing CMake"),
        ("sudo apt-get install -y build-essential", "Installing build tools"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True

def create_virtual_environment():
    """Create and activate virtual environment."""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("🔄 Creating virtual environment...")
        if not run_command("python3 -m venv venv", "Creating virtual environment"):
            return False
    
    print("🔄 Activating virtual environment...")
    activate_script = venv_path / "bin" / "activate"
    if not activate_script.exists():
        print("❌ Virtual environment activation script not found")
        return False
    
    return True

def install_python_dependencies():
    """Install Python dependencies."""
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
    
    # Install llama-cpp-python separately with optimizations
    print("🔄 Installing llama-cpp-python with optimizations...")
    if not run_command(
        "CMAKE_ARGS='-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS' venv/bin/pip install llama-cpp-python",
        "Installing llama-cpp-python with BLAS optimization"
    ):
        print("⚠️  Warning: Failed to install llama-cpp-python with optimizations, trying standard install...")
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
    env_content = """# Voice Assistant Configuration
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

def create_startup_script():
    """Create startup script for the voice assistant."""
    startup_content = """#!/bin/bash
# Voice Assistant Startup Script

# Change to the project directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the voice assistant
python voice_assistant.py
"""
    
    with open("start_voice_assistant.sh", "w") as f:
        f.write(startup_content)
    
    # Make executable
    os.chmod("start_voice_assistant.sh", 0o755)
    
    print("✅ Created startup script: start_voice_assistant.sh")
    return True

def create_systemd_service():
    """Create systemd service for auto-start."""
    service_content = """[Unit]
Description=Voice Assistant AI Bot
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/trauma-assistant
ExecStart=/home/pi/trauma-assistant/start_voice_assistant.sh
Restart=always
RestartSec=10
Environment=PYTHONPATH=/home/pi/trauma-assistant

[Install]
WantedBy=multi-user.target
"""
    
    with open("voice-assistant.service", "w") as f:
        f.write(service_content)
    
    print("✅ Created systemd service file: voice-assistant.service")
    print("📝 To enable auto-start, run:")
    print("   sudo cp voice-assistant.service /etc/systemd/system/")
    print("   sudo systemctl enable voice-assistant.service")
    print("   sudo systemctl start voice-assistant.service")
    
    return True

def main():
    """Main setup function."""
    print("🚀 Setting up Voice Assistant AI Bot for Raspberry Pi 4")
    print("=" * 60)
    
    # Check if running on Raspberry Pi
    if not os.path.exists("/proc/device-tree/model"):
        print("⚠️  Warning: This script is designed for Raspberry Pi")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Install system dependencies
    if not install_system_dependencies():
        print("❌ Failed to install system dependencies")
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
    if not create_startup_script():
        print("❌ Failed to create startup script")
        sys.exit(1)
    
    # Create systemd service
    if not create_systemd_service():
        print("❌ Failed to create systemd service")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Copy env.example to .env and configure your settings")
    print("2. Download your Mistral model to models/ directory")
    print("3. Place your PDF documents in pdfs/ directory")
    print("4. Run: python scripts/build_index.py")
    print("5. Run: ./start_voice_assistant.sh")
    print("\n🔧 For auto-start on boot:")
    print("   sudo cp voice-assistant.service /etc/systemd/system/")
    print("   sudo systemctl enable voice-assistant.service")
    print("\n🎤 Say 'Hey Assistant' to begin using the voice assistant!")

if __name__ == "__main__":
    main() 