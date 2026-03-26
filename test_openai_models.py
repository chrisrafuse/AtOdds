#!/usr/bin/env python3
"""
List available OpenAI models for your API key.
Run with: python test_openai_models.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def main():
    print("🔍 Checking OpenAI Models Available")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env")
        return
    
    print(f"✅ API Key: {api_key[:10]}...{api_key[-10:]}")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        # List models
        print("\n📋 Fetching model list...")
        models = client.models.list()
        
        # Filter for chat models
        chat_models = [model for model in models.data if "gpt" in model.id.lower()]
        
        print(f"\n🤖 Found {len(chat_models)} GPT models:")
        print("-" * 50)
        
        # Sort by relevance (common models first)
        priority_models = [
            "gpt-4o",
            "gpt-4o-mini", 
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ]
        
        # Show priority models first
        shown = set()
        for model_name in priority_models:
            for model in chat_models:
                if model_name in model.id and model.id not in shown:
                    print(f"  ✅ {model.id}")
                    shown.add(model.id)
                    break
        
        # Show other models
        for model in chat_models:
            if model.id not in shown:
                print(f"  • {model.id}")
                shown.add(model.id)
        
        # Show current model in .env
        current_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        print(f"\n🎯 Current model in .env: {current_model}")
        
        # Check if current model is available
        model_available = any(current_model in model.id for model in chat_models)
        if model_available:
            print(f"  ✅ {current_model} is available")
        else:
            print(f"  ❌ {current_model} NOT found in available models")
            
            # Suggest alternatives
            print("\n💡 Suggested alternatives:")
            for model_name in priority_models:
                if any(model_name in model.id for model in chat_models):
                    print(f"  - Set OPENAI_MODEL={model_name}")
                    break
        
        # Test current model
        print(f"\n🧪 Testing {current_model}...")
        try:
            response = client.chat.completions.create(
                model=current_model,
                messages=[{"role": "user", "content": "Say 'Hello' in 1 word."}],
                max_tokens=5,
                timeout=10
            )
            print(f"  ✅ Response: {response.choices[0].message.content}")
            print(f"  📊 Usage: {response.usage}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            
    except ImportError:
        print("❌ OpenAI package not installed. Run: pip install openai")
    except Exception as e:
        print(f"❌ Error: {e}")
        
        if "insufficient_quota" in str(e):
            print("💡 Fix: Add credits to your OpenAI account")
        elif "invalid_api_key" in str(e):
            print("💡 Fix: Check your API key in .env")
        elif "401" in str(e):
            print("💡 Fix: API key is invalid or expired")

if __name__ == "__main__":
    main()
