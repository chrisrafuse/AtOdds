#!/usr/bin/env python3
"""
Test Suite for Phase 8: LLM Agent Integration
Tests for LLM adapters, mock provider, tool executor, and agent pipeline.
All tests run without real API keys using the mock provider.
"""

import unittest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from packages.llm.base import CR_LLMProvider, CR_ToolCall, CR_LLMResponse
from packages.llm.mock_provider import CR_MockProvider
from packages.llm.factory import get_CR_llm_provider, get_CR_provider_name
from packages.llm.tool_schemas import CR_TOOL_SCHEMAS
from packages.tools.registry import CR_TOOL_REGISTRY


# ---------------------------------------------------------------------------
# Minimal snapshot fixture
# ---------------------------------------------------------------------------
def _make_snapshot():
    return {
        "CR_events": [
            {
                "CR_event_id": "test_evt_001",
                "CR_markets": [
                    {
                        "CR_bookmaker": "DraftKings",
                        "CR_name": "moneyline",
                        "CR_last_update": "2020-01-01T00:00:00Z",
                        "CR_outcomes": [
                            {"CR_name": "Home", "CR_price": -110},
                            {"CR_name": "Away", "CR_price": -110},
                        ]
                    },
                    {
                        "CR_bookmaker": "FanDuel",
                        "CR_name": "moneyline",
                        "CR_last_update": "2020-01-01T00:00:00Z",
                        "CR_outcomes": [
                            {"CR_name": "Home", "CR_price": 120},
                            {"CR_name": "Away", "CR_price": -140},
                        ]
                    },
                ]
            }
        ]
    }


# ---------------------------------------------------------------------------
# Tool schema tests
# ---------------------------------------------------------------------------
class TestCRToolSchemas(unittest.TestCase):

    def test_schemas_is_list(self):
        self.assertIsInstance(CR_TOOL_SCHEMAS, list)

    def test_schemas_not_empty(self):
        self.assertGreater(len(CR_TOOL_SCHEMAS), 0)

    def test_each_schema_has_required_fields(self):
        required = {"name", "description", "parameters"}
        for schema in CR_TOOL_SCHEMAS:
            for field in required:
                self.assertIn(field, schema, f"Schema missing '{field}': {schema.get('name')}")

    def test_schema_names_have_cr_prefix(self):
        for schema in CR_TOOL_SCHEMAS:
            self.assertTrue(
                schema["name"].startswith("CR_"),
                f"Schema name missing CR_ prefix: {schema['name']}"
            )

    def test_analysis_tools_present(self):
        names = {s["name"] for s in CR_TOOL_SCHEMAS}
        for expected in ["CR_detect_arbitrage", "CR_detect_value_edges",
                         "CR_detect_stale_lines", "CR_detect_outliers"]:
            self.assertIn(expected, names)


# ---------------------------------------------------------------------------
# Base dataclass tests
# ---------------------------------------------------------------------------
class TestCRToolCall(unittest.TestCase):

    def test_tool_call_creation(self):
        tc = CR_ToolCall(
            CR_tool_name="CR_detect_arbitrage",
            CR_arguments={"CR_snapshot": {}},
            CR_result={"CR_success": True, "CR_count": 0},
            CR_error=None
        )
        self.assertEqual(tc.CR_tool_name, "CR_detect_arbitrage")
        self.assertIsNone(tc.CR_error)

    def test_tool_call_with_error(self):
        tc = CR_ToolCall(
            CR_tool_name="CR_detect_arbitrage",
            CR_arguments={},
            CR_result=None,
            CR_error="Snapshot missing"
        )
        self.assertIsNotNone(tc.CR_error)
        self.assertIsNone(tc.CR_result)

    def test_llm_response_creation(self):
        resp = CR_LLMResponse(
            CR_content="Analysis complete",
            CR_tool_calls=[],
            CR_finish_reason="stop",
            CR_usage={"prompt_tokens": 10, "completion_tokens": 20},
            CR_provider="mock",
            CR_model="mock-deterministic"
        )
        self.assertEqual(resp.CR_provider, "mock")
        self.assertEqual(resp.CR_finish_reason, "stop")


