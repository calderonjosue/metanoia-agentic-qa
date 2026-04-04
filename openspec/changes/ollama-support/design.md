# Design: LLM Provider Abstraction for Air-Gapped Support

## Technical Approach

Introduce a provider abstraction layer that allows runtime selection of LLM backends. Each provider implements a common interface and maps to its runtime's OpenAI-compatible endpoint. This approach minimizes changes to agents while enabling air-gapped operation.

## Architecture Decisions

### Decision: Abstract Base Class for Providers

**Choice**: `LLMProvider` abstract class in `src/llm/base.py`  
**Alternatives considered**: Protocol-based duck typing, factory pattern with conditional imports  
**Rationale**: ABC provides clear interface contract and enables `isinstance()` checks. Factory pattern would scatter provider instantiation logic.

### Decision: OpenAI-Compatible API as Common Interface

**Choice**: All providers expose OpenAI-compatible endpoint shapes (`/v1/chat/completions`, `/v1/embeddings`)  
**Alternatives considered**: Provider-specific native interfaces  
**Rationale**: Ollama, vLLM, and llama.cpp all ship OpenAI-compatible APIs. Normalizing at this layer minimizes translation code.

### Decision: Environment Variable for Provider Selection

**Choice**: `LLM_PROVIDER` env var controls active provider  
**Alternatives considered**: Config file, runtime flag, build-time flag  
**Rationale**: Env vars are the standard 12-factor approach, work well with Docker/K8s, and don't require code changes for provider switching.

## Data Flow

```
Agent.execute(state)
    │
    ▼
AgentConfig.provider  ← Injected at initialization
    │
    ▼
LLMProvider.chat(messages)  ← Polymorphic call
    │
    ├──► OpenAIProvider.chat() ──→ OpenAI API
    ├──► OllamaProvider.chat() ──→ Ollama /v1/chat/completions
    ├──► VLLMProvider.chat() ──→ vLLM /v1/chat/completions
    └──► LlamaCppProvider.chat() ──→ llama.cpp /v1/chat/completions
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/llm/__init__.py` | Create | Package init with `get_provider()` factory |
| `src/llm/base.py` | Create | `LLMProvider` abstract base class |
| `src/llm/openai.py` | Modify | Refactor to `OpenAIProvider` concrete class |
| `src/llm/ollama.py` | Create | `OllamaProvider` implementation |
| `src/llm/vllm.py` | Create | `VLLMProvider` implementation |
| `src/llm/llamacpp.py` | Create | `LlamaCppProvider` implementation |
| `src/agents/base.py` | Modify | Add `provider` field to `AgentConfig`, remove hardcoded model |
| `.env.example` | Modify | Add `LLM_PROVIDER`, `OLLAMA_URL`, `VLLM_URL`, `LLAMACPP_URL` |

## Interfaces / Contracts

### LLMProvider Abstract Class

```python
class LLMProvider(ABC):
    @abstractmethod
    def chat(self, messages: list[dict], **kwargs) -> dict:
        """Send a chat completion request."""
        pass

    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> dict:
        """Send a text completion request."""
        pass

    @abstractmethod
    def embed(self, text: str, **kwargs) -> list[float]:
        """Generate embeddings for text."""
        pass
```

### Provider Factory

```python
def get_provider() -> LLMProvider:
    """Return the active provider based on LLM_PROVIDER env var."""
    provider_name = os.getenv("LLM_PROVIDER", "openai")
    # ... dispatch logic
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Each provider's request formatting | Mock HTTP responses, verify request shape |
| Unit | Provider factory dispatch | Patch env vars, verify correct class instantiated |
| Integration | Full provider → actual server (optional) | Skip in CI if no local runtime |
| Integration | Agent uses injected provider | Inject mock provider, verify calls |

## Migration / Rollout

No migration required. The change is additive:
1. New provider files added alongside existing code
2. `LLM_PROVIDER=openai` maintains existing behavior
3. Agents receive provider via injection (backward compatible with current usage)

## Open Questions

None identified. All provider APIs are OpenAI-compatible, and the abstraction boundary is clear.
