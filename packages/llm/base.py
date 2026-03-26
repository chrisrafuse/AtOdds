"""
LLM provider abstraction — base classes and data contracts.
All providers implement CR_LLMProvider. No provider-specific code outside adapters.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class CR_ToolCall:
    """Represents a single tool call made by the LLM during a run."""
    CR_tool_name: str
    CR_arguments: Dict[str, Any]
    CR_result: Any = None
    CR_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'CR_tool_name': self.CR_tool_name,
            'CR_arguments': self.CR_arguments,
            'CR_result': self.CR_result,
            'CR_error': self.CR_error,
        }


@dataclass
class CR_LLMResponse:
    """Unified response from any LLM provider."""
    CR_content: str                                    # final text output
    CR_tool_calls: List[CR_ToolCall] = field(default_factory=list)
    CR_finish_reason: str = "stop"                    # "stop" | "tool_calls" | "error"
    CR_usage: Dict[str, int] = field(default_factory=dict)  # prompt/completion tokens
    CR_provider: str = ""
    CR_model: str = ""


class CR_LLMProvider(ABC):
    """Abstract base for all LLM providers."""

    @abstractmethod
    def chat_with_tools(
        self,
        CR_messages: List[Dict[str, Any]],
        CR_tools: List[Dict[str, Any]],
        CR_tool_executor: Any,          # callable: (name, args) -> result
        CR_max_iterations: int = 10
    ) -> CR_LLMResponse:
        """
        Run a tool-calling conversation loop until the model stops.

        Args:
            CR_messages: OpenAI-style message list
            CR_tools: Tool schema list (OpenAI format — adapters convert internally)
            CR_tool_executor: callable(tool_name, args) -> Any
            CR_max_iterations: Safety cap on tool-calling rounds

        Returns:
            CR_LLMResponse with final content and full tool call trace
        """
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        ...

    @abstractmethod
    def get_model_name(self) -> str:
        ...
