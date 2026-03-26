"""
Mock LLM provider — deterministic, no API key needed.
Used for tests and when no provider is configured.
Calls all analysis tools and returns a canned summary.
"""

import json
from typing import List, Dict, Any

from packages.llm.base import CR_LLMProvider, CR_LLMResponse, CR_ToolCall

# Tools the mock always calls in order
_CR_DEFAULT_TOOL_SEQUENCE = [
    ("CR_detect_stale_lines",   {"CR_snapshot": None}),
    ("CR_detect_arbitrage",     {"CR_snapshot": None}),
    ("CR_detect_outliers",      {"CR_snapshot": None}),
    ("CR_detect_value_edges",   {"CR_snapshot": None}),
    ("CR_compute_best_lines",   {"CR_snapshot": None}),
    ("CR_compute_consensus",    {"CR_snapshot": None}),
]


class CR_MockProvider(CR_LLMProvider):
    """
    Deterministic mock that executes all analysis tools and returns
    a structured summary string. No LLM API required.
    """

    def get_provider_name(self) -> str:
        return "mock"

    def get_model_name(self) -> str:
        return "mock-deterministic"

    def chat_with_tools(
        self,
        CR_messages: List[Dict[str, Any]],
        CR_tools: List[Dict[str, Any]],
        CR_tool_executor: Any,
        CR_max_iterations: int = 10
    ) -> CR_LLMResponse:
        # Extract snapshot from the last user message if present
        CR_snapshot = self._extract_snapshot(CR_messages)

        CR_all_tool_calls: List[CR_ToolCall] = []
        CR_findings_summary: Dict[str, int] = {}

        for CR_tool_name, CR_base_args in _CR_DEFAULT_TOOL_SEQUENCE:
            CR_args = dict(CR_base_args)
            if CR_snapshot is not None:
                CR_args["CR_snapshot"] = CR_snapshot
            else:
                continue

            try:
                CR_result = CR_tool_executor(CR_tool_name, CR_args)
                CR_error = None
                if isinstance(CR_result, dict) and "CR_count" in CR_result:
                    CR_findings_summary[CR_tool_name] = CR_result["CR_count"]
            except Exception as CR_e:
                CR_result = None
                CR_error = str(CR_e)

            CR_all_tool_calls.append(CR_ToolCall(
                CR_tool_name=CR_tool_name,
                CR_arguments=CR_args,
                CR_result=CR_result,
                CR_error=CR_error
            ))

        CR_summary = self._build_summary(CR_findings_summary)

        return CR_LLMResponse(
            CR_content=CR_summary,
            CR_tool_calls=CR_all_tool_calls,
            CR_finish_reason="stop",
            CR_usage={"prompt_tokens": 0, "completion_tokens": 0},
            CR_provider=self.get_provider_name(),
            CR_model=self.get_model_name()
        )

    def _extract_snapshot(self, CR_messages: List[Dict]) -> Any:
        """
        Pull CR_snapshot out of the last user message.
        Handles two formats:
        1. Pure JSON dict with "CR_events" key
        2. Text message from build_CR_analysis_user_message with embedded JSON after "Snapshot data:\n"
        """
        for CR_msg in reversed(CR_messages):
            if CR_msg.get("role") != "user":
                continue
            CR_content = CR_msg.get("content", "")
            if not isinstance(CR_content, str) or "CR_events" not in CR_content:
                continue

            # Format 1: pure JSON
            try:
                CR_data = json.loads(CR_content)
                if "CR_snapshot" in CR_data:
                    return CR_data["CR_snapshot"]
                if "CR_events" in CR_data:
                    return CR_data
            except (json.JSONDecodeError, TypeError):
                pass

            # Format 2: text with embedded JSON after "Snapshot data:\n"
            CR_marker = "Snapshot data:\n"
            CR_pos = CR_content.find(CR_marker)
            if CR_pos != -1:
                try:
                    CR_json_str = CR_content[CR_pos + len(CR_marker):]
                    CR_data = json.loads(CR_json_str)
                    if "CR_events" in CR_data:
                        return CR_data
                    if "CR_snapshot" in CR_data:
                        return CR_data["CR_snapshot"]
                except (json.JSONDecodeError, TypeError):
                    pass

        return None

    def _build_summary(self, CR_findings_summary: Dict[str, int]) -> str:
        CR_lines = ["## Market Analysis Summary (Mock Provider)\n"]
        CR_map = {
            "CR_detect_stale_lines":  "Stale Lines",
            "CR_detect_arbitrage":    "Arbitrage Opportunities",
            "CR_detect_outliers":     "Outlier Prices",
            "CR_detect_value_edges":  "Value Edges",
        }
        for CR_key, CR_label in CR_map.items():
            CR_count = CR_findings_summary.get(CR_key, 0)
            CR_lines.append(f"- **{CR_label}**: {CR_count} finding(s)")

        CR_lines.append("\nAll calculations performed via deterministic tools. "
                        "Set LLM_PROVIDER=openai|anthropic|gemini with an API key "
                        "for AI-powered narrative explanations.")
        return "\n".join(CR_lines)
