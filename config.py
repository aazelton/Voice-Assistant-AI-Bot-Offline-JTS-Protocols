import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Model Configuration
MODEL_PATH = os.getenv("MODEL_PATH", "models/mistral.Q4_K_M.gguf")
EMBEDDINGS_PATH = os.getenv("EMBEDDINGS_PATH", "embeds/faiss.idx")
METADATA_PATH = os.getenv("METADATA_PATH", "embeds/meta.json")
DOCS_PATH = os.getenv("DOCS_PATH", "embeds/docs.txt")

# Audio Configuration
AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
AUDIO_CHANNELS = int(os.getenv("AUDIO_CHANNELS", "1"))
AUDIO_CHUNK_SIZE = int(os.getenv("AUDIO_CHUNK_SIZE", "1024"))
AUDIO_FORMAT = int(os.getenv("AUDIO_FORMAT", "16"))  # 16-bit

# Speech Recognition
SPEECH_RECOGNITION_TIMEOUT = float(os.getenv("SPEECH_RECOGNITION_TIMEOUT", "5.0"))
SPEECH_RECOGNITION_PHRASE_TIME_LIMIT = float(os.getenv("SPEECH_RECOGNITION_PHRASE_TIME_LIMIT", "10.0"))
SPEECH_RECOGNITION_NON_SPEAKING_DURATION = float(os.getenv("SPEECH_RECOGNITION_NON_SPEAKING_DURATION", "0.5"))

# Wake Word Configuration
WAKE_WORD = os.getenv("WAKE_WORD", "Hey Assistant")
WAKE_WORD_SENSITIVITY = float(os.getenv("WAKE_WORD_SENSITIVITY", "0.5"))
WAKE_WORD_DETECTION_MODE = os.getenv("WAKE_WORD_DETECTION_MODE", "porcupine")  # porcupine or snowboy

# Gemini Voice Configuration
GEMINI_VOICE_API_KEY = os.getenv("GEMINI_VOICE_API_KEY", "")
GEMINI_VOICE_MODEL = os.getenv("GEMINI_VOICE_MODEL", "gemini-1.5-flash")
GEMINI_VOICE_VOICE_ID = os.getenv("GEMINI_VOICE_VOICE_ID", "medical-professional")
GEMINI_VOICE_SPEED = float(os.getenv("GEMINI_VOICE_SPEED", "1.0"))

# TTS Configuration
TTS_ENGINE = os.getenv("TTS_ENGINE", "gemini")  # gemini, espeak, pyttsx3, gtts
TTS_VOICE = os.getenv("TTS_VOICE", "en-us")
TTS_RATE = int(os.getenv("TTS_RATE", "150"))
TTS_VOLUME = float(os.getenv("TTS_VOLUME", "1.0"))

# LLM Configuration
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "150"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_TOP_P = float(os.getenv("LLM_TOP_P", "0.9"))
LLM_CONTEXT_WINDOW = int(os.getenv("LLM_CONTEXT_WINDOW", "4096"))

# Vector Search Configuration
VECTOR_SEARCH_TOP_K = int(os.getenv("VECTOR_SEARCH_TOP_K", "3"))
VECTOR_SEARCH_THRESHOLD = float(os.getenv("VECTOR_SEARCH_THRESHOLD", "0.5"))

# System Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/voice_assistant.log")
MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "10"))

# Performance Configuration
CPU_GOVERNOR = os.getenv("CPU_GOVERNOR", "performance")
MAX_TEMPERATURE = float(os.getenv("MAX_TEMPERATURE", "80.0"))
MEMORY_LIMIT = int(os.getenv("MEMORY_LIMIT", "6144"))  # MB

# Security Configuration
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")
API_KEY_FILE = os.getenv("API_KEY_FILE", ".env")

# Network Configuration
ONLINE_MODE = os.getenv("ONLINE_MODE", "false").lower() == "true"
PROXY_URL = os.getenv("PROXY_URL", "")
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "30"))

# File Paths
PDFS_DIR = os.getenv("PDFS_DIR", "pdfs/")
MODELS_DIR = os.getenv("MODELS_DIR", "models/")
EMBEDS_DIR = os.getenv("EMBEDS_DIR", "embeds/")
LOGS_DIR = os.getenv("LOGS_DIR", "logs/")
CACHE_DIR = os.getenv("CACHE_DIR", "cache/")

# Create directories if they don't exist
for directory in [PDFS_DIR, MODELS_DIR, EMBEDS_DIR, LOGS_DIR, CACHE_DIR]:
    os.makedirs(directory, exist_ok=True)
