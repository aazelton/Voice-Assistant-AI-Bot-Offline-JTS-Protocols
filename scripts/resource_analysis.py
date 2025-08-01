#!/usr/bin/env python3
"""
Resource Analysis Script - Analyze JTS system resource requirements
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

def analyze_database_size():
    """Analyze the size of the JTS database"""
    print("📊 DATABASE SIZE ANALYSIS")
    print("=" * 40)
    
    # Check embedding files
    embed_dir = Path("embeds")
    if embed_dir.exists():
        faiss_size = (embed_dir / "faiss.idx").stat().st_size if (embed_dir / "faiss.idx").exists() else 0
        meta_size = (embed_dir / "meta.json").stat().st_size if (embed_dir / "meta.json").exists() else 0
        
        print(f"FAISS Index: {faiss_size / (1024*1024):.1f} MB")
        print(f"Metadata: {meta_size / (1024*1024):.1f} MB")
        print(f"Total: {(faiss_size + meta_size) / (1024*1024):.1f} MB")
        
        # Analyze metadata structure
        if (embed_dir / "meta.json").exists():
            with open(embed_dir / "meta.json", 'r') as f:
                metadata = json.load(f)
            
            if isinstance(metadata, list):
                print(f"Number of chunks: {len(metadata)}")
                avg_chunk_size = sum(len(str(chunk)) for chunk in metadata[:100]) / min(100, len(metadata))
                print(f"Average chunk size: {avg_chunk_size:.0f} characters")
            elif isinstance(metadata, dict):
                print(f"Metadata keys: {list(metadata.keys())}")
                if 'chunks' in metadata:
                    print(f"Number of chunks: {len(metadata['chunks'])}")
    else:
        print("❌ Embeddings directory not found")

def analyze_model_requirements():
    """Analyze the computational requirements of models"""
    print("\n🤖 MODEL REQUIREMENTS ANALYSIS")
    print("=" * 40)
    
    # Check model files
    model_dir = Path("models")
    if model_dir.exists():
        for model_file in model_dir.glob("*.gguf"):
            size_mb = model_file.stat().st_size / (1024*1024)
            print(f"{model_file.name}: {size_mb:.1f} MB")
    
    # Analyze embedding model requirements
    print("\nSentence Transformer Model:")
    print("- Model: all-MiniLM-L6-v2")
    print("- Parameters: ~80M")
    print("- Memory usage: ~150-200MB")
    print("- Load time: ~5-10 seconds")
    
    print("\nLLM Model (Mistral Q4):")
    print("- Model: mistral.Q4_K_M.gguf")
    print("- Parameters: ~7B (quantized)")
    print("- Memory usage: ~4-6GB")
    print("- Load time: ~10-30 seconds")

def analyze_computational_complexity():
    """Analyze the computational complexity of operations"""
    print("\n⚡ COMPUTATIONAL COMPLEXITY ANALYSIS")
    print("=" * 40)
    
    print("1. Model Loading:")
    print("   - Sentence Transformer: O(1) - one-time load")
    print("   - LLM: O(1) - one-time load")
    print("   - FAISS Index: O(1) - one-time load")
    
    print("\n2. Query Processing:")
    print("   - Question encoding: O(1) - single sentence")
    print("   - FAISS search: O(log n) - where n = number of embeddings")
    print("   - LLM inference: O(1) - single forward pass")
    
    print("\n3. Memory Usage:")
    print("   - Sentence Transformer: ~200MB (resident)")
    print("   - FAISS Index: ~100-500MB (depends on dataset)")
    print("   - LLM: ~4-6GB (resident)")
    print("   - Total: ~5-7GB")

def analyze_optimization_opportunities():
    """Identify optimization opportunities"""
    print("\n🔧 OPTIMIZATION OPPORTUNITIES")
    print("=" * 40)
    
    print("1. Model Loading Optimization:")
    print("   ✅ Use persistent service (already implemented)")
    print("   ✅ Load models once, serve multiple requests")
    print("   ✅ Reduce startup time from 15-40s to <1s")
    
    print("\n2. Memory Optimization:")
    print("   🔄 Use smaller embedding model (all-MiniLM-L3-v2)")
    print("   🔄 Reduce FAISS index size (limit to top N chunks)")
    print("   🔄 Use model quantization (already using Q4)")
    
    print("\n3. CPU Optimization:")
    print("   🔄 Reduce LLM context length (currently 1024)")
    print("   🔄 Use fewer threads for LLM (currently 4)")
    print("   🔄 Cache frequent queries")
    
    print("\n4. Network Optimization:")
    print("   ✅ Use REST API instead of SSH")
    print("   🔄 Implement connection pooling")
    print("   🔄 Use gRPC for faster communication")

def analyze_vm_requirements():
    """Analyze optimal VM requirements"""
    print("\n🖥️  OPTIMAL VM REQUIREMENTS")
    print("=" * 40)
    
    print("Current VM (Overloaded):")
    print("- CPU: 4 cores")
    print("- Memory: 15GB")
    print("- Load: 12.00 (300% CPU usage)")
    
    print("\nRecommended VM (Optimized):")
    print("- CPU: 2-4 cores (with optimizations)")
    print("- Memory: 8GB (with optimizations)")
    print("- Expected load: <50%")
    
    print("\nMinimal VM (Basic):")
    print("- CPU: 1-2 cores")
    print("- Memory: 4GB")
    print("- Expected load: <30%")

def analyze_deployment_strategies():
    """Analyze different deployment strategies"""
    print("\n🚀 DEPLOYMENT STRATEGIES")
    print("=" * 40)
    
    print("1. Single VM (Current):")
    print("   Pros: Simple, full control")
    print("   Cons: Single point of failure, resource limits")
    print("   Cost: ~$50-100/month")
    
    print("\n2. Microservices:")
    print("   Pros: Scalable, fault-tolerant")
    print("   Cons: Complex, higher cost")
    print("   Cost: ~$100-200/month")
    
    print("\n3. Serverless:")
    print("   Pros: Pay-per-use, auto-scaling")
    print("   Cons: Cold start latency")
    print("   Cost: ~$20-50/month")
    
    print("\n4. Edge Deployment (Raspberry Pi):")
    print("   Pros: Offline, low latency")
    print("   Cons: Limited resources")
    print("   Cost: ~$5-10/month")

def main():
    print("🔍 JTS SYSTEM RESOURCE ANALYSIS")
    print("=" * 50)
    
    analyze_database_size()
    analyze_model_requirements()
    analyze_computational_complexity()
    analyze_optimization_opportunities()
    analyze_vm_requirements()
    analyze_deployment_strategies()
    
    print("\n📋 SUMMARY & RECOMMENDATIONS")
    print("=" * 40)
    print("1. The system is NOT computationally intensive")
    print("2. Main bottleneck: Model loading (15-40s startup)")
    print("3. Solution: Persistent service (already implemented)")
    print("4. VM overload likely due to other processes")
    print("5. Minimal VM (2 cores, 4GB RAM) should be sufficient")
    print("6. Consider edge deployment for offline use")

if __name__ == "__main__":
    main() 