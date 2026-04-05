#!/usr/bin/env python3
"""
WireMock Stub Examples - Basic API stubbing patterns.
"""

from skills.wiremock_executor import WireMockExecutor


def basic_stubs():
    """Basic stubbing examples."""
    with WireMockExecutor() as executor:
        executor.stub_get("/api/health", {"status": "healthy"})
        executor.stub_get("/api/version", {"version": "1.0.0", "build": "abc123"})

        executor.stub_post("/api/users", {"id": 1, "name": "Alice"}, status=201)
        executor.stub_post("/api/users", {"error": "invalid"}, status=400)

        executor.stub_put("/api/users/1", {"id": 1, "name": "Alice Updated"})
        executor.stub_delete("/api/users/1")

        print("Basic stubs created successfully")
        print(f"Mappings: {executor.get_mappings()}")


def matching_stubs():
    """Request matching examples."""
    with WireMockExecutor() as executor:
        executor.stub_matching(
            url_path="/api/search",
            method="GET",
            body_pattern=None,
            headers={"Authorization": "Bearer .+"},
            response_status=200,
            response_body={"results": ["item1", "item2"]}
        )

        executor.stub_matching(
            url_path="/api/users",
            method="POST",
            body_pattern=r'\{"name": "[A-Za-z]+"\}',
            response_status=201,
            response_body={"id": 2, "name": "Created"}
        )

        print("Matching stubs created successfully")


def priority_stubs():
    """Priority-based stubbing (higher priority = evaluated first)."""
    with WireMockExecutor() as executor:
        executor.stub_get("/api/users", {"users": []})

        executor.stub_matching(
            url_path="/api/users",
            method="GET",
            headers={"Accept": "application/xml"},
            response_status=200,
            response_body={"xml": "<users/>"},
            priority=1
        )

        print("Priority stubs created successfully")


def delay_stubs():
    """Stubs with simulated delays."""
    with WireMockExecutor() as executor:
        mapping = {
            "request": {"method": "GET", "urlPath": "/api/slow"},
            "response": {
                "status": 200,
                "jsonBody": {"data": "value"},
                "delayDistribution": {"type": "fixed", "value": 2000}
            }
        }

        import requests
        requests.post(
            f"{executor.base_url}/__admin/mappings",
            json=mapping
        )

        print("Delayed stub created successfully")


def header_stubs():
    """Stubs with response headers."""
    with WireMockExecutor() as executor:
        executor.stub_get(
            "/api/cached",
            {"data": "value"},
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "max-age=3600",
                "X-Custom-Header": "custom"
            }
        )

        print("Header stubs created successfully")


def error_stubs():
    """Error response stubs."""
    with WireMockExecutor() as executor:
        executor.stub_get("/api/not-found", {"error": "Not Found"}, status=404)
        executor.stub_get("/api/server-error", {"error": "Internal Server Error"}, status=500)
        executor.stub_post("/api/unauthorized", {"error": "Unauthorized"}, status=401)

        print("Error stubs created successfully")


def file_stubs():
    """Stubs that serve files."""
    with WireMockExecutor() as executor:
        json_content = '{"message": "Hello from file"}'
        filepath = executor.serve_file("greeting.json", json_content)

        mapping = {
            "request": {"method": "GET", "urlPath": "/api/file"},
            "response": {
                "status": 200,
                "bodyFileName": "greeting.json",
                "headers": {"Content-Type": "application/json"}
            }
        }

        import requests
        requests.post(f"{executor.base_url}/__admin/mappings", json=mapping)
        print(f"File stub created with file: {filepath}")


if __name__ == "__main__":
    print("=== Basic Stubs ===")
    basic_stubs()

    print("\n=== Matching Stubs ===")
    matching_stubs()

    print("\n=== Priority Stubs ===")
    priority_stubs()

    print("\n=== Delay Stubs ===")
    delay_stubs()

    print("\n=== Header Stubs ===")
    header_stubs()

    print("\n=== Error Stubs ===")
    error_stubs()

    print("\n=== File Stubs ===")
    file_stubs()
