# Delta for LLM Provider Abstraction

## Purpose

Enable Metanoia to operate within air-gapped environments by supporting local LLM inference engines through a unified provider interface.

## ADDED Requirements

### Requirement: Provider Interface Abstraction

The system MUST provide a `LLMProvider` abstract interface in `src/llm/base.py` that defines `chat()`, `complete()`, and `embed()` methods.

### Requirement: Ollama Provider

The system SHALL implement an `OllamaProvider` in `src/llm/ollama.py` that connects to local Ollama instances via OpenAI-compatible API.

#### Scenario: Chat via Ollama

- GIVEN `LLM_PROVIDER=ollama` and `OLLAMA_URL=http://localhost:11434`
- WHEN an agent calls `provider.chat(messages)`
- THEN the system MUST route the request to the Ollama `/v1/chat/completions` endpoint
- AND return responses in OpenAI chat completion format

#### Scenario: Ollama Connection Failure

- GIVEN `LLM_PROVIDER=ollama` with an unreachable Ollama instance
- WHEN an agent calls `provider.chat(messages)`
- THEN the system MUST raise a `ConnectionError` with a descriptive message
- AND the agent's error handler MUST log the failure

### Requirement: vLLM Provider

The system SHALL implement a `VLLMProvider` in `src/llm/vllm.py` that connects to local vLLM endpoints.

#### Scenario: Chat via vLLM

- GIVEN `LLM_PROVIDER=vllm` and `VLLM_URL=http://localhost:8000`
- WHEN an agent calls `provider.chat(messages)`
- THEN the system MUST route the request to the vLLM `/v1/chat/completions` endpoint
- AND return responses in OpenAI chat completion format

### Requirement: llama.cpp Provider

The system SHALL implement a `LlamaCppProvider` in `src/llm/llamacpp.py` that connects to llama.cpp server mode.

#### Scenario: Chat via llama.cpp

- GIVEN `LLM_PROVIDER=llamacpp` and `LLAMACPP_URL=http://localhost:8080`
- WHEN an agent calls `provider.chat(messages)`
- THEN the system MUST route the request to the llama.cpp `/v1/chat/completions` endpoint
- AND return responses in OpenAI chat completion format

### Requirement: Runtime Provider Selection

The system MUST support runtime provider selection via the `LLM_PROVIDER` environment variable.

#### Scenario: Provider Switching

- GIVEN a running Metanoia instance with `LLM_PROVIDER=openai`
- WHEN the environment variable changes to `LLM_PROVIDER=ollama`
- THEN on next agent execution, the system MUST use the Ollama provider
- AND the previous OpenAI provider MUST be released

### Requirement: Agent Provider Injection

The system SHALL inject the active LLM provider into agents via configuration, not hardcoding.

#### Scenario: Agent Receives Provider

- GIVEN a configured `AgentConfig` with a provider instance
- WHEN the agent executes
- THEN the agent MUST use the injected provider for all LLM calls

## MODIFIED Requirements

### Requirement: Agent Default Model

(Previously: Agents defaulted to `gemini-1.5-flash`)

Agents MUST NOT hardcode a default LLM model. The model SHALL be determined by the provider configuration.

## REMOVED Requirements

None.

## Configuration Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `openai` | Active provider: `openai`, `ollama`, `vllm`, `llamacpp` |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server endpoint |
| `VLLM_URL` | `http://localhost:8000` | vLLM server endpoint |
| `LLAMACPP_URL` | `http://localhost:8080` | llama.cpp server endpoint |
| `OPENAI_API_KEY` | (none) | API key for OpenAI |
| `OLLAMA_API_KEY` | (none) | API key for Ollama (if required) |
