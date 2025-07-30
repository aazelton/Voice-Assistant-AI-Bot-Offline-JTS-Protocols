#!/bin/bash

echo "🚀 Quick Development Push Script"
echo "================================"

# Test if we can import basic modules
echo "🧪 Testing imports..."
python3 -c "
try:
    import json, numpy, faiss, sentence_transformers
    print('✅ All imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Run simple test if available
if [ -f "scripts/test_simple.py" ]; then
    echo "🧪 Running simple test..."
    python3 scripts/test_simple.py
fi

# Git operations
echo "📝 Git operations..."
git add .
git status --short

read -p "Commit message (or press Enter for default): " commit_msg
if [ -z "$commit_msg" ]; then
    commit_msg="Update $(date +%H:%M:%S)"
fi

git commit -m "$commit_msg"
git push

echo "✅ Pushed to remote! Now test on VM:"
echo "   ssh vm && cd project && git pull && python3 scripts/ask_fast.py" 