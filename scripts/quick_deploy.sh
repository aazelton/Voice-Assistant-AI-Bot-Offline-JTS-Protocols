#!/bin/bash
# Quick Deploy Script - One-command deployment to VM

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VM_IP=${VM_IP:-""}
VM_USER=${VM_USER:-"akaclinicalco"}
PROJECT_DIR="Voice-Assistant-AI-Bot-Offline-JTS-Protocols"

echo -e "${BLUE}🚀 TRAUMA ASSISTANT - QUICK DEPLOY${NC}"
echo "=================================================="

# Get VM IP if not set
if [ -z "$VM_IP" ]; then
    echo -e "${YELLOW}VM_IP not set. Please enter your VM IP address:${NC}"
    read VM_IP
fi

echo -e "${GREEN}📋 Configuration:${NC}"
echo "   VM IP: $VM_IP"
echo "   VM User: $VM_USER"
echo "   Project: $PROJECT_DIR"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Not in a git repository. Please run this from the project root.${NC}"
    exit 1
fi

# Step 1: Check for changes
echo -e "\n${BLUE}🔄 Checking for changes...${NC}"
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}📝 No changes to commit${NC}"
else
    echo -e "${GREEN}📝 Changes detected, committing...${NC}"
    
    # Add all changes
    git add .
    
    # Commit with timestamp
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    git commit -m "Auto-deploy: $TIMESTAMP"
    
    # Push to remote
    echo -e "${BLUE}📤 Pushing to remote...${NC}"
    git push
    
    echo -e "${GREEN}✅ Successfully pushed to remote!${NC}"
fi

# Step 2: Pull on VM
echo -e "\n${BLUE}📥 Pulling on VM...${NC}"
ssh $VM_USER@$VM_IP "cd ~/$PROJECT_DIR && git pull"

echo -e "${GREEN}✅ Successfully pulled on VM!${NC}"

# Step 3: Ask if user wants to run test
echo -e "\n${YELLOW}Run test on VM? (y/n):${NC}"
read -r choice

if [[ $choice =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Script to run (default: scripts/ask_fast.py):${NC}"
    read -r script_choice
    
    if [ -z "$script_choice" ]; then
        script_choice="scripts/ask_fast.py"
    fi
    
    echo -e "\n${BLUE}🧪 Running $script_choice on VM...${NC}"
    echo "=================================================="
    
    ssh $VM_USER@$VM_IP "cd ~/$PROJECT_DIR && source venv/bin/activate && python3 $script_choice"
fi

echo -e "\n${GREEN}✅ Quick deploy complete!${NC}" 