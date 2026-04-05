---
name: pact-executor
version: 1.0.0
author: Metanoia-QA Team
description: Contract testing with Pact. Consumer-driven contracts, provider verification, Pact broker integration, and Docker-based provider testing.
triggers:
  - contract:testing
  - pact
  - consumer:contract
  - provider:verification
---

# Pact Executor Skill

Contract testing skill using Pact for consumer-driven contract testing.

## Capabilities

- Consumer-driven contract testing
- Provider verification with Docker
- Pact broker integration for contract sharing
- Parallel test execution
- CI/CD integration support

## Architecture

```
PactExecutor
├── PactConsumer
│   ├── Define interactions
│   ├── Write pact file
│   └── Publish to broker
├── PactProvider
│   ├── Verify against pact
│   ├── Docker-based testing
│   └── State management
└── PactBroker
    ├── Publish contracts
    ├── Retrieve contracts
    └── Webhook triggers
```

## Setup

```bash
pip install pact>=4.0.0
docker pull pactfoundation/pact-provider-verifier
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| PACT_BROKER_URL | Base URL of Pact Broker |
| PACT_BROKER_TOKEN | Authentication token |
| PACT_CONSUMER_VERSION | Consumer version tag |
| PACT_PROVIDER_VERSION | Provider version tag |

## Usage

```python
from metanoia.skills.pact_executor.executor import PactExecutor

executor = PactExecutor()

# Consumer: create contract
result = await executor.execute({
    "mode": "consumer",
    "consumer": "my-service",
    "provider": "user-api",
    "interactions": [
        {
            "description": "get user by id",
            "request": {"method": "GET", "path": "/users/1"},
            "response": {"status": 200, "body": {"id": 1, "name": "Test User"}}
        }
    ]
})
```
