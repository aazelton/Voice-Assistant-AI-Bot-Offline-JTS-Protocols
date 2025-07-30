# Trauma Assistant - Voice-Activated Clinical Decision Support

A voice-assisted AI bot for rapid clinical decision support using Joint Trauma System (JTS) Clinical Practice Guidelines. Designed to run on Raspberry Pi 4 with offline capabilities and cloud development support.

🚧 Not for Clinical Use
This is a proof-of-concept project for exploration and learning. It’s not certified or approved for clinical decision-making. Please don’t use it for actual patient care.

## 🚀 Quick Start

### Step 1: Get JTS Clinical Practice Guidelines
```bash
# Download JTS PDFs (required for the system to work)
python3 scripts/download_jts_pdfs.py

# This will guide you through:
# 1. Manual download from JTS website (recommended)
# 2. Auto-download attempt (limited)
# 3. Sample files for testing
```

### Step 2: Mac Development Setup
```bash
# Clone and setup
git clone <your-repo>
cd trauma-assistant
python3 setup_mac.py

# Build the knowledge base
python3 scripts/build_index.py

# Test locally (fast iteration)
python3 scripts/ask_conversational.py

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
│   ├── download_jts_pdfs.py  # JTS PDF downloader
│   ├── build_index.py        # Build FAISS knowledge base
│   ├── ask_conversational.py # Human-like clinical assistant
│   ├── ask_cloud.py          # Cloud-enhanced assistant
│   ├── ask_fast.py           # Optimized Q&A (VM/Pi)
│   ├── local_test.py         # Local testing (Mac)
│   ├── dev_workflow.py       # Development workflow
│   └── quick_deploy.sh       # One-command deployment
├── pdfs/                     # JTS Clinical Practice Guidelines (80+ PDFs)
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

## 📚 JTS Clinical Practice Guidelines

The system uses **Joint Trauma System (JTS) Clinical Practice Guidelines** as its knowledge base:

- **80+ PDF files** covering trauma protocols
- **~100MB total** when downloaded
- **Official military medical guidelines**
- **Updated regularly** by JTS

### Getting the PDFs:
```bash
# Run the downloader script
python3 scripts/download_jts_pdfs.py

# Options:
# 1. Manual download from JTS website (recommended)
# 2. Auto-download attempt (limited availability)
# 3. Sample files for testing
```

**Note**: JTS PDFs are not included in the GitHub repository due to size and licensing. Users must download them separately.

### Expected PDF Files:
- `Acute_Coronary_Syndrome_14_May_2021_ID86.pdf`
- `Airway_Management_of_Traumatic_Injuries_17_Jul_2017_ID39.pdf`
- `Burn_Care_CPG_10_June_2025_ID12.pdf`
- `Damage_Control_Resuscitation_12_Jul_2019_ID18.pdf`
- `Ketamine_Protocol_Management_15_Mar_2024_ID88.pdf`
- `TXA_Tranexamic_Acid_Protocol_22_Jan_2025_ID99.pdf`
- ... and 70+ more protocols

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
