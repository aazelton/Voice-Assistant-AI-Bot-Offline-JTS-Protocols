# 🚑 **TRAUMA ASSISTANT - ARCHITECTURE DOCUMENTATION**

## **🎯 Project Overview**

Voice-activated AI bot for rapid clinical decision support using Joint Trauma System (JTS) Clinical Practice Guidelines. Designed for paramedics and trauma providers with direct, concise responses. Supports multiple deployment scenarios: local development, cloud VM, and future Raspberry Pi deployment.

---

## **🏗️ System Architecture**

### **Core Components**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Voice Input   │───▶│  Speech-to-Text │───▶│   Query Text    │
│   (Microphone)  │    │   (STT Engine)  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Text Output   │◀───│ Text-to-Speech  │◀───│  AI Response    │
│   (Speaker)     │    │   (TTS Engine)  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       ▲
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   JTS Database  │───▶│  Vector Search  │───▶│  LLM Processing │
│   (Embeddings)  │    │   (FAISS/API)   │    │  (ChatGPT/Gemini)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## **📁 Current Project Structure**

```
trauma-assistant/
├── voice_assistant.py              # Core voice assistant class
├── config/
│   └── api_keys.py                 # API keys (IGNORED by git)
├── scripts/
│   ├── voice_jts_local.py         # Local JTS database assistant
│   ├── voice_jts_vm.py            # Remote VM integration
│   ├── voice_jts_hybrid.py        # Hybrid with fallback
│   ├── voice_calculator_assistant.py # Drug dose calculator
│   ├── voice_calculator_quick.py  # Quick dose calculations
│   ├── voice_demo.py              # Basic voice demo
│   ├── voice_demo_mac.py          # Mac-specific demo
│   ├── voice_ai_assistant.py      # General AI assistant
│   ├── voice_remote.py            # Remote voice interface
│   ├── ask_medical.py             # Medical query script
│   ├── ask_balanced.py            # Balanced query approach
│   ├── ask_simple.py              # Simple query interface
│   ├── ask_fast.py                # Fast query mode
│   ├── ask_smart.py               # Smart query with context
│   ├── ask_tiny.py                # Minimal resource mode
│   ├── ask_ultra_fast.py          # Ultra-fast responses
│   ├── ask_conversational.py      # Conversational mode
│   ├── ask_interactive.py         # Interactive query mode
│   ├── ask_lookup.py              # Direct lookup mode
│   ├── ask_cloud.py               # Cloud API queries
│   ├── ask_hybrid.py              # Hybrid query approach
│   ├── vm_diagnostic.py           # VM health checks
│   ├── vm_load_analysis.py        # VM performance analysis
│   ├── resource_analysis.py       # Resource usage analysis
│   ├── optimize_jts_service.py    # VM optimization
│   ├── setup_vm_service.py        # VM service setup
│   ├── setup_vm_connection.sh     # VM connection script
│   ├── test_vm_alternatives.sh    # VM testing
│   ├── setup_ssh_tunnel.sh        # SSH tunnel setup
│   └── vm_optimization_guide.md   # Optimization guide
├── models/                        # Local models (IGNORED)
├── embeds/                        # Embeddings (IGNORED)
├── logs/                          # Logs (IGNORED)
├── cache/                         # Cache files (IGNORED)
├── pdfs/                          # JTS PDFs (IGNORED)
├── venv/                          # Virtual environment (IGNORED)
├── requirements.txt               # Python dependencies
├── setup.py                       # Setup script
├── setup_mac.py                   # Mac-specific setup
├── config.py                      # Configuration
├── jts_service_optimized.py       # Optimized VM service
├── jts-api-optimized.service      # Systemd service file
├── configure_firewall.sh          # Firewall configuration
├── OPTIMIZATION_STEPS.md          # Optimization guide
├── API_SETUP.md                   # API setup instructions
├── README.md                      # Main documentation
└── .gitignore                     # Git ignore rules
```

---

## **🤖 Voice Assistant Variants**

### **1. Local JTS Assistant (`voice_jts_local.py`)**
- **Purpose**: Local development with embedded JTS database
- **Features**: 
  - Offline operation
  - Local embeddings search
  - Fast response times
  - No internet dependency
- **Use Case**: Development, testing, offline scenarios

### **2. VM Integration (`voice_jts_vm.py`)**
- **Purpose**: Full JTS database access via cloud VM
- **Features**:
  - Complete JTS protocol access
  - Persistent REST API service
  - Remote accessibility
  - Optimized resource usage
- **Use Case**: Production deployment, full protocol access

### **3. Hybrid Assistant (`voice_jts_hybrid.py`)**
- **Purpose**: Best of both worlds with fallback
- **Features**:
  - VM primary, local fallback
  - Automatic failover
  - Reliable operation
  - Graceful degradation
- **Use Case**: Production with reliability

### **4. Calculator Assistant (`voice_calculator_assistant.py`)**
- **Purpose**: Drug dose calculations
- **Features**:
  - Patient weight-based dosing
  - Total dose calculations
  - Medical unit conversions
  - Context memory
- **Use Case**: Quick dose calculations

---

## **🧠 AI Integration Architecture**

