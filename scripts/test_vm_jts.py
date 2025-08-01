#!/usr/bin/env python3
"""
Test script to check JTS database access on VM
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

def test_vm_files():
    """Test what files are available on the VM"""
    try:
        print("🔍 Checking VM files...")
        
        # Check what's in the project directory
        cmd = f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'ls -la ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols/'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ VM files found:")
            print(result.stdout)
        else:
            print(f"❌ Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_jts_data():
    """Test if JTS data files exist"""
    try:
        print("🔍 Checking JTS data files...")
        
        # Check for embeddings and metadata
        cmd = f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'ls -la ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols/embeds/'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ JTS data files found:")
            print(result.stdout)
        else:
            print(f"❌ Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_simple_query():
    """Test a simple query approach"""
    try:
        print("🔍 Testing simple query...")
        
        # Create a simple Python script to test the database
        python_script = """
import sys
import os
sys.path.append('/home/akaclinicalco/Voice-Assistant-AI-Bot-Offline-JTS-Protocols')

try:
    from scripts.ask_balanced import load_model, load_embeddings, search_context, generate_response
    
    print("Loading model...")
    model = load_model()
    
    print("Loading embeddings...")
    embedding_model, index, metadata = load_embeddings()
    
    if model and embedding_model and index and metadata:
        print("All components loaded successfully!")
        print(f"Index has {index.ntotal} entries")
        print(f"Metadata type: {type(metadata)}")
        
        # Test a simple search
        question = "ketamine RSI"
        context = search_context(question, embedding_model, index, metadata)
        print(f"Found {len(context)} context chunks")
        
        if context:
            response = generate_response(question, context, model)
            print("Response:", response)
        else:
            print("No context found")
    else:
        print("Failed to load components")
        
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
        scp_cmd = f"scp {script_path} {VM_CONFIG['username']}@{VM_CONFIG['hostname']}:~/test_jts.py"
        ssh_cmd = f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols && source venv/bin/activate && python3 ~/test_jts.py'"
        
        # Copy script
        subprocess.run(scp_cmd, shell=True, check=True, timeout=15)
        
        # Execute script
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        # Clean up
        os.unlink(script_path)
        subprocess.run(f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'rm ~/test_jts.py'", shell=True)
        
        if result.returncode == 0:
            print("✅ Test successful:")
            print(result.stdout)
        else:
            print(f"❌ Test failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 VM JTS Database Test")
    print("=" * 40)
    
    test_vm_files()
    print()
    test_jts_data()
    print()
    test_simple_query() 