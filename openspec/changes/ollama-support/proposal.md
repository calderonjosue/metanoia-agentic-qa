# Proposal: LLM Agnosticism / Air-Gapped Mode

## Intent

Enable Metanoia to operate entirely within air-gapped environments by supporting local LLM inference engines (Ollama, vLLM, llama.cpp). This addresses enterprise requirements from regulated industries (banks, insurers, government) where data sovereignty is non-negotiable and external API calls are prohibited.

## Scope

### In Scope
- Ollama provider: Connect to local Ollama instances via OpenAI-compatible API
- vLLM provider: Support vLLM's OpenAI-compatible endpoints
- llama.cpp backend: Direct model loading via llama.cpp's server mode
- Unified provider interface: `LLMProvider` abstraction with pluggable backends
- Configuration: Runtime provider selection via config/env vars
- Model management: Support DeepSeek-Coder, Llama-3 family on local hardware

### Out of Scope
- Model fine-tuning or training pipelines
- Multi-node vLLM clustering (single-node only)
- Ollama model pulling/management (assumes pre-downloaded models)
- GPU allocation strategies

## Approach

Introduce a `LLMProvider` interface in `src/llm/` that abstracts `chat()`, `complete()`, and `embed()` operations. Implement concrete providers:

```
src/llm/
├── base.py           # LLMProvider abstract class
├── openai.py         # Existing cloud OpenAI
├── ollama.py         # NEW: Ollama provider
├── vllm.py           # NEW: vLLM provider  
└── llamacpp.py       # NEW: llama.cpp provider
```

Each provider maps to its respective runtime's OpenAI-compatible endpoint. Provider selection is runtime-configured via `LLM_PROVIDER` env var (default: `openai`).

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/llm/` | New | Provider interface and implementations |
| `src/agents/` | Modified | Swap provider via config injection |
| `config/` | Modified | Add `LLM_PROVIDER`, `OLLAMA_URL`, `VLLM_URL` vars |
| `src/llm/openai.py` | Modified | Refactor to concrete provider implementation |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Inconsistent OpenAI-compatible API coverage across engines | Medium | Abstract at interface level; test each provider |
| Performance variance across local HW configurations | Low | Document minimum specs; async handling in provider |
| Authentication differences between providers | Low | Use API key env vars per provider |

## Rollback Plan

1. Set `LLM_PROVIDER=openai` env var
2. Revert config changes to remove provider-specific vars
3. Remove new provider files; restore original `src/llm/openai.py` import

## Dependencies

- Ollama v0.1+ running locally (or vLLM/llama.cpp)
- Existing OpenAI provider remains functional (no breaking changes)

## Success Criteria

- [ ] `LLM_PROVIDER=ollama` routes all LLM calls to local Ollama instance
- [ ] `LLM_PROVIDER=vllm` routes all LLM calls to local vLLM endpoint
- [ ] Agents function identically regardless of provider selection
- [ ] No external network calls when operating in air-gapped mode
- [ ] DeepSeek-Coder and Llama-3 models load and respond correctly
