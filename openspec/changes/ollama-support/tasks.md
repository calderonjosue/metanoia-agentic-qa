# Tasks: LLM Provider Abstraction for Air-Gapped Support

## Phase 1: Foundation

- [ ] 1.1 Create `src/llm/__init__.py` with `get_provider()` factory function
- [ ] 1.2 Create `src/llm/base.py` with `LLMProvider` abstract base class defining `chat()`, `complete()`, `embed()`
- [ ] 1.3 Update `.env.example` with `LLM_PROVIDER=openai`, `OLLAMA_URL`, `VLLM_URL`, `LLAMACPP_URL` variables

## Phase 2: Provider Implementations

- [ ] 2.1 Refactor `src/llm/openai.py` to `OpenAIProvider` class inheriting from `LLMProvider`
- [ ] 2.2 Create `src/llm/ollama.py` with `OllamaProvider` implementing OpenAI-compatible `/v1/chat/completions` calls
- [ ] 2.3 Create `src/llm/vllm.py` with `VLLMProvider` implementing OpenAI-compatible `/v1/chat/completions` calls
- [ ] 2.4 Create `src/llm/llamacpp.py` with `LlamaCppProvider` implementing OpenAI-compatible `/v1/chat/completions` calls

## Phase 3: Agent Integration

- [ ] 3.1 Add `provider: LLMProvider` field to `AgentConfig` in `src/agents/base.py`
- [ ] 3.2 Remove hardcoded `gemini-1.5-flash` model from `AgentConfig` defaults
- [ ] 3.3 Update agent initialization to accept provider via config injection

## Phase 4: Testing

- [ ] 4.1 Write unit tests for `get_provider()` factory with mocked env vars
- [ ] 4.2 Write unit tests for each provider's request formatting (mock HTTP responses)
- [ ] 4.3 Write integration test verifying agent uses injected provider (inject mock provider)

## Phase 5: Documentation

- [ ] 5.1 Update `.env.example` comments to document air-gapped provider configuration
- [ ] 5.2 Add provider selection documentation to `docs/` or `README.md`
