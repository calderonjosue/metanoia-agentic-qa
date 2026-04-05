import subprocess
import json
import time
import signal
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class LocustStats:
    total_requests: int = 0
    failed_requests: int = 0
    median_response_time: float = 0
    avg_response_time: float = 0
    rps: float = 0
    users: int = 0


@dataclass
class LocustConfig:
    host: str
    locust_file: str
    users: int = 10
    spawn_rate: int = 1
    run_time: Optional[str] = None
    headless: bool = False
    web_port: int = 8089
    master: bool = False
    worker: bool = False
    master_host: Optional[str] = None
    tags: Optional[List[str]] = None
    exclude_tags: Optional[List[str]] = None


class LocustExecutor:
    def __init__(self, host: str, web_port: int = 8089):
        self.host = host
        self.web_port = web_port
        self.process: Optional[subprocess.Popen] = None
        self.config: Optional[LocustConfig] = None

    def run(
        self,
        locust_file: str,
        users: int = 10,
        spawn_rate: int = 1,
        run_time: Optional[str] = None,
        headless: bool = False,
        tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None
    ) -> subprocess.Popen:
        self.config = LocustConfig(
            host=self.host,
            locust_file=locust_file,
            users=users,
            spawn_rate=spawn_rate,
            run_time=run_time,
            headless=headless,
            web_port=self.web_port,
            tags=tags,
            exclude_tags=exclude_tags
        )

        cmd = [
            "locust",
            "-f", locust_file,
            "--host", self.host,
            "--users", str(users),
            "--spawn-rate", str(spawn_rate),
            "--web-port", str(self.web_port)
        ]

        if headless:
            cmd.append("--headless")
            if run_time:
                cmd.extend(["--run-time", run_time])
                cmd.append("--headless")

        if tags:
            for tag in tags:
                cmd.extend(["--tags", tag])

        if exclude_tags:
            for tag in exclude_tags:
                cmd.extend(["--exclude-tags", tag])

        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        return self.process

    def spawn_users(self, users: int, spawn_rate: int = 1) -> None:
        if not self.process or self.process.poll() is not None:
            raise RuntimeError("Locust process is not running")

        self.process.stdin.write(f"spawn {users} {spawn_rate}\n".encode())
        self.process.stdin.flush()

    def stop(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.send_signal(signal.SIGTERM)
            self.process.wait(timeout=10)

    def get_stats(self) -> LocustStats:
        stats = LocustStats()
        if self.config:
            stats.users = self.config.users
        return stats

    def generate_locust_file(
        self,
        name: str,
        tasks: List[Dict[str, Any]],
        output_path: str
    ) -> None:
        wait_time_min = 1
        wait_time_max = 3

        imports = [
            "from locust import HttpUser, task, between, tag",
            "import json"
        ]

        task_methods = []
        for i, t in enumerate(tasks):
            method = t.get("method", "GET").lower()
            path = t.get("path", "/")
            weight = t.get("weight", 1)
            headers = t.get("headers", {})
            task_name = t.get("name", f"task_{i}")
            json_body = t.get("json")
            data = t.get("data")

            decorator = f"    @task({weight})"
            if "tag" in t:
                decorator += f'\n    @tag("{t["tag"]}")'

            method_body = f'        self.client.{method}("{path}"'

            if json_body:
                method_body += f', json={json.dumps(json_body)}'
            elif data:
                method_body += f', data={json.dumps(data) if isinstance(data, dict) else json.dumps({{"data": data}})}'

            if headers:
                method_body += f', headers={json.dumps(headers)}'

            method_body += ")"

            task_methods.append(f"{decorator}\n    def {task_name}(self):\n{method_body}")

        class_code = f"""
class {name.replace(' ', '').replace('-', '')}User(HttpUser):
    wait_time = between({wait_time_min}, {wait_time_max})

{chr(10).join(task_methods)}
"""

        full_code = "\n".join(imports) + class_code

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(full_code)

    @staticmethod
    def run_distributed(
        locust_file: str,
        host: str,
        users: int = 100,
        spawn_rate: int = 10,
        worker_count: int = 4
    ) -> Dict[str, subprocess.Popen]:
        processes = {}

        master_process = subprocess.Popen([
            "locust",
            "-f", locust_file,
            "--master",
            "--host", host,
            "--users", str(users),
            "--spawn-rate", str(spawn_rate)
        ])
        processes["master"] = master_process

        for i in range(worker_count):
            worker_process = subprocess.Popen([
                "locust",
                "-f", locust_file,
                "--worker",
                "--master-host", "localhost"
            ])
            processes[f"worker_{i}"] = worker_process

        return processes
