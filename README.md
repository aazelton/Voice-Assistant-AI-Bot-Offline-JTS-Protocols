# Voice Assistant AI Bot (Offline JTS Protocols)

A fully offline-capable voice assistant for answering clinical treatment questions using the Joint Trauma System (JTS) guideline PDFs, designed specifically for Raspberry Pi 4 deployment with Gemini Voice integration.

## 🎤 Features

### Voice Interaction
- **Wake Word Detection**: "Hey Assistant" activation
- **Speech Recognition**: Google Speech Recognition (online) + Vosk (offline fallback)
- **Natural Voice Output**: Gemini Voice API + eSpeak-ng fallback
- **Real-time Audio Processing**: Low-latency voice interaction

### AI & Knowledge Base
- **Local LLM Processing**: Mistral 7B (quantized GGUF format)
- **Vector Search**: FAISS-based semantic search
- **Medical Knowledge**: JTS clinical guidelines and protocols
- **Context-Aware Responses**: Relevant document retrieval

### System Features
- **Fully Offline**: Works without internet connection
- **Raspberry Pi 4 Optimized**: ARM64 architecture support
- **Auto-start Capability**: Systemd service integration
- **Performance Monitoring**: CPU, memory, temperature tracking
- **Security**: Local data processing, no cloud storage

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Voice Input   │───▶│  Speech-to-Text │───▶│  Query Analysis │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Knowledge     │◀───│  Context        │◀───│  Vector Search  │
│   Base          │    │  Retrieval      │    │  (FAISS)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Voice Output  │◀───│  Text-to-Speech │◀───│  LLM Response   │
│   (Speaker)     │    │  (Gemini Voice) │    │  Generation     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Hardware Requirements

### Raspberry Pi 4 Specifications
- **Model**: Raspberry Pi 4B (4GB or 8GB RAM recommended)
- **Storage**: 64GB+ microSD card (Class 10, A2)
- **Audio**: USB microphone or Pi HAT microphone
- **Speaker**: USB speaker or 3.5mm audio output
- **Cooling**: Active cooling recommended for sustained LLM processing

### Performance Considerations
- **CPU**: ARM Cortex-A72 quad-core (1.5GHz)
- **Memory**: 4-8GB LPDDR4
- **Storage**: SSD recommended for faster I/O
- **Network**: WiFi 5GHz or Ethernet for online features

## 🚀 Quick Setup

### Mac Development Setup
```bash
# Clone the repository
git clone <repository-url>
cd trauma-assistant

# Run the Mac development setup script
python3 setup_mac.py
```

### Raspberry Pi Production Setup
```bash
# SSH into your Raspberry Pi
ssh pi@your-pi-ip-address

# Clone the repository
git clone <repository-url>
cd trauma-assistant

# Run the automated setup script
python3 setup.py
```

### 2. Manual Setup
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv portaudio19-dev espeak-ng mpg123

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p models pdfs embeds logs cache
```

### 3. Configuration
```bash
# The .env file is created automatically by setup.py
# Edit the configuration if needed
nano .env
```

### 4. Model Setup
```bash
# Download Mistral model (example)
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf -O models/mistral.Q4_K_M.gguf

# Place your PDF documents in pdfs/ directory
cp your_medical_documents.pdf pdfs/

# Build the knowledge base index
python3 scripts/build_index.py
```

### 5. Run the Voice Assistant
```bash
# Start the voice assistant
./start_voice_assistant.sh

# Or run directly
python3 voice_assistant.py
```

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Gemini Voice Configuration
GEMINI_VOICE_API_KEY=your_gemini_api_key_here
GEMINI_VOICE_MODEL=gemini-1.5-flash
GEMINI_VOICE_VOICE_ID=medical-professional

# Audio Configuration
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
AUDIO_CHUNK_SIZE=1024

# Wake Word Configuration
WAKE_WORD=Hey Assistant
WAKE_WORD_SENSITIVITY=0.5

# TTS Configuration
TTS_ENGINE=gemini  # gemini, espeak, pyttsx3, gtts
TTS_VOICE=en-us
TTS_RATE=150
TTS_VOLUME=1.0

# LLM Configuration
LLM_MAX_TOKENS=150
LLM_TEMPERATURE=0.7
LLM_CONTEXT_WINDOW=4096
```

## 🎯 Usage

### Voice Commands
1. **Activate**: Say "Hey Assistant"
2. **Ask Questions**: Speak your medical query naturally
3. **Examples**:
   - "What is the treatment for hemorrhagic shock?"
   - "How do I manage a tension pneumothorax?"
   - "What are the signs of compartment syndrome?"

### Text Interface (Alternative)
```bash
# Run text-based interface
python3 scripts/ask.py
```

## 🔧 Advanced Configuration

### Auto-start on Boot
```bash
# Enable systemd service
sudo cp voice-assistant.service /etc/systemd/system/
sudo systemctl enable voice-assistant.service
sudo systemctl start voice-assistant.service

# Check status
sudo systemctl status voice-assistant.service
```

### Performance Optimization
```bash
# Set CPU governor to performance
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Monitor system resources
htop
```

### Custom Wake Words
```bash
# Edit wake word in .env
WAKE_WORD=Your Custom Wake Word
```

## 📊 Monitoring & Logs

### Log Files
- **Main Log**: `logs/voice_assistant.log`
- **System Logs**: `sudo journalctl -u voice-assistant.service`

### Performance Monitoring
```bash
# Check CPU temperature
vcgencmd measure_temp

# Monitor memory usage
free -h

# Check disk space
df -h
```

## 🔒 Security & Privacy

### Data Protection
- **Local Processing**: All sensitive data processed locally
- **No Cloud Storage**: No medical data transmitted to cloud
- **Encryption**: Local file encryption for stored documents
- **Access Control**: User authentication for system access

### Network Security
- **Firewall**: UFW configuration for minimal network exposure
- **VPN**: Optional VPN for secure remote access
- **SSL/TLS**: Encrypted communication for online features
- **API Keys**: Secure storage of Gemini Voice API credentials

## 🐛 Troubleshooting

### Common Issues

#### Audio Problems
```bash
# Check audio devices
aplay -l
arecord -l

# Test microphone
arecord -D hw:1,0 -f S16_LE -r 16000 -c 1 test.wav
aplay test.wav
```

#### Model Loading Issues
```bash
# Check model file
ls -la models/

# Verify model integrity
file models/mistral.Q4_K_M.gguf
```

#### Performance Issues
```bash
# Monitor system resources
htop
iostat 1

# Check temperature
vcgencmd measure_temp
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python3 voice_assistant.py
```

## 📚 API Reference

### VoiceAssistant Class
```python
from voice_assistant import VoiceAssistant

# Initialize
assistant = VoiceAssistant()

# Process query
response = assistant.process_query("What is hemorrhagic shock?")

# Run main loop
assistant.run()
```

### Configuration Functions
```python
from config import *

# Access configuration
print(MODEL_PATH)
print(TTS_ENGINE)
print(WAKE_WORD)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Joint Trauma System (JTS)** for clinical guidelines
- **Mistral AI** for the language model
- **Google** for Gemini Voice API
- **Raspberry Pi Foundation** for the hardware platform

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs for error details

---

**Note**: This system is designed for educational and research purposes. Always consult with qualified medical professionals for clinical decision-making.
