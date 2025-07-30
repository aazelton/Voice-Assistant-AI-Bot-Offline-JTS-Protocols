#!/usr/bin/env python3
"""
Test Cloud APIs - Simple test without FAISS index
"""

import os
import sys
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_gemini_api():
    """Test Gemini API"""
    try:
        import google.generativeai as genai
        
        gemini_key = os.getenv('GEMINI_API_KEY')
        if not gemini_key:
            print("❌ GEMINI_API_KEY not found")
            return False
            
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = "You are a clinical decision support assistant. Answer this medical question: What is the recommended dose of ketamine for RSI in a 70kg patient?"
        
        print("🧠 Testing Gemini API...")
        start_time = time.time()
        
        response = model.generate_content(prompt)
        
        end_time = time.time()
        
        print(f"✅ Gemini API working! ({end_time - start_time:.1f}s)")
        print(f"📋 Response: {response.text.strip()[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API failed: {e}")
        return False

def test_openai_api():
    """Test OpenAI API"""
    try:
        import openai
        
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            print("❌ OPENAI_API_KEY not found")
            return False
            
        openai.api_key = openai_key
        
        prompt = "You are a clinical decision support assistant. Answer this medical question: What is the recommended dose of ketamine for RSI in a 70kg patient?"
        
        print("🧠 Testing OpenAI API...")
        start_time = time.time()
        
        client = openai.OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a clinical decision support assistant for trauma care."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.3
        )
        
        end_time = time.time()
        
        print(f"✅ OpenAI API working! ({end_time - start_time:.1f}s)")
        print(f"📋 Response: {response.choices[0].message.content.strip()[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API failed: {e}")
        return False

def main():
    print("🧪 CLOUD API TEST")
    print("=" * 30)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Testing API connections...")
    print()
    
    gemini_working = test_gemini_api()
    print()
    openai_working = test_openai_api()
    print()
    
    if gemini_working or openai_working:
        print("🎉 Cloud APIs are working!")
        print("💡 You can now use ask_cloud.py on your VM where the FAISS index exists")
    else:
        print("❌ No cloud APIs are working")
        print("💡 Check your API keys and internet connection")

if __name__ == "__main__":
    main() 