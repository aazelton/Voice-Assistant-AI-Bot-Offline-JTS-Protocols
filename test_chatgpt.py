#!/usr/bin/env python3
"""
Quick test to verify ChatGPT integration
"""

import os
import sys
from openai import OpenAI

# Load API keys
try:
    sys.path.append('config')
    from api_keys import OPENAI_API_KEY
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
except ImportError:
    pass

def test_chatgpt():
    """Test ChatGPT connection"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ No OpenAI API key found")
            return False
        
        print(f"🔑 API Key found: {api_key[:20]}...")
        
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful clinical assistant."},
                {"role": "user", "content": "Say 'ChatGPT is working!' in one sentence."}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ ChatGPT Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ ChatGPT test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing ChatGPT Integration...")
    success = test_chatgpt()
    if success:
        print("🎉 ChatGPT integration is working!")
    else:
        print("⚠️  ChatGPT integration failed") 