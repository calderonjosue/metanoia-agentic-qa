"""OpenAI LLM provider implementation."""

from typing import Any

from langchain_openai import ChatOpenAI

from src.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI provider using langchain_openai ChatOpenAI.

    Attributes:
        model: The OpenAI model to use (default: gpt-4o-mini).
        temperature: Sampling temperature (default: 0.7).
        **kwargs: Additional ChatOpenAI arguments.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        **kwargs: Any,
    ):
        """Initialize the OpenAI provider.

        Args:
            model: The OpenAI model name.
            temperature: Sampling temperature for generation.
            **kwargs: Additional ChatOpenAI arguments.
        """
        self.model = model
        self.temperature = temperature
        self._client = ChatOpenAI(model=model, temperature=temperature, **kwargs)

    def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate a completion for the given prompt.

        Args:
            prompt: The input prompt to generate a completion for.
            **kwargs: Additional arguments (max_tokens, stop, etc.).

        Returns:
            The generated completion as a string.
        """
        response = self._client.invoke(prompt, **kwargs)
        return response.content if hasattr(response, "content") else str(response)

    def health_check(self) -> bool:
        """Check if the OpenAI provider is healthy.

        Returns:
            True if the provider is healthy, False otherwise.
        """
        try:
            self._client.invoke("ping")
            return True
        except Exception:
            return False

    def supports_functions(self) -> bool:
        """Check if the provider supports function calling.

        Returns:
            True - OpenAI models support function calling.
        """
        return True
