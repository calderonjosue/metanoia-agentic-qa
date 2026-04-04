# Metanoia-QA v2.0 Specification

## Purpose

Define requirements for Metanoia-QA v2.0 platform upgrade while **guaranteeing all v1.0 APIs remain functional**.

## Backward Compatibility Guarantee

**All existing v1.0 APIs, interfaces, and behaviors MUST remain operational after v2.0 deployment.** The v2.0 release is additive-only except where explicitly documented in the Compatibility Matrix.

## Compatibility Matrix

| Component | v1.0 Behavior | v2.0 Change | Breaking? |
|-----------|--------------|-------------|-----------|
| `AgentType` enum | Duplicated across modules | Consolidated single enum | **Non-breaking** — old references auto-resolve via alias |
| `gemini-1.5-flash` hardcode | Default provider | Configurable via `AgentConfig.provider` | **Non-breaking** — default remains `gemini` if unspecified |
| Mock agent invocations | Returns stub data | Real agent execution | **Non-breaking** — output format unchanged |
| `src/llm/` module | Non-existent | New provider abstraction | **Non-breaking** — no v1.0 dependencies |
| `src/agents/` interface | `ReleaseAnalyst`, `CodeReviewer`, `TestDesigner` | + `InfrastructureAgent`, `ChaosAgent` | **Non-breaking** — existing agents unchanged |
| `src/skill_runtime/` | Proprietary skill runtime | Refactored to `src/skill_hub/` | **Non-breaking** — imports alias to new location |
| Graph checkpointing | `PostgresCheckpointSaver` | Unchanged | **Non-breaking** |

**Summary**: Zero breaking changes to v1.0 APIs. All modifications are additive or refactor-only.

---

## Requirements

### REQ-001: LLM Provider Abstraction

**The system MUST provide a provider-agnostic LLM interface that supports OpenAI, Ollama, vLLM, and LlamaCpp.**

The system SHALL default to `gemini` provider for backward compatibility when `AgentConfig.provider` is unspecified.

#### Scenario: Default gemini provider (backward compatible)

- GIVEN a v1.0 agent configuration with no explicit provider
- WHEN the agent executes
- THEN the system SHALL use `gemini-1.5-flash` as the provider
- AND the response format SHALL match v1.0 behavior exactly

#### Scenario: Explicit Ollama provider in air-gapped environment

- GIVEN `AgentConfig(provider="ollama", model="llama3")`
- WHEN network is unavailable
- THEN `OllamaProvider` SHALL use cached model weights
- AND return responses without external network calls

#### Scenario: OpenAI provider with API key

- GIVEN `AgentConfig(provider="openai", model="gpt-4")` and valid `OPENAI_API_KEY`
- WHEN agent executes
- THEN `OpenAIProvider` SHALL forward requests to OpenAI endpoint
- AND return responses in standard JSON format

---

### REQ-002: Agent Enum Consolidation

**The system MUST consolidate duplicate `AgentType` enums into a single canonical enum in `src/orchestrator/agents.py`.**

Duplicate enums in other modules SHALL be deprecated and reference the canonical enum via alias.

#### Scenario: Legacy enum import still works

- GIVEN code imports `AgentType` from a deprecated module location
- WHEN the import is resolved
- THEN the system SHALL return the canonical `AgentType` enum
- AND no `AttributeError` SHALL be raised

#### Scenario: New canonical enum usage

- GIVEN code imports `AgentType` from `src/orchestrator/agents.py`
- WHEN accessing enum members
- THEN all v1.0 enum values SHALL be present
- AND new v2.0 values SHALL be appended without conflict

---

### REQ-003: Real Agent Invocation

**The system MUST replace all mock/stub agent invocations with real agent execution.**

Mock data paths SHALL produce a deprecation warning but SHALL NOT error.

#### Scenario: Mock path triggers warning

- GIVEN a graph node previously marked as mock
- WHEN executed in v2.0
- THEN the system SHALL log `DeprecationWarning: Mock agent path deprecated`
- AND execute real agent logic instead
- AND return result in same format as v1.0 mock

---

### REQ-004: Parallel Execution Fan-out

**The system MUST implement LangGraph `Send()` parallel execution for multi-agent fan-out.**

Sequential execution SHALL remain the default; parallel mode SHALL be opt-in via `ExecutionConfig(parallel=True)`.

#### Scenario: Sequential default (backward compatible)

- GIVEN `ExecutionConfig()` with no parallel flag
- WHEN graph executes with multiple agents
- THEN agents SHALL execute sequentially
- AND output order SHALL match v1.0 behavior

#### Scenario: Parallel execution opt-in

- GIVEN `ExecutionConfig(parallel=True, max_concurrency=4)`
- WHEN graph executes
- THEN agents SHALL execute in parallel up to 4 concurrent
- AND all results SHALL be collected before proceeding

---

### REQ-005: Skill Hub CLI

**The system MUST provide a `skill-hub` CLI with `install`, `list`, `search`, and `publish` commands.**

The `src/skill_runtime/` module SHALL be refactored to `src/skill_hub/` with backward-compatible aliases.

#### Scenario: Skill install

- GIVEN a valid community skill manifest v2
- WHEN user runs `skill-hub install community/skill-name`
- THEN the skill SHALL be downloaded and installed
- AND `skill-hub list` SHALL display the newly installed skill

