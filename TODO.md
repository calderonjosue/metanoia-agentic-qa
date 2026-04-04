# Metanoia-QA: Implementation Tasks

## Project Goal
Build Metanoia-QA to a 10/10 GitHub-ready state with functional code, demo, and polish.

---

## Phase 1: Core Agents & Framework (Priority: CRITICAL)

### 1.1 Context & Regression Analyzer
- **File**: `src/agents/context_analyst.py`
- **Class**: `ContextAnalyst`
- **Responsibilities**:
  - Connect to Supabase pgvector
  - Search historical sprints for similar modules/features
  - Identify flaky tests from history
  - Calculate defect density per module
  - Return risk assessment for new sprint

### 1.2 Strategy Manager
- **File**: `src/agents/strategy_manager.py`
- **Class**: `StrategyManager`
- **Responsibilities**:
  - Receive Context Analyst output
  - Apply ISTQB Defect Clustering
  - Calculate effort distribution (func/regress/perf/security)
  - Generate test plan with priorities
  - Coordinate with Design Lead

### 1.3 Design Lead
- **File**: `src/agents/design_lead.py`
- **Class**: `TestDesignLead`
- **Responsibilities**:
  - Generate test scenarios (happy paths)
  - Infer edge cases using LLM
  - Create synthetic test data
  - Design test environment requirements
  - Output test cases to execution agents

### 1.4 UI Automation Engineer
- **File**: `src/agents/ui_automation.py`
- **Class**: `UIAutomationEngineer`
- **Responsibilities**:
  - Execute Playwright tests
  - Use vision-healing skill on selector failure
  - Generate PR for broken selectors
  - Report pass/fail with screenshots
  - Integrate with skill_runtime

### 1.5 Performance Test Engineer
- **File**: `src/agents/performance.py`
- **Class**: `PerformanceEngineer`
- **Responsibilities**:
  - Identify bottleneck endpoints from code changes
  - Generate k6 load scripts
  - Execute performance tests
  - Analyze results (response time, throughput)
  - Flag performance regressions

### 1.6 Security Test Engineer
- **File**: `src/agents/security.py`
- **Class**: `SecurityEngineer`
- **Responsibilities**:
  - Run OWASP ZAP scans
  - Perform API fuzzing
  - Check for OWASP Top 10 vulnerabilities
  - Generate security report
  - Integrate with skill_runtime (zap-executor)

### 1.7 QA Release Analyst
- **File**: `src/agents/release_analyst.py`
- **Class**: `ReleaseAnalyst`
- **Responsibilities**:
  - Collect results from all execution agents
  - Calculate weighted release score
  - Cross technical errors with business impact
  - Generate release certification report
  - Make go/no-go recommendation

### 1.8 LangGraph Orchestrator
- **File**: `src/orchestrator/graph.py`
- **Classes**: `MetanoiaState`, `MetanoiaGraph`
- **Responsibilities**:
  - Define STLC state machine
  - Connect all 7 agents as graph nodes
  - Implement checkpointing (PostgreSQL)
  - Handle state persistence across restarts
  - Manage parallel execution of Level 2 agents

### 1.9 Knowledge Base (Supabase + pgvector)
- **File**: `src/knowledge/rag.py`
- **File**: `src/knowledge/client.py`
- **Responsibilities**:
  - Supabase client connection
  - RAG queries for historical context
  - Embedding generation (Gemini)
  - `match_historical_testing` function
  - `agent_lessons_learned` management

### 1.10 FastAPI Application
- **File**: `src/api/main.py`
- **File**: `src/api/routes/sprint.py`
- **File**: `src/api/routes/agents.py`
- **File**: `src/api/routes/reports.py`
- **Responsibilities**:
  - `POST /v1/metanoia/sprint/start` - Start quality mission
  - `GET /v1/metanoia/sprint/{id}/status` - Get sprint status
  - `GET /v1/metanoia/sprint/{id}/test-plan` - Get test plan
  - `GET /v1/metanoia/sprint/{id}/certification` - Get certification
  - `GET /v1/metanoia/agents/status` - Agent status
  - Health check endpoint

---

## Phase 2: Demo Infrastructure (Priority: HIGH)

### 2.1 Docker Setup
- **Files**:
  - `examples/e-commerce-demo/docker-compose.yml` (update)
  - `examples/e-commerce-demo/api/Dockerfile`
  - `examples/e-commerce-demo/app/Dockerfile`

