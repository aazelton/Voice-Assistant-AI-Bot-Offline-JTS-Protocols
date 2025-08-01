#!/usr/bin/env python3
"""
Test New VM IP Address
"""

import subprocess
import sys
import os
import re

def test_ip_connectivity(ip_address):
    """Test connectivity to new IP address"""
    print(f"🔍 Testing new VM IP: {ip_address}")
    print("=" * 50)
    
    # Test ping
    print("1️⃣ Testing ping...")
    try:
        result = subprocess.run(["ping", "-c", "3", ip_address], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("   ✅ Ping successful")
            return True
        else:
            print("   ❌ Ping failed")
            return False
    except:
        print("   ❌ Ping failed")
        return False

def test_ssh_connection(ip_address, username="akaclinicalco"):
    """Test SSH connection to new IP"""
    print(f"\n2️⃣ Testing SSH connection...")
    try:
        ssh_cmd = f"ssh -o ConnectTimeout=10 -o BatchMode=yes {username}@{ip_address} 'echo SSH connection successful'"
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print("   ✅ SSH connection successful")
            return True
        else:
            print(f"   ❌ SSH failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ SSH failed: {e}")
        return False

def test_api_endpoint(ip_address):
    """Test API endpoint on new IP"""
    print(f"\n3️⃣ Testing API endpoint...")
    try:
        result = subprocess.run(["curl", "-s", f"http://{ip_address}:5000/health"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and "ok" in result.stdout.lower():
            print("   ✅ API endpoint responding")
            return True
        else:
            print("   ❌ API endpoint not responding")
            return False
    except:
        print("   ❌ API endpoint not responding")
        return False

def update_ip_in_files(old_ip, new_ip):
    """Update IP address in all relevant files"""
    print(f"\n4️⃣ Updating IP address in files...")
    print(f"   Old IP: {old_ip}")
    print(f"   New IP: {new_ip}")
    
    files_to_update = [
        "scripts/vm_diagnostic.py",
        "scripts/voice_jts_vm.py", 
        "scripts/voice_jts_assistant.py",
        "scripts/optimize_jts_service.py",
        "scripts/setup_vm_service.py",
        "scripts/vm_troubleshoot.py",
        "scripts/check_vm_status.py",
        "jts_service_optimized.py"
    ]
    
    updated_count = 0
    for file_path in files_to_update:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                if old_ip in content:
                    content = content.replace(old_ip, new_ip)
                    with open(file_path, 'w') as f:
                        f.write(content)
                    print(f"   ✅ Updated: {file_path}")
                    updated_count += 1
                else:
                    print(f"   ⏭️  No changes: {file_path}")
            except Exception as e:
                print(f"   ❌ Error updating {file_path}: {e}")
    
    return updated_count

def main():
    """Main function"""
    print("🔧 VM IP ADDRESS UPDATE TOOL")
    print("=" * 50)
    
    # Get new IP from user
    new_ip = input("Enter the new VM IP address: ").strip()
    if not new_ip:
        print("❌ No IP address provided")
        return
    
    old_ip = "34.45.48.120"
    
    # Test connectivity
    if not test_ip_connectivity(new_ip):
        print("\n❌ IP address not reachable. Please verify:")
        print("   1. VM is running in Google Cloud Console")
        print("   2. IP address is correct")
        print("   3. Firewall rules allow access")
        return
    
    # Test SSH
    if not test_ssh_connection(new_ip):
        print("\n⚠️  SSH connection failed. This might be normal if:")
        print("   1. SSH keys not configured")
        print("   2. Firewall blocking SSH")
        print("   3. VM still starting up")
        print("\n   Continue with IP update anyway? (y/n): ", end="")
        if input().lower() != 'y':
            return
    
    # Test API
    test_api_endpoint(new_ip)
    
    # Update files
    updated_count = update_ip_in_files(old_ip, new_ip)
    
    print(f"\n✅ IP ADDRESS UPDATE COMPLETE")
    print(f"   Updated {updated_count} files")
    print(f"   New IP: {new_ip}")
    
    print(f"\n🔧 NEXT STEPS:")
    print(f"   1. Test VM connection: python3 scripts/vm_diagnostic.py")
    print(f"   2. Test voice assistant: python3 scripts/voice_jts_vm.py")
    print(f"   3. Commit changes: git add . && git commit -m 'Update VM IP'")

if __name__ == "__main__":
    main() 