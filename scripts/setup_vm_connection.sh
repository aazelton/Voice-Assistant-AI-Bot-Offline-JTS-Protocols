#!/bin/bash

echo "🔧 VM Connection Setup for JTS Voice Assistant"
echo "=============================================="

# VM Configuration
VM_HOST="10.128.0.2"
VM_USER="akaclinicalco"

echo "📋 Testing basic connectivity..."
ping -c 3 $VM_HOST

echo ""
echo "🔑 Testing SSH connection..."
ssh -o ConnectTimeout=10 $VM_USER@$VM_HOST "echo 'SSH connection successful'"

if [ $? -eq 0 ]; then
    echo "✅ SSH connection working!"
    
    echo ""
    echo "🧠 Testing JTS knowledge base..."
    ssh $VM_USER@$VM_HOST "cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols && source venv/bin/activate && echo 'ketamine RSI' | python3 scripts/ask_balanced.py"
    
    echo ""
    echo "🎤 Ready to use voice assistant with VM connection!"
    echo "Run: python3 scripts/voice_jts_vm.py"
else
    echo "❌ SSH connection failed"
    echo ""
    echo "🔧 Troubleshooting steps:"
    echo "1. Complete 2FA authentication manually:"
    echo "   ssh $VM_USER@$VM_HOST"
    echo ""
    echo "2. Test the connection again:"
    echo "   ./scripts/setup_vm_connection.sh"
    echo ""
    echo "3. Or use local version:"
    echo "   python3 scripts/voice_jts_local.py"
fi 