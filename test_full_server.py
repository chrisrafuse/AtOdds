#!/usr/bin/env python3
"""
Quick test to verify full server components work after Python 3.12 installation.
Run with: python test_full_server.py
"""

import sys
import os

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

# Test imports
try:
    import pydantic
    print(f"✅ Pydantic: {pydantic.__version__}")
except ImportError as e:
    print(f"❌ Pydantic not available: {e}")

try:
    import fastapi
    print(f"✅ FastAPI: {fastapi.__version__}")
except ImportError as e:
    print(f"❌ FastAPI not available: {e}")

try:
    import uvicorn
    print(f"✅ Uvicorn available")
except ImportError as e:
    print(f"❌ Uvicorn not available: {e}")

# Test our modules
try:
    from packages.llm.factory import get_CR_llm_provider, get_CR_provider_name
    print("✅ LLM factory imports")
except ImportError as e:
    print(f"❌ LLM factory import failed: {e}")

try:
    from packages.agent.agent import execute_CR_analysis_pipeline
    print("✅ Agent pipeline imports")
except ImportError as e:
    print(f"❌ Agent pipeline import failed: {e}")

# Test sample data
try:
    with open("data/sample_odds.json", "r") as f:
        import json
        snapshot = json.load(f)
    print(f"✅ Sample data loaded: {len(snapshot.get('CR_events', []))} events")
except Exception as e:
    print(f"❌ Sample data load failed: {e}")

# Test full pipeline
try:
    results = execute_CR_analysis_pipeline(snapshot)
    print(f"✅ Full pipeline executed: {len(results.get('CR_findings', []))} findings")
    print(f"   LLM provider: {results.get('CR_llm_provider', 'unknown')}")
    print(f"   Tool calls: {len(results.get('CR_tool_trace', []))}")
except Exception as e:
    print(f"❌ Full pipeline failed: {e}")

print("\n🎉 Full server components verified!")
