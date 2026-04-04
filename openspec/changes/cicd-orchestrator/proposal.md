# Proposal: Metanoia CI/CD Orchestrator

## Intent

Transform Metanoia-QA from a pipeline step into the pipeline controller. Enable agent-driven CI/CD with auto-merge capabilities based on quality thresholds, bidirectional GitHub/GitLab integration, and orchestrated deployments triggered by release decisions.

## Scope

### In Scope
- Metanoia-QA as central pipeline orchestrator (not passive participant)
- ReleaseAnalyst agent with GitHub/GitLab token management for auto-merge
- Quality gate: auto-merge + deploy when score exceeds 95%
- Agent-driven deployment orchestration (push-based, not webhooks)
- Token storage/retrieval for repo operations

### Out of Scope
- Custom CI runner infrastructure
- Multi-cloud deployment targets (Phase 2)
- Rollback automation (separate change)

## Approach

Grant the ReleaseAnalyst agent repository-level permissions (read code, read PRs, merge PRs, comment). Metanoia-QA evaluates code quality post-build, then instructs ReleaseAnalyst to auto-merge if quality score > 95% and all checks pass. Deployment is triggered as an agent action, not a webhook callback.

```
Build → QA Analysis → Quality Score → [ReleaseAnalyst] → Auto-Merge → Deploy Agent → Environment
```

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `agents/release_analyst.py` | Modified | Add token auth, merge PR, quality gate logic |
| `api/` | Modified | New endpoints: quality webhook, deploy trigger |
| `github/integration.py` | Modified | PR review, merge, status check APIs |
| `config/secrets.py` | Modified | Token storage/retrieval for repo access |
| `ci/` | New | Pipeline orchestration logic |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Token exposure | Medium | Encrypted storage, audit logging |
| Auto-merge on false positive | Low | 95% threshold + manual override flag |
| Deployment to wrong env | Low | Explicit env targeting, confirmation gate |

## Rollback Plan

1. Revoke ReleaseAnalyst token from GitHub/GitLab org settings
2. Disable auto-merge via config flag `auto_merge: false`
3. Revert `agents/release_analyst.py` to previous commit
4. Remove deploy webhook endpoints

## Dependencies

- GitHub App or Personal Access Token with `repo` scope
- GitLab Personal Access Token with `api` and `write_repository` scopes

## Success Criteria

- [ ] PR merged automatically when quality score > 95%
- [ ] Deployment triggered post-merge without manual intervention
- [ ] Token rotation without downtime
- [ ] Quality gate prevents merge when score ≤ 95%
