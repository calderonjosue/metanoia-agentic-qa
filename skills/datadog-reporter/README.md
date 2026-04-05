# Datadog Test Metrics Reporter

Report test metrics to Datadog for monitoring, alerting, and dashboards.

## Features

- Submit test results as metrics to Datadog
- Support for test duration, pass/fail rates, and custom metrics
- Pre-configured dashboard definitions (JSON)
- Alert monitor definitions (JSON)
- Easy integration with CI/CD pipelines

## Files

- `SKILL.md` - Skill definition and usage guide
- `executor.py` - Python executor for submitting metrics
- `schema.json` - JSON schema for metric payloads
- `examples/reporter.py` - Example usage script
- `dashboards/` - Pre-configured Datadog dashboard definitions
- `alerts/` - Pre-configured Datadog alert monitor definitions

## Quick Start

```bash
# Install dependencies
pip install datadog

# Set your API key
export DATADOG_API_KEY=your_api_key_here
export DATADOG_APP_KEY=your_app_key_here

# Submit test metrics
python examples/reporter.py --suite "my-tests" --passed 95 --failed 5 --duration 120.5
```

## Dashboard

Import `dashboards/test-metrics.json` into Datadog to visualize:
- Test pass rate over time
- Test duration trends
- Flaky test detection
- Test suite comparison

## Alerts

Import `alerts/*.json` into Datadog to get notified about:
- Test failure spikes
- Slow test suites
- Flaky test increases
