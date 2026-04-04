"""Ollama LLM provider for air-gapped operation."""

import os
import socket
from typing import Any

from langchain_ollama import ChatOllama

from src.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    """Ollama provider using langchain_ollama ChatOllama.

    Supports air-gapped operation with offline mode detection and
    model caching awareness.

    Attributes:
        model: The Ollama model name (default: llama3.2).
        base_url: The Ollama server URL (default: http://localhost:11434).
        temperature: Sampling temperature (default: 0.7).
        **kwargs: Additional ChatOllama arguments.
    """

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        **kwargs: Any,
    ):
        """Initialize the Ollama provider.

        Args:
            model: The Ollama model name.
            base_url: The Ollama server URL.
            temperature: Sampling temperature for generation.
            **kwargs: Additional ChatOllama arguments.
        """
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self._client = ChatOllama(
            model=model,
            base_url=base_url,
            temperature=temperature,
            **kwargs,
        )

    def is_offline(self) -> bool:
        """Detect if the system is in air-gapped mode.

        Checks if the Ollama server is unreachable by attempting
        a socket connection to the host and port.

        Returns:
            True if the system appears to be offline (cannot reach server),
            False otherwise.
        """
        try:
            host = self.base_url.replace("http://", "").replace("https://", "").split(":")[0]
            port = 11434
            if ":" in self.base_url:
                port_str = self.base_url.split(":")[-1].split("/")[0]
                port = int(port_str)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            return result != 0
        except Exception:
            return True

    def is_cached(self) -> bool:
        """Check if the model is cached locally.

        Attempts to list models via Ollama API to determine if the
        current model is available in the local cache.

        Returns:
            True if the model appears to be cached locally,
            False otherwise or if API call fails.
        """
        try:
            import urllib.request
            import json

            url = f"{self.base_url}/api/tags"
            req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                models = data.get("models", [])
                for m in models:
                    if m.get("name") == self.model:
                        return True
                return False
        except Exception:
            return False

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
        """Check if the Ollama provider is healthy.

        Returns:
            True if the provider is healthy and reachable,
            False otherwise.
        """
        try:
            self._client.invoke("ping")
            return True
        except Exception:
            return False

    def supports_functions(self) -> bool:
        """Check if the provider supports function calling.

        Note:
            Ollama models have varying function calling support.
            Most recent models (llama3.2+, mistral-nemo) support it.

        Returns:
            True if the model typically supports function calling,
            False otherwise.
        """
        return True
