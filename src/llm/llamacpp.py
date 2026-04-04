"""Llama.cpp provider for local inference."""

import os
from typing import Any

from langchain_community.llms import LlamaCpp

from src.llm.base import LLMProvider


class LlamaCppProvider(LLMProvider):
    """Llama.cpp provider for local LLM inference."""

    def __init__(self) -> None:
        """Initialize the LlamaCpp provider."""
        model_path = os.environ.get("LLAMACPP_MODEL_PATH")
        if not model_path:
            raise ValueError("LLAMACPP_MODEL_PATH environment variable is not set")
        self._llm = LlamaCpp(model_path=model_path)

    def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate a completion for the given prompt.

        Args:
            prompt: The input prompt to generate a completion for.
            **kwargs: Additional arguments such as temperature, max_tokens, etc.

        Returns:
            The generated completion as a string.
        """
        return self._llm.invoke(prompt, **kwargs)

    def health_check(self) -> bool:
        """Check if the Llama.cpp provider is healthy.

        Returns:
            True if the provider is healthy, False otherwise.
        """
        try:
            self._llm.invoke("hello")
            return True
        except Exception:
            return False

    def supports_functions(self) -> bool:
        """Check if the provider supports function calling.

        Note:
            Llama.cpp typically does not support function calling.

        Returns:
            False, as Llama.cpp does not support function calling.
        """
        return False
