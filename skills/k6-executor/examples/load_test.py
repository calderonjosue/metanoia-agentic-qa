# k6 Executor Examples

## Basic Load Test

```python
from metanoia.skills.k6_executor.executor import K6Executor

async def basic_load_test():
    executor = K6Executor()
    result = await executor.execute({
        "script": """
import http from "k6/http";
import { check } from "k6";

export const options = {
    vus: 10,
    duration: "30s"
};

export default function() {
    const res = http.get("https://example.com/api/health");
    check(res, { "status is 200": (r) => r.status === 200 });
}
""",
        "vus": 10,
        "duration": "30s"
    })
    assert result["status"] == "success"
```

## API Load Test with JSON Config

```python
async def api_load_test():
    executor = K6Executor()
    result = await executor.execute({
        "script": [
            {
                "method": "GET",
                "path": "/api/users"
            },
            {
                "method": "POST",
                "path": "/api/users",
                "body": {"name": "test", "email": "test@example.com"}
            }
        ],
        "base_url": "https://api.example.com",
        "vus": 50,
        "duration": "1m"
    })
    assert result["status"] == "success"
```

## Stress Test

```python
async def stress_test():
    executor = K6Executor()
    result = await executor.execute({
        "script": [
            {"method": "GET", "path": "/api/products"},
            {"method": "GET", "path": "/api/orders"}
        ],
        "base_url": "https://staging.example.com",
        "vus": 500,
        "duration": "5m"
    })
    assert result["status"] == "success"
```
