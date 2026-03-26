"""
Google Gemini adapter — implements CR_LLMProvider using google-generativeai SDK.
Reads GEMINI_API_KEY and GEMINI_MODEL from environment.
"""

import json
import os
from typing import List, Dict, Any

from packages.llm.base import CR_LLMProvider, CR_LLMResponse, CR_ToolCall


class CR_GeminiAdapter(CR_LLMProvider):
    """Google Gemini function-calling adapter."""

    def __init__(self):
        try:
            import google.generativeai as genai
            self._genai = genai
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. "
                "Run: pip install google-generativeai>=0.7.0"
            )

        CR_api_key = os.environ.get("GEMINI_API_KEY", "")
        if not CR_api_key:
            raise ValueError("GEMINI_API_KEY not set in environment")

        genai.configure(api_key=CR_api_key)
        self._model_name = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

    def get_provider_name(self) -> str:
        return "gemini"

    def get_model_name(self) -> str:
        return self._model_name

    def chat_with_tools(
        self,
        CR_messages: List[Dict[str, Any]],
        CR_tools: List[Dict[str, Any]],
        CR_tool_executor: Any,
        CR_max_iterations: int = 10
    ) -> CR_LLMResponse:
        CR_all_tool_calls: List[CR_ToolCall] = []
        CR_total_usage = {"prompt_tokens": 0, "completion_tokens": 0}

        # Extract system prompt and build Gemini history
        CR_system_parts = []
        CR_history = []
        CR_last_user_msg = ""

        for CR_msg in CR_messages:
            if CR_msg["role"] == "system":
                CR_system_parts.append(CR_msg["content"])
            elif CR_msg["role"] == "user":
                CR_last_user_msg = CR_msg["content"]
                CR_history.append({"role": "user", "parts": [CR_msg["content"]]})
            elif CR_msg["role"] == "assistant":
                CR_history.append({"role": "model", "parts": [CR_msg["content"]]})

        # Convert tool schemas to Gemini function declarations
        CR_gemini_tools = self._build_gemini_tools(CR_tools)

        CR_system_instruction = "\n".join(CR_system_parts) if CR_system_parts else None

        CR_model = self._genai.GenerativeModel(
            model_name=self._model_name,
            tools=CR_gemini_tools,
            system_instruction=CR_system_instruction
        )

        # Remove last user message from history, use it as the starting send
        if CR_history and CR_history[-1]["role"] == "user":
            CR_history = CR_history[:-1]

        CR_chat = CR_model.start_chat(history=CR_history)

        CR_current_msg = CR_last_user_msg

        for _ in range(CR_max_iterations):
            CR_response = CR_chat.send_message(CR_current_msg)
            CR_candidate = CR_response.candidates[0]

            # Check for function calls
            CR_fn_calls = []
            for CR_part in CR_candidate.content.parts:
                if hasattr(CR_part, 'function_call') and CR_part.function_call.name:
                    CR_fn_calls.append(CR_part.function_call)

            if not CR_fn_calls:
                CR_final_text = CR_response.text if hasattr(CR_response, 'text') else ""
                return CR_LLMResponse(
                    CR_content=CR_final_text,
                    CR_tool_calls=CR_all_tool_calls,
                    CR_finish_reason="stop",
                    CR_usage=CR_total_usage,
                    CR_provider=self.get_provider_name(),
                    CR_model=self._model_name
                )

            # Execute function calls and build function_response parts
            CR_response_parts = []
            for CR_fn in CR_fn_calls:
                CR_name = CR_fn.name
                CR_args = dict(CR_fn.args)
                try:
                    CR_result = CR_tool_executor(CR_name, CR_args)
                    CR_error = None
                except Exception as CR_e:
                    CR_result = {"error": str(CR_e)}
                    CR_error = str(CR_e)

                CR_all_tool_calls.append(CR_ToolCall(
                    CR_tool_name=CR_name,
                    CR_arguments=CR_args,
                    CR_result=CR_result,
                    CR_error=CR_error
                ))

                CR_response_parts.append(
                    self._genai.protos.Part(
                        function_response=self._genai.protos.FunctionResponse(
                            name=CR_name,
                            response={"result": json.dumps(CR_result) if CR_result else "{}"}
                        )
                    )
                )

            CR_current_msg = CR_response_parts

        return CR_LLMResponse(
            CR_content="Analysis complete (max tool iterations reached).",
            CR_tool_calls=CR_all_tool_calls,
            CR_finish_reason="stop",
            CR_usage=CR_total_usage,
            CR_provider=self.get_provider_name(),
            CR_model=self._model_name
        )

    def _build_gemini_tools(self, CR_schemas: List[Dict]) -> list:
        """Convert OpenAI-style schemas to Gemini function declarations."""
        CR_declarations = []
        for CR_schema in CR_schemas:
            CR_declarations.append(
                self._genai.protos.FunctionDeclaration(
                    name=CR_schema["name"],
                    description=CR_schema["description"],
                    parameters=self._genai.protos.Schema(
                        type=self._genai.protos.Type.OBJECT,
                        properties={
                            k: self._genai.protos.Schema(type=self._genai.protos.Type.STRING)
                            for k in CR_schema.get("parameters", {}).get("properties", {})
                        }
                    )
                )
            )
        return [self._genai.protos.Tool(function_declarations=CR_declarations)]
