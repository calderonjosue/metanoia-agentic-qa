"""Tests for LLM providers."""
import pytest

class TestLLMProvider:
    """Tests for LLMProvider ABC."""
    
    def test_provider_has_required_methods(self):
        """Each provider must implement complete, health_check, supports_functions."""
        from src.llm.base import LLMProvider
        # ABC cannot be instantiated directly
        assert hasattr(LLMProvider, 'complete')
        assert hasattr(LLMProvider, 'health_check')
        assert hasattr(LLMProvider, 'supports_functions')

class TestOpenAIProvider:
    """Tests for OpenAIProvider."""
    
    @pytest.fixture
    def provider(self):
        from src.llm.openai import OpenAIProvider
        return OpenAIProvider()
    
    def test_supports_functions(self, provider):
        assert provider.supports_functions() is True

class TestOllamaProvider:
    """Tests for OllamaProvider."""
    
    @pytest.fixture
    def provider(self):
        from src.llm.ollama import OllamaProvider
        return OllamaProvider()
    
    def test_supports_functions(self, provider):
        # Ollama may not support function calling
        result = provider.supports_functions()
        assert isinstance(result, bool)

class TestRegistry:
    """Tests for get_provider factory."""
    
    def test_get_openai_provider(self):
        from src.llm.registry import get_provider
        provider = get_provider('openai')
        assert provider is not None
    
    def test_get_unknown_raises(self):
        from src.llm.registry import get_provider
        with pytest.raises(ValueError):
            get_provider('unknown-provider')
