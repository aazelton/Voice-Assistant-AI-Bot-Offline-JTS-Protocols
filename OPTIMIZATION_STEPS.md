# 🚀 VM Optimization Steps - Option 1: Optimized Single VM

## 🎯 Goal
Optimize your VM to run the JTS system efficiently with minimal resources (cost reduction: $100/month → $40/month).

## 📋 Files Created
- `jts_service_optimized.py` - Optimized JTS service (smaller model, fewer threads)
- `jts-api-optimized.service` - Systemd service with resource limits
- `configure_firewall.sh` - GCP firewall configuration script

## 🔧 Step-by-Step Instructions

### Step 1: Access VM via Google Cloud Console
1. **Open Google Cloud Console**
   - Go to: https://console.cloud.google.com
   - Navigate to **Compute Engine** > **VM instances**
   - Find your VM instance (IP: 34.45.48.120)

2. **Connect via Cloud Console**
   - Click on your VM instance
   - Click the **"SSH"** button (opens browser-based terminal)
   - This bypasses SSH connection issues

### Step 2: Upload Optimization Files
In the Cloud Console terminal, run:

```bash
# Create a temporary directory
mkdir ~/optimization
cd ~/optimization
```

3. **Upload the files** (copy-paste the contents):
   - Copy `jts_service_optimized.py` content and create the file
   - Copy `jts-api-optimized.service` content and create the file
   - Copy `configure_firewall.sh` content and create the file

### Step 3: Clean Up VM Processes
```bash
# Check what's consuming CPU
top
ps aux --sort=-%cpu | head -10

# Stop unnecessary processes
sudo systemctl list-units --type=service --state=running
sudo systemctl stop [unnecessary-services]

# Kill high-CPU processes (if needed)
pkill -f training
pkill -f background
```

### Step 4: Install Optimized Service
```bash
# Copy files to proper locations
cp jts_service_optimized.py ~/
cp jts-api-optimized.service ~/

# Install the optimized service
sudo mv ~/jts-api-optimized.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jts-api-optimized

# Stop old service and start optimized service
sudo systemctl stop jts-api
sudo systemctl start jts-api-optimized

# Check status
sudo systemctl status jts-api-optimized
```

### Step 5: Configure Firewall
```bash
# Make firewall script executable
chmod +x configure_firewall.sh

# Run firewall configuration
./configure_firewall.sh
```

### Step 6: Test the Optimized System
```bash
# Test local access
curl http://localhost:5000/health

# Test query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "ketamine RSI"}'
```

### Step 7: Test from Your Mac
```bash
# Test external access
curl http://34.45.48.120:5000/health

# Run voice assistant
python3 scripts/voice_jts_vm.py
```

## 🎯 Expected Results

After optimization:
- ✅ CPU load: <50% (down from 300%)
- ✅ Memory usage: ~6GB (down from 15GB)
- ✅ Query response time: <2 seconds
- ✅ External access: Working
- ✅ SSH connections: Stable
- ✅ Cost reduction: $100/month → $40/month

## 🔍 Troubleshooting

### If service fails to start:
```bash
# Check logs
sudo journalctl -u jts-api-optimized -f

# Check if smaller model is available
cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols
source venv/bin/activate
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-MiniLM-L3-v2')"
```

### If firewall fails:
```bash
# Manual firewall rule via Cloud Console
# 1. Go to VPC Network > Firewall
# 2. Click "Create Firewall Rule"
# 3. Name: allow-jts-api
# 4. Targets: All instances in the network
# 5. Source IP ranges: 0.0.0.0/0
# 6. Protocols and ports: tcp:5000
```

## 💰 Cost Optimization

**Current VM specs (overkill):**
- CPU: 4 cores
- Memory: 15GB
- Cost: ~$100/month

**Optimized specs (sufficient):**
- CPU: 2 cores (limited by service)
- Memory: 8GB (limited by service)
- Cost: ~$40/month

## 🚀 Next Steps

1. Follow the steps above via Google Cloud Console
2. Test the optimized system
3. Consider downgrading VM specs in GCP Console
4. Monitor performance over time
5. Enjoy your cost-effective JTS voice assistant! 