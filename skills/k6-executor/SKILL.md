---
name: k6-executor
version: 1.0.0
author: Metanoia-QA Team
description: Performance testing with k6 - load generation, stress testing, and scalability analysis
triggers:
  - performance
  - k6
  - load:test
  - stress:test
---

# k6 Executor Skill

Performance testing skill using k6 for load generation and analysis.

## Capabilities

- Load testing with configurable virtual users
- Stress testing to identify breaking points
- Scalability analysis and reporting
- Custom metrics and thresholds
- Integration with Grafana/InfluxDB
- API endpoint testing with assertions

## Usage

```bash
# Install k6
brew install k6  # macOS
# or: sudo apt install k6  # Linux
```

```python
from metanoia.skills.k6_executor.executor import K6Executor

executor = K6Executor()
result = await executor.execute({
    "script": "load-test.js",
    "vus": 100,
    "duration": "30s"
})
```
