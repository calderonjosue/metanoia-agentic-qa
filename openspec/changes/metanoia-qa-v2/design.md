# Design: Metanoia-QA v2.0 — Unified Platform Upgrade

## Technical Approach

Transform Metanoia-QA from a Gemini-only single-provider framework into a multi-provider platform via horizontal slicing across three phases: Foundation (LLM abstraction + enum consolidation), Core (parallel execution + IaC + CI/CD), and Advanced (chaos + Skill Hub).

**Compatibility Contract**: All existing v1.0 APIs remain functional. New features are additive. Feature flags control opt-in capabilities.

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM Provider Selection | `AgentConfig.provider` field | Non-breaking; defaults to `gemini` for backward compat |
| Enum Source of Truth | `src/orchestrator/agents.py` | Consolidate duplicates; import aliases preserve existing code |
| Parallel Execution | LangGraph `Send()` API | Native LangGraph fan-out; no external queue deps |
| IaC Abstraction | Terraform-first protocol | AWS-only for v2; protocol allows future providers |
| Skill Registry | Manifest v2 schema | Backward-compatible with v1 manifests via version detection |
| Ollama Air-Gap | Offline detection + model caching | Works online/offline; transparent to agents |

## Data Flow

```
                    ┌─────────────────────────────────────────┐
                    │           LLM Provider Layer            │
                    │  ┌─────────┐ ┌─────────┐ ┌─────────┐  │
                    │  │ Gemini  │ │ OpenAI  │ │ Ollama  │  │
                    │  │(default)│ │         │ │(air-gap)│  │
                    │  └────┬────┘ └────┬────┘ └────┬────┘  │
                    └───────┼───────────┼───────────┼───────┘
                            │           │           │
            ┌───────────────┴───────────┴───────────┴───────────────┐
            │                    Skill Hub (any provider)            │
            └─────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
    ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
    │     IaC      │       │ Shift-Right  │       │   CI/CD      │
    │ (Terraform)  │       │ (APM/Tel)    │       │ (GitHub/GitLab)│
    └──────────────┘       └──────────────┘       └──────────────┘
```

### v1.0 to v2.0 Integration Sequence

```
User (v1.0) ──► Graph (v2.0) ──► Agents (v1.0-compatible)
                     │
                     ├── GeminiProvider (default, backward compat)
                     ├── OpenAIProvider (opt-in)
                     ├── OllamaProvider (air-gap mode)
                     └── Existing agents unchanged
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/llm/__init__.py` | **Create** | LLM provider package init |
| `src/llm/base.py` | **Create** | ABC for all LLM providers |
| `src/llm/gemini.py` | **Create** | Google Gemini provider (preserves existing behavior) |
| `src/llm/openai.py` | **Create** | OpenAI GPT provider |
| `src/llm/ollama.py` | **Create** | Ollama local provider with air-gap support |
| `src/llm/vllm.py` | **Create** | vLLM server provider |
| `src/llm/llamacpp.py` | **Create** | LlamaCpp provider |
| `src/orchestrator/agents.py` | **Create** | Consolidated AgentType enum (v1.0 compat alias) |
| `src/orchestrator/graph.py` | Modify | Replace mock nodes with real agent invocations; add `Send()` |
| `src/orchestrator/state.py` | Modify | Add `provider` field to AgentConfig; preserve existing fields |
| `src/skill_hub/__init__.py` | **Create** | Skill Hub package (refactored from skill_runtime) |
| `src/skill_hub/cli.py` | **Create** | CLI: install, list, search, publish |
| `src/skill_hub/registry.py` | **Create** | Manifest v2 registry |
| `src/skill_hub/loader.py` | **Create** | Dynamic skill loader |
| `src/infrastructure/__init__.py` | **Create** | IaC package |
| `src/infrastructure/iac_providers.py` | **Create** | Terraform IaCProvider protocol |
| `src/infrastructure/lab_manager.py` | **Create** | Lab lifecycle with auto-teardown |
| `src/infrastructure/cost_controller.py` | **Create** | Cost watchdog |
| `src/observability/__init__.py` | **Create** | APM/Observability package |
| `src/observability/telemetry.py` | **Create** | OpenTelemetry integration |
| `src/observability/anomaly_detector.py` | **Create** | Anomaly detection |
| `src/observability/apm/datadog.py` | **Create** | Datadog client |
| `src/observability/apm/newrelic.py` | **Create** | New Relic client |
| `src/ci/__init__.py` | **Create** | CI/CD orchestrator package |
| `src/ci/orchestrator.py` | **Create** | Quality gate orchestration |
| `src/ci/quality_gate.py` | **Create** | Quality gate logic |
| `src/ci/webhook.py` | **Create** | Quality webhook handler |
| `src/github/__init__.py` | **Create** | GitHub integration |
| `src/github/integration.py` | **Create** | GitHub API client |
| `src/gitlab/__init__.py | **Create** | GitLab integration |
| `src/gitlab/integration.py` | **Create** | GitLab API client |
| `src/agents/infrastructure_agent.py` | **Create** | k6 lab provisioning agent |
| `src/agents/chaos_agent.py` | **Create** | Chaos engineering agent |
| `src/config/secrets.py` | **Create** | Secrets management |
| `src/skill_runtime/__init__.py` | Deprecate | Redirects to skill_hub (v1.0 compat) |

**Files Modified (Not Deleted)**:
- `src/orchestrator/graph.py`: Add parallel execution via `Send()`
- `src/orchestrator/state.py`: Extend AgentType, add provider config
- `src/agents/base.py`: Extend AgentConfig with provider field

## Interface Definitions

### LLM Provider Protocol

```python
# src/llm/base.py
from abc import ABC, abstractmethod
from typing import Any

