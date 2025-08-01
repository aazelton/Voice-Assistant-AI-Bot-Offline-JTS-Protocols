#!/usr/bin/env python3
"""
Test VM Voice Assistant with simulated voice input
"""

import sys
import time
import requests
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

def test_vm_voice_assistant():
    """Test the VM voice assistant with simulated queries"""
    print("🧪 TESTING VM VOICE ASSISTANT")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "ketamine RSI for 80 kg patient",
        "rocuronium dose for 70 kg patient",
        "TXA protocol for trauma",
        "epinephrine cardiac arrest dose",
        "fentanyl pain management"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 40)
        
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
        
        print(f"🤖 Response: {response}")
        
        # Simulate speaking (just print for now)
        print(f"🔊 Would speak: {response}")
        
        time.sleep(1)  # Brief pause between tests
    
    print(f"\n✅ All {len(test_queries)} tests completed!")

def test_specific_query():
    """Test a specific query with full processing"""
    query = input("Enter a test query (or press Enter for default): ").strip()
    if not query:
        query = "ketamine RSI for 80 kg patient"
    
    print(f"\n🧪 Testing: {query}")
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
    
    # Ask if user wants to hear it spoken
    speak = input("\n🔊 Speak the response? (y/n): ").strip().lower()
    if speak == 'y':
        speak_response(response)

def main():
    """Main test function"""
    print("🎤 VM VOICE ASSISTANT TESTER")
    print("=" * 50)
    print("1. Run all test queries")
    print("2. Test specific query")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        test_vm_voice_assistant()
    elif choice == "2":
        test_specific_query()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 