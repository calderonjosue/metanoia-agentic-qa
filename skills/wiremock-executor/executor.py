#!/usr/bin/env python3
"""
WireMock Executor - API mocking with WireMock.
"""

import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class StubMapping:
    url_path: str
    method: str = "GET"
    response_status: int = 200
    response_body: Optional[dict] = None
    response_headers: Optional[dict] = None
    request_headers: Optional[dict] = None
    request_body_pattern: Optional[str] = None
    priority: int = 0
    scenario_name: Optional[str] = None
    required_state: Optional[str] = None
    new_state: Optional[str] = None

    def to_wiremock(self) -> dict:
        mapping = {
            "request": {
                "method": self.method.upper(),
                "urlPath": self.url_path
            },
            "response": {
                "status": self.response_status
            }
        }

        if self.response_body is not None:
            mapping["response"]["jsonBody"] = self.response_body

        if self.response_headers:
            mapping["response"]["headers"] = self.response_headers

        if self.request_headers:
            mapping["request"]["headers"] = {
                k: {"matches": v} for k, v in self.request_headers.items()
            }

        if self.request_body_pattern:
            mapping["request"]["bodyPatterns"] = [
                {"matches": self.request_body_pattern}
            ]

        if self.priority:
            mapping["priority"] = self.priority

        if self.scenario_name:
            mapping["scenarioName"] = self.scenario_name
            if self.required_state:
                mapping["requiredScenarioState"] = self.required_state
            if self.new_state:
                mapping["newScenarioState"] = self.new_state

        return mapping


@dataclass
class Scenario:
    name: str
    stubs: list = field(default_factory=list)

    def stub_get(self, path: str, response_body: dict, status: int = 200):
        self.stubs.append(StubMapping(
            url_path=path,
            method="GET",
            response_status=status,
            response_body=response_body
        ))
        return self

    def stub_post(self, path: str, response_body: dict, status: int = 201):
        self.stubs.append(StubMapping(
            url_path=path,
            method="POST",
            response_status=status,
            response_body=response_body
        ))
        return self

    def in_state(self, state: str):
        if self.stubs:
            self.stubs[-1].required_state = state
        return self

    def will_set_state_to(self, new_state: str):
        if self.stubs:
            self.stubs[-1].new_state = new_state
        return self


