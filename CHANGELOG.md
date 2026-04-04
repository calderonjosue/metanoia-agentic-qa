# Changelog

## v2.0.0 (2026-04-04)

### Phase 1: LLM Abstraction
- Added LLM providers: OpenAI, Ollama, vLLM, Llama.cpp
- Consolidated AgentType enum
- Provider factory: `get_provider()`

### Phase 2: Core Features
- Real agent execution in graph
- Parallel execution with LangGraph Send()
- IaC providers (Terraform)
- Lab lifecycle manager
- Cost controller
- GitHub/GitLab integration
- CI/CD orchestration
- Quality gate

### Phase 3: Advanced Features
- Skill Hub CLI
- Observability (Datadog, New Relic, OpenTelemetry)
- Chaos Engineering (ChaosAgent, AbortController)

## v1.0.0 (2026-04-04)
- Initial release
