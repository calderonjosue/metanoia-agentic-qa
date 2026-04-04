# Exploration: Metanoia-QA v2 — Strategic Upgrade Analysis

## Current State

### Architecture Overview

Metanoia-QA v1.0.0 is a mature, production-ready autonomous QA framework built with:

| Component | Technology | Status |
|-----------|------------|--------|
| Core Runtime | Python 3.12+ | Stable |
| Orchestration | LangGraph 0.0.20 | Stable |
| API Layer | FastAPI 0.109+ | Stable |
| LLM Backend | Google Gemini 1.5 Pro/Flash | Stable |
| Knowledge Base | Supabase pgvector | Stable |
| Testing | Playwright, k6, OWASP ZAP | Stable |
| Compliance | SOC2, ISO27001 Templates | Stable |
| Extensions | MCP (Cursor, VS Code) | Stable |

### Existing Agent Architecture

The system implements 8 corporate agents via LangGraph nodes:

```
INIT → CONTEXT_ANALYST → STRATEGY_MANAGER → DESIGN_LEAD
                                              ↓
                                    ┌─────────┴─────────┐
                                    ↓                   ↓
                            UI_AUTOMATION          PERFORMANCE
                                    ↓                   ↓
                            INTEGRATION            SECURITY
                                    └─────────┬─────────┘
                                              ↓
                                    RELEASE_ANALYST → CLOSE
```

**Key Files:**
- `/src/orchestrator/graph.py` — LangGraph state machine (621 lines)
- `/src/orchestrator/state.py` — Pydantic state models (194 lines)
- `/src/agents/base.py` — Abstract base agent class (151 lines)
- `/src/agents/strategy_manager.py` — ISTQB-based test planning (547 lines)
- `/src/agents/context_analyst.py` — Historical RAG analysis (493 lines)

---

## 1. Architecture Strengths

### 1.1 Well-Separated Agent Responsibilities
Each agent has a clear corporate role and单一 responsibility:
- `ContextAnalyst` — Historical pattern mining via pgvector
- `StrategyManager` — ISTQB Defect Clustering-based planning
- `DesignLead` — Test case generation
- `UIAutomation`, `Performance`, `Security`, `Integration` — Execution specialists
- `ReleaseAnalyst` — Certification gate

### 1.2 Mature Skill System
- `/src/skill_runtime/loader.py` — Dynamic skill discovery and loading
- `/src/skill_runtime/registry.py` — Centralized skill registry with metadata
- Extensible via `SKILL.md` + `executor.py` pattern
- Already supports skill versioning and triggers

### 1.3 Comprehensive Knowledge Layer
- `MetanoiaRAG` — Vector similarity search over historical sprints
- `AgentLessonsLearned` — Agent experience capture and retrieval
- `FailurePredictor` — ML-based failure probability estimation
- Evidence collection for SOC2/ISO27001 compliance

### 1.4 Strong Observability Foundation
- Checkpointing via `PostgresCheckpointSaver`
- LangGraph debug mode support
- Structured logging throughout
- Health check endpoints

### 1.5 CI/CD Integration Ready
- GitHub Actions workflows (release.yml, ci.yml)
- Docker containerization
- 181 tests with pytest

---

## 2. Technical Debt

### 2.1 Hardcoded LLM Provider
**Location:** `src/agents/base.py`, `src/knowledge/rag.py`

The system has `gemini-1.5-flash` hardcoded as the default model:
```python
# src/agents/base.py:51
model: str = "gemini-1.5-flash"
```

**Impact:** Cannot operate in air-gapped environments. This is addressed by `ollama-support` proposal but not yet implemented.

### 2.2 Dual AgentType Enums
**Location:** 
- `/src/orchestrator/state.py:13` — `AgentType` enum (8 agents)
- `/src/agents/base.py:16` — Duplicate `AgentType` enum (8 agents)

**Impact:** Potential sync issues. Both define the same agents but in different modules.

### 2.3 Incomplete LangGraph Implementation
**Location:** `/src/orchestrator/graph.py`

