#!/bin/bash

echo "🔧 SSH Tunnel Setup for VM Access"
echo "================================="

# Configuration
VM_HOST="10.128.0.2"
VM_USER="akaclinicalco"
LOCAL_PORT="2222"
REMOTE_PORT="22"

echo "Setting up SSH tunnel..."
echo "Local port: $LOCAL_PORT -> VM: $VM_HOST:$REMOTE_PORT"

# Kill any existing tunnel
pkill -f "ssh.*$LOCAL_PORT"

# Create tunnel in background
ssh -L $LOCAL_PORT:$VM_HOST:$REMOTE_PORT -N $VM_USER@$VM_HOST &
TUNNEL_PID=$!

echo "Tunnel PID: $TUNNEL_PID"
echo "Testing tunnel connection..."

sleep 2

# Test tunnel
ssh -p $LOCAL_PORT -o ConnectTimeout=10 $VM_USER@localhost "echo 'Tunnel connection successful'"

if [ $? -eq 0 ]; then
    echo "✅ Tunnel established successfully!"
    echo "You can now use:"
    echo "  ssh -p $LOCAL_PORT $VM_USER@localhost"
    echo ""
    echo "To test JTS voice assistant:"
    echo "  python3 scripts/voice_jts_tunnel.py"
else
    echo "❌ Tunnel failed to establish"
    echo "Check if you can reach the VM directly first"
fi 