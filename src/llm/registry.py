"""Provider registry for LLM factory."""

from src.llm.base import LLMProvider
from src.llm.openai import OpenAIProvider
from src.llm.ollama import OllamaProvider
from src.llm.vllm import vLLMProvider
from src.llm.llamacpp import LlamaCppProvider


_PROVIDERS = {
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
    "vllm": vLLMProvider,
    "llamacpp": LlamaCppProvider,
    "gemini": OllamaProvider,
}


def get_provider(name: str) -> LLMProvider:
    """Factory to get LLM provider by name.

    Supported: 'openai', 'ollama', 'vllm', 'llamacpp', 'gemini' (default)
    """
    if name not in _PROVIDERS:
        raise ValueError(
            f"Unknown provider '{name}'. Supported: {list(_PROVIDERS.keys())}"
        )
    return _PROVIDERS[name]()
