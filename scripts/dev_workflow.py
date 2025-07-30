#!/usr/bin/env python3
"""
Development Workflow Script
Automates the push/pull cycle for rapid iteration between Mac and VM
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and return success status"""
    print(f"🔄 {description}")
    print(f"   Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Error: {description}")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def check_git_status():
    """Check if there are changes to commit"""
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    return bool(result.stdout.strip())

def push_to_remote():
    """Push changes to remote repository"""
    print("\n🚀 PUSHING TO REMOTE REPOSITORY")
    print("=" * 50)
    
    if not check_git_status():
        print("📝 No changes to commit")
        return True
    
    # Add all changes
    if not run_command("git add .", "Adding all changes"):
        return False
    
    # Commit with timestamp
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"Auto-deploy: {timestamp}"
    if not run_command(f'git commit -m "{commit_msg}"', "Committing changes"):
        return False
    
    # Push to remote
    if not run_command("git push", "Pushing to remote"):
        return False
    
    print("\n✅ Successfully pushed to remote!")
    return True

def pull_on_vm(vm_ip, vm_user="akaclinicalco"):
    """Pull changes on VM"""
    print(f"\n📥 PULLING ON VM ({vm_user}@{vm_ip})")
    print("=" * 50)
    
    ssh_cmd = f"ssh {vm_user}@{vm_ip} 'cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols && git pull'"
    return run_command(ssh_cmd, "Pulling latest changes on VM")

def run_test_on_vm(vm_ip, script="scripts/ask_fast.py", vm_user="akaclinicalco"):
    """Run a test script on VM"""
    print(f"\n🧪 RUNNING TEST ON VM")
    print("=" * 50)
    
    ssh_cmd = f"ssh {vm_user}@{vm_ip} 'cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols && source venv/bin/activate && python3 {script}'"
    return run_command(ssh_cmd, f"Running {script} on VM")

def main():
    print("🚀 TRAUMA ASSISTANT - DEVELOPMENT WORKFLOW")
    print("=" * 50)
    
    # Get VM IP from environment or prompt
    vm_ip = os.getenv("VM_IP")
    if not vm_ip:
        vm_ip = input("Enter your VM IP address: ").strip()
    
    vm_user = os.getenv("VM_USER", "akaclinicalco")
    
    print(f"📋 Workflow Configuration:")
    print(f"   VM IP: {vm_ip}")
    print(f"   VM User: {vm_user}")
    print(f"   Project: Voice-Assistant-AI-Bot-Offline-JTS-Protocols")
    
    # Step 1: Push to remote
    if not push_to_remote():
        print("❌ Failed to push to remote. Stopping.")
        return
    
    # Step 2: Pull on VM
    if not pull_on_vm(vm_ip, vm_user):
        print("❌ Failed to pull on VM. Stopping.")
        return
    
    # Step 3: Ask if user wants to run test
    print("\n" + "=" * 50)
    choice = input("Run test on VM? (y/n): ").strip().lower()
    
    if choice == 'y':
        script_choice = input("Script to run (default: scripts/ask_fast.py): ").strip()
        if not script_choice:
            script_choice = "scripts/ask_fast.py"
        
        run_test_on_vm(vm_ip, script_choice, vm_user)
    
    print("\n✅ Development workflow complete!")

if __name__ == "__main__":
    main() 