# ---------------------------------------------------------------------------
# Mock provider tests
# ---------------------------------------------------------------------------
class TestCRMockProvider(unittest.TestCase):

    def setUp(self):
        self.provider = CR_MockProvider()
        self.snapshot = _make_snapshot()

    def test_provider_name(self):
        self.assertEqual(self.provider.get_provider_name(), "mock")

    def test_model_name(self):
        self.assertEqual(self.provider.get_model_name(), "mock-deterministic")

    def test_extract_snapshot_from_text_message(self):
        """Mock provider must parse snapshot embedded in build_CR_analysis_user_message format."""
        snapshot = self.snapshot
        msg_content = f"Analyze this odds snapshot.\n\nSnapshot data:\n{json.dumps(snapshot)}"
        messages = [{"role": "user", "content": msg_content}]
        result = self.provider._extract_snapshot(messages)
        self.assertIsNotNone(result)
        self.assertIn("CR_events", result)

    def test_extract_snapshot_from_pure_json(self):
        """Mock provider must parse snapshot from pure JSON message."""
        snapshot = self.snapshot
        messages = [{"role": "user", "content": json.dumps(snapshot)}]
        result = self.provider._extract_snapshot(messages)
        self.assertIsNotNone(result)
        self.assertIn("CR_events", result)

    def test_extract_snapshot_returns_none_when_missing(self):
        messages = [{"role": "user", "content": "Hello, what is arbitrage?"}]
        result = self.provider._extract_snapshot(messages)
        self.assertIsNone(result)

    def test_chat_with_tools_returns_llm_response(self):
        snapshot = self.snapshot
        msg_content = f"Analyze.\n\nSnapshot data:\n{json.dumps(snapshot)}"
        messages = [{"role": "user", "content": msg_content}]

        def _executor(tool_name, args):
            func = CR_TOOL_REGISTRY.get(tool_name)
            if func:
                return func(args.get("CR_snapshot", snapshot))
            return {"CR_success": False, "CR_error": f"Unknown tool: {tool_name}"}

        response = self.provider.chat_with_tools(messages, CR_TOOL_SCHEMAS, _executor)

        self.assertIsInstance(response, CR_LLMResponse)
        self.assertEqual(response.CR_provider, "mock")
        self.assertIsNotNone(response.CR_content)

    def test_chat_with_tools_calls_all_analysis_tools(self):
        snapshot = self.snapshot
        msg_content = f"Analyze.\n\nSnapshot data:\n{json.dumps(snapshot)}"
        messages = [{"role": "user", "content": msg_content}]
        called_tools = []

        def _tracking_executor(tool_name, args):
            called_tools.append(tool_name)
            func = CR_TOOL_REGISTRY.get(tool_name)
            if func:
                return func(args.get("CR_snapshot", snapshot))
            return {"CR_success": False}

        self.provider.chat_with_tools(messages, CR_TOOL_SCHEMAS, _tracking_executor)

        # Verify the four core analysis tools were all called
        for expected in ["CR_detect_stale_lines", "CR_detect_arbitrage",
                         "CR_detect_outliers", "CR_detect_value_edges"]:
            self.assertIn(expected, called_tools, f"Mock provider did not call {expected}")

    def test_build_summary_returns_string(self):
        summary = self.provider._build_summary({"CR_detect_arbitrage": 2})
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 0)


# ---------------------------------------------------------------------------
# Factory tests
# ---------------------------------------------------------------------------
class TestCRFactory(unittest.TestCase):

    def test_get_provider_defaults_to_mock(self):
        os.environ.pop("LLM_PROVIDER", None)
        provider = get_CR_llm_provider()
        self.assertEqual(provider.get_provider_name(), "mock")

    def test_get_provider_explicit_mock(self):
        provider = get_CR_llm_provider("mock")
        self.assertEqual(provider.get_provider_name(), "mock")

    def test_get_provider_falls_back_to_mock_without_key(self):
        os.environ.pop("OPENAI_API_KEY", None)
        provider = get_CR_llm_provider("openai")
        self.assertEqual(provider.get_provider_name(), "mock")

    def test_get_provider_name_no_key_returns_mock(self):
        os.environ["LLM_PROVIDER"] = "openai"
        os.environ.pop("OPENAI_API_KEY", None)
        name = get_CR_provider_name()
        self.assertEqual(name, "mock")

    def test_get_provider_name_mock_explicit(self):
        os.environ["LLM_PROVIDER"] = "mock"
        name = get_CR_provider_name()
        self.assertEqual(name, "mock")


