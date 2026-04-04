# Design: Shift-Right Testing / Chaos Engineering

## Technical Approach

Deploy lightweight ChaosAgents alongside existing services that receive injection instructions from a central ChaosEngineer. Agents use APM vendor APIs to observe system behavior before/during/after experiments. ML models analyze telemetry to detect anomalies and validate hypotheses. Abstract APM vendors behind an OpenTelemetry interface to avoid vendor lock-in.

## Architecture Decisions

### Decision: OpenTelemetry as the abstraction layer

**Choice**: Implement a vendor-agnostic telemetry interface using OpenTelemetry SDK
**Alternatives considered**: Direct Datadog SDK, Direct New Relic SDK, Native vendor plugins
**Rationale**: OpenTelemetry is the industry standard for observability. It allows switching APM vendors without code changes and provides a unified trace/metric/log model.

### Decision: Sidecar deployment for ChaosAgent

**Choice**: Deploy ChaosAgent as a sidecar container alongside existing services
**Alternatives considered**: Standalone pod deployment, DaemonSet, Centralized remote agent
**Rationale**: Sidecar provides the tightest coupling for failure injection while maintaining isolation. Each service gets its own agent without shared state issues.

### Decision: Declarative experiment definitions

**Choice**: Store chaos experiments as declarative configuration (YAML/JSON)
**Alternatives considered**: Imperative API calls, ad-hoc scripts
**Rationale**: Declarative experiments can be version-controlled, reviewed, and rolled back instantly via feature flags. Critical for production safety.

### Decision: Feature-flag kill switch

**Choice**: `CHAOS_ENABLED` environment variable as the primary kill switch
**Alternatives considered**: API-based abort, timeout-based auto-terminate
**Rationale**: Environment variables are the simplest, most reliable mechanism across all environments. Can be set via Kubernetes ConfigMap without restarting pods.

## Data Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ ChaosEngineer│────▶│ ChaosAgent   │────▶│ Target Service  │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ APM Vendor   │
                    │ (Datadog/NR) │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ ML Anomaly   │
                    │ Detector     │
                    └──────────────┘
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `agents/chaos/chaos_agent.py` | Create | ChaosAgent implementation with APM client |
| `agents/chaos/chaos_engineer.py` | Create | ChaosEngineer agent for experiment orchestration |
| `agents/chaos/experiment.py` | Create | Declarative experiment definitions |
| `ml/anomaly_detector.py` | Modify | Add chaos validation model |
| `observability/telemetry.py` | Create | OpenTelemetry wrapper and pipeline |
| `observability/apm/datadog.py` | Create | Datadog APM client wrapper |
| `observability/apm/newrelic.py` | Create | New Relic APM client wrapper |
| `observability/otel_collector.py` | Create | OpenTelemetry Collector config |
| `k8s/chaos-agent.yaml` | Create | Helm chart for ChaosAgent deployment |

## Interfaces / Contracts

### ChaosExperiment Schema

```yaml
apiVersion: chaos.metanoia.io/v1
kind: Experiment
metadata:
  name: latency-injection
spec:
  target:
    service: api-gateway
    namespace: staging
  action:
    type: latency
    params:
      delay_ms: 500
      duration_s: 30
  guardrails:
    max_duration_s: 60
    abort_on_error: true
```

### APM Client Interface

```python
class APMClient(Protocol):
    def ingest_traces(self, traces: List[Trace]) -> None: ...
    def ingest_metrics(self, metrics: List[Metric]) -> None: ...
    def query(self, query: str) -> QueryResult: ...
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | APM client wrappers, experiment parsing | pytest with mocked vendor APIs |
| Integration | Agent-to-APM connectivity, telemetry flow | k6 load test with chaos hooks |
| E2E | Full experiment with Playwright UI validation | Playwright scenarios with chaos triggers |
| Security | OWASP ZAP scan on chaos API endpoints | ZAP baseline scan in CI |

## Migration / Rollout

1. Deploy OpenTelemetry Collector to staging (week 1)
2. Deploy ChaosAgent to staging with `CHAOS_ENABLED=false` (week 2)
3. Enable chaos in staging only, run initial experiments (week 3)
4. Add ML anomaly detector, validate accuracy >80% (week 4)
5. Deploy to production with feature flag off, validate telemetry (week 5)
6. Enable production chaos via `CHAOS_ENABLED=true` on opt-in basis (week 6)

## Open Questions

- [ ] Should chaos experiments auto-rollback on cascading failure detection?
- [ ] What is the retention policy for experiment telemetry data?