The `_parallel_execution_node` method is stubbed:
```python
def _parallel_execution_node(self, state: MetanoiaState) -> dict[str, Any]:
    """Execute all test agents in parallel.
    This node fans out to multiple agents that run concurrently.
    In a real implementation, this would use Send() for parallel execution.
    """
```

**Impact:** Execution phase doesn't actually run agents in parallel despite the architecture diagram showing parallel branches.

### 2.4 Mock Data in Graph Nodes
**Location:** `/src/orchestrator/graph.py:218-325`

All agent nodes return hardcoded mock data rather than invoking actual agents:
```python
def context_analyst_node(state: MetanoiaState) -> dict[str, Any]:
    context = {
        "historical_risks": ["legacy_auth_issues", "api_versioning_deprecations"],
        "regression_score": 0.45,
        ...
    }
```

**Impact:** The graph runs but doesn't actually use the agent implementations.

### 2.5 Incomplete MCP Server
**Location:** `/src/mcp_server/server.py`

MCP server references `skill_runtime.registry.SkillRegistry` but import path may not resolve:
```python
from skill_runtime.registry import SkillRegistry  # Likely needs src. prefix
```

### 2.6 No IaC Infrastructure
**Location:** `/src/agents/infrastructure_agent.py` — Does not exist

The `iac-integration` proposal requires new infrastructure but no code exists yet.

### 2.7 No Chaos Engineering Components
**Location:** `/observability/` — Does not exist

The `shift-right` proposal requires APM clients, telemetry pipeline, and ChaosAgent but no code exists.

### 2.8 CI/CD Orchestrator Incomplete
**Location:** `/ci/`, `/github/integration.py` — Do not exist

The `cicd-orchestrator` proposal requires token storage, GitHub/GitLab integration, and quality gate logic.

---

## 3. Integration Points Between Features

### 3.1 Skill Hub → All Agents
**Integration:** Skills are loaded via `SkillLoader` and executed by agents.

```
skills/ → SkillLoader.discover_skills() → SkillRegistry → AgentConfig
```

**Key files:**
- `src/skill_runtime/loader.py`
- `src/skill_runtime/registry.py`
- `src/agents/base.py:AgentConfig`

### 3.2 Ollama Support → All Agents
**Integration:** Provider abstraction allows swapping LLM backends.

```
LLMProvider (abstract)
    ├── OpenAIProvider (existing)
    ├── OllamaProvider (proposed)
    ├── VLLMProvider (proposed)
    └── LlamaCppProvider (proposed)

AgentConfig.provider → LLMProvider.chat()
```

**Key files:**
- `src/agents/base.py:AgentConfig` (needs `provider` field)
- `src/llm/` (needs creation)

### 3.3 IaC Integration → StrategyManager
**Integration:** StrategyManager triggers InfrastructureAgent for concurrency testing.

```
StrategyManager._calculate_effort_distribution()
    → detects high concurrency requirement
    → invokes InfrastructureAgent
    → InfrastructureAgent provisions lab
    → k6 executes against lab
    → LabLifecycleManager destroys lab
```

**Key files:**
- `src/agents/strategy_manager.py` (needs `invoke_infrastructure_agent()`)
- `src/infrastructure/` (needs creation)

### 3.4 Shift-Right → ContextAnalyst + ReleaseAnalyst
**Integration:** APM telemetry flows into historical analysis; chaos experiments validate in production.

```
APM Vendors (Datadog/New Relic/OTel)
    → Telemetry Pipeline
    → ContextAnalyst.analyze() [enhanced with production data]
    → ML Anomaly Detection
    → ChaosEngineer plans experiments
    → ChaosAgent executes in sidecar
    → ReleaseAnalyst uses production feedback
```

**Key files:**
- `src/agents/context_analyst.py` (needs APM integration)
- `src/ml/failure_predictor.py` (needs chaos validation)
- `observability/` (needs creation)

### 3.5 CI/CD Orchestrator → ReleaseAnalyst
**Integration:** ReleaseAnalyst gains repo permissions for auto-merge.

