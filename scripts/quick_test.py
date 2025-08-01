#!/usr/bin/env python3
"""
Quick test of VM voice assistant with a specific query
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.voice_jts_vm import (
    query_jts_rest_api, 
    get_ai_enhanced_response, 
    get_fallback_response,
    extract_weight_and_drug,
    speak_response
)

def test_query(query):
    """Test a specific query"""
    print(f"🧪 Testing: {query}")
    print("=" * 50)
    
    # Extract weight and drug
    weight, drug = extract_weight_and_drug(query)
    print(f"📊 Extracted: Weight={weight}kg, Drug={drug}")
    
    # Query JTS database
    print("🔍 Querying JTS database...")
    jts_response = query_jts_rest_api(query)
    
    if jts_response:
        print(f"✅ JTS Response: {jts_response}")
        
        # Get AI enhanced response
        print("🧠 Getting AI enhanced response...")
        response = get_ai_enhanced_response(
            query, 
            weight, 
            drug, 
            jts_response, 
            conversation_history=[]
        )
    else:
        print("⚠️  JTS query failed, using fallback...")
        response = get_fallback_response(query, weight, drug, None)
    
    print(f"\n🤖 Final Response: {response}")
    
    # Speak the response
    print("🔊 Speaking response...")
    speak_response(response)
    
    return response

if __name__ == "__main__":
    # Test a specific query
    query = "morphine pain management for 75 kg patient"
    test_query(query) 