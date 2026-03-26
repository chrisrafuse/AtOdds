"""
OpenAI adapter — implements CR_LLMProvider using the openai SDK.
Reads OPENAI_API_KEY and OPENAI_MODEL from environment.
"""

import json
import os
from typing import List, Dict, Any

from packages.llm.base import CR_LLMProvider, CR_LLMResponse, CR_ToolCall


class CR_OpenAIAdapter(CR_LLMProvider):
    """OpenAI function-calling adapter."""

    def __init__(self):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai>=1.0.0")

        CR_api_key = os.environ.get("OPENAI_API_KEY", "")
        if not CR_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        self._client = OpenAI(api_key=CR_api_key)
        self._model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    def get_provider_name(self) -> str:
        return "openai"

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
        CR_messages = list(CR_messages)  # local copy

        # Convert tool schemas to OpenAI format
        CR_oai_tools = [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["parameters"]
                }
            }
            for t in CR_tools
        ]

        CR_total_usage = {"prompt_tokens": 0, "completion_tokens": 0}

        for _ in range(CR_max_iterations):
            CR_response = self._client.chat.completions.create(
                model=self._model,
                messages=CR_messages,
                tools=CR_oai_tools,
                tool_choice="auto"
            )

            CR_choice = CR_response.choices[0]
            CR_message = CR_choice.message

            # Accumulate token usage
            if CR_response.usage:
                CR_total_usage["prompt_tokens"] += CR_response.usage.prompt_tokens or 0
                CR_total_usage["completion_tokens"] += CR_response.usage.completion_tokens or 0

            # No tool calls → model is done
            if CR_choice.finish_reason == "stop" or not CR_message.tool_calls:
                return CR_LLMResponse(
                    CR_content=CR_message.content or "",
                    CR_tool_calls=CR_all_tool_calls,
                    CR_finish_reason="stop",
                    CR_usage=CR_total_usage,
                    CR_provider=self.get_provider_name(),
                    CR_model=self._model
                )

            # Append assistant message with tool_calls to history
            CR_messages.append(CR_message)

            # Execute each tool call
            for CR_tc in CR_message.tool_calls:
                CR_name = CR_tc.function.name
                CR_args = {}
                CR_result = None
                CR_error = None
                try:
                    CR_args = json.loads(CR_tc.function.arguments)
                    CR_result = CR_tool_executor(CR_name, CR_args)
                except Exception as CR_e:
                    CR_error = str(CR_e)

                CR_tool_call = CR_ToolCall(
                    CR_tool_name=CR_name,
                    CR_arguments=CR_args,
                    CR_result=CR_result,
                    CR_error=CR_error
                )
                CR_all_tool_calls.append(CR_tool_call)

                CR_messages.append({
                    "role": "tool",
                    "tool_call_id": CR_tc.id,
                    "content": json.dumps(CR_result) if CR_result is not None else f"Error: {CR_error}"
                })

        # Max iterations hit
        return CR_LLMResponse(
            CR_content="Analysis complete (max tool iterations reached).",
            CR_tool_calls=CR_all_tool_calls,
            CR_finish_reason="stop",
            CR_usage=CR_total_usage,
            CR_provider=self.get_provider_name(),
            CR_model=self._model
        )
