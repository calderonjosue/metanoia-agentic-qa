# Tasks: Metanoia CI/CD Orchestrator

## Phase 1: Infrastructure

- [ ] 1.1 Create `config/secrets.py` - Add `SecretsManager` class with encrypted token storage and `get_token()`, `rotate_token()` methods
- [ ] 1.2 Create `config/cicd_config.py` - Add `CICDConfig` with threshold settings, environment definitions, `auto_merge` flag
- [ ] 1.3 Create `ci/quality_gate.py` - Add `QualityGate` class with `evaluate(score, threshold)` returning `QualityGateResult`

## Phase 2: Core Implementation

- [ ] 2.1 Create `ci/orchestrator.py` - Add `PipelineOrchestrator` class with `run_quality_gate()`, `execute_merge()`, `trigger_deployment()` methods
- [ ] 2.2 Modify `agents/release_analyst.py` - Add token auth methods, `merge_pr()`, `trigger_deploy()`, `get_token()` methods
- [ ] 2.3 Create `github/integration.py` methods - Add `merge_pull_request()`, `get_pr_status()`, `post_comment()` to existing integration module
- [ ] 2.4 Create `gitlab/integration.py` - Add GitLab-specific PR merge, status, and comment methods

## Phase 3: API Layer

- [ ] 3.1 Create `api/quality_webhook.py` - Add POST endpoint `/webhook/quality` accepting `QualityPayload`, forwarding to orchestrator
- [ ] 3.2 Create `api/deploy_trigger.py` - Add POST endpoint `/deploy/trigger` accepting deploy requests, calling ReleaseAnalyst
- [ ] 3.3 Register new endpoints in API router

## Phase 4: Testing

- [ ] 4.1 Write unit tests for `QualityGate.evaluate()` - Test scores 95+, 94, exactly 95
- [ ] 4.2 Write unit tests for `SecretsManager.get_token()` - Test encrypted retrieval
- [ ] 4.3 Write integration tests for `ReleaseAnalyst.merge_pr()` - Mock GitHub API
- [ ] 4.4 Write integration tests for full pipeline flow - Mock quality webhook → orchestrator → merge
- [ ] 4.5 Add scenario tests: auto-merge blocked when score ≤ 94%, allowed when score ≥ 95%

## Phase 5: Validation

- [ ] 5.1 Validate token storage/retrieval works with real credentials (staging)
- [ ] 5.2 Validate quality gate blocks merge at 94% score
- [ ] 5.3 Validate auto-merge succeeds at 96% score
- [ ] 5.4 Validate deployment triggers after merge
