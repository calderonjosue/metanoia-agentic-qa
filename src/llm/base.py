"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for LLM (Large Language Model) providers.

    This class defines the interface that all LLM provider implementations
    must follow. Concrete implementations should extend this class and
    implement the required abstract methods.

    Attributes:
        None

    Example:
        >>> class MyProvider(LLMProvider):
        ...     def complete(self, prompt: str, **kwargs) -> str:
        ...         return "response"
        ...     def health_check(self) -> bool:
        ...         return True
        ...     def supports_functions(self) -> bool:
        ...         return False
    """

    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        """Generate a completion for the given prompt.

        Args:
            prompt: The input prompt to generate a completion for.
            **kwargs: Additional provider-specific arguments such as
                temperature, max_tokens, stop_sequences, etc.

        Returns:
            The generated completion as a string.

        Raises:
            NotImplementedError: If not implemented by subclass.
        """
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the LLM provider is healthy and available.

        This method should perform a lightweight check to verify
        that the provider is reachable and properly configured.

        Returns:
            True if the provider is healthy, False otherwise.

        Raises:
            NotImplementedError: If not implemented by subclass.
        """
        ...

    @abstractmethod
    def supports_functions(self) -> bool:
        """Check if the provider supports function calling.

        Function calling allows the model to invoke external
        functions/tools as part of its response generation.

        Returns:
            True if function calling is supported, False otherwise.

        Raises:
            NotImplementedError: If not implemented by subclass.
        """
        ...
