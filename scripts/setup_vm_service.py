#!/usr/bin/env python3
"""
Setup VM Service - Create a persistent REST API service on the VM
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

def create_jts_service():
    """Create a Flask REST API service for JTS queries"""
    try:
        print("🔧 Creating JTS REST API service...")
        
        # Create the Flask service script
        service_script = """#!/usr/bin/env python3
# JTS REST API Service
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
        print("Loading sentence transformer...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
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
        
        # Search for relevant context
        question_embedding = model.encode([question])
        distances, indices = index.search(question_embedding, 3)
        
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
    print("Starting JTS REST API service...")
    load_models()
    app.run(host='0.0.0.0', port=5000, debug=False)
"""
        
        # Write the service script to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(service_script)
            script_path = f.name
        
        # Copy service script to VM
        scp_cmd = f"scp {script_path} {VM_CONFIG['username']}@{VM_CONFIG['hostname']}:~/jts_service.py"
        subprocess.run(scp_cmd, shell=True, check=True, timeout=15)
        
        # Create systemd service file
        service_file = f"""[Unit]
Description=JTS REST API Service
After=network.target

[Service]
Type=simple
User={VM_CONFIG['username']}
WorkingDirectory=/home/{VM_CONFIG['username']}/Voice-Assistant-AI-Bot-Offline-JTS-Protocols
Environment=PATH=/home/{VM_CONFIG['username']}/Voice-Assistant-AI-Bot-Offline-JTS-Protocols/venv/bin
ExecStart=/home/{VM_CONFIG['username']}/Voice-Assistant-AI-Bot-Offline-JTS-Protocols/venv/bin/python3 /home/{VM_CONFIG['username']}/jts_service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        # Write service file to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.service', delete=False) as f:
            f.write(service_file)
            service_path = f.name
        
        # Copy service file to VM
        scp_service_cmd = f"scp {service_path} {VM_CONFIG['username']}@{VM_CONFIG['hostname']}:~/jts-api.service"
        subprocess.run(scp_service_cmd, shell=True, check=True, timeout=15)
        
        # Install and start the service
        install_cmd = f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'sudo mv ~/jts-api.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable jts-api && sudo systemctl start jts-api'"
        result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        # Clean up
        os.unlink(script_path)
        os.unlink(service_path)
        
        if result.returncode == 0:
            print("✅ JTS REST API service installed and started successfully!")
            print("Service will be available at: http://34.69.34.151:5000")
            print("Health check: http://34.69.34.151:5000/health")
        else:
            print(f"❌ Service installation failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_service():
    """Test the REST API service"""
    try:
        print("🧪 Testing JTS REST API service...")
        
        # Test health endpoint
        health_cmd = "curl -s http://34.69.34.151:5000/health"
        result = subprocess.run(health_cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Health check successful:")
            print(result.stdout)
            
            # Test query endpoint
            query_cmd = 'curl -s -X POST http://34.69.34.151:5000/query -H "Content-Type: application/json" -d \'{"question": "ketamine RSI"}\''
            result = subprocess.run(query_cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Query test successful:")
                print(result.stdout)
            else:
                print(f"❌ Query test failed: {result.stderr}")
        else:
            print(f"❌ Health check failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔧 VM JTS Service Setup")
    print("=" * 40)
    
    create_jts_service()
    print()
    test_service() 