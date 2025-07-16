#!/usr/bin/env python3
"""
Test script for Voice Assistant AI Bot
Verifies all components are working correctly
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

def test_import(module_name, description):
    """Test if a module can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {description}: {module_name} - {e}")
        return False

def test_file_exists(file_path, description):
    """Test if a file exists."""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - File not found")
        return False

def test_command(command, description):
    """Test if a command can be executed."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ {description}: {command}")
            return True
        else:
            print(f"❌ {description}: {command} - Return code: {result.returncode}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⚠️  {description}: {command} - Timeout")
        return False
    except Exception as e:
        print(f"❌ {description}: {command} - {e}")
        return False

def test_audio_devices():
    """Test audio device detection."""
    try:
        # Test if audio devices are available
        result = subprocess.run(["aplay", "-l"], capture_output=True, text=True)
        if result.returncode == 0 and "card" in result.stdout:
            print("✅ Audio devices detected")
            return True
        else:
            print("❌ No audio devices found")
            return False
    except Exception as e:
        print(f"❌ Audio device test failed: {e}")
        return False

def test_python_environment():
    """Test Python environment and dependencies."""
    print("\n🐍 Testing Python Environment")
    print("=" * 40)
    
    tests = [
        ("numpy", "NumPy"),
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
        ("sentence_transformers", "Sentence Transformers"),
        ("faiss", "FAISS"),
        ("llama_cpp", "Llama CPP"),
        ("pyaudio", "PyAudio"),
        ("speech_recognition", "Speech Recognition"),
        ("sounddevice", "SoundDevice"),
        ("pdfplumber", "PDFPlumber"),
        ("psutil", "PSUtil"),
        ("configparser", "ConfigParser"),
        ("dotenv", "Python-dotenv"),
    ]
    
    passed = 0
    for module, description in tests:
        if test_import(module, description):
            passed += 1
    
    print(f"\n📊 Python Environment: {passed}/{len(tests)} tests passed")
    return passed == len(tests)

def test_system_dependencies():
    """Test system dependencies."""
    print("\n🔧 Testing System Dependencies")
    print("=" * 40)
    
    tests = [
        ("espeak-ng --version", "eSpeak-ng"),
        ("mpg123 --version", "MPG123"),
        ("python3 --version", "Python 3"),
        ("pip --version", "Pip"),
    ]
    
    passed = 0
    for command, description in tests:
        if test_command(command, description):
            passed += 1
    
    print(f"\n📊 System Dependencies: {passed}/{len(tests)} tests passed")
    return passed == len(tests)

def test_configuration():
    """Test configuration files and directories."""
    print("\n⚙️  Testing Configuration")
    print("=" * 40)
    
    tests = [
        ("config.py", "Configuration file"),
        ("requirements.txt", "Requirements file"),
        ("models/", "Models directory"),
        ("pdfs/", "PDFs directory"),
        ("embeds/", "Embeddings directory"),
        ("logs/", "Logs directory"),
        ("cache/", "Cache directory"),
    ]
    
    passed = 0
    for path, description in tests:
        if test_file_exists(path, description):
            passed += 1
    
    # Test environment file
    if Path(".env").exists():
        print("✅ Environment file: .env")
        passed += 1
    else:
        print("⚠️  Environment file: .env - Not found (run setup.py to create)")
    
    print(f"\n📊 Configuration: {passed}/{len(tests) + 1} tests passed")
    return passed == len(tests) + 1

def test_models():
    """Test model files."""
    print("\n🤖 Testing Models")
    print("=" * 40)
    
    # Check if model file exists
    model_path = "models/mistral.Q4_K_M.gguf"
    if test_file_exists(model_path, "Mistral model"):
        # Check file size (should be several GB)
        size_gb = Path(model_path).stat().st_size / (1024**3)
        if size_gb > 1:
            print(f"✅ Model size: {size_gb:.1f} GB")
            return True
        else:
            print(f"⚠️  Model size: {size_gb:.1f} GB (suspiciously small)")
            return False
    else:
        print("📝 Download a Mistral model to models/ directory")
        return False

def test_knowledge_base():
    """Test knowledge base files."""
    print("\n📚 Testing Knowledge Base")
    print("=" * 40)
    
    tests = [
        ("embeds/faiss.idx", "FAISS index"),
        ("embeds/meta.json", "Metadata file"),
        ("embeds/docs.txt", "Documents file"),
    ]
    
    passed = 0
    for path, description in tests:
        if test_file_exists(path, description):
            passed += 1
    
    if passed == 0:
        print("📝 Run 'python3 scripts/build_index.py' to build knowledge base")
    
    print(f"\n📊 Knowledge Base: {passed}/{len(tests)} tests passed")
    return passed == len(tests)

def test_audio_system():
    """Test audio system."""
    print("\n🎤 Testing Audio System")
    print("=" * 40)
    
    # Test audio devices
    audio_ok = test_audio_devices()
    
    # Test TTS
    try:
        result = subprocess.run([
            "espeak-ng", "-v", "en-us", "Test message"
        ], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Text-to-Speech: eSpeak-ng working")
            tts_ok = True
        else:
            print("❌ Text-to-Speech: eSpeak-ng failed")
            tts_ok = False
    except Exception as e:
        print(f"❌ Text-to-Speech test failed: {e}")
        tts_ok = False
    
    return audio_ok and tts_ok

def test_voice_assistant_import():
    """Test if voice assistant can be imported."""
    print("\n🎯 Testing Voice Assistant Import")
    print("=" * 40)
    
    try:
        from voice_assistant import VoiceAssistant
        print("✅ Voice Assistant module imported successfully")
        return True
    except Exception as e:
        print(f"❌ Voice Assistant import failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Voice Assistant Test Suite")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Python Environment", test_python_environment),
        ("System Dependencies", test_system_dependencies),
        ("Configuration", test_configuration),
        ("Models", test_models),
        ("Knowledge Base", test_knowledge_base),
        ("Audio System", test_audio_system),
        ("Voice Assistant Import", test_voice_assistant_import),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} test categories passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Voice Assistant is ready to use.")
        print("Run: python3 voice_assistant.py")
    else:
        print(f"\n⚠️  {total - passed} test categories failed.")
        print("Please fix the issues above before running the voice assistant.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 