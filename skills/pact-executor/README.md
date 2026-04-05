# Pact Executor Skill

Contract testing with Pact for consumer-driven contract testing.

## Features

- **Consumer Contracts**: Define and generate pact files
- **Provider Verification**: Verify provider against consumer contracts
- **Pact Broker**: Publish and retrieve contracts from broker
- **Docker Support**: Run provider verification in Docker containers
- **CI/CD Ready**: Easy integration with GitHub Actions, GitLab CI

## Quick Start

### Consumer Side

```python
from metanoia.skills.pact_executor.executor import PactExecutor

executor = PactExecutor()
result = await executor.execute({
    "mode": "consumer",
    "consumer": "web-frontend",
    "provider": "user-service",
    "interactions": [
        {
            "description": "a request to get user",
            "request": {"method": "GET", "path": "/users/123"},
            "response": {
                "status": 200,
                "headers": {"Content-Type": "application/json"},
                "body": {"id": 123, "name": "John Doe", "email": "john@example.com"}
            }
        }
    ]
})
```

### Provider Side

```python
result = await executor.execute({
    "mode": "provider",
    "provider": "user-service",
    "pact_url": "./pacts/web-frontend-user-service.json",
    "provider_base_url": "http://localhost:8080",
    "docker": {"enabled": True, "image": "my-user-service:latest"}
})
```

## Pact Broker Integration

```python
result = await executor.execute({
    "mode": "publish",
    "pact_files": ["./pacts/*.json"],
    "broker_url": "https://pact-broker.example.com",
    "broker_token": "env:PACT_BROKER_TOKEN"
})
```

## Docker-Based Provider Testing

```python
result = await executor.execute({
    "mode": "provider",
    "provider": "user-service",
    "pact_url": "pact://web-frontend/user-service:latest",
    "docker": {
        "enabled": True,
        "image": "my-service:latest",
        "port": 8080,
        "health_check": "/health",
        "startup_timeout": 30
    }
})
```

## Configuration

| Parameter | Type | Description |
|-----------|------|-------------|
| mode | string | `consumer`, `provider`, or `publish` |
| consumer | string | Consumer service name |
| provider | string | Provider service name |
| interactions | list | List of interaction definitions |
| pact_url | string | Path or broker URL for pact file |
| docker | object | Docker configuration for provider |

## Environment Variables

- `PACT_BROKER_URL` - Pact Broker URL
- `PACT_BROKER_TOKEN` - Broker authentication token
- `DOCKER_HOST` - Docker daemon socket (default: unix:///var/run/docker.sock)
