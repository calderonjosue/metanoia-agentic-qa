"""Provider registry for LLM factory."""

from src.llm.base import LLMProvider
from src.llm.openai import OpenAIProvider
from src.llm.ollama import OllamaProvider
from src.llm.vllm import vLLMProvider
from src.llm.llamacpp import LlamaCppProvider
from src.llm.minimax import MiniMaxProvider
from src.llm.kimi import KimiProvider
from src.llm.glm import GLMProvider
from src.llm.deepseek import DeepSeekProvider


_PROVIDERS = {
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
    "vllm": vLLMProvider,
    "llamacpp": LlamaCppProvider,
    "gemini": OllamaProvider,
    "minimax": MiniMaxProvider,
    "kimi": KimiProvider,
    "glm": GLMProvider,
    "deepseek": DeepSeekProvider,
}


def get_provider(name: str) -> LLMProvider:
    """Factory to get LLM provider by name.

    Supported: 'openai', 'ollama', 'vllm', 'llamacpp', 'gemini', 'minimax', 'kimi', 'glm', 'deepseek'
    """
    if name not in _PROVIDERS:
        raise ValueError(
            f"Unknown provider '{name}'. Supported: {list(_PROVIDERS.keys())}"
        )
    return _PROVIDERS[name]()
