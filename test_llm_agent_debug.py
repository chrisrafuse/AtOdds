#!/usr/bin/env python3
"""
Debug LLM agent with minimal data to identify hanging issue.
Run with: python test_llm_agent_debug.py
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_minimal_agent():
    """Test LLM agent with minimal data"""
    print("🔍 Testing LLM Agent with Minimal Data")
    print("=" * 50)
    
    try:
        from packages.agent.agent import execute_CR_analysis_pipeline
        from packages.data.loader import load_data
        
        # Create minimal test data
        minimal_snapshot = {
            "CR_events": [{
                "CR_event_id": "test_event",
                "CR_sport": "NBA",
                "CR_home_team": "Team A",
                "CR_away_team": "Team B",
                "CR_commence_time": "2026-03-27T00:00:00Z",
                "CR_bookmakers": [{
                    "CR_name": "TestBook",
                    "CR_markets": {
                        "moneyline": {
                            "CR_home_odds": -110,
                            "CR_away_odds": -110
                        }
                    },
                    "CR_last_updated": "2026-03-26T23:00:00Z"
                }]
            }],
            "CR_metadata": {
                "CR_source": "test",
                "CR_timestamp": "2026-03-26T23:00:00Z"
            }
        }
        
        print(f"📊 Testing with {len(minimal_snapshot['CR_events'])} event")
        
        # Time the execution
        start_time = time.time()
        print("🚀 Starting analysis...")
        
        results = execute_CR_analysis_pipeline(minimal_snapshot)
        
        elapsed = time.time() - start_time
        print(f"✅ Analysis completed in {elapsed:.2f} seconds")
        print(f"📈 Found {len(results.get('CR_findings', []))} findings")
        print(f"🤖 LLM Provider: {results.get('CR_llm_provider', 'unknown')}")
        print(f"📝 LLM Summary: {results.get('CR_llm_summary', 'N/A')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_llm():
    """Test direct LLM call without tools"""
    print("\n🔍 Testing Direct LLM Call")
    print("=" * 50)
    
    try:
        from packages.llm.factory import get_CR_llm_provider
        from packages.llm.tool_schemas import CR_TOOL_SCHEMAS
        
        provider = get_CR_llm_provider()
        print(f"🤖 Provider: {type(provider).__name__}")
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello' in exactly 1 word."}
        ]
        
        print("📤 Sending simple message...")
        start = time.time()
        
        # Create dummy tool executor
        def dummy_executor(tool_call):
            return {"result": "dummy"}
        
        response = provider.chat_with_tools(messages, CR_TOOL_SCHEMAS, dummy_executor)
        
        elapsed = time.time() - start
        print(f"✅ Response in {elapsed:.2f} seconds")
        print(f"📝 Content: {response.CR_content}")
        print(f"🔧 Tool calls: {len(response.CR_tool_calls)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🐛 LLM Agent Debug Tests")
    print("=" * 50)
    
    # Test 1: Direct LLM
    if not test_direct_llm():
        print("\n❌ Direct LLM test failed")
        return
    
    # Test 2: Minimal agent
    if not test_minimal_agent():
        print("\n❌ Minimal agent test failed")
        return
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    main()
