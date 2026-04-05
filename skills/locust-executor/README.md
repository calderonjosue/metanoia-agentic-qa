# Locust Executor

Python-based load testing with Locust.

## Overview

This skill provides a Python wrapper around Locust for running scalable load tests. It enables distributed testing, real-time monitoring, and programmatic control over test execution.

## Installation

```bash
pip install locust>=2.15.0
```

## LocustExecutor

The `LocustExecutor` class provides programmatic control over Locust tests.

```python
from locust_executor import LocustExecutor

executor = LocustExecutor(host="https://api.example.com")
executor.run(
    locust_file="examples/api_load_test.py",
    users=100,
    spawn_rate=10,
    run_time="5m",
    headless=False
)
```

## Writing Locust Tasks

Locust tasks are defined as Python classes extending `HttpUser`:

```python
from locust import HttpUser, task, between

class MyUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def get_index(self):
        self.client.get("/")
    
    @task(3)
    def get_products(self):
        self.client.get("/products")
```

## Running Tests

### Command Line

```bash
locust -f examples/api_load_test.py --host=https://api.example.com
```

### Programmatic

```python
executor = LocustExecutor(host="https://api.example.com")
executor.run(locust_file="examples/api_load_test.py", users=100, spawn_rate=10)
```

## Distributed Testing

Run a master:
```bash
locust -f locustfile.py --master
```

Run workers:
```bash
locust -f locustfile.py --worker --master-host=<master-ip>
```

## Web UI

Access real-time statistics at `http://localhost:8089` during test execution.

## Examples

- `examples/api_load_test.py` - REST API load testing
- `examples/website_test.py` - Website load testing

## Options Reference

| Option | Description | Default |
|--------|-------------|---------|
| `host` | Target host URL | Required |
| `users` | Concurrent users | 10 |
| `spawn_rate` | Users spawned per second | 1 |
| `run_time` | Test duration | Indefinite |
| `headless` | Disable web UI | false |
| `web_port` | Web UI port | 8089 |
| `master` | Run as master node | false |
| `worker` | Run as worker node | false |