#### Scenario: Legacy import path

- GIVEN code imports from `src.skill_runtime`
- WHEN the import is resolved
- THEN the system SHALL alias to `src.skill_hub`
- AND no `ModuleNotFoundError` SHALL be raised

---

### REQ-006: Ollama Air-Gapped Support

**The system MUST support full Ollama operation without external network access.**

#### Scenario: Air-gapped model cache hit

- GIVEN `OllamaProvider` with `model="llama3"` previously cached
- WHEN executed with no network connectivity
- THEN the provider SHALL load from local cache
- AND complete inference without network calls
- AND return valid response

#### Scenario: Air-gapped cache miss

- GIVEN `OllamaProvider` with `model="llama3"` NOT cached
- WHEN executed with no network connectivity
- THEN the provider SHALL raise `ModelCacheError`
- AND the error message SHALL indicate offline unavailability

---

### REQ-007: IaC Integration

**The system MUST provide `InfrastructureAgent` for k6 lab provisioning with Terraform.**

Lab lifecycle management SHALL include auto-teardown and cost control.

#### Scenario: k6 lab provisioning

- GIVEN valid cloud credentials and `InfrastructureAgent`
- WHEN `agent.provision_lab(framework="k6")` is called
- THEN the system SHALL provision lab infrastructure
- AND complete within 60 seconds
- AND return lab connection details

#### Scenario: Lab auto-teardown

- GIVEN a running lab with `auto_teardown_minutes=30`
- WHEN 30 minutes elapse without activity
- THEN the system SHALL call `lab_lifecycle_manager.destroy_all()`
- AND release all associated resources

---

### REQ-008: Shift-Right / Chaos Engineering

**The system MUST provide `ChaosAgent` and `ChaosEngineer` for declarative chaos experiments.**

Experiments MUST support configurable abort triggers on cascading failure detection.

#### Scenario: Chaos experiment with abort trigger

- GIVEN a chaos experiment definition with `abort_on_error_rate > 0.5`
- WHEN error rate exceeds 50%
- THEN the system SHALL call `ChaosEngineer.abort_experiment()`
- AND the experiment SHALL terminate within 30 seconds
- AND a report SHALL be generated

---

### REQ-009: CI/CD Orchestrator

**The system MUST provide quality gates that block merge when `regression_score > 0.7`.**

#### Scenario: Quality gate pass

- GIVEN `regression_score = 0.5`
- WHEN quality gate evaluates
- THEN the gate SHALL pass
- AND the PR SHALL be eligible for merge

#### Scenario: Quality gate block

- GIVEN `regression_score = 0.75`
- WHEN quality gate evaluates
- THEN the gate SHALL fail
- AND the PR SHALL be blocked from merge
- AND GitHub/GitLab status check SHALL report failure

---

### REQ-010: APM Telemetry Integration

**The system MUST ingest APM telemetry (Datadog, New Relic, OpenTelemetry) and make it queryable within 5 minutes.**

#### Scenario: OpenTelemetry ingestion

- GIVEN OpenTelemetry-compatible instrumented application
- WHEN telemetry is emitted
- THEN the observability layer SHALL ingest spans
- AND they SHALL be queryable within 5 minutes

---

## Testing Requirements

| ID | Requirement | Test Type | Pass Criteria |
|----|-------------|-----------|---------------|
| TEST-001 | v1.0 API backward compatibility | Regression suite | All existing tests pass without modification |
| TEST-002 | Default gemini provider | Unit | `AgentConfig()` defaults to `gemini` |
| TEST-003 | Ollama air-gapped cache hit | Integration | Response returned with network disabled |
| TEST-004 | Parallel execution throughput | Performance | ≥2x throughput vs sequential on 4-agent fan-out |
| TEST-005 | Enum consolidation alias | Unit | Old import paths resolve without error |
| TEST-006 | Quality gate threshold | Integration | Merge blocked at `regression_score=0.71` |
| TEST-007 | Chaos abort trigger timing | Integration | Experiment abort within 30s of threshold breach |
| TEST-008 | Skill Hub install | CLI integration | Community skill installs and lists in <30s |

---

## v1.0 API Contract (Must Not Break)

| API | File | Constraint |
|-----|------|------------|
| `AgentType` enum values | Any | MUST remain accessible |
| `ReleaseAnalyst.execute()` | `src/agents/release_analyst.py` | MUST return same schema |
| `CodeReviewer.execute()` | `src/agents/code_reviewer.py` | MUST return same schema |
| `TestDesigner.execute()` | `src/agents/test_designer.py` | MUST return same schema |
| `graph.execute()` | `src/orchestrator/graph.py` | MUST accept same signature |
| `PostgresCheckpointSaver` | `src/orchestrator/checkpoint.py` | MUST remain functional |

---

## Success Criteria

- [ ] All v1.0 regression tests pass without modification
- [ ] Zero breaking changes to documented APIs
- [ ] `AgentConfig(provider=None)` defaults to `gemini-1.5-flash`
- [ ] Ollama air-gapped tests pass with network disabled
- [ ] Parallel execution achieves ≥2x throughput improvement
- [ ] Quality gate blocks merge at `regression_score > 0.7`
