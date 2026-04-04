# Proposal: Metanoia-QA Core Architecture

## Intent

Build the autonomous QA system foundation using LangGraph orchestration with Supabase pgvector for historical awareness. POC validates multi-agent STLC execution with 2-agents before scaling to full 8-agent hierarchy.

## Scope

### In Scope
- LangGraph StateGraph orchestration foundation with checkpointing
- El Arqueólogo agent: Historical analysis, regression risk prediction
- El Estratega agent: Test planning with ISTQB defect clustering
- Supabase schema + pgvector integration for knowledge base
- FastAPI coordination layer
- Basic dashboard stub (Next.js + Tremor)

### Out of Scope
- Execution agents (Agente Funcional, Agente de Rendimiento, Agente de Seguridad)
- Vision-based self-healing DOM selectors
- k6/ZAP integration
- Full 8-agent production deployment

## Approach

**Incremental POC (4 weeks)**:
1. Bootstrap LangGraph project with custom State classes
2. Implement El Arqueólogo → El Estratega graph edges
3. Stub execution agents with mock responses
4. Connect Supabase pgvector for historical retrieval
5. Validate: Generate Test Plan from Sprint scope input

**Tech**: Python 3.12+, LangGraph/LangChain, FastAPI, Gemini 1.5 Flash (planning), Supabase pgvector

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/agents/` | New | El Arqueólogo + El Estratega implementations |
| `src/orchestrator/` | New | LangGraph StateGraph + checkpointing |
| `src/knowledge/` | New | Supabase pgvector client + schema |
| `src/api/` | New | FastAPI endpoints for agent coordination |
| `src/dashboard/` | New | Next.js + Tremor UI stub |
| `tests/` | New | Integration tests for agent graph |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| LLM cost at scale | High | Use Gemini Flash for planning; batch queries |
| Agent loops (infinite retry) | Medium | Max iteration limits per phase; circuit breakers |
| Knowledge base drift | Medium | TTL-based embedding refresh; manual override |
| LangGraph learning curve | Medium | Invest in graph debugging tooling early |

## Rollback Plan

- **Feature flags**: Disable agents individually via `AGENT_ENABLED_*` env vars
- **Container rollback**: Docker image tags for last-known-working state
- **Data rollback**: Supabase point-in-time restore for vector DB
- **Kill switch**: `METANOIA_ENABLED=false` env var halts all agent activity

## Dependencies

- Supabase instance with pgvector extension enabled
- Gemini API keys (Flash for planning, Pro for complex reasoning)
- Python 3.12+, Node.js 20+

## Success Criteria

- [ ] El Arqueólogo returns historical risk analysis for given Sprint scope
- [ ] El Estratega generates Test Plan with effort allocation
- [ ] LangGraph checkpointing survives process restart
- [ ] pgvector query returns relevant historical defects < 500ms
- [ ] FastAPI returns agent coordination response < 30s
- [ ] Integration tests pass for core graph flow