```
CI/CD Pipeline → Quality Webhook → QualityGate
    → ReleaseAnalyst.merge_pr()
    → ReleaseAnalyst.trigger_deploy()
```

**Key files:**
- `src/agents/release_analyst.py` (needs token auth, merge/deploy methods)
- `ci/` (needs creation)
- `config/secrets.py` (needs creation)

### 3.6 Skill Hub ↔ Ollama Support
**Integration:** Community skills may require specific LLM providers.

```
SkillHub installs community skill
    → Skill manifest may specify LLM provider requirement
    → If ollama-required skill: verify OllamaProvider available
    → Agent uses appropriate provider
```

---

## 4. Common Infrastructure Needed

### 4.1 LLM Provider Abstraction Layer
**Location:** `/src/llm/` (new)

Required by: `ollama-support`, `skill-hub` (community skills may need specific providers)

```
src/llm/
├── __init__.py          # get_provider() factory
├── base.py              # LLMProvider ABC
├── openai.py            # Refactored from existing
├── ollama.py            # NEW
├── vllm.py              # NEW
└── llamacpp.py          # NEW
```

### 4.2 Secrets Management
**Location:** `/src/config/secrets.py` (new)

Required by: `cicd-orchestrator`, `iac-integration`

```
src/config/
└── secrets.py           # Encrypted token storage, rotation
```

### 4.3 Infrastructure Abstraction
**Location:** `/src/infrastructure/` (new)

Required by: `iac-integration`

```
src/infrastructure/
├── __init__.py
├── iac_providers/
│   ├── base.py          # IaCProvider ABC
│   ├── terraform_provider.py
│   └── pulumi_provider.py
├── lab_lifecycle_manager.py
├── cost_controller.py
└── watchdog.py
```

### 4.4 Observability Pipeline
**Location:** `/src/observability/` (new)

Required by: `shift-right`

```
src/observability/
├── __init__.py
├── telemetry.py         # OpenTelemetry wrapper
├── anomaly_detector.py # ML-based anomaly detection
└── apm/
    ├── __init__.py
    ├── base.py          # APMClient protocol
    ├── datadog.py
    └── newrelic.py
```

### 4.5 CI/CD Orchestration
**Location:** `/src/ci/` (new)

Required by: `cicd-orchestrator`

```
src/ci/
├── __init__.py
├── orchestrator.py      # Pipeline orchestration
├── quality_gate.py      # Threshold evaluation
└── quality_webhook.py   # Build system integration
```

### 4.6 GitHub/GitLab Integration
**Location:** `/src/github/`, `/src/gitlab/` (new)

Required by: `cicd-orchestrator`

```
src/github/
└── integration.py       # PR merge, deploy triggers

src/gitlab/
└── integration.py       # GitLab equivalent
```

### 4.7 Chaos Engineering
**Location:** `/src/agents/chaos/` (new)

Required by: `shift-right`

```
src/agents/chaos/
├── __init__.py
├── chaos_agent.py       # Sidecar agent
├── chaos_engineer.py    # Central orchestrator
└── experiment.py        # Declarative experiment definitions
```

---

## 5. Risks and Dependencies

### 5.1 High-Priority Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **LLM Provider Lock-in** | High | Air-gapped customers cannot use system | Prioritize `ollama-support` implementation |
| **Graph Nodes Not Executing Real Agents** | High | System runs but produces dummy data | Implement actual agent invocations in graph |
| **Parallel Execution Not Implemented** | Medium | Performance bottleneck as complexity grows | Use LangGraph Send() API for fan-out |
| **Duplicate AgentType Enums** | Medium | Maintenance burden, potential bugs | Consolidate into single enum in shared module |

### 5.2 Feature Dependencies

```
ollama-support (foundation)
├── ↓ enables skill-hub (community skills may need local LLM)
└── ↓ enables shift-right (ML models need local inference)

iac-integration
├── ↓ depends on ollama-support (no-op if air-gapped IaC)
└── ↓ depends on cicd-orchestrator (lab provisioning for CI)

shift-right
├── ↓ depends on ollama-support (anomaly detection ML)
└── ↓ depends on cicd-orchestrator (production feedback loop)

cicd-orchestrator
├── ↓ depends on iac-integration (lab environment for testing)
└── ↓ depends on shift-right (production telemetry)

skill-hub
└── ↓ orthogonal — works with any provider
```

