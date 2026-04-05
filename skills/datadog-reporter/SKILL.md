---
name: datadog-reporter
description: Report test metrics to Datadog for monitoring, alerting, and dashboards. Use when submitting test results from CI/CD pipelines, tracking test performance over time, monitoring flakiness, or setting up test-related alerts and dashboards.
---

# Datadog Test Metrics Reporter

## When to use this skill

Use this skill when you need to:

- Submit test metrics to Datadog from CI/CD pipelines
- Track test pass rates, duration, and flakiness over time
- Create dashboards for test metrics visualization
- Set up alerts for test failures or performance degradation
- Monitor test suite health in production-like environments

## Prerequisites

```bash
pip install datadog
```

Required environment variables:
- `DATADOG_API_KEY` - Your Datadog API key
- `DATADOG_APP_KEY` - Your Datadog application key

## Usage

### Basic Metrics Submission

```bash
python skills/datadog-reporter/executor.py submit \
  --metrics test_results,test_duration,test_flakiness \
  --suite "my-test-suite" \
  --passed 95 \
  --failed 5 \
  --duration 120.5 \
  --flaky 2
```

### Available Commands

| Command | Description |
|---------|-------------|
| `submit` | Submit test metrics to Datadog |
| `validate` | Validate metric payload against schema |
| `dashboards` | List available dashboard definitions |
| `alerts` | List available alert definitions |

### Metric Types

| Metric | Type | Description |
|--------|------|-------------|
| `test.results` | count | Pass/fail counts with tags |
| `test.duration` | gauge | Test suite duration in seconds |
| `test.flakiness` | gauge | Percentage of flaky tests |
| `test.skipped` | count | Number of skipped tests |

## Dashboards

Pre-configured dashboards available in `dashboards/`:

- `test-metrics.json` - Overview dashboard with key metrics
- `test-performance.json` - Detailed performance analysis
- `test-flakiness.json` - Flaky test monitoring

Import via Datadog UI: Dashboards > New Dashboard > Import JSON

## Alerts

Pre-configured alert monitors in `alerts/`:

- `test-failure-spike.json` - Alert on sudden failure rate increase
- `slow-test-suite.json` - Alert when test duration exceeds threshold
- `flaky-test-increase.json` - Alert on rising flakiness

Import via Datadog UI: Monitors > New Monitor > Import JSON

## Examples

See `examples/reporter.py` for complete usage examples.