class WireMockExecutor:
    DEFAULT_PORT = 8080
    DEFAULT_HOST = "localhost"

    def __init__(
        self,
        port: int = DEFAULT_PORT,
        host: str = DEFAULT_HOST,
        docker_image: str = "wiremock/wiremock:3.5.0",
        docker_container_name: Optional[str] = None,
        mappings_dir: Optional[Path] = None,
        files_dir: Optional[Path] = None
    ):
        self.port = port
        self.host = host
        self.base_url = f"http://{host}:{port}"
        self.docker_image = docker_image
        self.docker_container_name = docker_container_name or f"wiremock-{port}"
        self.mappings_dir = mappings_dir or Path("./wiremock/mappings")
        self.files_dir = files_dir or Path("./wiremock/__files")
        self._container_id: Optional[str] = None
        self._using_docker: bool = False
        self._process: Optional[subprocess.Popen] = None

    def start(self, use_docker: bool = False):
        if use_docker:
            self._start_docker()
        else:
            self._start_standalone()

    def _start_standalone(self):
        self.mappings_dir.mkdir(parents=True, exist_ok=True)
        self.files_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            "java", "-jar", "wiremock-standalone-3.5.0.jar",
            "--port", str(self.port),
            "--root-dir", str(self.mappings_dir.parent)
        ]
        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(2)

    def _start_docker(self):
        self.mappings_dir.mkdir(parents=True, exist_ok=True)
        self.files_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            "docker", "run", "-d",
            "--name", self.docker_container_name,
            "-p", f"{self.port}:8080",
            "-v", f"{self.mappings_dir.absolute()}:/home/wiremock/mappings",
            "-v", f"{self.files_dir.absolute()}:/home/wiremock/__files",
            self.docker_image
        ]
        subprocess.run(cmd, check=True)
        self._container_id = self.docker_container_name
        self._using_docker = True
        time.sleep(2)

    def stop(self):
        if self._using_docker and self._container_id:
            subprocess.run(["docker", "stop", self._container_id], check=False)
            subprocess.run(["docker", "rm", self._container_id], check=False)
            self._container_id = None
        elif self._process:
            self._process.terminate()
            self._process.wait()
            self._process = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def reset(self):
        import requests
        requests.post(f"{self.base_url}/__reset")

    def stub_get(self, path: str, response_body: dict, status: int = 200, headers: Optional[dict] = None):
        return self._add_stub(StubMapping(
            url_path=path,
            method="GET",
            response_status=status,
            response_body=response_body,
            response_headers=headers
        ))

    def stub_post(self, path: str, response_body: dict, status: int = 201, headers: Optional[dict] = None):
        return self._add_stub(StubMapping(
            url_path=path,
            method="POST",
            response_status=status,
            response_body=response_body,
            response_headers=headers
        ))

    def stub_put(self, path: str, response_body: dict, status: int = 200, headers: Optional[dict] = None):
        return self._add_stub(StubMapping(
            url_path=path,
            method="PUT",
            response_status=status,
            response_body=response_body,
            response_headers=headers
        ))

    def stub_delete(self, path: str, status: int = 204):
        return self._add_stub(StubMapping(
            url_path=path,
            method="DELETE",
            response_status=status
        ))

    def stub_matching(
        self,
        url_path: str,
        method: str = "GET",
        body_pattern: Optional[str] = None,
        headers: Optional[dict] = None,
        response_status: int = 200,
        response_body: Optional[dict] = None,
        response_headers: Optional[dict] = None,
        priority: int = 10
    ):
        return self._add_stub(StubMapping(
            url_path=url_path,
            method=method,
            request_body_pattern=body_pattern,
            request_headers=headers,
            response_status=response_status,
            response_body=response_body,
            response_headers=response_headers,
            priority=priority
        ))

    def _add_stub(self, stub: StubMapping) -> dict:
        import requests
        mapping = stub.to_wiremock()
        response = requests.post(
            f"{self.base_url}/__admin/mappings",
            json=mapping
        )
        response.raise_for_status()
        return response.json()

    def create_scenario(self, name: str) -> Scenario:
        return Scenario(name=name)

    def add_scenario_stub(self, scenario: Scenario):
        for stub in scenario.stubs:
            if stub.scenario_name is None:
                stub.scenario_name = scenario.name
            self._add_stub(stub)

    def get_mappings(self) -> list:
        import requests
        response = requests.get(f"{self.base_url}/__admin/mappings")
        response.raise_for_status()
        return response.json()["mappings"]

    def get_requests(self) -> list:
        import requests
        response = requests.get(f"{self.base_url}/__admin/requests")
        response.raise_for_status()
        return response.json()["requests"]

    def start_recording(self, target_base_url: str):
        import requests
        config = {
            "targetBaseUrl": target_base_url,
            "captureHeaders": {"*": {}}
        }
        response = requests.post(
            f"{self.base_url}/__admin/recordings/start",
            json=config
        )
        response.raise_for_status()

    def stop_recording(self):
        import requests
        response = requests.post(f"{self.base_url}/__admin/recordings/stop")
        response.raise_for_status()
        return response.json()

    def get_recorded_requests(self) -> list:
        import requests
        response = requests.get(f"{self.base_url}/__admin/requests")
        response.raise_for_status()
        return response.json()["requests"]

    def save_recording(self, filepath: str):
        requests_data = self.get_recorded_requests()
        mappings = []
        for req in requests_data:
            mapping = {
                "request": {
                    "method": req.get("method", "ANY"),
                    "urlPath": req.get("url", {}).get("path", "/")
                },
                "response": {
                    "status": 200,
                    "jsonBody": req.get("responseBody")
                }
            }
            mappings.append(mapping)

        with open(filepath, "w") as f:
            json.dump({"mappings": mappings}, f, indent=2)

    def load_mappings_from_file(self, filepath: str):
        with open(filepath) as f:
            data = json.load(f)

        if "mappings" in data:
            for mapping in data["mappings"]:
                import requests
                requests.post(f"{self.base_url}/__admin/mappings", json=mapping)

    def serve_file(self, filename: str, content: str):
        self.files_dir.mkdir(parents=True, exist_ok=True)
        filepath = self.files_dir / filename
        filepath.write_text(content)
        return filepath

    def validate_against_schema(self, data: dict, schema_name: str = "mapping") -> bool:
        import jsonschema
        schema_path = Path(__file__).parent / "schema.json"
        if schema_path.exists():
            with open(schema_path) as f:
                schema = json.load(f)
            try:
                jsonschema.validate(data, schema)
                return True
            except jsonschema.ValidationError:
                return False
        return True


if __name__ == "__main__":
    with WireMockExecutor() as executor:
        executor.stub_get("/api/health", {"status": "ok"})
        executor.stub_post("/api/echo", {"echo": True})
        print("WireMock running at http://localhost:8080")
