# Exploration: Metanoia-QA — Autonomous Agentic STLC Framework

## 1. Concept Overview

Metanoia-QA is an **Autonomous Quality System** that reimagines software testing as a hierarchical multi-agent graph orchestrated by LLMs. Unlike traditional automation frameworks (Selenium, pytest, etc.), it treats the entire Software Testing Life Cycle (STLC) as a first-class concern, with each phase managed by specialized agents that collaborate through a shared knowledge base.

**Core Innovation**: Historical Awareness — before planning a new test cycle, the system explores past sprints to predict risks, identify flaky tests, and optimize coverage allocation.

**Reference Inspiration**: agent-teams-lite (Gentleman-Programming) — Spec-Driven Development with AI Sub-Agents, providing the orchestration + skill-based agent pattern that Metanoia-QA extends for QA-specific workflows.

---

## 2. Current State

Metanoia-QA does not exist yet — this is a greenfield project. The concept maps STLC phases to a 3-level agent hierarchy:

### Level 1: Context & Strategy Intelligence
| Agent | STLC Phase | Responsibility |
|-------|------------|----------------|
| El Arqueólogo | Pre-Requirement Analysis | Historical analysis, regression risk prediction, technical debt identification |
| El Estratega | Test Planning | Effort allocation using ISTQB Defect Clustering principles |

### Level 2: Design & Execution (Domain Leads)
| Agent | STLC Phase | Responsibility |
|-------|------------|----------------|
| El Diseñador | Test Design & Environment Setup | Test scenario generation, edge case inference via LLM reasoning, synthetic test data |
| Agente Funcional | Test Execution | Vision-driven Playwright automation with self-healing DOM selectors |
| Agente de Rendimiento | Test Design & Execution | Bottleneck inference, k6/JMeter load script delegation |
| Agente de Seguridad | Dynamic Analysis | DAST, logical fuzzing, OWASP Top 10 prevention |

### Level 3: Closure & Audit
| Agent | STLC Phase | Responsibility |
|-------|------------|----------------|
| El Oráculo | Test Execution Analysis & Closure | Cross-technical-error + business-value-flow impact analysis, Release certification |

---

## 3. Affected Areas

### Core Infrastructure (must be built)
- `src/agents/` — Agent implementations (LangGraph nodes)
- `src/orchestrator/` — Graph orchestration and state management
- `src/knowledge/` — Supabase pgvector integration for historical awareness
- `src/stlc/` — STLC phase state machines

### Execution Engines (integration points)
- `src/executors/playwright/` — Vision-driven UI automation
- `src/executors/k6/` — Performance testing scripts
- `src/executors/zap/` — Security scanning integration

### API & Frontend
- `src/api/` — FastAPI endpoints for agent coordination
- `src/dashboard/` — Next.js + Tremor monitoring UI

### Configuration & Convention
- `openspec/config.yaml` — Already exists with stack metadata
- `.atl/skill-registry.md` — Already references Metanoia-QA stack

---

## 4. Architectural Approaches

### Approach A: Full LangGraph Native (Recommended)
Implement entire multi-agent graph using LangGraph's StateGraph with custom state classes per agent.

```
Pros:
- Native support for cyclic graph execution (agents can loop back)
- Built-in checkpointing for long-running cycles
- Strong typing with Pydantic states
- LangChain ecosystem integration (retrieval, tools, memory)
Cons:
- Steep learning curve for LangGraph's graph construction patterns
- Debugging complex graphs requires specialized tooling
- Performance overhead compared to bare Python
Effort: High (12-16 weeks for MVP)
```

### Approach B: Hybrid LangGraph + Custom Orchestrator
Use LangGraph for agent-level state, but implement custom phase orchestration layer.

```
Pros:
- Flexibility to optimize critical paths
- Easier incremental migration from existing systems
- Clearer separation between agent logic and workflow orchestration
Cons:
- Dual abstraction layers increase maintenance burden
- Risk of re-implementing LangGraph features poorly
- Tighter coupling between custom code and LangGraph internals
Effort: High (14-18 weeks for MVP)
```

### Approach C: Agent Teams Lite Extension
Extend agent-teams-lite's SDD orchestrator with QA-specific skills and agents.

```
Pros:
- Leverages proven orchestration patterns
- Existing skill registry and phase conventions
- Faster initial setup (2-3 weeks)
Cons:
- ATL is deprecated in favor of gentle-ai (maintenance risk)
- QA-specific concerns (test execution, visual healing) not native
- Would require significant extension to support 3-level hierarchy
Effort: Medium (8-12 weeks) but with architectural debt
```

---

## 5. Key Architectural Decisions

### A. Agent Communication Pattern
**Decision**: Use LangGraph's built-in message passing with shared pgvector knowledge base as persistent memory.

**Rationale**: Each agent needs access to historical sprint data (El Arqueólogo's output) and cross-agent context (El Estratega's allocations). A shared vector store enables:
- Semantic retrieval of past test results
- Query-by-example for similar defect patterns
- Accumulated learning across sprints

### B. Visual Self-Healing Strategy
**Decision**: Agente Funcional uses multimodal LLM (Gemini 1.5 Pro Vision) to compare DOM screenshots before/after selector failure.

