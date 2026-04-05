---
name: wiremock-executor
description: API mocking with WireMock for stubbing HTTP responses, request matching, stateful behavior simulation, record/playback, and Docker support. Trigger: When the user needs to mock APIs, create test fixtures, simulate backend services, or set up contract testing.
---

# WireMock Executor Skill

Executes WireMock operations for API mocking, stubbing, and simulation.

## Capabilities

- **Stub HTTP Responses**: Configure fixed or dynamic responses for HTTP endpoints
- **Request Matching**: Match requests by URL, headers, body patterns, and more
- **Stateful Behavior**: Simulate stateful API interactions and scenarios
- **Record/Playback**: Record real API interactions and replay them later
- **Docker Support**: Run WireMock standalone in Docker containers

## Usage

```python
from skills.wiremock_executor import WireMockExecutor

executor = WireMockExecutor()
executor.start()

executor.stub_get("/api/users", {"users": []})
executor.stub_post("/api/users", {"id": 1, "name": "John"})

executor.stop()
```

## Architecture

- `executor.py`: Main WireMockExecutor class
- `schema.json`: JSON schema for configuration validation
- `examples/stub_api.py`: Basic stubbing examples
- `examples/stateful_mock.py`: Stateful behavior examples
