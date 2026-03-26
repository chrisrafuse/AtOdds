"""
LLM provider factory — selects and instantiates the right adapter from env config.
Priority: explicit argument > LLM_PROVIDER env var > "mock" fallback.
"""

import os
from typing import Optional

from packages.llm.base import CR_LLMProvider


def get_CR_llm_provider(CR_provider: Optional[str] = None) -> CR_LLMProvider:
    """
    Return a configured CR_LLMProvider instance.

    Resolution order:
    1. CR_provider argument (explicit override)
    2. LLM_PROVIDER environment variable
    3. "mock" fallback (no API key required)

    Supported values: "openai", "anthropic", "gemini", "mock"
    """
    CR_selected = (CR_provider or os.environ.get("LLM_PROVIDER", "mock")).lower().strip()

    if CR_selected == "openai":
        if not os.environ.get("OPENAI_API_KEY"):
            return _fallback_to_mock("openai", "OPENAI_API_KEY")
        from packages.llm.openai_adapter import CR_OpenAIAdapter
        return CR_OpenAIAdapter()

    if CR_selected == "anthropic":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return _fallback_to_mock("anthropic", "ANTHROPIC_API_KEY")
        from packages.llm.anthropic_adapter import CR_AnthropicAdapter
        return CR_AnthropicAdapter()

    if CR_selected == "gemini":
        if not os.environ.get("GEMINI_API_KEY"):
            return _fallback_to_mock("gemini", "GEMINI_API_KEY")
        from packages.llm.gemini_adapter import CR_GeminiAdapter
        return CR_GeminiAdapter()

    # "mock" or anything unrecognised
    from packages.llm.mock_provider import CR_MockProvider
    return CR_MockProvider()


def get_CR_provider_name() -> str:
    """Return the active provider name without instantiating."""
    CR_selected = os.environ.get("LLM_PROVIDER", "mock").lower().strip()
    CR_key_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": "GEMINI_API_KEY",
    }
    if CR_selected in CR_key_map and os.environ.get(CR_key_map[CR_selected]):
        return CR_selected
    return "mock"


def _fallback_to_mock(CR_requested: str, CR_key_name: str) -> CR_LLMProvider:
    import logging
    logging.getLogger("atodds.llm").warning(
        f"LLM_PROVIDER={CR_requested} but {CR_key_name} is not set — falling back to mock provider"
    )
    from packages.llm.mock_provider import CR_MockProvider
    return CR_MockProvider()
