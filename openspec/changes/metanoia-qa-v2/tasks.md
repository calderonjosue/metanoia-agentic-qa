# Tasks: Metanoia-QA v2.0 — Unified Platform Upgrade

## Phase 0: Verification & Backup

- [x] 0.1 [MODIFY] Run existing test suite: `pytest tests/ --tb=short` — capture baseline
- [x] 0.2 [NEW] Create backup tag: `git tag -a backup-v1.0.0 -m "Pre-v2.0 baseline"`
- [x] 0.3 [NEW] Verify current LLM works: `python -c "from src.llm.gemini import GeminiProvider; print(GeminiProvider().health_check())"`
- [x] 0.4 [MODIFY] Document current `AgentType` enum locations — list all files with enum definitions
- [x] 0.5 [NEW] Create rollback script: `scripts/rollback-v1.sh` with git revert instructions
- [x] 0.6 [NEW] Verify LangGraph checkpoint saver works: `python -c "from langgraph.checkpoint.postgres import PostgresSaver; print('OK')"`

---

## Phase 1: Foundation (LLM Abstraction)

- [x] 1.1 [NEW] Create `src/llm/base.py` — abstract `LLMProvider` ABC with `complete()`, `health_check()`, `supports_functions()` methods
- [x] 1.2 [NEW] Create `src/llm/openai.py` — `OpenAIProvider` implementation
- [x] 1.3 [NEW] Create `src/llm/ollama.py` — `OllamaProvider` with offline detection and model caching
- [x] 1.4 [NEW] Create `src/llm/vllm.py` — `vLLMProvider` implementation
- [x] 1.5 [NEW] Create `src/llm/llamacpp.py` — `LlamaCppProvider` implementation
- [x] 1.6 [NEW] Create `src/llm/registry.py` — provider factory: `get_provider(name: str) -> LLMProvider`
- [x] 1.7 [NEW] Create `src/llm/__init__.py` — export `get_provider`, `LLMProvider`
- [x] 1.8 [MODIFY] Update `src/orchestrator/agents.py` — consolidate duplicate `AgentType` enums into single source
- [x] 1.9 [NEW] Create `tests/llm/test_providers.py` — unit tests for each provider with mocked responses
- [x] 1.10 [ROLLBACK] Tag checkpoint: `git tag phase1-complete`

### Phase 1 Rollback
- [ ] RB1.1 Revert `src/llm/` to empty state: `git checkout HEAD -- src/llm/`
- [ ] RB1.2 Restore original `AgentType` enum from backup tag

### Phase 1 Validation
- [ ] V1.1 Run: `pytest tests/llm/ -v` — all providers pass
- [ ] V1.2 Verify v1.0 agent still works: `pytest tests/agents/test_gemini_agent.py -v`
- [ ] V1.3 Check no new files in `src/agents/` — ensure nothing else broke

---

## Phase 2: Core Features

- [ ] 2.1 [MODIFY] Replace mock agent calls in `src/orchestrator/graph.py` — use real `AgentType` invocation
- [ ] 2.2 [NEW] Implement LangGraph `Send()` fan-out in `src/orchestrator/graph.py` for parallel execution
- [ ] 2.3 [NEW] Create `src/infrastructure/iac_providers/base.py` — abstract `IaCProvider` protocol
- [ ] 2.4 [NEW] Create `src/infrastructure/iac_providers/terraform.py` — Terraform provider implementation
- [ ] 2.5 [NEW] Create `src/infrastructure/lab_lifecycle_manager.py` — provision, teardown, status
- [x] 2.6 [NEW] Create `src/infrastructure/cost_controller.py` — spend watchdog with thresholds
- [x] 2.7 [NEW] Create `src/github/integration.py` — GitHub API client for PR/commit checks
- [x] 2.8 [NEW] Create `src/gitlab/integration.py` — GitLab API client
- [x] 2.9 [NEW] Create `src/ci/orchestrator.py` — CI/CD pipeline orchestration
- [x] 2.10 [NEW] Create `src/ci/quality_gate.py` — quality gate with `regression_score` threshold
- [x] 2.11 [NEW] Create `src/ci/quality_webhook.py` — webhook handler for GitHub/GitLab events
- [ ] 2.12 [NEW] Create `src/config/secrets.py` — secrets management with env var and vault support
- [ ] 2.13 [NEW] Create `tests/infrastructure/test_lifecycle.py` — lab provisioning tests (mocked)
- [ ] 2.14 [NEW] Create `tests/ci/test_quality_gate.py` — quality gate threshold tests
- [ ] 2.15 [ROLLBACK] Tag checkpoint: `git tag phase2-complete`

### Phase 2 Rollback
- [ ] RB2.1 Revert `src/orchestrator/graph.py` to Phase 1 state
- [ ] RB2.2 Remove `src/infrastructure/` directory: `git checkout HEAD -- src/infrastructure/`
- [ ] RB2.3 Remove `src/ci/` directory: `git checkout HEAD -- src/ci/`
- [ ] RB2.4 Restore `src/github/` and `src/gitlab/` if existed before

### Phase 2 Validation
- [ ] V2.1 Run: `pytest tests/llm/ -v` — still pass
- [ ] V2.2 Run: `pytest tests/agents/ -v` — existing agent tests pass
- [ ] V2.3 Run: `pytest tests/infrastructure/ -v` — new tests pass
- [ ] V2.4 Run: `pytest tests/ci/ -v` — new tests pass
- [ ] V2.5 Manual: Verify parallel fan-out works with 4-agent test

