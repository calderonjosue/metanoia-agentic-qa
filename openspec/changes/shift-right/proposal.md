# Proposal: Shift-Right Testing / Chaos Engineering

## Intent

Extend agent capabilities from pre-production (Shift-Left) to production monitoring through APM integration and chaos engineering. Enable agents to observe production telemetry, inject controlled failures, and self-heal based on real environment behavior.

## Scope

### In Scope
- APM integration (Datadog, New Relic, OpenTelemetry) for telemetry ingestion
- ChaosEngineer agent for controlled failure injection in staging/production
- Agent observability hooks (traces, metrics, logs)
- Production feedback loop: monitor → analyze → act → validate

### Out of Scope
- Full chaos engineering platform (Litmus, Gremlin)
- Real user monitoring (RUM)
- Incident auto-remediation (future work)

## Approach

Agent-based chaos engineering: deploy lightweight chaos agents alongside existing services that receive injection instructions from a central ChaosEngineer. Agents use APM APIs to observe system behavior before/during/after experiments. ML models analyze telemetry to detect anomalies and validate hypotheses.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `agents/` | Modified | New ChaosAgent, APM client wrappers |
| `ml/` | Modified | Anomaly detection models for chaos validation |
| `observability/` | New | Telemetry ingestion, chaos experiment runner |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Production impact from chaos experiments | High | Staged rollout, kill switches, experiment guardrails |
| APM vendor lock-in | Medium | Abstract behind OpenTelemetry interface |

## Rollback Plan

Disable chaos agents via feature flag (`CHAOS_ENABLED=false`). Revert APM config to default. All chaos experiments are declarative and can be stopped immediately.

## Dependencies

- OpenTelemetry Collector deployment
- APM vendor credentials (Datadog/New Relic)

## Success Criteria

- [ ] ChaosAgent deploys to k8s staging env
- [ ] APM telemetry visible in dashboard within 60s of deployment
- [ ] Chaos experiment (latency injection) completes without cascading failure
- [ ] Anomaly detection model flags injected failure with >80% accuracy
