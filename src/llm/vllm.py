"""vLLM LLM provider implementation."""

import os
from typing import Any

from openai import OpenAI

from src.llm.base import LLMProvider


class vLLMProvider(LLMProvider):
    """vLLM provider for self-hosted inference.

    Uses OpenAI-compatible API client to connect to vLLM endpoints.

    Attributes:
        model: The vLLM model to use.
        temperature: Sampling temperature for generation.
    """

    def __init__(
        self,
        model: str = "meta-llama/Llama-3.1-8B-Instruct",
        temperature: float = 0.7,
        **kwargs: Any,
    ):
        """Initialize the vLLM provider.

        Args:
            model: The vLLM model name.
            temperature: Sampling temperature for generation.
            **kwargs: Additional OpenAI client arguments.
        """
        self.model = model
        self.temperature = temperature
        endpoint = os.getenv("VLLM_ENDPOINT", "http://localhost:8000")
        self._client = OpenAI(base_url=endpoint, api_key="not-needed", **kwargs)

    def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate a completion for the given prompt.

        Args:
            prompt: The input prompt to generate a completion for.
            **kwargs: Additional arguments (max_tokens, stop, etc.).

        Returns:
            The generated completion as a string.
        """
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            **kwargs,
        )
        return response.choices[0].message.content or ""

    def health_check(self) -> bool:
        """Check if the vLLM provider is healthy.

        Returns:
            True if the provider is healthy, False otherwise.
        """
        try:
            self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1,
            )
            return True
        except Exception:
            return False

    def supports_functions(self) -> bool:
        """Check if the provider supports function calling.

        Returns:
            False - vLLM support varies by model and configuration.
        """
        return False
