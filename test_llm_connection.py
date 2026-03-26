#!/usr/bin/env python3
"""
Test LLM connection and API key validity.
Run with: python test_llm_connection.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_env_vars():
    """Test environment variables are loaded"""
    print("🔍 Testing environment variables...")

    provider = os.getenv("LLM_PROVIDER", "mock")
    print(f"   LLM_PROVIDER: {provider}")

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        print(f"   OPENAI_API_KEY: {'✅ Set' if api_key else '❌ Missing'}")
        print(f"   OPENAI_MODEL: {model}")

        if not api_key:
            print("   ❌ OPENAI_API_KEY is missing!")
            return False

        if api_key.startswith("sk-"):
            print("   ✅ API key format looks correct")
        else:
            print("   ⚠️  API key format might be incorrect (should start with sk-)")

    return True

def test_llm_import():
    """Test LLM modules can be imported"""
    print("\n📦 Testing imports...")

    try:
        from packages.llm.factory import get_CR_llm_provider, get_CR_provider_name
        print("   ✅ LLM factory imported")

        provider_name = get_CR_provider_name()
        print(f"   Active provider: {provider_name}")

        provider = get_CR_llm_provider()
        print(f"   Provider instance: {type(provider).__name__}")

        return provider
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return None

def test_openai_connection(provider):
    """Test actual OpenAI API call via chat_with_tools"""
    print("\n🌐 Testing OpenAI connection...")

    if not provider or "openai" not in str(type(provider)).lower():
        print("   ⚠️  Not using OpenAI provider")
        return

    try:
        from packages.llm.tool_schemas import CR_TOOL_SCHEMAS
        from packages.tools.registry import CR_TOOL_REGISTRY

        # Test with a simple message and tools
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello from OpenAI!' and do not use any tools."}
        ]

        print("   Making test API call...")
        # Create a dummy tool executor
        def dummy_tool_executor(tool_call):
            return {"result": "dummy"}

        response = provider.chat_with_tools(
            messages,
            CR_TOOL_SCHEMAS,
            dummy_tool_executor
        )

        if response and hasattr(response, 'CR_content'):
            print(f"   ✅ Response: {response.CR_content}")
            print(f"   📊 Tokens used: {response.CR_usage}")
            return True
        else:
            print(f"   ⚠️  Unexpected response format: {response}")
            return False

    except Exception as e:
        print(f"   ❌ API call failed: {e}")

        # Common error explanations
        if "invalid_api_key" in str(e):
            print("   💡 Fix: Check your OPENAI_API_KEY in .env")
        elif "insufficient_quota" in str(e):
            print("   💡 Fix: Add credits to your OpenAI account")
        elif "400" in str(e):
            print("   💡 Fix: Check API key format and model selection")
        elif "connection" in str(e).lower():
            print("   💡 Fix: Check internet connection")
        elif "authentication" in str(e).lower():
            print("   💡 Fix: Verify API key is valid and active")

        return False

def main():
    print("🚀 AtOdds LLM Connection Test")
    print("=" * 50)

    # Test environment
    if not test_env_vars():
        return

    # Test imports
    provider = test_llm_import()

    # Test OpenAI specifically
    if provider and "openai" in str(type(provider)).lower():
        test_openai_connection(provider)
    else:
        print("\n⚠️  OpenAI not configured - using mock or other provider")
        print("   To use OpenAI, set LLM_PROVIDER=openai in .env")

if __name__ == "__main__":
    main()
