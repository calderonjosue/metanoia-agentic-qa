# k6 Executor Skill

Performance testing with k6 load generator.

## Features

- **Load Testing**: Configurable virtual users and duration
- **Stress Testing**: Identify breaking points
- **Auto Script Generation**: From JSON endpoint configuration
- **Metrics Export**: JSON output for integration
- **Grafana Integration**: Visualize with dashboards

## Installation

```bash
# macOS
brew install k6

# Linux
sudo apt install k6

# Docker
docker pull loadimpact/k6
```

## Quick Start

```python
from metanoia.skills.k6_executor.executor import K6Executor

executor = K6Executor()
result = await executor.execute({
    "script": [
        {"method": "GET", "path": "/api/health"}
    ],
    "base_url": "https://example.com",
    "vus": 100,
    "duration": "30s"
})
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `script` | string | required | k6 script or JSON config |
| `vus` | integer | 10 | Virtual users |
| `duration` | string | "30s" | Test duration |
| `base_url` | string | - | Base URL for JSON config |
| `output_json` | boolean | true | JSON output |
