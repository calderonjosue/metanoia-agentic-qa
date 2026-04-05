---
name: locust-executor
description: Python-based load testing with Locust. Trigger: When running load tests, performance testing, stress testing, or scalability testing with Locust.
base: /Users/calderonjosue_/metanoia/skills/locust-executor
files:
  - executor.py
  - schema.json
  - examples/api_load_test.py
  - examples/website_test.py
---

# Locust Executor Skill

Python-based load testing with Locust for simulating user traffic, measuring performance, and identifying bottlenecks.

## Capabilities

- **Python scripting** - Write Locust tasks as Python classes
- **Distributed testing** - Run load tests across multiple machines
- **Web UI** - Real-time monitoring dashboard at port 8089
- **Real-time reporting** - Live statistics during test execution
- **Custom client behavior** - Full control over HTTP clients and task logic

## Files

| File | Purpose |
|------|---------|
| `executor.py` | LocustExecutor class for programmatic control |
| `schema.json` | JSON schema for Locust task definitions |
| `examples/api_load_test.py` | REST API load testing example |
| `examples/website_test.py` | Website load testing example |

## Quick Start

```python
from executor import LocustExecutor

executor = LocustExecutor(host="https://api.example.com")
executor.run(locust_file="examples/api_load_test.py", users=100, spawn_rate=10)
```

## LocustExecutor API

### Methods

| Method | Description |
|--------|-------------|
| `run()` | Execute a locust test |
| `stop()` | Stop running test |
| `spawn_users()` | Dynamically add users |
| `get_stats()` | Retrieve current statistics |

### Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `host` | str | Target host URL |
| `users` | int | Concurrent users |
| `spawn_rate` | int | Users per second |
| `run_time` | str | Test duration (e.g., "5m", "1h") |
| `headless` | bool | Run without web UI |
| `web_port` | int | Web UI port (default 8089) |

## Examples

See `examples/` directory for working examples.

## Requirements

```
locust>=2.15.0
pyjson>=5.0
```
