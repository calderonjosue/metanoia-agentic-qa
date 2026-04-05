"""Pact executor for consumer-driven contract testing.

This skill provides contract testing capabilities using Pact for
consumer-driven contract testing with provider verification.
"""

import asyncio
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, TypedDict

from metanoia.skills.base import SkillExecutor

logger = logging.getLogger(__name__)


class PactInteraction(TypedDict):
    """A single interaction in a pact contract."""
    description: str
    request: dict[str, Any]
    response: dict[str, Any]
    provider_state: str | None


class PactConsumerInput(TypedDict):
    """Input for consumer mode - creating pact contracts."""
    mode: str
    consumer: str
    provider: str
    interactions: list[PactInteraction]
    pact_dir: str | None
    version: str | None


class PactProviderInput(TypedDict):
    """Input for provider mode - verifying against pact."""
    mode: str
    provider: str
    pact_url: str
    provider_base_url: str
    docker: dict[str, Any] | None
    state_handlers: dict[str, str] | None


class PactPublishInput(TypedDict):
    """Input for publishing pacts to broker."""
    mode: str
    pact_files: list[str]
    broker_url: str
    broker_token: str | None
    consumer_version: str | None


class PactOutput(TypedDict):
    """Output from pact execution."""
    status: str
    pact_file: str | None
    verification_result: dict[str, Any] | None
    error: str | None


