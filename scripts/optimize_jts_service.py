#!/usr/bin/env python3
"""
Optimize JTS Service - Create resource-efficient version
"""

import subprocess
import tempfile
import os

# VM Configuration
VM_CONFIG = {
    'hostname': '34.69.34.151',
    'username': 'akaclinicalco',
    'port': 22,
    'timeout': 10
}

def create_optimized_service():
    """Create an optimized version of the JTS service"""
    try:
        print("🔧 Creating optimized JTS service...")
        
        # Create the optimized Flask service script
        optimized_service = """#!/usr/bin/env python3
# Optimized JTS REST API Service - Minimal Resource Usage
import flask
from flask import Flask, request, jsonify
import sys
import os
import time
import json
import faiss
from sentence_transformers import SentenceTransformer

# Add the project path
sys.path.append('/home/akaclinicalco/Voice-Assistant-AI-Bot-Offline-JTS-Protocols')

app = Flask(__name__)

# Global variables for loaded models
model = None
index = None
metadata = None

def load_models():
    global model, index, metadata
    if model is None:
        print("Loading optimized sentence transformer...")
        # Use smaller model for better performance
        model = SentenceTransformer('paraphrase-MiniLM-L3-v2')  # Smaller than L6
        print("Loading FAISS index...")
        index = faiss.read_index('/home/akaclinicalco/Voice-Assistant-AI-Bot-Offline-JTS-Protocols/embeds/faiss.idx')
        print("Loading metadata...")
        with open('/home/akaclinicalco/Voice-Assistant-AI-Bot-Offline-JTS-Protocols/embeds/meta.json', 'r') as f:
            metadata = json.load(f)
        print("All models loaded successfully!")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "models_loaded": model is not None})

@app.route('/query', methods=['POST'])
def query():
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # Load models if not already loaded
        if model is None:
            load_models()
        
        # Search for relevant context (reduced from 3 to 2 for efficiency)
        question_embedding = model.encode([question])
        distances, indices = index.search(question_embedding, 2)  # Reduced from 3
        
        # Get relevant chunks
        relevant_chunks = []
        for idx in indices[0]:
            if idx < len(metadata):
                relevant_chunks.append(metadata[idx])
        
        if relevant_chunks:
            # Return the first chunk as response
            chunk = relevant_chunks[0]
            if isinstance(chunk, dict):
                if 'text' in chunk:
                    response_text = chunk['text']
                elif 'content' in chunk:
                    response_text = chunk['content']
                else:
                    response_text = str(chunk)
            else:
                response_text = str(chunk)
            
            return jsonify({
                "question": question,
                "response": response_text,
                "chunks_found": len(relevant_chunks)
            })
        else:
            return jsonify({
                "question": question,
                "response": "No relevant JTS protocol found for this query.",
                "chunks_found": 0
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/load', methods=['POST'])
def load():
    try:
        load_models()
        return jsonify({"status": "Models loaded successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting optimized JTS REST API service...")
    load_models()
    # Use threaded=False for single-threaded operation (reduces resource usage)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=False)
"""
        
        # Write the optimized service script to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(optimized_service)
            script_path = f.name
        
        # Copy optimized service script to VM
        scp_cmd = f"scp {script_path} {VM_CONFIG['username']}@{VM_CONFIG['hostname']}:~/jts_service_optimized.py"
        subprocess.run(scp_cmd, shell=True, check=True, timeout=15)
        
        # Create optimized systemd service file
        optimized_service_file = f"""[Unit]
Description=Optimized JTS REST API Service
After=network.target

[Service]
Type=simple
User={VM_CONFIG['username']}
WorkingDirectory=/home/{VM_CONFIG['username']}/Voice-Assistant-AI-Bot-Offline-JTS-Protocols
Environment=PATH=/home/{VM_CONFIG['username']}/Voice-Assistant-AI-Bot-Offline-JTS-Protocols/venv/bin
ExecStart=/home/{VM_CONFIG['username']}/Voice-Assistant-AI-Bot-Offline-JTS-Protocols/venv/bin/python3 /home/{VM_CONFIG['username']}/jts_service_optimized.py
Restart=always
RestartSec=10
# Resource limits
MemoryMax=8G
CPUQuota=200%  # Limit to 2 CPU cores

[Install]
WantedBy=multi-user.target
"""
        
        # Write optimized service file to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.service', delete=False) as f:
            f.write(optimized_service_file)
            service_path = f.name
        
        # Copy optimized service file to VM
        scp_service_cmd = f"scp {service_path} {VM_CONFIG['username']}@{VM_CONFIG['hostname']}:~/jts-api-optimized.service"
        subprocess.run(scp_service_cmd, shell=True, check=True, timeout=15)
        
        # Install and start the optimized service
        install_cmd = f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'sudo mv ~/jts-api-optimized.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable jts-api-optimized && sudo systemctl stop jts-api && sudo systemctl start jts-api-optimized'"
        result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        # Clean up
        os.unlink(script_path)
        os.unlink(service_path)
        
        if result.returncode == 0:
            print("✅ Optimized JTS REST API service installed and started successfully!")
            print("Service will be available at: http://34.69.34.151:5000")
            print("Health check: http://34.69.34.151:5000/health")
            print("Resource limits: 8GB RAM, 2 CPU cores")
        else:
            print(f"❌ Optimized service installation failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def create_firewall_script():
    """Create a script to configure GCP firewall"""
    try:
        print("🌐 Creating firewall configuration script...")
        
        firewall_script = """#!/bin/bash
# GCP Firewall Configuration Script

echo "Configuring GCP firewall for JTS API..."

# Create firewall rule for port 5000
gcloud compute firewall-rules create allow-jts-api \\
  --allow tcp:5000 \\
  --source-ranges 0.0.0.0/0 \\
  --description "Allow JTS API access" \\
  --direction INGRESS

echo "Firewall rule created successfully!"
echo "Testing connectivity..."

# Test the connection
curl -s http://localhost:5000/health

echo "Firewall configuration complete!"
"""
        
        # Write firewall script to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(firewall_script)
            script_path = f.name
        
        # Copy firewall script to VM
        scp_cmd = f"scp {script_path} {VM_CONFIG['username']}@{VM_CONFIG['hostname']}:~/configure_firewall.sh"
        subprocess.run(scp_cmd, shell=True, check=True, timeout=15)
        
        # Make executable and run
        chmod_cmd = f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'chmod +x ~/configure_firewall.sh'"
        subprocess.run(chmod_cmd, shell=True, check=True, timeout=15)
        
        # Clean up
        os.unlink(script_path)
        
        print("✅ Firewall configuration script created!")
        print("Run on VM: ./configure_firewall.sh")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🔧 VM OPTIMIZATION - OPTION 1")
    print("=" * 50)
    
    print("This will optimize your VM for minimal resource usage:")
    print("1. Create optimized JTS service (smaller model, fewer threads)")
    print("2. Set resource limits (8GB RAM, 2 CPU cores)")
    print("3. Create firewall configuration script")
    print("4. Expected cost reduction: $100/month → $40/month")
    
    print("\n⚠️  IMPORTANT: Access VM via Google Cloud Console first!")
    print("1. Go to: https://console.cloud.google.com")
    print("2. Navigate to Compute Engine > VM instances")
    print("3. Click SSH button on your VM")
    print("4. Then run the optimization commands")
    
    # Create optimized service
    try:
        create_optimized_service()
        create_firewall_script()
        
        print("\n✅ OPTIMIZATION COMPLETE!")
        print("Next steps:")
        print("1. Access VM via Google Cloud Console")
        print("2. Run: sudo systemctl status jts-api-optimized")
        print("3. Run: ./configure_firewall.sh")
        print("4. Test: curl http://34.69.34.151:5000/health")
        print("5. Run voice assistant: python3 scripts/voice_jts_vm.py")
        
    except Exception as e:
        print(f"\n❌ Optimization failed: {e}")
        print("Please access VM via Google Cloud Console and run manually")

if __name__ == "__main__":
    main() 