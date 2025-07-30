# 🔐 API Key Setup Guide

## **Secure API Key Management**

### **Step 1: Get Your API Keys**

**Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key (starts with `AIza...`)

**OpenAI API Key:**
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Copy the key (starts with `sk-...`)

### **Step 2: Create Local `.env` File**

**On your Mac (development):**
```bash
# In your project directory
echo "GEMINI_API_KEY=your_actual_gemini_key_here" > .env
echo "OPENAI_API_KEY=your_actual_openai_key_here" >> .env
```

**On your VM (testing):**
```bash
# SSH into your VM, then:
echo "GEMINI_API_KEY=your_actual_gemini_key_here" > .env
echo "OPENAI_API_KEY=your_actual_openai_key_here" >> .env
```

**On your Raspberry Pi (production):**
```bash
# SSH into your Pi, then:
echo "GEMINI_API_KEY=your_actual_gemini_key_here" > .env
echo "OPENAI_API_KEY=your_actual_openai_key_here" >> .env
```

### **Step 3: Keep `.env` Secure**

**✅ DO:**
- Add `.env` to `.gitignore` (already done)
- Use different keys for different environments
- Rotate keys regularly
- Store keys securely on each device

**❌ DON'T:**
- Never commit `.env` to git
- Never share keys in chat/email
- Never hardcode keys in scripts
- Never use same key everywhere

### **Step 4: Test Your Setup**

**Test locally:**
```bash
python3 scripts/ask_cloud.py
```

**Test on VM:**
```bash
# SSH to VM, then:
git pull
python3 scripts/ask_cloud.py
```

### **Step 5: Environment-Specific Keys**

**Development (Mac):**
```bash
GEMINI_API_KEY=dev_gemini_key
OPENAI_API_KEY=dev_openai_key
```

**Testing (VM):**
```bash
GEMINI_API_KEY=test_gemini_key
OPENAI_API_KEY=test_openai_key
```

**Production (Pi):**
```bash
GEMINI_API_KEY=prod_gemini_key
OPENAI_API_KEY=prod_openai_key
```

## **🔒 Security Best Practices**

### **1. Key Rotation**
- Change keys every 90 days
- Use environment-specific keys
- Monitor API usage

### **2. Access Control**
- Limit API key permissions
- Use read-only keys when possible
- Monitor for unusual activity

### **3. Backup Strategy**
- Store keys in password manager
- Keep encrypted backups
- Document key purposes

## **🚀 Quick Setup Commands**

**For each device, run these commands:**

```bash
# 1. Navigate to project
cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols

# 2. Create .env file
cat > .env << EOF
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here
EOF

# 3. Test the setup
python3 scripts/ask_cloud.py
```

## **📱 Device-Specific Setup**

### **Mac (Development)**
```bash
# Already done - you have the project here
# Just add your API keys to .env
```

### **VM (Testing)**
```bash
# SSH into VM
ssh akaclinicalco@your_vm_ip

# Navigate and setup
cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols
# Add .env with your keys
```

### **Raspberry Pi (Production)**
```bash
# SSH into Pi
ssh pi@your_pi_ip

# Navigate and setup  
cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols
# Add .env with your keys
```

## **🔍 Troubleshooting**

**"API key not found" error:**
- Check `.env` file exists
- Verify key format is correct
- Ensure no extra spaces

**"API failed" error:**
- Check internet connection
- Verify key is valid
- Check API quotas

**"Module not found" error:**
- Install requirements: `pip install -r requirements.txt`
- Add missing packages to requirements.txt 