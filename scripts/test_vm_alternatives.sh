#!/bin/bash

echo "🔧 VM Connection Alternatives Test"
echo "=================================="

VM_HOST="10.128.0.2"
VM_USER="akaclinicalco"

echo "1. Testing direct SSH with different ports..."
for port in 22 2222 8022; do
    echo "   Testing port $port..."
    timeout 5 ssh -p $port -o ConnectTimeout=5 $VM_USER@$VM_HOST "echo 'Connection successful'" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "   ✅ Port $port works!"
        break
    else
        echo "   ❌ Port $port failed"
    fi
done

echo ""
echo "2. Testing with different hostnames..."
for host in $VM_HOST "mistral-vm" "vm.local"; do
    echo "   Testing $host..."
    timeout 5 ssh -o ConnectTimeout=5 $VM_USER@$host "echo 'Connection successful'" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "   ✅ $host works!"
        break
    else
        echo "   ❌ $host failed"
    fi
done

echo ""
echo "3. Network diagnostic..."
echo "   Your current network info:"
ifconfig | grep "inet " | grep -v 127.0.0.1

echo ""
echo "4. Possible solutions:"
echo "   A. Connect to VPN first"
echo "   B. Use cloud console to access VM directly"
echo "   C. Check if VM IP has changed"
echo "   D. Set up SSH tunnel/port forwarding" 