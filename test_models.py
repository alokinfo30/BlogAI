#!/usr/bin/env python
"""
Test script for validating all configured models
Run: python test_models.py
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_all_models():
    """Test all configured models"""
    print("=" * 70)
    print("🤖 MULTI-MODEL SYSTEM TEST")
    print("=" * 70)
    
    # Check environment variables
    print("\n📋 Environment Configuration:")
    print("-" * 70)
    print(f"OpenAI API Key: {'✓ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
    print(f"Primary Model: {os.getenv('OPENAI_MODEL_NAME', 'Not set')}")
    print(f"Fallback Models:")
    for i in range(1, 4):
        model = os.getenv(f'OPENAI_MODEL_FALLBACK_{i}')
        if model:
            print(f"  - Fallback {i}: {model}")
    
    print(f"\nAgent Models:")
    for agent in ['PLANNER', 'WRITER', 'EDITOR']:
        model = os.getenv(f'{agent}_MODEL')
        if model:
            print(f"  - {agent}: {model}")
        else:
            print(f"  - {agent}: Using primary model")
    
    print(f"\nStrategy: {os.getenv('MODEL_FALLBACK_STRATEGY', 'sequential')}")
    print("-" * 70)
    
    try:
        from app.model_manager import model_manager
        print("\n🔄 Testing all models...")
        print("-" * 70)
        
        results = model_manager.test_models()
        
        print("\n📊 Model Status:")
        print("-" * 70)
        available_count = 0
        for model, available in results.items():
            status = "✅ AVAILABLE" if available else "❌ UNAVAILABLE"
            print(f"{model:35} : {status}")
            if available:
                available_count += 1
        
        total_count = len(results)
        print("-" * 70)
        print(f"\n📈 SUMMARY: {available_count}/{total_count} models available")
        
        if available_count > 0:
            print("\n🎯 Available Models (will be used in this order):")
            for model, available in results.items():
                if available:
                    print(f"   → {model}")
            
            print("\n💡 Model Fallback Strategy:")
            strategy = os.getenv('MODEL_FALLBACK_STRATEGY', 'sequential')
            if strategy == 'sequential':
                print("   → If a model fails, try the next one in sequence")
            elif strategy == 'random':
                print("   → Randomly select an available model")
            elif strategy == 'round_robin':
                print("   → Cycle through available models")
            
            print("\n🎨 Per-Agent Model Assignment:")
            print(f"   → Planner: {model_manager.get_agent_model('planner')}")
            print(f"   → Writer: {model_manager.get_agent_model('writer')}")
            print(f"   → Editor: {model_manager.get_agent_model('editor')}")
            
        else:
            print("\n⚠️  No models available! Please check:")
            print("   1. Your OpenAI API key in .env file")
            print("   2. Model names are correct")
            print("   3. Your internet connection")
            print("   4. Your OpenAI account has access to these models")
        
        print("\n" + "=" * 70)
        return available_count > 0
        
    except ImportError as e:
        print(f"\n❌ Import Error: {str(e)}")
        print("Make sure you're in the right directory and all dependencies are installed.")
        return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_model_api():
    """Test if the API endpoints are working"""
    print("\n" + "=" * 70)
    print("🌐 API ENDPOINT TEST")
    print("=" * 70)
    
    try:
        import requests
        base_url = "http://192.168.1.39:5000"
        
        print("\n📡 Testing /api/health...")
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check successful!")
            print(f"   Status: {data.get('status')}")
            print(f"   API Key: {'✓ Valid' if data.get('api_key_valid') else '❌ Invalid'}")
            print(f"   Secret Key: {'✓ Valid' if data.get('secret_key_valid') else '❌ Too short'}")
            
            if 'models' in data:
                print(f"   Models Available: {len(data['models'].get('available', {}))}/{len(data['models'].get('available', {})) + len(data['models'].get('unavailable', {}))}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")
        print("Make sure the Flask server is running (python -m app.main)")

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🔍 MULTI-MODEL SYSTEM VALIDATION")
    print("=" * 70)
    
    # Test models
    success = test_all_models()
    
    # Test API if server is running
    test_model_api()
    
    print("\n✅ Test complete!")
    print("=" * 70)