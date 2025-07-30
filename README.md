# Trauma Assistant - Voice-Activated Clinical Decision Support

A voice-assisted AI bot for rapid clinical decision support using Joint Trauma System (JTS) Clinical Practice Guidelines. Designed to run on Raspberry Pi 4 with offline capabilities and cloud development support.

## 🚀 Quick Start

### Mac Development Setup
```bash
# Clone and setup
git clone <your-repo>
cd trauma-assistant
python3 setup_mac.py

# Test locally (fast iteration)
python3 scripts/local_test.py

# Deploy to VM (one command)
./scripts/quick_deploy.sh
```

### Raspberry Pi 4 Setup
```bash
# Automated setup
python3 setup.py

# Run voice assistant
python3 voice_assistant.py
```

## 🔄 Streamlined Development Workflow

### **Option 1: Local Development + Remote Testing (Recommended)**

**Mac (Development):**
```bash
# Fast local testing without full model
python3 scripts/local_test.py

# Edit code, then deploy with one command
./scripts/quick_deploy.sh
```

**VM (Testing):**
```bash
# Automatically pulls latest changes
# Runs full model inference
python3 scripts/ask_fast.py
```

### **Option 2: Python Workflow Script**
```bash
# Interactive deployment
python3 scripts/dev_workflow.py
```

### **Option 3: Manual Git Workflow**
```bash
# On Mac
git add .
git commit -m "Update prompt engineering"
git push

# On VM
git pull
python3 scripts/ask_fast.py
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mac (Dev)     │    │   VM (Test)     │    │   Pi 4 (Prod)   │
│                 │    │                 │    │                 │
│ • Fast editing  │───▶│ • Full model    │───▶│ • Edge deploy   │
│ • Local tests   │    │ • Performance   │    │ • Offline       │
│ • Git push      │    │ • Validation    │    │ • Voice I/O     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
trauma-assistant/
├── config.py                 # Centralized configuration
├── voice_assistant.py        # Main voice assistant
├── setup.py                  # Pi 4 setup script
├── setup_mac.py             # Mac development setup
├── scripts/
│   ├── ask_fast.py          # Optimized Q&A (VM/Pi)
│   ├── local_test.py        # Local testing (Mac)
│   ├── build_index.py       # Build knowledge base
│   ├── dev_workflow.py      # Development workflow
│   └── quick_deploy.sh      # One-command deployment
├── pdfs/                    # JTS CPG documents
├── models/                  # LLM models
├── embeds/                  # Vector embeddings
└── requirements.txt         # Dependencies
```

## ⚙️ Configuration

### Environment Variables
```bash
# .env file
GEMINI_API_KEY=your_api_key
VM_IP=your_vm_ip
VM_USER=akaclinicalco
```

### Performance Settings
```python
# config.py
LLM_PARAMS = {
    'n_ctx': 256,           # Context window
    'n_batch': 1,           # Batch size
    'n_threads': 2,         # CPU threads
    'max_tokens': 50,       # Response length
    'temperature': 0.0      # Deterministic
}
```

## 🧪 Testing Strategy

### **Mac (Fast Iteration)**
- ✅ Config loading
- ✅ Embeddings validation
- ✅ Prompt engineering
- ✅ Audio components
- ❌ Full model inference (too slow)

### **VM (Performance Testing)**
- ✅ Full model loading
- ✅ Vector search
- ✅ Response generation
- ✅ Medical accuracy

### **Pi 4 (Production)**
- ✅ Voice interaction
- ✅ Offline operation
- ✅ Real-world testing

## 🚀 Deployment Commands

### **Quick Deploy (Recommended)**
```bash
# Set your VM IP
export VM_IP=your_vm_ip

# Deploy with one command
./scripts/quick_deploy.sh
```

### **Manual Deployment**
```bash
# On Mac
git add .
git commit -m "Update"
git push

# On VM
ssh akaclinicalco@your-vm-ip
cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols
git pull
source venv/bin/activate
python3 scripts/ask_fast.py
```

## 📊 Performance Comparison

| Platform | Model Load | Response Time | Best For |
|----------|------------|---------------|----------|
| **Mac** | 30-60s | 10-30s | Development |
| **VM** | 10-20s | 2-5s | Testing |
| **Pi 4** | 15-30s | 3-8s | Production |

## 🔧 Troubleshooting

### **Common Issues**

**Mac Development:**
```bash
# Module not found
pip install -r requirements.txt

# Audio issues
brew install portaudio espeak mpg123
```

**VM Testing:**
```bash
# Git not updating
git fetch --all
git reset --hard origin/main

# Model too slow
python3 scripts/ask_fast.py  # Use optimized version
```

**Pi 4 Production:**
```bash
# Memory issues
sudo raspi-config  # Increase swap
# Or use smaller model
```

## 📈 Next Steps

1. **Optimize prompts** for medical accuracy
2. **Test on Pi 4** with real hardware
3. **Add voice wake word** detection
4. **Implement offline TTS** fallback
5. **Deploy to production** environment

## 🤝 Contributing

1. Edit code on Mac
2. Test locally: `python3 scripts/local_test.py`
3. Deploy to VM: `./scripts/quick_deploy.sh`
4. Validate performance
5. Deploy to Pi 4

---

**Goal**: Simple but practical voice assistant for rapid clinical decision support on edge devices.
