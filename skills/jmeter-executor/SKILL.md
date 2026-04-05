---
name: jmeter-executor
version: 1.0.0
author: Metanoia-QA Team
description: Apache JMeter performance testing - load testing, stress testing, and HTML report generation
triggers:
  - jmeter
  - load:test
  - performance
  - stress:test
  - jmx
---

# JMeter Executor Skill

Performance testing skill using Apache JMeter for load generation and analysis.

## Capabilities

- Load testing with configurable thread groups
- Stress testing to identify breaking points
- HTML report generation for visualization
- CSV result collection
- Custom assertions and timers
- Distributed testing support
- JMX file execution and generation

## Usage

```bash
# Install JMeter
brew install jmeter  # macOS
# or: wget https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-5.6.3.tgz
```

```python
from metanoia.skills.jmeter_executor.executor import JMeterExecutor

executor = JMeterExecutor()
result = await executor.execute({
    "jmx_file": "load_test.jmx",
    "report_output": "./reports"
})
```