**Rationale**: Traditional self-healing (re-selectoring by attributes) fails on dynamic apps. Vision-based comparison can detect:
- Layout shifts causing element drift
- Identical elements in new positions
- Semantic changes (same button, different label)

### C. Defect Clustering for Effort Allocation
**Decision**: El Estratega applies ISTQB Defect Clustering principle via LLM reasoning over historical defect data.

**Rationale**: Manual effort allocation (e.g., 70/20/10 for func/reg/performance) is suboptimal. LLM can infer:
- Modules with highest historical defect density → more regression
- Code churn rate in Sprint → performance risk
- API surface changes → security testing priority

### D. Release Certification Logic
**Decision**: El Oráculo generates a weighted decision matrix combining:
- Technical pass rate (weighted by severity)
- Business flow coverage percentage
- Historical flaky test variance
- Security scan findings

**Rationale**: Binary pass/fail masks nuance. A release certification score provides:
- Justifiable go/no-go decision
- Traceable reasoning for stakeholders
- Early warning signals for marginal releases

---

## 6. Integration Points

### With Existing Tools
| Tool | Integration Method | Purpose |
|------|-------------------|---------|
| Supabase | pgvector extension | Historical test data, defect clustering vectors |
| Gemini 1.5 Pro/Flash | Google AI API | Reasoning, vision, code generation |
| Playwright | @playwright/test + custom runner | UI automation with vision healing |
| k6 | k6 JavaScript API | Performance test generation and execution |
| OWASP ZAP | zaproxy Python API | DAST scanning, fuzzing |
| FastAPI | native | Agent coordination API |
| Next.js + Tremor | native | Dashboard visualization |

### With agent-teams-lite/gentle-ai
Metanoia-QA can adopt the SDD workflow for its own development process, using:
- `sdd-init` for project initialization
- `sdd-propose` for feature proposals
- `sdd-design` for architectural decisions
- `sdd-verify` for implementation validation

---

## 7. Complexity & Risks

### Technical Complexity
| Area | Complexity | Mitigation |
|------|------------|------------|
| Multi-agent state synchronization | High | Use LangGraph checkpointing + versioned state transitions |
| Vision-based self-healing latency | Medium | Cache recent DOM states; async healing on failure |
| pgvector query performance | Medium | Pre-compute embeddings on test completion; incremental updates |
| LLM cost at scale | High | Use Flash for planning, Pro for execution; batch similar queries |

### Systemic Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Agent loops (infinite retry cycles) | Medium | High | Define max iteration limits per phase; circuit breakers |
| False positive defect clustering | Low | Medium | Validate LLM allocations against historical accuracy |
| Knowledge base drift (stale embeddings) | Medium | Medium | Implement TTL-based refresh; manual override capability |
| LLM API rate limits during peak | Medium | High | Request queuing; fallback to rule-based defaults |

### Security Considerations
- LLM prompts may contain sensitive test data → implement prompt sanitization
- Knowledge base stores historical defects → access control required
- Agent-generated code (Playwright scripts) → sandboxed execution

---

## 8. Recommended Next Steps

1. **Proof of Concept (4 weeks)**: Implement single Sprint cycle with:
   - El Arqueólogo + El Estratega only
   - Stubbed execution agents
   - Mock knowledge base

2. **Core Infrastructure (8 weeks)**: Build:
   - LangGraph orchestration foundation
   - Supabase schema + pgvector setup
   - FastAPI coordination layer

3. **Execution Agents (6 weeks)**: Implement:
   - Agente Funcional with vision self-healing
   - Basic k6 integration
   - OWASP ZAP wrapper

4. **Dashboard (4 weeks)**: Build:
   - Next.js + Tremor monitoring UI
   - Real-time agent state visualization

---

## 9. Recommendation

**Adopt Approach A (Full LangGraph Native)** with the following rationale:

1. The 3-level agent hierarchy requires cyclic graph execution (Level 2 agents report to Level 3, which can trigger Level 1 re-analysis)
2. LangGraph's checkpointing is essential for long-running Sprint cycles that may span days
3. The typed state system reduces debugging complexity for 8+ agents
4. Historical awareness via pgvector integrates naturally with LangChain's retrieval abstractions

The higher initial effort (12-16 weeks) is justified by architectural coherence. Approach C (ATL extension) would be faster initially but would require fundamental restructuring once visual self-healing and defect clustering are added.

---

## 10. Exploration Status

| Criterion | Status |
|-----------|--------|
| Concept clarified | Yes |
| Reference architecture understood | Yes (agent-teams-lite) |
| Tech stack validated | Yes |
| Integration points identified | Yes |
| Complexity assessed | Yes |
| Risks identified | Yes |
| **Ready for Proposal** | **Yes** |

The orchestrator should proceed to `sdd-propose` with:
- Change name: `metanoia-qa-core`
- Core scope: LangGraph orchestration foundation + 2-agent POC (El Arqueólogo + El Estratega)
- Known constraints: Requires Supabase instance, Gemini API keys, Playwright/k6/ZAP tooling

---

*Artifact saved to: `openspec/changes/metanoia-qa-core/exploration.md`*
*Exploration completed: 2026-04-04*
