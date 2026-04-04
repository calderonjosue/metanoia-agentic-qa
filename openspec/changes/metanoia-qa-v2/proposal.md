# Proposal: Metanoia-QA v2.0 — Unified Platform Upgrade

## Intent

Transform Metanoia-QA from a single-provider Gemini-only autonomous QA framework into a multi-provider, production-grade platform supporting air-gapped deployments, infrastructure-as-code provisioning, chaos engineering, and community-driven skill extensibility.

## Scope

### In Scope (v2.0)
- **Foundational Fixes**
  - LLM provider abstraction layer (`src/llm/`) with OpenAI, Ollama, vLLM, LlamaCpp providers
  - Consolidate duplicate `AgentType` enums into `src/orchestrator/agents.py`
  - Replace mock agent invocations with real agent execution in `graph.py`
  - Implement LangGraph `Send()` parallel execution fan-out

- **Skill Hub CLI**
  - `src/skill_runtime/` → `src/skill_hub/` refactor
  - `skill-hub` CLI command: `install`, `list`, `search`, `publish`
  - Community skill registry with manifest schema v2

- **Ollama Air-Gapped Support**
  - `OllamaProvider` implementation
  - Model caching and offline detection
  - Local model management CLI

- **IaC Integration**
  - `InfrastructureAgent` for k6 lab provisioning
  - Terraform/Pulumi provider abstraction (`src/infrastructure/`)
  - Lab lifecycle management with auto-teardown
  - Cost control and watchdog

- **Shift-Right / Chaos Engineering**
  - APM clients: Datadog, New Relic, OpenTelemetry (`src/observability/`)
  - `ChaosAgent` and `ChaosEngineer` (`src/agents/chaos/`)
  - Declarative experiment definitions
  - Abort triggers on cascading failure

- **CI/CD Orchestrator**
  - `src/ci/` module: orchestrator, quality gate, quality webhook
  - GitHub/GitLab integration (`src/github/`, `src/gitlab/`)
  - Automated PR merge and deploy triggers
  - Secrets management (`src/config/secrets.py`)

### Out of Scope (Future)
- Multi-cloud IaC (AWS-only for v2; GCP/Azure later)
- Featured/official skills distinction in hub
- Message-passing scale architecture (deferred to v3)
- Chaos auto-rollback (manual abort only for v2)

## Approach

**Horizontal Slice by Phase** (recommended from exploration):

| Phase | Focus | Deliverables |
|-------|-------|--------------|
| 1 | Foundation | Enum consolidation, LLM abstraction, real agent invocation |
| 2 | Core | Parallel execution, IaC integration, CI/CD orchestration |
| 3 | Advanced | Shift-right/chaos, Skill Hub CLI |

**Key Architectural Decisions:**
- Direct agent invocation in v2; message-passing deferred to v3
- AWS-only for IaC; multi-cloud as future work
- 30-day rolling telemetry retention for v2
- Provider selection via `AgentConfig.provider` field

## Affected Areas

| Area | Impact | Files |
|------|--------|-------|
| `src/orchestrator/` | Modified | `graph.py`, `state.py`, new `agents.py` |
| `src/llm/` | New | `base.py`, `openai.py`, `ollama.py`, `vllm.py`, `llamacpp.py` |
| `src/agents/` | Modified + New | `infrastructure_agent.py`, `chaos_agent.py`, extended `release_analyst.py` |
| `src/infrastructure/` | New | `iac_providers/`, `lab_lifecycle_manager.py`, `cost_controller.py` |
| `src/observability/` | New | `telemetry.py`, `anomaly_detector.py`, `apm/` |
| `src/ci/` | New | `orchestrator.py`, `quality_gate.py`, `quality_webhook.py` |
| `src/github/`, `src/gitlab/` | New | `integration.py` |
| `src/config/` | Modified | new `secrets.py` |
| `src/skill_hub/` | New (refactor) | CLI, registry v2 |
| `src/knowledge/` | Modified | Enhanced with production telemetry |

## Integration Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM Provider Layer                        │
│  (OpenAI / Ollama / vLLM / LlamaCpp)                       │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
   ┌────────────┐      ┌────────────┐      ┌────────────┐
   │  Skill Hub │      │   IaC      │      │ Shift-Right│
   │  (any LLM) │      │ (IaCProv)  │      │  (APM/Tel) │
   └────────────┘      └────────────┘      └────────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
                    ┌─────────────────────┐
                    │  CI/CD Orchestrator │
                    │  (GitHub/GitLab)    │
                    └─────────────────────┘
```

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Graph nodes produce mock data | High | Replace all stub nodes with real agent calls in Phase 1 |
| Provider abstraction complexity | Med | ABC with minimal interface; 1:1 mapping initially |
| IaC provider lock-in | Med | Abstract IaCProvider behind protocol; Terraform-first |
| Chaos experiment cascading failure | Med | Abort triggers with configurable thresholds |
| Concurrent feature scope creep | High | Strict phase gates; defer to v2.1 if needed |

## Rollback Plan

| Change | Rollback Mechanism |
|--------|-------------------|
| LLM provider abstraction | Revert to hardcoded `gemini-1.5-flash`; remove `provider` field |
| Enum consolidation | Restore duplicate enums; mark deprecated module |
| Graph node changes | PostgresCheckpointSaver provides state rollback |
| IaC provisioning | `lab_lifecycle_manager.destroy_all()` cleanup script |
| CI/CD integration | Disable webhooks; revert `release_analyst.py` to read-only |
| Chaos experiments | `ChaosEngineer.abort_all()` via sidecar management |

## Dependencies

- `ollama-support` is foundational → required before shift-right and skill-hub
- `iac-integration` depends on `ollama-support` and `cicd-orchestrator`
- `cicd-orchestrator` depends on `iac-integration` and `shift-right`
- `skill-hub` is orthogonal → can ship independently

## Success Criteria

- [ ] All 8 agents execute real logic (no mock data) via `pytest` validation
- [ ] OllamaProvider passes air-gapped integration tests (no external calls)
- [ ] Parallel execution achieves ≥2x throughput on 4-agent fan-out
- [ ] Single `AgentType` enum with zero duplicates across codebase
- [ ] `InfrastructureAgent` provisions k6 lab in <60 seconds
- [ ] Chaos experiments abort within 30s of threshold breach
- [ ] CI/CD quality gate blocks merge when `regression_score > 0.7`
- [ ] Skill Hub CLI installs community skill from manifest in <30 seconds
- [ ] APM telemetry ingested and queryable within 5 minutes of generation
