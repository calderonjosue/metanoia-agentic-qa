"""DeepSeek provider - https://api.deepseek.com"""

from typing import Any

from langchain_openai import ChatOpenAI

from src.llm.base import LLMProvider


class DeepSeekProvider(LLMProvider):
    """DeepSeek provider using langchain_openai ChatOpenAI.

    Attributes:
        model: The DeepSeek model to use (default: deepseek-chat).
        temperature: Sampling temperature (default: 0.7).
        **kwargs: Additional ChatOpenAI arguments.
    """

    def __init__(
        self,
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        **kwargs: Any,
    ):
        """Initialize the DeepSeek provider.

        Args:
            model: The DeepSeek model name.
            temperature: Sampling temperature for generation.
            **kwargs: Additional ChatOpenAI arguments.
        """
        self.model = model
        self.temperature = temperature
        self._client = ChatOpenAI(
            model=model,
            temperature=temperature,
            base_url="https://api.deepseek.com",
            **kwargs,
        )

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
        """Check if the DeepSeek provider is healthy.

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
            True if function calling is supported, False otherwise.
        """
        return True
