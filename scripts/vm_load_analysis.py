#!/usr/bin/env python3
"""
VM Load Analysis - Understand why the VM is overloaded
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

def analyze_vm_processes():
    """Analyze what processes are running on the VM"""
    try:
        print("🔍 ANALYZING VM PROCESSES")
        print("=" * 40)
        
        # Create a script to analyze processes
        analysis_script = """
import psutil
import json

print("=== PROCESS ANALYSIS ===")
print(f"CPU Count: {psutil.cpu_count()}")
print(f"Memory Total: {psutil.virtual_memory().total / (1024**3):.1f} GB")
print(f"Memory Available: {psutil.virtual_memory().available / (1024**3):.1f} GB")
print(f"Memory Used: {psutil.virtual_memory().used / (1024**3):.1f} GB")
print(f"CPU Load: {psutil.getloadavg()}")

print("\\n=== TOP CPU PROCESSES ===")
processes = []
for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'cmdline']):
    try:
        if proc.info['cpu_percent'] > 0:
            processes.append(proc.info)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

# Sort by CPU usage
processes.sort(key=lambda x: x['cpu_percent'], reverse=True)

for proc in processes[:10]:
    cmdline = ' '.join(proc['cmdline'][:3]) if proc['cmdline'] else proc['name']
    print(f"PID {proc['pid']}: {proc['name']} - CPU: {proc['cpu_percent']:.1f}% - MEM: {proc['memory_percent']:.1f}% - {cmdline}")

print("\\n=== PYTHON PROCESSES ===")
python_procs = [p for p in processes if 'python' in p['name'].lower()]
for proc in python_procs[:5]:
    cmdline = ' '.join(proc['cmdline'][:3]) if proc['cmdline'] else proc['name']
    print(f"PID {proc['pid']}: {proc['name']} - CPU: {proc['cpu_percent']:.1f}% - MEM: {proc['memory_percent']:.1f}% - {cmdline}")

print("\\n=== SYSTEMD SERVICES ===")
try:
    import subprocess
    result = subprocess.run(['systemctl', 'list-units', '--type=service', '--state=running'], 
                          capture_output=True, text=True, timeout=10)
    lines = result.stdout.split('\\n')[:20]
    for line in lines:
        if 'jts' in line.lower() or 'python' in line.lower():
            print(line.strip())
except:
    print("Could not get systemd services")
"""
        
        # Write script to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(analysis_script)
            script_path = f.name
        
        # Copy to VM and run
        scp_cmd = f"scp {script_path} {VM_CONFIG['username']}@{VM_CONFIG['hostname']}:~/vm_analysis.py"
        ssh_cmd = f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols && source venv/bin/activate && pip install psutil && python3 ~/vm_analysis.py'"
        
        # Copy script
        subprocess.run(scp_cmd, shell=True, check=True, timeout=15)
        
        # Run analysis
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        # Clean up
        os.unlink(script_path)
        subprocess.run(f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'rm ~/vm_analysis.py'", shell=True)
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ Analysis failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def analyze_jts_service_performance():
    """Analyze the JTS service performance"""
    try:
        print("\n🔍 ANALYZING JTS SERVICE PERFORMANCE")
        print("=" * 40)
        
        # Test service response time
        test_script = """
import time
import requests
import json

print("Testing JTS service performance...")

# Test health endpoint
start_time = time.time()
try:
    response = requests.get('http://localhost:5000/health', timeout=5)
    health_time = time.time() - start_time
    print(f"Health check: {health_time:.3f}s - Status: {response.status_code}")
except Exception as e:
    print(f"Health check failed: {e}")

# Test query endpoint
start_time = time.time()
try:
    data = {"question": "ketamine RSI"}
    response = requests.post('http://localhost:5000/query', json=data, timeout=30)
    query_time = time.time() - start_time
    print(f"Query test: {query_time:.3f}s - Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response length: {len(result.get('response', ''))} characters")
except Exception as e:
    print(f"Query test failed: {e}")

# Check service logs
print("\\nRecent service logs:")
import subprocess
try:
    result = subprocess.run(['journalctl', '-u', 'jts-api', '-n', '10', '--no-pager'], 
                          capture_output=True, text=True, timeout=10)
    print(result.stdout)
except:
    print("Could not get service logs")
"""
        
        # Write script to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            script_path = f.name
        
        # Copy to VM and run
        scp_cmd = f"scp {script_path} {VM_CONFIG['username']}@{VM_CONFIG['hostname']}:~/service_test.py"
        ssh_cmd = f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols && source venv/bin/activate && python3 ~/service_test.py'"
        
        # Copy script
        subprocess.run(scp_cmd, shell=True, check=True, timeout=15)
        
        # Run test
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        # Clean up
        os.unlink(script_path)
        subprocess.run(f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'rm ~/service_test.py'", shell=True)
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ Service test failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def provide_optimization_recommendations():
    """Provide specific optimization recommendations"""
    print("\n🔧 OPTIMIZATION RECOMMENDATIONS")
    print("=" * 40)
    
    print("1. IMMEDIATE ACTIONS:")
    print("   🔄 Stop unnecessary processes on VM")
    print("   🔄 Restart VM to clear memory")
    print("   🔄 Check for background training jobs")
    print("   🔄 Monitor systemd services")
    
    print("\n2. JTS SERVICE OPTIMIZATIONS:")
    print("   ✅ Service is already optimized (persistent)")
    print("   🔄 Reduce LLM context from 1024 to 512")
    print("   🔄 Use fewer LLM threads (2 instead of 4)")
    print("   🔄 Implement response caching")
    
    print("\n3. VM RESOURCE OPTIMIZATIONS:")
    print("   🔄 Upgrade to 8GB RAM (from 15GB)")
    print("   🔄 Use 2-4 CPU cores (current is fine)")
    print("   🔄 Enable swap if needed")
    print("   🔄 Use SSD storage")
    
    print("\n4. NETWORK OPTIMIZATIONS:")
    print("   🔄 Configure GCP firewall for port 5000")
    print("   🔄 Use load balancer for multiple instances")
    print("   🔄 Implement connection pooling")
    
    print("\n5. DEPLOYMENT OPTIMIZATIONS:")
    print("   🔄 Use Docker containers")
    print("   🔄 Implement health checks")
    print("   🔄 Use auto-scaling groups")
    print("   🔄 Consider edge deployment")

def main():
    print("🔍 VM LOAD ANALYSIS")
    print("=" * 50)
    
    print("Based on the diagnostic data, here's what we know:")
    print("✅ VM is reachable (ping successful)")
    print("✅ JTS service is running and healthy")
    print("✅ Models load in ~10 seconds")
    print("❌ SSH connections timeout due to high load")
    print("❌ External port 5000 not accessible")
    
    print("\n🎯 ROOT CAUSE ANALYSIS:")
    print("The VM is NOT overloaded by the JTS system itself.")
    print("The issue is likely:")
    print("1. Other processes consuming CPU (load average 12.00)")
    print("2. GCP firewall blocking external port access")
    print("3. SSH connection limits due to resource contention")
    
    print("\n💡 SOLUTION STRATEGY:")
    print("1. The JTS system is already optimized")
    print("2. Need to identify and stop other CPU-intensive processes")
    print("3. Configure GCP firewall for external access")
    print("4. Consider upgrading VM resources if needed")
    
    # Try to get more detailed analysis
    try:
        analyze_vm_processes()
        analyze_jts_service_performance()
    except:
        print("\n⚠️  Could not get detailed VM analysis due to connection issues")
    
    provide_optimization_recommendations()

if __name__ == "__main__":
    main() 