### 5.3 Recommended Implementation Order

1. **Phase 1: Foundation**
   - Fix dual enum issue (consolidate to shared module)
   - Implement actual agent invocations in graph nodes
   - Implement LLM provider abstraction (`ollama-support`)

2. **Phase 2: Core Enhancements**
   - Implement parallel execution in LangGraph
   - Add `iac-integration` (InfrastructureAgent)
   - Add CI/CD orchestration (`cicd-orchestrator`)

3. **Phase 3: Advanced Capabilities**
   - Add `shift-right` (chaos engineering, APM)
   - `skill-hub` (can be implemented anytime as orthogonal)

### 5.4 Open Questions

| Question | Impact | Recommendation |
|----------|--------|----------------|
| Should graph nodes directly invoke agent classes or use message passing? | Architectural | Use direct invocation for v2; message passing for v3 scale |
| Does InfrastructureAgent need multi-cloud support beyond AWS? | Scope | AWS-only for v2; GCP/Azure as future work |
| Should chaos experiments auto-rollback on cascading failure? | Safety | Yes — implement abort triggers |
| What is the retention policy for APM telemetry data? | Compliance/Cost | 30 days rolling for v2 |
| Should skill-hub support featured/official skills distinction? | Business | Add later; not v2 scope |

---

## Affected Areas Summary

| Area | Files | Changes Needed |
|------|-------|----------------|
| **Orchestration** | `src/orchestrator/graph.py`, `src/orchestrator/state.py` | Fix mock data, implement parallel execution |
| **LLM Layer** | `src/llm/` (new), `src/agents/base.py` | Create provider abstraction, inject provider |
| **Agents** | `src/agents/*.py` | Add InfrastructureAgent, ChaosAgent, extend ReleaseAnalyst |
| **Infrastructure** | `src/infrastructure/` (new) | IaC providers, lab lifecycle, cost control |
| **Observability** | `src/observability/` (new) | APM clients, telemetry, anomaly detection |
| **CI/CD** | `src/ci/` (new), `src/github/`, `src/gitlab/` | Orchestration, quality gate, integration |
| **Secrets** | `src/config/secrets.py` (new) | Encrypted token storage |
| **Skills** | `src/skill_runtime/` | Hub CLI, community skill support |
| **Knowledge** | `src/knowledge/rag.py`, `src/ml/` | Enhanced with production telemetry |

---

## Approaches

### Approach A: Incremental Enhancement (Recommended)
- **Pros:** Lower risk, each feature is independent, easier to validate
- **Cons:** Technical debt accumulates if foundational issues aren't fixed first
- **Effort:** ~6 months for all 5 features

### Approach B: Big Bang Redesign
- **Pros:** Clean slate, all pieces designed together
- **Cons:** High risk, long time to value, breaks existing functionality
- **Effort:** ~12 months

### Approach C: Horizontal Slice by Layer
- **Pros:** Stable foundation, clear milestones, parallel team work
- **Cons:** Requires careful coordination between teams
- **Effort:** ~8 months

---

## Recommendation

**Approach A (Incremental Enhancement)** with Phase 1 focusing on:
1. Consolidating duplicate enums
2. Implementing LLM provider abstraction
3. Fixing graph nodes to invoke real agents

This establishes a solid foundation before building advanced features. Each subsequent phase (IaC, CI/CD, Shift-Right, Skill Hub) builds on this foundation with clear dependencies.

---

## Ready for Proposal

**Yes** — The codebase is well-understood. Key integration points are documented. Risks have been identified with mitigations. The 5 existing proposals (skill-hub, shift-right, iac-integration, ollama-support, cicd-orchestrator) provide detailed requirements for each feature.

**Next Step:** Proceed to sdd-propose to formalize scope and approach for v2 release.
