"""
Anthropic adapter — implements CR_LLMProvider using the anthropic SDK.
Reads ANTHROPIC_API_KEY and ANTHROPIC_MODEL from environment.
"""

import json
import os
from typing import List, Dict, Any

from packages.llm.base import CR_LLMProvider, CR_LLMResponse, CR_ToolCall


class CR_AnthropicAdapter(CR_LLMProvider):
    """Anthropic Claude tool-use adapter."""

    def __init__(self):
        try:
            import anthropic
            self._anthropic = anthropic
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic>=0.30.0")

        CR_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not CR_api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")

        self._client = anthropic.Anthropic(api_key=CR_api_key)
        self._model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")

    def get_provider_name(self) -> str:
        return "anthropic"

    def get_model_name(self) -> str:
        return self._model

    def chat_with_tools(
        self,
        CR_messages: List[Dict[str, Any]],
        CR_tools: List[Dict[str, Any]],
        CR_tool_executor: Any,
        CR_max_iterations: int = 10
    ) -> CR_LLMResponse:
        CR_all_tool_calls: List[CR_ToolCall] = []
        CR_total_usage = {"prompt_tokens": 0, "completion_tokens": 0}

        # Extract system prompt from messages (Anthropic uses separate system param)
        CR_system = ""
        CR_conv_messages = []
        for CR_msg in CR_messages:
            if CR_msg["role"] == "system":
                CR_system = CR_msg["content"]
            else:
                CR_conv_messages.append(CR_msg)

        # Convert tool schemas to Anthropic format
        CR_ant_tools = [
            {
                "name": t["name"],
                "description": t["description"],
                "input_schema": t["parameters"]
            }
            for t in CR_tools
        ]

        CR_messages_copy = list(CR_conv_messages)

        for _ in range(CR_max_iterations):
            CR_response = self._client.messages.create(
                model=self._model,
                max_tokens=4096,
                system=CR_system,
                messages=CR_messages_copy,
                tools=CR_ant_tools
            )

            CR_total_usage["prompt_tokens"] += CR_response.usage.input_tokens or 0
            CR_total_usage["completion_tokens"] += CR_response.usage.output_tokens or 0

            # Check for tool_use blocks
            CR_tool_use_blocks = [b for b in CR_response.content if b.type == "tool_use"]
            CR_text_blocks = [b for b in CR_response.content if b.type == "text"]

            if CR_response.stop_reason == "end_turn" or not CR_tool_use_blocks:
                CR_final_text = " ".join(b.text for b in CR_text_blocks)
                return CR_LLMResponse(
                    CR_content=CR_final_text,
                    CR_tool_calls=CR_all_tool_calls,
                    CR_finish_reason="stop",
                    CR_usage=CR_total_usage,
                    CR_provider=self.get_provider_name(),
                    CR_model=self._model
                )

            # Append assistant turn
            CR_messages_copy.append({"role": "assistant", "content": CR_response.content})

            # Execute tool calls and build tool_result blocks
            CR_tool_results = []
            for CR_block in CR_tool_use_blocks:
                CR_name = CR_block.name
                CR_args = CR_block.input
                try:
                    CR_result = CR_tool_executor(CR_name, CR_args)
                    CR_result_str = json.dumps(CR_result)
                    CR_error = None
                except Exception as CR_e:
                    CR_result = None
                    CR_result_str = f"Error: {str(CR_e)}"
                    CR_error = str(CR_e)

                CR_all_tool_calls.append(CR_ToolCall(
                    CR_tool_name=CR_name,
                    CR_arguments=CR_args,
                    CR_result=CR_result,
                    CR_error=CR_error
                ))

                CR_tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": CR_block.id,
                    "content": CR_result_str
                })

            CR_messages_copy.append({"role": "user", "content": CR_tool_results})

        return CR_LLMResponse(
            CR_content="Analysis complete (max tool iterations reached).",
            CR_tool_calls=CR_all_tool_calls,
            CR_finish_reason="stop",
            CR_usage=CR_total_usage,
            CR_provider=self.get_provider_name(),
            CR_model=self._model
        )
