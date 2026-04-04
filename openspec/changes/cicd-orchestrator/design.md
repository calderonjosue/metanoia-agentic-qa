# Design: Metanoia CI/CD Orchestrator

## Technical Approach

Metanoia-QA becomes the pipeline controller. A new `ci/` module orchestrates the flow: Build → QA Analysis → Quality Score → Quality Gate → [ReleaseAnalyst] → Auto-Merge → Deploy Agent → Environment. ReleaseAnalyst agent gains repository-level permissions to execute merge/deploy actions on behalf of Metanoia-QA.

## Architecture Decisions

### Decision: Agent-Based Orchestration vs Webhook Callbacks

**Choice**: Agent-driven actions (ReleaseAnalyst issues commands to GitHub/GitLab APIs directly)
**Alternatives considered**: Webhook callbacks from CI system, polling-based CI integration
**Rationale**: Agents can make decisions based on quality scores and maintain state across the pipeline. Webhooks are passive and require external coordination. Push-based agents decouple the pipeline from CI infrastructure.

### Decision: Centralized Token Storage in `config/secrets.py`

**Choice**: Shared secrets module handles all token storage/retrieval
**Alternatives considered**: Per-agent token management, external vault integration
**Rationale**: Centralized audit logging for token usage, easier rotation, consistent encryption. Phase 2 could migrate to external vault if needed.

### Decision: 95% Quality Threshold

**Choice**: Fixed threshold with manual override capability
**Alternatives considered**: Configurable per-repo thresholds, ML-adaptive thresholds
**Rationale**: Simple, predictable, aligned with success criteria. Manual override provides escape hatch without complex configuration.

## Data Flow

```
Build System
    │
    ▼
Metanoia-QA (ci/orchestrator.py)
    │
    ├──► Quality Analysis (qa/)
    │         │
    │         ▼
    │    Quality Score
    │         │
    ▼         │
QualityGate ◄┘
    │
    ├──[Pass]──► ReleaseAnalyst ──► GitHub/GitLab API ──► Merge PR
    │                                          │
    │                                          ▼
    │                                   Deploy Agent ──► Deploy
    │
    └──[Fail]──► Block Pipeline + Notify
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `ci/orchestrator.py` | Create | Pipeline orchestration logic, quality gate evaluation |
| `ci/quality_gate.py` | Create | Quality score threshold checking |
| `agents/release_analyst.py` | Modify | Add: token auth methods, `merge_pr()`, `trigger_deploy()` |
| `api/quality_webhook.py` | Create | Endpoint: receive quality scores from build system |
| `api/deploy_trigger.py` | Create | Endpoint: trigger deployment actions |
| `github/integration.py` | Modify | Add: PR merge, status check, review APIs |
| `gitlab/integration.py` | Create | GitLab equivalent of GitHub integration |
| `config/secrets.py` | Modify | Add: token encryption, `get_token()`, `rotate_token()` |
| `config/cicd_config.py` | Create | CI/CD settings: thresholds, environments |

## Interfaces / Contracts

### Quality Gate Result

```python
@dataclass
class QualityGateResult:
    passed: bool
    score: float
    threshold: float = 95.0
    reasons: list[str] = field(default_factory=list)
```

### ReleaseAnalyst Actions

```python
class ReleaseAnalyst:
    def merge_pr(self, pr_url: str, commit_sha: str) -> MergeResult: ...
    def trigger_deploy(self, env: str, artifact: str) -> DeployResult: ...
    def get_token(self, provider: str) -> str: ...
```

### Quality Webhook Payload

```python
@dataclass
class QualityPayload:
    pr_id: str
    repository: str
    score: float
    analysis_output: dict
    build_status: str  # "passed" | "failed"
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | QualityGate threshold logic | Mock scores, assert pass/fail |
| Unit | Token retrieval from secrets | Mock encrypted store |
| Integration | ReleaseAnalyst → GitHub API | Test with recorded responses |
| Integration | Full pipeline flow | End-to-end test with mocked build |
| E2E | Real PR merge scenario | Staged environment only |

## Migration / Rollout

1. Deploy `config/secrets.py` with token storage (no active usage yet)
2. Deploy `github/integration.py` and `gitlab/integration.py` updates
3. Deploy `agents/release_analyst.py` with dry-run mode
4. Enable quality webhook endpoint
5. Enable auto-merge with manual confirmation initially
6. Graduate to fully automatic after validation

## Open Questions

- [ ] Should deployment require separate approval for production environment?
- [ ] What is the retry strategy if merge API call fails?
- [ ] Do we need rate limiting on quality webhook endpoint?
