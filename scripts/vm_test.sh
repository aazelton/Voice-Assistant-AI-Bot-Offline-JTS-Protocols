#!/bin/bash

echo "🖥️  VM Quick Test Script"
echo "======================="

# Navigate to project
cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Quick test
echo "🧪 Testing imports..."
python3 -c "
try:
    import json, numpy, faiss, sentence_transformers, llama_cpp
    print('✅ All imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Check if model exists
if [ ! -f "models/mistral.Q4_K_M.gguf" ]; then
    echo "❌ Model not found! Download it first."
    exit(1)
fi

# Check if embeddings exist
if [ ! -f "embeds/faiss.idx" ]; then
    echo "❌ Embeddings not found! Run build_index.py first."
    exit(1)
fi

echo "✅ Ready to test! Running ask_fast.py..."
echo "💡 Try: 'What is the dose for ketamine induction?'"
echo ""

python3 scripts/ask_fast.py 