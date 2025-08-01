#!/usr/bin/env python3
"""
Quick VM Status Checker
"""

import subprocess
import sys

def check_vm_status():
    """Check VM connectivity and provide status"""
    print("🔍 VM STATUS CHECK")
    print("=" * 40)
    
    vm_ip = "34.45.48.120"
    vm_user = "akaclinicalco"
    
    print(f"Testing VM: {vm_user}@{vm_ip}")
    print()
    
    # Test 1: Ping
    print("1️⃣ Testing ping...")
    try:
        result = subprocess.run(["ping", "-c", "1", vm_ip], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("   ✅ VM responds to ping")
        else:
            print("   ❌ VM not responding to ping")
    except:
        print("   ❌ VM not responding to ping")
    
    # Test 2: SSH port
    print("\n2️⃣ Testing SSH port...")
    try:
        result = subprocess.run(["nc", "-z", "-w", "3", vm_ip, "22"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("   ✅ SSH port 22 is open")
        else:
            print("   ❌ SSH port 22 is closed")
    except:
        print("   ❌ SSH port 22 is closed")
    
    # Test 3: API port
    print("\n3️⃣ Testing API port...")
    try:
        result = subprocess.run(["nc", "-z", "-w", "3", vm_ip, "5000"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("   ✅ API port 5000 is open")
        else:
            print("   ❌ API port 5000 is closed")
    except:
        print("   ❌ API port 5000 is closed")
    
    print("\n" + "=" * 40)
    print("🔧 LIKELY ISSUES & SOLUTIONS:")
    print()
    
    print("❌ VM NOT RESPONDING:")
    print("   • VM is stopped or deleted")
    print("   • IP address changed")
    print("   • Network connectivity issues")
    print()
    
    print("🔗 NEXT STEPS:")
    print("   1. Check Google Cloud Console:")
    print("      https://console.cloud.google.com/compute/instances")
    print()
    print("   2. If VM exists but IP changed:")
    print("      • Update IP in scripts")
    print("      • Test new connection")
    print()
    print("   3. If VM is stopped:")
    print("      • Start VM in console")
    print("      • Wait for IP assignment")
    print()
    print("   4. If VM is deleted:")
    print("      • Create new VM")
    print("      • Deploy JTS service")
    print()
    print("   5. Alternative: Use local mode")
    print("      • python3 scripts/voice_jts_local.py")
    print("      • Works without VM")

if __name__ == "__main__":
    check_vm_status() 