class PactBrokerClient:
    """Client for Pact Broker operations."""

    def __init__(self, broker_url: str, token: str | None = None):
        self.broker_url = broker_url.rstrip("/")
        self.token = token or os.getenv("PACT_BROKER_TOKEN")
        self.headers = {"Content-Type": "application/json"}
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def publish_pact(
        self,
        pact_content: dict,
        consumer: str,
        provider: str,
        version: str
    ) -> dict[str, Any]:
        """Publish a pact to the broker."""
        import urllib.request

        url = f"{self.broker_url}/pacts/provider/{provider}/consumer/{consumer}/version/{version}"

        data = json.dumps(pact_content).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            headers=self.headers,
            method="PUT"
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return {"status": "success", "url": response.geturl()}
        except urllib.error.HTTPError as e:
            return {"status": "error", "error": f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def get_pact(
        self,
        consumer: str,
        provider: str,
        tag: str | None = None
    ) -> dict[str, Any]:
        """Retrieve a pact from the broker."""
        import urllib.request

        url = f"{self.broker_url}/pacts/provider/{provider}/consumer/{consumer}"
        if tag:
            url = f"{self.broker_url}/pacts/provider/{provider}/consumer/{consumer}/{tag}"

        request = urllib.request.Request(url, headers=self.headers)

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                content = response.read().decode("utf-8")
                return {"status": "success", "pact": json.loads(content)}
        except urllib.error.HTTPError as e:
            return {"status": "error", "error": f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}


class DockerProviderRunner:
    """Runs provider verification in Docker containers."""

    def __init__(self, docker_config: dict[str, Any]):
        self.image = docker_config.get("image")
        self.port = docker_config.get("port", 8080)
        self.health_check = docker_config.get("health_check", "/health")
        self.startup_timeout = docker_config.get("startup_timeout", 30)
        self.container_id: str | None = None

    async def start(self) -> str:
        """Start the Docker container and return base URL."""

        os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock")

        try:
            result = subprocess.run(
                ["docker", "run", "-d", "-P", self.image],
                capture_output=True,
                text=True,
                timeout=60
            )
            result.check_returncode()
            self.container_id = result.stdout.strip()

            container_port = subprocess.run(
                ["docker", "port", self.container_id, str(self.port)],
                capture_output=True,
                text=True,
                timeout=10
            ).stdout.strip()

            host_port = container_port.split("->")[0].split(":")[1] if "->" in container_port else self.port

            base_url = f"http://localhost:{host_port}"

            await self._wait_for_health(base_url)
            return base_url

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Docker container start timed out after {self.startup_timeout}s")
        except Exception as e:
            raise RuntimeError(f"Failed to start Docker container: {e}")

    async def _wait_for_health(self, base_url: str) -> None:
        """Wait for container to be healthy."""
        import urllib.request

        url = f"{base_url}{self.health_check}"
        elapsed = 0
        interval = 1

        while elapsed < self.startup_timeout:
            try:
                request = urllib.request.Request(url)
                with urllib.request.urlopen(request, timeout=5) as response:
                    if response.status == 200:
                        return
            except Exception:
                pass

            await asyncio.sleep(interval)
            elapsed += interval

        raise RuntimeError(f"Container health check failed after {self.startup_timeout}s")

    async def stop(self) -> None:
        """Stop and remove the Docker container."""
        if self.container_id:
            try:
                subprocess.run(
                    ["docker", "stop", self.container_id],
                    capture_output=True,
                    timeout=30
                )
                subprocess.run(
                    ["docker", "rm", "-f", self.container_id],
                    capture_output=True,
                    timeout=30
                )
            except Exception as e:
                logger.warning(f"Failed to cleanup Docker container: {e}")
            finally:
                self.container_id = None


class PactVerifier:
    """Verifies providers against Pact contracts."""

    @staticmethod
    async def verify(
        pact_path: str,
        provider_base_url: str,
        provider_name: str,
        state_handlers: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Run pact verification using the verifier Docker image."""

        verifier_image = "pactfoundation/pact-provider-verifier"

        cmd = [
            "docker", "run", "--rm",
            "-v", f"{os.path.abspath(pact_path)}:/pact/contract.json:ro",
            verifier_image,
            "--provider-base-url", provider_base_url,
            "--pact-url", "/pact/contract.json",
            "--provider", provider_name,
        ]

        if state_handlers:
            for state, handler_url in state_handlers.items():
                cmd.extend(["--state-change-url", f"{state}={handler_url}"])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            output = result.stdout + result.stderr

            if result.returncode == 0:
                return {
                    "status": "success",
                    "verified": True,
                    "output": output
                }
            else:
                return {
                    "status": "error",
                    "verified": False,
                    "output": output,
                    "error": f"Verification failed with exit code {result.returncode}"
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "verified": False,
                "error": "Verification timed out after 300s"
            }
        except Exception as e:
            return {
                "status": "error",
                "verified": False,
                "error": str(e)
            }


class PactExecutor(SkillExecutor):
    """Executor for Pact contract testing."""

    name = "pact-executor"
    version = "1.0.0"

    def __init__(self):
        super().__init__()
        self._pact_dir = Path("./pacts")
        self._pact_dir.mkdir(exist_ok=True)

    async def execute(self, input_data: dict) -> PactOutput:
        """Execute a Pact operation.
        
        Args:
            input_data: Operation parameters including mode (consumer/provider/publish).
            
        Returns:
            PactOutput with status and results.
        """
        mode = input_data.get("mode", "")

        try:
            if mode == "consumer":
                return await self._execute_consumer(input_data)
            elif mode == "provider":
                return await self._execute_provider(input_data)
            elif mode == "publish":
                return await self._execute_publish(input_data)
            elif mode == "verify":
                return await self._execute_verify(input_data)
            else:
                return self._error_output(f"Unknown mode: {mode}")
        except Exception as e:
            logger.exception("Pact execution failed")
            return self._error_output(str(e))

    async def _execute_consumer(self, input_data: PactConsumerInput) -> PactOutput:
        """Create a pact contract from consumer interactions."""
        consumer = input_data["consumer"]
        provider = input_data["provider"]
        interactions = input_data["interactions"]
        pact_dir = Path(input_data.get("pact_dir", "./pacts"))
        version = input_data.get("version", "1.0.0")

        pact_dir.mkdir(parents=True, exist_ok=True)

        pact_content = {
            "consumer": {"name": consumer},
            "provider": {"name": provider},
            "interactions": interactions,
            "metadata": {
                "pactSpecificationVersion": "3.0.0",
                "version": version
            }
        }

        pact_file = pact_dir / f"{consumer}-{provider}.json"
        with open(pact_file, "w") as f:
            json.dump(pact_content, f, indent=2)

        logger.info(f"Pact file created: {pact_file}")

        return {
            "status": "success",
            "pact_file": str(pact_file),
            "verification_result": None,
            "error": None
        }

    async def _execute_provider(self, input_data: PactProviderInput) -> PactOutput:
        """Verify provider against a pact contract."""
        provider = input_data["provider"]
        pact_url = input_data["pact_url"]
        docker_config = input_data.get("docker")

        provider_base_url = input_data.get("provider_base_url", "http://localhost:8080")
        state_handlers = input_data.get("state_handlers")

        docker_runner: DockerProviderRunner | None = None

        try:
            if docker_config and docker_config.get("enabled"):
                docker_runner = DockerProviderRunner(docker_config)
                provider_base_url = await docker_runner.start()
                logger.info(f"Provider running at: {provider_base_url}")

            if pact_url.startswith("pact://"):
                parts = pact_url.replace("pact://", "").split("/")
                if len(parts) >= 2:
                    consumer, rest = parts[0], "/".join(parts[1:])
                    tag = rest if rest else None
                    broker = PactBrokerClient(os.getenv("PACT_BROKER_URL", ""))
                    pact_result = await broker.get_pact(consumer, provider, tag)
                    if pact_result["status"] == "success":
                        import tempfile
                        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                            json.dump(pact_result["pact"]["pact"], f)
                            pact_url = f.name
                    else:
                        return self._error_output(f"Failed to fetch pact: {pact_result.get('error')}")

            if not os.path.exists(pact_url):
                return self._error_output(f"Pact file not found: {pact_url}")

            verifier = PactVerifier()
            result = await verifier.verify(
                pact_url=pact_url,
                provider_base_url=provider_base_url,
                provider_name=provider,
                state_handlers=state_handlers
            )

            return {
                "status": result["status"],
                "pact_file": pact_url,
                "verification_result": result,
                "error": result.get("error")
            }

        finally:
            if docker_runner:
                await docker_runner.stop()

    async def _execute_publish(self, input_data: PactPublishInput) -> PactOutput:
        """Publish pact files to a Pact Broker."""
        pact_files = input_data["pact_files"]
        broker_url = input_data["broker_url"]
        broker_token = input_data.get("broker_token") or os.getenv("PACT_BROKER_TOKEN")
        consumer_version = input_data.get("consumer_version", "1.0.0")

        broker = PactBrokerClient(broker_url, broker_token)

        results = []
        for pattern in pact_files:
            from glob import glob
            for file_path in glob(pattern):
                with open(file_path) as f:
                    pact_content = json.load(f)

                consumer = pact_content["consumer"]["name"]
                provider = pact_content["provider"]["name"]

                result = await broker.publish_pact(
                    pact_content=pact_content,
                    consumer=consumer,
                    provider=provider,
                    version=consumer_version
                )
                results.append({
                    "file": file_path,
                    "consumer": consumer,
                    "provider": provider,
                    "result": result
                })

        return {
            "status": "success",
            "pact_file": None,
            "verification_result": {"publish_results": results},
            "error": None
        }

    async def _execute_verify(self, input_data: dict) -> PactOutput:
        """Verify provider against contracts (alias for provider mode)."""
        return await self._execute_provider(input_data)

    def _error_output(self, error: str) -> PactOutput:
        """Create an error output."""
        return {
            "status": "error",
            "pact_file": None,
            "verification_result": None,
            "error": error
        }
