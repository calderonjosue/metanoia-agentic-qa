# WireMock Executor

API mocking with WireMock for tests, development, and CI/CD pipelines.

## Features

- **Stub HTTP Responses**: Define fixed or dynamic responses for any endpoint
- **Request Matching**: Match by URL path, query params, headers, body patterns
- **Stateful Behavior**: Simulate multi-step API conversations and session state
- **Record/Playback**: Proxy and record real APIs, then replay in tests
- **Docker Support**: Run WireMock as a sidecar or in testcontainers

## Quick Start

```bash
pip install wiremock

# Or use Docker
docker run -d --name wiremock -p 8080:8080 \
  -v $(pwd)/mappings:/home/wiremock/mappings \
  -v $(pwd)/files:/home/wiremock/__files \
  wiremock/wiremock:3.5.0
```

## Python API

```python
from skills.wiremock_executor import WireMockExecutor

executor = WireMockExecutor()
executor.start()

# Stub a GET endpoint
executor.stub_get("/api/users", {"id": 1, "name": "Alice"})

# Stub with request matching
executor.stub_matching(
    url_path="/api/users",
    method="POST",
    body_pattern=r'{"name": ".+"}',
    response={"id": 2, "name": "Bob"}
)

executor.stop()
```

## Stateful Mocking

```python
executor = WireMockExecutor()

scenario = executor.create_scenario("user_registration")
scenario.stub_post("/register", {"userId": 1})
    .in_state("started")
    .will_set_state_to("user_created")

scenario.stub_get("/profile/1", {"id": 1, "name": "New User"})
    .in_state("user_created")

scenario.execute()
```

## Record/Playback

```python
executor = WireMockExecutor()
executor.start_recording(target_base_url="https://api.example.com")

# Make requests through proxy
requests = executor.get_recorded_requests()

executor.stop_recording()
executor.save_recording("saved_api.json")
```

## Files

```
wiremock-executor/
├── SKILL.md
├── README.md
├── executor.py
├── schema.json
└── examples/
    ├── stub_api.py
    └── stateful_mock.py
```
