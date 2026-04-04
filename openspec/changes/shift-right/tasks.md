# Tasks: Shift-Right Testing / Chaos Engineering

## Phase 1: Infrastructure

- [ ] 1.1 Create `observability/otel_collector.yaml` with OpenTelemetry Collector configuration for staging/production
- [ ] 1.2 Create `observability/apm/base.py` with abstract `APMClient` interface and vendor-agnostic methods
- [ ] 1.3 Create `observability/apm/datadog.py` implementing Datadog APM client wrapper
- [ ] 1.4 Create `observability/apm/newrelic.py` implementing New Relic APM client wrapper
- [ ] 1.5 Create `observability/telemetry.py` with unified trace/metric/log ingestion pipeline

## Phase 2: ChaosAgent Core

- [ ] 2.1 Create `agents/chaos/experiment.py` with declarative `ChaosExperiment` schema and YAML parser
- [ ] 2.2 Create `agents/chaos/chaos_agent.py` implementing ChaosAgent with APM client, experiment runner, and kill switch logic
- [ ] 2.3 Create `k8s/chaos-agent.yaml` Helm chart for sidecar deployment with `CHAOS_ENABLED` env var support
- [ ] 2.4 Implement agent registration and heartbeat to control plane in `chaos_agent.py`
- [ ] 2.5 Implement experiment guardrails (max_duration, abort_on_error) in `experiment.py`

## Phase 3: ChaosEngineer Agent

- [ ] 3.1 Create `agents/chaos/chaos_engineer.py` implementing ChaosEngineer agent with experiment definition and orchestration logic
- [ ] 3.2 Implement monitor → analyze → act → validate feedback loop in `chaos_engineer.py`
- [ ] 3.3 Connect ChaosEngineer to ChaosAgent via gRPC/REST API

## Phase 4: ML Anomaly Detection

- [ ] 4.1 Extend `ml/anomaly_detector.py` with chaos-specific anomaly detection model
- [ ] 4.2 Implement telemetry baseline capture for comparison during experiments
- [ ] 4.3 Integrate anomaly detection with ChaosEngineer for real-time validation

## Phase 5: Testing & Validation

- [ ] 5.1 Write unit tests for APM client wrappers with mocked vendor APIs (pytest)
- [ ] 5.2 Write unit tests for experiment parsing and guardrails
- [ ] 5.3 Write integration test with k6 to validate telemetry flow end-to-end
- [ ] 5.4 Write Playwright E2E test validating UI behavior during latency injection
- [ ] 5.5 Run OWASP ZAP security scan on chaos API endpoints
- [ ] 5.6 Validate anomaly detection accuracy >80% against known failure patterns

## Phase 6: Deployment & Rollout

- [ ] 6.1 Deploy OpenTelemetry Collector to staging environment
- [ ] 6.2 Deploy ChaosAgent to staging with `CHAOS_ENABLED=false`
- [ ] 6.3 Run initial chaos experiments in staging, verify no cascading failures
- [ ] 6.4 Deploy ChaosAgent to production with `CHAOS_ENABLED=false`
- [ ] 6.5 Validate production telemetry visible in APM dashboard within 60s
- [ ] 6.6 Enable production chaos on opt-in basis, monitor closely