---

## Phase 3: Advanced Features

- [ ] 3.1 [NEW] Create `src/skill_hub/` — refactor from `src/skill_runtime/`
- [ ] 3.2 [NEW] Create `src/skill_hub/cli.py` — CLI with `install`, `list`, `search`, `publish` commands
- [ ] 3.3 [NEW] Create `src/skill_hub/registry.py` — community skill manifest v2 registry
- [ ] 3.4 [NEW] Create `src/skill_hub/manifest.py` — manifest schema v2 validation
- [ ] 3.5 [NEW] Create `src/observability/telemetry.py` — telemetry ingestion with 30-day retention
- [ ] 3.6 [NEW] Create `src/observability/anomaly_detector.py` — APM anomaly detection
- [ ] 3.7 [NEW] Create `src/observability/apm/datadog.py` — Datadog APM client
- [ ] 3.8 [NEW] Create `src/observability/apm/newrelic.py` — New Relic APM client
- [ ] 3.9 [NEW] Create `src/observability/apm/opentelemetry.py` — OpenTelemetry exporter
- [ ] 3.10 [NEW] Create `src/agents/chaos_agent.py` — `ChaosAgent` implementation
- [ ] 3.11 [NEW] Create `src/agents/chaos_engineer.py` — `ChaosEngineer` with abort triggers
- [ ] 3.12 [NEW] Create `src/chaos/experiments.py` — declarative experiment definitions
- [ ] 3.13 [NEW] Create `src/chaos/abort_controller.py` — cascade failure detection and abort
- [ ] 3.14 [NEW] Create `tests/skill_hub/test_cli.py` — CLI command tests
- [ ] 3.15 [NEW] Create `tests/observability/test_telemetry.py` — telemetry ingestion tests
- [ ] 3.16 [NEW] Create `tests/chaos/test_abort.py` — chaos abort trigger tests
- [ ] 3.17 [NEW] Create `tests/integration/test_shift_right.py` — end-to-end shift-right test
- [ ] 3.18 [ROLLBACK] Tag checkpoint: `git tag phase3-complete`

### Phase 3 Rollback
- [ ] RB3.1 Remove `src/skill_hub/` directory: `git checkout HEAD -- src/skill_hub/`
- [ ] RB3.2 Remove `src/observability/` directory
- [ ] RB3.3 Remove `src/agents/chaos_agent.py` and `src/agents/chaos_engineer.py`
- [ ] RB3.4 Remove `src/chaos/` directory
- [ ] RB3.5 Restore `src/skill_runtime/` if it existed

### Phase 3 Validation
- [ ] V3.1 Run: `pytest tests/ -v` — full suite passes
- [ ] V3.2 Test skill-hub install: `python -m src.skill_hub.cli install test-skill --dry-run`
- [ ] V3.3 Test chaos abort: `pytest tests/chaos/test_abort.py -v`
- [ ] V3.4 Verify APM clients initialize without errors: `python -c "from src.observability.apm import DatadogAPM; print('OK')"`
- [ ] V3.5 Verify `src/orchestrator/graph.py` parallel execution ≥2x throughput

---

## Phase 4: Final Verification

- [ ] 4.1 [MODIFY] Run full test suite: `pytest tests/ --tb=short -q`
- [ ] 4.2 [NEW] Run integration tests: `pytest tests/integration/ -v`
- [ ] 4.3 [MODIFY] Verify all 8 agents execute real logic: `pytest tests/agents/ -k "real"`
- [ ] 4.4 [NEW] Verify OllamaProvider air-gapped: `python -c "from src.llm.ollama import OllamaProvider; print(OllamaProvider().is_offline())"`
- [ ] 4.5 [NEW] Create v2.0 release tag: `git tag -a v2.0.0 -m "Metanoia-QA v2.0.0"`
- [ ] 4.6 [NEW] Update CHANGELOG.md with v2.0 changes

### Phase 4 Rollback
- [ ] RB4.1 `git checkout backup-v1.0.0 -- .`
- [ ] RB4.2 Verify restored: `python -c "from src.llm.gemini import GeminiProvider; print(GeminiProvider().health_check())"`

---

## Task Summary

| Phase | Tasks | Focus |
|-------|-------|-------|
| Phase 0 | 6 | Verification & Backup |
| Phase 1 | 10 | Foundation (LLM Abstraction) |
| Phase 2 | 17 | Core Features |
| Phase 3 | 18 | Advanced Features |
| Phase 4 | 6 | Final Verification |
| **Total** | **57** | |

## Implementation Order

1. **Phase 0 first** — establish baseline and backup before any changes
2. **Phase 1 before all others** — LLM abstraction is the foundation everything else depends on
3. **Phase 2 builds on Phase 1** — graph changes and IaC require working LLM providers
4. **Phase 3 independent but last** — chaos, observability, and skill-hub ship last
5. **Phase 4 gates release** — full validation before tagging v2.0.0

## Notes

- All rollback tasks assume git tags are created at each phase boundary
- Provider abstraction in Phase 1 enables parallel development in later phases
- `ollama-support` is foundational — required before shift-right and skill-hub
- `iac-integration` depends on `ollama-support` and `cicd-orchestrator`
- `skill-hub` is orthogonal — can ship independently after Phase 1