### 2.2 Database Schemas
- **Files**:
  - `examples/e-commerce-demo/data/init.sql` - PostgreSQL schema
  - `examples/e-commerce-demo/data/supabase-schema.sql` - pgvector tables

### 2.3 Demo Application
- **Dir**: `examples/e-commerce-demo/app/`
- Simple Next.js e-commerce app for testing

### 2.4 Demo API
- **Dir**: `examples/e-commerce-demo/api/`
- FastAPI app with mock endpoints

---

## Phase 3: Polish (Priority: HIGH)

### 3.1 Requirements File
- **File**: `requirements.txt`
- Include all dependencies with versions

### 3.2 Package Configuration
- **File**: `pyproject.toml` or `setup.py`
- Package metadata, entry points

### 3.3 Environment Template
- **File**: `.env.example`
- All required environment variables

### 3.4 Documentation
- **File**: `docs/API.md` - API reference
- Update existing docs

---

## Phase 4: GitHub Setup (Priority: MEDIUM)

### 4.1 Repository
- Create GitHub repository
- Push code
- Configure topics/tags

### 4.2 GitHub Actions Secrets
- Add required secrets for CI/CD
- Configure protected branches

### 4.3 PyPI Configuration
- Setup trusted publishing
- Add maintainers

---

## Verification Checklist

- [ ] All 7 agents have functional code
- [ ] LangGraph orchestrator compiles and runs
- [ ] FastAPI endpoints are documented
- [ ] Docker compose works end-to-end
- [ ] CI passes (lint, typecheck, test)
- [ ] Demo runs in < 5 minutes
- [ ] README has no placeholder text

---

## 🚀 Phase 5: Post-Launch Features (For 9.5-10/10)

These features elevate Metanoia-QA from good to exceptional.

### 5.1 IDE Plugin (VS Code + Cursor)
- **Impact**: ⭐⭐⭐⭐⭐ | **Effort**: Alto
- **Files**: `extensions/vscode/`, `extensions/cursor/`
- **Features**:
  - Inline test status in editor
  - One-click sprint start
  - Real-time agent monitoring
  - Autocomplete for Metanoia-QA config

### 5.2 Self-Learning System
- **Impact**: ⭐⭐⭐⭐ | **Effort**: Alto
- **File**: `src/agents/self_learning.py`
- **Features**:
  - Track agent mistakes and corrections
  - Build learned patterns database
  - ML model for failure prediction
  - Automatic prompt optimization

### 5.3 Compliance Reports (SOC2, ISO 27001)
- **Impact**: ⭐⭐⭐⭐ | **Effort**: Medio
- **File**: `src/agents/compliance.py`
- **Features**:
  - Pre-built report templates (SOC2, ISO 27001, HIPAA)
  - Automated evidence collection
  - Audit trail generation
  - Compliance score calculation

### 5.4 Collaborative QA (Multi-Team)
- **Impact**: ⭐⭐⭐ | **Effort**: Medio
- **Files**: `src/api/routes/collaboration.py`
- **Features**:
  - Team workspaces
  - Shared test case library
  - Cross-team sprint coordination
  - Unified dashboard for QA managers

---

## 📊 Final Status

| Phase | Status | Progress |
|-------|--------|----------|
| Phase 1: Core Agents | ✅ Complete | 10/10 |
| Phase 2: Demo | ✅ Complete | 4/4 |
| Phase 3: Polish | ✅ Complete | 4/4 |
| Phase 4: GitHub | ⏳ Pending | 0/3 |
| Phase 5.1: IDE Plugin | ✅ Complete | 4/4 |
| Phase 5.2: Self-Learning | ✅ Complete | 4/4 |
| Phase 5.3: Compliance | ✅ Complete | 4/4 |
| Phase 5.4: Collaborative | ✅ Complete | 4/4 |

**Total: 100+ files created**

---

## 🎯 Roadmap

```
v1.0 (Current)          v1.5                 v2.0
    │                      │                    │
    ├── Phase 1-3         ├── Phase 4          ├── Phase 6
    │   ✅ DONE           │   GitHub Setup    │   (TBD)
    │                      │   ⏳ Pending       │
    │                      │                    │
    └── 🚀 READY TO      └── 🎉 LAUNCH        └── ⭐⭐⭐⭐⭐
       PUBLISH               v2.0               10/10
```

---

*Generated: 2026-04-04*
*Project: Metanoia-QA v1.0*
