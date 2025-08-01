#!/usr/bin/env python3
"""
VM Diagnostic Script - Check VM resources and model loading issues
"""

import subprocess
import tempfile
import os

# VM Configuration
VM_CONFIG = {
    'hostname': '34.45.48.120',
    'username': 'akaclinicalco',
    'port': 22,
    'timeout': 10
}

def check_vm_resources():
    """Check VM CPU, memory, and disk usage"""
    try:
        print("🔍 Checking VM resources...")
        
        # Check system resources
        cmd = f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'free -h && df -h && nproc && uptime'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ VM resources:")
            print(result.stdout)
        else:
            print(f"❌ Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def check_model_loading_time():
    """Test how long it takes to load the sentence transformer model"""
    try:
        print("🔍 Testing model loading time...")
        
        # Create a script to time model loading
        python_script = """
import time
import sys
sys.path.append('/home/akaclinicalco/Voice-Assistant-AI-Bot-Offline-JTS-Protocols')

print("Starting model loading test...")

try:
    print("Loading sentence transformer...")
    start_time = time.time()
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    load_time = time.time() - start_time
    print(f"Sentence transformer loaded in {load_time:.2f} seconds")
    
    print("Loading FAISS index...")
    start_time = time.time()
    import faiss
    index = faiss.read_index('/home/akaclinicalco/Voice-Assistant-AI-Bot-Offline-JTS-Protocols/embeds/faiss.idx')
    faiss_time = time.time() - start_time
    print(f"FAISS index loaded in {faiss_time:.2f} seconds")
    
    print("Loading metadata...")
    start_time = time.time()
    import json
    with open('/home/akaclinicalco/Voice-Assistant-AI-Bot-Offline-JTS-Protocols/embeds/meta.json', 'r') as f:
        metadata = json.load(f)
    meta_time = time.time() - start_time
    print(f"Metadata loaded in {meta_time:.2f} seconds")
    
    total_time = load_time + faiss_time + meta_time
    print(f"Total loading time: {total_time:.2f} seconds")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
"""
        
        # Write the script to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_script)
            script_path = f.name
        
        # Copy script to VM and execute
        scp_cmd = f"scp {script_path} {VM_CONFIG['username']}@{VM_CONFIG['hostname']}:~/model_test.py"
        ssh_cmd = f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols && source venv/bin/activate && python3 ~/model_test.py'"
        
        # Copy script
        subprocess.run(scp_cmd, shell=True, check=True, timeout=15)
        
        # Execute script with very long timeout
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=300)
        
        # Clean up
        os.unlink(script_path)
        subprocess.run(f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'rm ~/model_test.py'", shell=True)
        
        if result.returncode == 0:
            print("✅ Model loading test successful:")
            print(result.stdout)
        else:
            print(f"❌ Model loading test failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ Model loading test timed out after 5 minutes")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_alternative_approach():
    """Test if we can load a smaller model or use a different approach"""
    try:
        print("🔍 Testing alternative approach...")
        
        # Try loading a smaller model
        python_script = """
import time
import sys
sys.path.append('/home/akaclinicalco/Voice-Assistant-AI-Bot-Offline-JTS-Protocols')

print("Testing alternative model loading...")

try:
    # Try loading a smaller model first
    print("Loading smaller model...")
    start_time = time.time()
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('paraphrase-MiniLM-L3-v2')  # Smaller model
    load_time = time.time() - start_time
    print(f"Smaller model loaded in {load_time:.2f} seconds")
    
    # Test if we can encode a simple query
    print("Testing encoding...")
    start_time = time.time()
    embedding = model.encode(["test query"])
    encode_time = time.time() - start_time
    print(f"Encoding completed in {encode_time:.2f} seconds")
    
    print("Alternative approach successful!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
"""
        
        # Write the script to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_script)
            script_path = f.name
        
        # Copy script to VM and execute
        scp_cmd = f"scp {script_path} {VM_CONFIG['username']}@{VM_CONFIG['hostname']}:~/alt_test.py"
        ssh_cmd = f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols && source venv/bin/activate && python3 ~/alt_test.py'"
        
        # Copy script
        subprocess.run(scp_cmd, shell=True, check=True, timeout=15)
        
        # Execute script
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=120)
        
        # Clean up
        os.unlink(script_path)
        subprocess.run(f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'rm ~/alt_test.py'", shell=True)
        
        if result.returncode == 0:
            print("✅ Alternative approach successful:")
            print(result.stdout)
        else:
            print(f"❌ Alternative approach failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 VM Diagnostic Test")
    print("=" * 40)
    
    check_vm_resources()
    print()
    check_model_loading_time()
    print()
    check_alternative_approach() 