# ---------------------------------------------------------------------------
# Tool executor integration tests
# ---------------------------------------------------------------------------
class TestCRToolExecutor(unittest.TestCase):

    def setUp(self):
        self.snapshot = _make_snapshot()

    def _execute(self, tool_name, args):
        func = CR_TOOL_REGISTRY.get(tool_name)
        if not func:
            return {"CR_success": False, "CR_error": f"Unknown: {tool_name}"}
        return func(args.get("CR_snapshot", self.snapshot))

    def test_detect_arbitrage_tool_runs(self):
        result = self._execute("CR_detect_arbitrage", {"CR_snapshot": self.snapshot})
        self.assertIsInstance(result, dict)
        self.assertIn("CR_success", result)

    def test_detect_stale_lines_tool_runs(self):
        result = self._execute("CR_detect_stale_lines", {"CR_snapshot": self.snapshot})
        self.assertIsInstance(result, dict)

    def test_detect_outliers_tool_runs(self):
        result = self._execute("CR_detect_outliers", {"CR_snapshot": self.snapshot})
        self.assertIsInstance(result, dict)

    def test_detect_value_edges_tool_runs(self):
        result = self._execute("CR_detect_value_edges", {"CR_snapshot": self.snapshot})
        self.assertIsInstance(result, dict)

    def test_unknown_tool_returns_failure(self):
        result = self._execute("CR_nonexistent_tool", {})
        self.assertFalse(result.get("CR_success", True))


# ---------------------------------------------------------------------------
# Full agent pipeline (mock) tests
# ---------------------------------------------------------------------------
class TestCRAgentPipelineMock(unittest.TestCase):

    def setUp(self):
        self.snapshot = _make_snapshot()

    def test_pipeline_returns_required_keys(self):
        from packages.agent.agent import execute_CR_analysis_pipeline
        result = execute_CR_analysis_pipeline(self.snapshot)
        required = [
            "CR_findings", "CR_findings_summary", "CR_sportsbook_rankings",
            "CR_tool_trace", "CR_llm_summary", "CR_llm_provider", "CR_pipeline_timestamp"
        ]
        for key in required:
            self.assertIn(key, result, f"Pipeline result missing key: {key}")

    def test_pipeline_findings_is_list(self):
        from packages.agent.agent import execute_CR_analysis_pipeline
        result = execute_CR_analysis_pipeline(self.snapshot)
        self.assertIsInstance(result["CR_findings"], list)

    def test_pipeline_rankings_is_list(self):
        from packages.agent.agent import execute_CR_analysis_pipeline
        result = execute_CR_analysis_pipeline(self.snapshot)
        self.assertIsInstance(result["CR_sportsbook_rankings"], list)

    def test_pipeline_llm_provider_set(self):
        from packages.agent.agent import execute_CR_analysis_pipeline
        result = execute_CR_analysis_pipeline(self.snapshot)
        self.assertIsNotNone(result["CR_llm_provider"])
        self.assertIsInstance(result["CR_llm_provider"], str)

    def test_pipeline_summary_keys(self):
        from packages.agent.agent import execute_CR_analysis_pipeline
        result = execute_CR_analysis_pipeline(self.snapshot)
        summary = result["CR_findings_summary"]
        self.assertIn("CR_total_findings", summary)
        self.assertIn("CR_by_type", summary)


# ---------------------------------------------------------------------------
# Chat module tests
# ---------------------------------------------------------------------------
class TestCROddsChatDeterministic(unittest.TestCase):

    def setUp(self):
        from packages.chat.chat_cr import CR_OddsChat
        self.snapshot = _make_snapshot()
        self.chat = CR_OddsChat(CR_snapshot=self.snapshot, CR_findings=[])

    def test_answer_returns_dict(self):
        result = self.chat.answer_CR_question("What arbitrage opportunities are there?")
        self.assertIsInstance(result, dict)

    def test_answer_has_cr_answer_key(self):
        result = self.chat.answer_CR_question("Tell me about value edges")
        self.assertIn("CR_answer", result)

    def test_answer_has_confidence(self):
        result = self.chat.answer_CR_question("Are there stale lines?")
        self.assertIn("CR_confidence", result)

    def test_answer_general_question(self):
        result = self.chat.answer_CR_question("What is this analysis about?")
        self.assertIsInstance(result.get("CR_answer"), str)
        self.assertGreater(len(result["CR_answer"]), 0)

    def test_answer_does_not_raise(self):
        questions = [
            "Which sportsbooks should I avoid?",
            "Explain the outliers",
            "What is the best line for the game?",
            "Calculate the vig",
        ]
        for q in questions:
            result = self.chat.answer_CR_question(q)
            self.assertIn("CR_answer", result, f"No CR_answer for question: {q}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