### **Large Language Models**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Context Search │───▶│  ChatGPT API    │
│                 │    │   (JTS Data)    │    │  (gpt-4o-mini)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Fallback      │◀───│  Response       │◀───│  Gemini API     │
│   (Local Mode)  │    │   Processing    │    │  (gemini-2.0)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Prompt Engineering**
- **System Prompt**: Calm paramedic persona with tactical responses
- **User Prompt**: Direct medical queries with patient context
- **Response Style**: Concise, actionable (1-2 sentences)
- **Context Integration**: JTS guidelines + patient data

---

## **☁️ VM Infrastructure**

### **Google Cloud Platform Setup**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Local Client  │───▶│  GCP Firewall   │───▶│  VM Instance    │
│   (Mac/Pi)      │    │   (Port 5000)   │    │   (8GB RAM)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SSH Access    │◀───│  Systemd        │◀───│  JTS API        │
│   (Management)  │    │   Service       │    │  (Flask)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **VM Specifications**
- **Platform**: Google Cloud Platform
- **Machine Type**: e2-standard-2 (2 vCPU, 8GB RAM)
- **Storage**: 50GB SSD
- **OS**: Ubuntu 22.04 LTS
- **Cost**: ~$40/month (optimized)

### **Service Architecture**
- **REST API**: Flask-based JTS query service
- **Systemd**: Persistent service management
- **Firewall**: GCP firewall rules for port 5000
- **Monitoring**: Resource usage tracking

---

## **🔒 Security Architecture**

### **API Key Management**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Environment   │───▶│  Config Loader  │───▶│  API Client     │
│   Variables     │    │   (Secure)      │    │  (ChatGPT/Gemini)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Security Measures**
- **Git Protection**: `.gitignore` excludes sensitive files
- **Environment Variables**: API keys loaded from environment
- **Fallback Systems**: Works without external APIs
- **Local Operation**: No internet required for core features
- **VM Security**: SSH key-based access, firewall rules

---

## **📊 Data Flow Architecture**

### **Voice Processing Pipeline**
```
1. Voice Input → Speech Recognition → Text Query
2. Text Query → Context Search → JTS Data
3. JTS Data + Query → LLM Processing → AI Response
4. AI Response → Text-to-Speech → Voice Output
```

### **Context Management**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Patient       │───▶│  Context        │───▶│  Response       │
│   Weight        │    │   Memory        │    │  Generation     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Drug          │───▶│  Conversation   │───▶│  Dose           │
│   Indication    │    │   History       │    │  Calculation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## **🚀 Deployment Architecture**

### **Development Environment (Mac)**
- **Local JTS Database**: Embedded FAISS index
- **Voice Processing**: Native macOS audio
- **AI Integration**: ChatGPT/Gemini APIs
- **Cost**: $0 (local operation)

### **Production Environment (VM)**
- **Full JTS Database**: Complete protocol access
- **Persistent Service**: 24/7 availability
- **Remote Access**: SSH and API endpoints
- **Cost**: ~$40/month (optimized)

### **Future: Edge Deployment (Raspberry Pi)**
- **Offline Operation**: Local models and database
- **Low Power**: Optimized for battery operation
- **Rugged Design**: Field-ready hardware
- **Cost**: One-time hardware cost

---

## **🔧 Performance Optimization**

### **Resource Usage**
- **Memory**: < 4GB RAM for local operation
- **CPU**: < 50% during normal operation
- **Response Time**: < 2 seconds for voice queries
- **Network**: Minimal bandwidth for API calls

### **Optimization Strategies**
- **Embedding Model**: `all-MiniLM-L6-v2` (lightweight)
- **Context Length**: Reduced from 1024 to 512 tokens
- **LLM Threads**: 2 instead of 4 for VM
- **Response Caching**: Implemented for repeated queries
- **Resource Limits**: 8GB RAM, 2 CPU cores on VM

---

## **📋 API Architecture**

### **REST API Endpoints**
```
GET  /health          # Service health check
POST /query           # JTS query endpoint
GET  /protocols       # List available protocols
GET  /search          # Semantic search endpoint
```

### **Request/Response Format**
```json
{
  "query": "epinephrine dose for 70kg patient",
  "context": {
    "patient_weight": 70,
    "drug": "epinephrine",
    "indication": "cardiac arrest"
  }
}
```

---

## **🔄 Future Architecture (Raspberry Pi)**

### **Planned Components**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GPIO Button   │───▶│  Wake Word      │───▶│  Voice Input    │
│   (Physical)    │    │   Detection     │    │   (Microphone)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LED Status    │◀───│  Audio Output   │◀───│  TTS Engine     │
│   (Visual)      │    │   (Speaker)     │    │   (Local)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Edge Computing Features**
- **Offline Operation**: Local STT, TTS, and LLM models
- **Coral TPU**: Accelerated inference for medical QA
- **Low Power**: Optimized for battery operation
- **Boot Service**: Auto-start on power-up

---

## **📞 Monitoring & Maintenance**

### **Health Monitoring**
- **VM Status**: Resource usage tracking
- **API Health**: Endpoint availability checks
- **Performance Metrics**: Response time monitoring
- **Error Logging**: Comprehensive error tracking

### **Maintenance Tasks**
- **API Key Rotation**: Monthly security review
- **Database Updates**: JTS protocol updates
- **Performance Tuning**: Response time optimization
- **Backup Management**: Configuration and data backups

---

*Last Updated: August 2024*
*Architecture Version: 2.0*
*Status: Production Ready*