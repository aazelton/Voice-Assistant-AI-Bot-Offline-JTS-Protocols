#!/usr/bin/env python3
"""
VM Troubleshooting Script
Diagnoses VM connection issues and provides solutions
"""

import subprocess
import sys
import time
import json
from typing import Dict, List, Tuple

def run_command(cmd: str, timeout: int = 30) -> Tuple[bool, str, str]:
    """Run a command and return success, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        return False, "", str(e)

def test_network_connectivity(host: str) -> Dict[str, bool]:
    """Test basic network connectivity"""
    print(f"🔍 Testing network connectivity to {host}...")
    
    tests = {}
    
    # Ping test
    success, _, stderr = run_command(f"ping -c 3 {host}", timeout=10)
    tests["ping"] = success
    if not success:
        print(f"   ❌ Ping failed: {stderr}")
    else:
        print("   ✅ Ping successful")
    
    # Port 22 (SSH) test
    success, _, stderr = run_command(f"nc -z -w 5 {host} 22", timeout=10)
    tests["ssh_port"] = success
    if not success:
        print(f"   ❌ SSH port 22 closed: {stderr}")
    else:
        print("   ✅ SSH port 22 open")
    
    # Port 5000 (API) test
    success, _, stderr = run_command(f"nc -z -w 5 {host} 5000", timeout=10)
    tests["api_port"] = success
    if not success:
        print(f"   ❌ API port 5000 closed: {stderr}")
    else:
        print("   ✅ API port 5000 open")
    
    return tests

def test_ssh_connection(host: str, username: str) -> Dict[str, bool]:
    """Test SSH connection"""
    print(f"🔍 Testing SSH connection to {username}@{host}...")
    
    tests = {}
    
    # Basic SSH connection
    ssh_cmd = f"ssh -o ConnectTimeout=10 -o BatchMode=yes {username}@{host} 'echo SSH connection successful'"
    success, stdout, stderr = run_command(ssh_cmd, timeout=15)
    tests["ssh_basic"] = success
    if not success:
        print(f"   ❌ SSH connection failed: {stderr}")
    else:
        print("   ✅ SSH connection successful")
    
    # Check if project directory exists
    if success:
        ssh_cmd = f"ssh -o ConnectTimeout=10 {username}@{host} 'ls -la ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols'"
        success, stdout, stderr = run_command(ssh_cmd, timeout=15)
        tests["project_dir"] = success
        if not success:
            print(f"   ❌ Project directory not found: {stderr}")
        else:
            print("   ✅ Project directory exists")
    
    return tests

def check_gcp_status() -> Dict[str, str]:
    """Check if gcloud CLI is available and configured"""
    print("🔍 Checking Google Cloud CLI status...")
    
    status = {}
    
    # Check if gcloud is installed
    success, stdout, stderr = run_command("which gcloud")
    status["gcloud_installed"] = "Yes" if success else "No"
    
    if success:
        print("   ✅ gcloud CLI installed")
        
        # Check if authenticated
        success, stdout, stderr = run_command("gcloud auth list --filter=status:ACTIVE --format='value(account)'")
        status["authenticated"] = stdout.strip() if success else "No"
        
        if success and stdout.strip():
            print(f"   ✅ Authenticated as: {stdout.strip()}")
        else:
            print("   ❌ Not authenticated")
        
        # Check if project is set
        success, stdout, stderr = run_command("gcloud config get-value project")
        status["project"] = stdout.strip() if success else "Not set"
        
        if success and stdout.strip():
            print(f"   ✅ Project: {stdout.strip()}")
        else:
            print("   ❌ No project set")
    else:
        print("   ❌ gcloud CLI not installed")
    
    return status

def provide_solutions(network_tests: Dict[str, bool], ssh_tests: Dict[str, bool], gcp_status: Dict[str, str]):
    """Provide solutions based on test results"""
    print("\n🔧 TROUBLESHOOTING SOLUTIONS")
    print("=" * 50)
    
    # Network connectivity issues
    if not network_tests.get("ping", False):
        print("\n🌐 NETWORK CONNECTIVITY ISSUES:")
        print("   1. Check your internet connection")
        print("   2. Verify the VM IP address is correct")
        print("   3. The VM might be stopped or deleted")
        print("   4. Check Google Cloud Console: https://console.cloud.google.com")
    
    if network_tests.get("ping", False) and not network_tests.get("ssh_port", False):
        print("\n🔒 FIREWALL ISSUES:")
        print("   1. SSH port 22 is blocked")
        print("   2. Check GCP firewall rules")
        print("   3. Run: gcloud compute firewall-rules list")
        print("   4. Create rule: gcloud compute firewall-rules create allow-ssh --allow tcp:22")
    
    if network_tests.get("ssh_port", False) and not ssh_tests.get("ssh_basic", False):
        print("\n🔑 SSH AUTHENTICATION ISSUES:")
        print("   1. SSH keys not configured")
        print("   2. Run: ssh-keygen -t rsa -b 4096")
        print("   3. Add key to VM: gcloud compute instances add-metadata [INSTANCE] --metadata ssh-keys='[USER]:[KEY]'")
        print("   4. Or use: gcloud compute ssh [USER]@[INSTANCE]")
    
    if gcp_status.get("gcloud_installed") == "No":
        print("\n☁️ GOOGLE CLOUD CLI ISSUES:")
        print("   1. Install gcloud CLI:")
        print("      curl https://sdk.cloud.google.com | bash")
        print("      exec -l $SHELL")
        print("      gcloud init")
    
    if gcp_status.get("authenticated") == "No":
        print("\n🔐 AUTHENTICATION ISSUES:")
        print("   1. Authenticate with Google Cloud:")
        print("      gcloud auth login")
        print("      gcloud auth application-default login")
    
    # VM-specific solutions
    print("\n🖥️ VM-SPECIFIC SOLUTIONS:")
    print("   1. Check VM status in Google Cloud Console")
    print("   2. Start VM if stopped: gcloud compute instances start [INSTANCE]")
    print("   3. Check VM logs: gcloud compute instances get-serial-port-output [INSTANCE]")
    print("   4. Reset VM if needed: gcloud compute instances reset [INSTANCE]")

def main():
    """Main troubleshooting function"""
    print("🔧 VM TROUBLESHOOTING SCRIPT")
    print("=" * 50)
    
    # Get VM details
    vm_host = input("Enter VM IP address (default: 34.45.48.120): ").strip() or "34.45.48.120"
    vm_user = input("Enter VM username (default: akaclinicalco): ").strip() or "akaclinicalco"
    
    print(f"\n🔍 Testing VM: {vm_user}@{vm_host}")
    
    # Run tests
    network_tests = test_network_connectivity(vm_host)
    ssh_tests = test_ssh_connection(vm_host, vm_user)
    gcp_status = check_gcp_status()
    
    # Provide solutions
    provide_solutions(network_tests, ssh_tests, gcp_status)
    
    print("\n📋 NEXT STEPS:")
    print("   1. Check Google Cloud Console: https://console.cloud.google.com")
    print("   2. Navigate to Compute Engine > VM instances")
    print("   3. Check if your VM is running")
    print("   4. Note the external IP address")
    print("   5. Update scripts with correct IP if needed")
    
    print("\n🔗 USEFUL LINKS:")
    print("   - Google Cloud Console: https://console.cloud.google.com")
    print("   - VM Instance List: https://console.cloud.google.com/compute/instances")
    print("   - Firewall Rules: https://console.cloud.google.com/networking/firewall")
    print("   - SSH Keys: https://console.cloud.google.com/compute/metadata/ssh-keys")

if __name__ == "__main__":
    main() 