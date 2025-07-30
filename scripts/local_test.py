#!/usr/bin/env python3
"""
Local Testing Script - Fast development iteration on Mac
Tests core functionality without loading the full model
"""

import os
import sys
import json
import time
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_config_loading():
    """Test if config can be loaded"""
    print("🧪 Testing config loading...")
    try:
        import config
        print("✅ Config loaded successfully")
        print(f"   PDFS_DIR: {config.PDFS_DIR}")
        print(f"   EMBEDS_DIR: {config.EMBEDS_DIR}")
        return True
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

def test_embeddings():
    """Test if embeddings exist and can be loaded"""
    print("\n🧪 Testing embeddings...")
    try:
        import faiss
        from sentence_transformers import SentenceTransformer
        
        # Check if files exist
        embeds_dir = Path("../embeds")
        if not embeds_dir.exists():
            print("❌ Embeddings directory not found")
            return False
            
        index_path = embeds_dir / "faiss.idx"
        meta_path = embeds_dir / "meta.json"
        
        if not index_path.exists():
            print("❌ FAISS index not found")
            return False
            
        if not meta_path.exists():
            print("❌ Metadata not found")
            return False
            
        # Load metadata
        with open(meta_path, 'r') as f:
            metadata = json.load(f)
            
        print(f"✅ Embeddings found:")
        print(f"   Index: {index_path}")
        print(f"   Chunks: {metadata.get('num_chunks', 'unknown')}")
        print(f"   Embedding dim: {metadata.get('embedding_dim', 'unknown')}")
        
        return True
    except Exception as e:
        print(f"❌ Embeddings test failed: {e}")
        return False

def test_prompt_engineering():
    """Test prompt engineering without LLM"""
    print("\n🧪 Testing prompt engineering...")
    
    # Sample medical question
    question = "What is the dose for ketamine in trauma?"
    
    # Medical prompt template
    prompt_template = """You are a clinical decision support assistant. Answer the following medical question based on Joint Trauma System (JTS) Clinical Practice Guidelines.

Question: {question}

Instructions:
- Provide concise, evidence-based answers
- Include specific dosages when applicable
- Reference JTS guidelines when possible
- Keep answers under 100 words
- Use medical terminology appropriately

Answer:"""
    
    formatted_prompt = prompt_template.format(question=question)
    
    print(f"✅ Prompt template works:")
    print(f"   Question: {question}")
    print(f"   Prompt length: {len(formatted_prompt)} characters")
    
    return True

def test_vector_search_simulation():
    """Simulate vector search without loading model"""
    print("\n🧪 Testing vector search simulation...")
    
    # Simulate finding relevant chunks
    sample_chunks = [
        "Ketamine dosing: 1-2 mg/kg IV for procedural sedation",
        "Trauma resuscitation: ABCDE approach",
        "Hemorrhage control: direct pressure and tourniquets"
    ]
    
    question = "What is the dose for ketamine in trauma?"
    
    # Simple keyword matching simulation
    relevant_chunks = []
    for chunk in sample_chunks:
        if any(word in chunk.lower() for word in question.lower().split()):
            relevant_chunks.append(chunk)
    
    print(f"✅ Vector search simulation:")
    print(f"   Question: {question}")
    print(f"   Found {len(relevant_chunks)} relevant chunks")
    for i, chunk in enumerate(relevant_chunks, 1):
        print(f"   {i}. {chunk}")
    
    return True

def test_audio_components():
    """Test audio component availability"""
    print("\n🧪 Testing audio components...")
    
    audio_modules = [
        ('pyaudio', 'Audio capture'),
        ('speech_recognition', 'Speech recognition'),
        ('google.cloud.texttospeech', 'Google TTS'),
        ('pyttsx3', 'Offline TTS')
    ]
    
    available = []
    missing = []
    
    for module, description in audio_modules:
        try:
            __import__(module)
            available.append(f"✅ {description} ({module})")
        except ImportError:
            missing.append(f"❌ {description} ({module})")
    
    print("Audio component status:")
    for status in available + missing:
        print(f"   {status}")
    
    return len(missing) == 0

def main():
    print("🚀 TRAUMA ASSISTANT - LOCAL TESTING")
    print("=" * 50)
    print("Testing core functionality without full model loading")
    print()
    
    tests = [
        ("Config Loading", test_config_loading),
        ("Embeddings", test_embeddings),
        ("Prompt Engineering", test_prompt_engineering),
        ("Vector Search Simulation", test_vector_search_simulation),
        ("Audio Components", test_audio_components)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for deployment.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
    
    print("\n💡 Next steps:")
    print("   1. Fix any failed tests")
    print("   2. Run: ./scripts/quick_deploy.sh")
    print("   3. Test on VM with full model")

if __name__ == "__main__":
    main() 