class LLMProvider(ABC):
    """Protocol for LLM providers."""
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider identifier (gemini, openai, ollama, vllm, llamacpp)."""
        pass
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate completion from prompt."""
        pass
    
    @abstractmethod
    async def generate_async(self, prompts: list[str], **kwargs) -> list[str]:
        """Generate completions for multiple prompts in parallel."""
        pass
    
    def supports_streaming(self) -> bool:
        """Whether provider supports streaming responses."""
        return False
    
    def is_offline_capable(self) -> bool:
        """Whether provider works in air-gapped environments."""
        return False
```

### IaC Provider Protocol

```python
# src/infrastructure/iac_providers.py
from abc import ABC, abstractmethod

class IaCProvider(ABC):
    """Protocol for infrastructure-as-code providers."""
    
    @abstractmethod
    async def provision(self, config: dict[str, Any]) -> str:
        """Provision infrastructure; returns resource ID."""
        pass
    
    @abstractmethod
    async def destroy(self, resource_id: str) -> None:
        """Tear down provisioned infrastructure."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Verify provider connectivity."""
        pass
```

### Skill Manifest V2

```python
# src/skill_hub/registry.py
from pydantic import BaseModel

class SkillManifestV2(BaseModel):
    """Skill manifest schema v2."""
    name: str
    version: str  # semver
    manifest_version: str = "2.0"
    author: str
    description: str
    triggers: list[str]
    dependencies: list[str] = []
    runtime: str  # python, node, etc.
    entrypoint: str  # relative path to executor
    compatibility: dict[str, str] = {}  # {"metanoia": ">=1.0.0"}
```

## Migration Strategy

### For Existing Users (v1.0 → v2.0)

1. **Zero-Migration Default**: Default provider remains `gemini`. Existing configs work without changes.
2. **Opt-In New Features**: Feature flags enable new capabilities progressively:
   ```bash
   METANOIA_ENABLE_OLLAMA=1    # Enable air-gap support
   METANOIA_ENABLE_IAC=1       # Enable IaC provisioning
   METANOIA_ENABLE_CHAOS=1     # Enable chaos engineering
   ```
3. **Parallel Execution**: Controlled via `METANOIA_PARALLEL_ENABLED=1`. Off by default for v2.0 to preserve sequential behavior.
4. **Skill Hub Migration**: `skill_runtime` redirects to `skill_hub` with deprecation warning. No manifest changes required for v1 skills.

### For New Users (Fresh v2.0 Install)

1. All features enabled by default
2. Provider selection via `METANOIA_LLM_PROVIDER` env var
3. IaC/CI/CD require explicit configuration

## Deprecation Notices

| Item | Deprecated In | Removal In | Replacement |
|------|---------------|------------|-------------|
| `src/orchestrator/AgentType` duplicate | v2.0 | v3.0 | `src/orchestrator/agents.AgentType` |
| `src/skill_runtime` module | v2.0 | v3.0 | `src/skill_hub` |
| Sequential execution (graph nodes) | v2.0 | v3.0 | LangGraph `Send()` parallel |
| Hardcoded `gemini-1.5-flash` | v2.0 | v3.0 | Configurable provider |
| Mock agent return values | v2.0 (Phase 1) | v2.1 | Real agent invocations |

## v1.0 Functionality Preservation

| v1.0 Feature | Preservation Mechanism |
|--------------|------------------------|
| Single-provider (Gemini) | Default provider; no config change required |
| Existing graph flow | Sequential nodes unchanged unless parallel enabled |
| Agent interfaces | `AgentConfig` extended, not replaced |
| Skill execution | `skill_runtime` alias redirects to `skill_hub` |
| Checkpointing | PostgresCheckpointSaver unchanged |
| API routes | Unchanged; no breaking REST API changes |

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Unit | LLM providers, IaC providers, agents | `pytest` with mocked external calls |
| Integration | Provider selection, Skill Hub CLI | `pytest-integration` with real providers |
| E2E | Full graph execution (sequential + parallel) | `pytest-e2e` with sprint fixtures |
| Air-gap | OllamaProvider offline detection | Mock network; validate cache hit |

## Open Questions

- [ ] Should `OllamaProvider` auto-detect available models or require explicit config?
- [ ] What is the timeout strategy for chaos experiment abort triggers?
- [ ] Should CI/CD webhooks use push or pull model for quality gate status?
