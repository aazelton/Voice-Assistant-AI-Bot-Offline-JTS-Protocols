# VM Optimization Guide - Option 1: Optimized Single VM

## 🎯 Goal
Optimize the current VM to run the JTS system efficiently with minimal resources.

## 📋 Current Status
- ✅ VM is reachable (ping successful)
- ✅ JTS REST API service is running
- ✅ Models load in ~10 seconds
- ❌ SSH connections timeout due to high load
- ❌ External port 5000 not accessible

## 🔧 Step 1: Access VM via Google Cloud Console

1. **Open Google Cloud Console**
   - Go to: https://console.cloud.google.com
   - Navigate to Compute Engine > VM instances
   - Find your VM instance

2. **Connect via Cloud Console**
   - Click on your VM instance
   - Click "SSH" button (opens browser-based terminal)
   - This bypasses SSH connection issues

## 🧹 Step 2: Clean Up VM Processes

Once connected via Cloud Console, run these commands:

```bash
# Check what's consuming CPU
top
ps aux --sort=-%cpu | head -10

# Stop unnecessary processes
sudo systemctl list-units --type=service --state=running
sudo systemctl stop [unnecessary-services]

# Kill high-CPU processes (if needed)
pkill -f [process-name]

# Check for background training jobs
ps aux | grep python
pkill -f training
pkill -f background
```

## 🔥 Step 3: Optimize JTS Service

```bash
# Check JTS service status
sudo systemctl status jts-api

# Optimize LLM settings (reduce resource usage)
cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols
nano jts_service.py

# Change these settings in the LLM initialization:
# n_ctx=512,          # Reduce from 1024
# n_threads=2,        # Reduce from 4
# n_batch=16,         # Reduce from 32

# Restart the service
sudo systemctl restart jts-api
```

## 🌐 Step 4: Configure GCP Firewall

```bash
# Create firewall rule for port 5000
gcloud compute firewall-rules create allow-jts-api \
  --allow tcp:5000 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow JTS API access"

# Or via Cloud Console:
# 1. Go to VPC Network > Firewall
# 2. Click "Create Firewall Rule"
# 3. Name: allow-jts-api
# 4. Targets: All instances in the network
# 5. Source IP ranges: 0.0.0.0/0
# 6. Protocols and ports: tcp:5000
```

## 📊 Step 5: Monitor Performance

```bash
# Check system resources
htop
free -h
df -h

# Test JTS service
curl http://localhost:5000/health
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "ketamine RSI"}'

# Monitor service logs
sudo journalctl -u jts-api -f
```

## 🎯 Expected Results

After optimization:
- CPU load: <50% (down from 300%)
- Memory usage: ~6GB (down from 15GB)
- Query response time: <2 seconds
- External access: ✅ Working
- SSH connections: ✅ Stable

## 🚀 Step 6: Test from Mac

Once optimized, test from your Mac:

```bash
# Test external access
curl http://34.45.48.120:5000/health

# Test voice assistant
python3 scripts/voice_jts_vm.py
```

## 💰 Cost Optimization

Current VM specs (overkill):
- CPU: 4 cores
- Memory: 15GB
- Cost: ~$100/month

Optimized specs (sufficient):
- CPU: 2 cores
- Memory: 8GB
- Cost: ~$40/month

## 🔄 Next Steps

1. Follow the steps above via Cloud Console
2. Test the optimized system
3. Consider downgrading VM specs if needed
4. Monitor performance over time 