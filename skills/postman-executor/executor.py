"""Postman executor for API testing.

This skill provides API testing capabilities using Postman collections
and the Newman CLI for automated test execution.
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, TypedDict

from metanoia.skills.base import SkillExecutor, SkillInput, SkillOutput

logger = logging.getLogger(__name__)


class PostmanInput(TypedDict, total=False):
    """Input schema for Postman executor."""
    collection: str
    environment: str | None
    iteration_count: int | None
    iteration_data: str | None
    delay_request: int | None
    export_results: bool | None
    report_format: str | None
    folder: str | None
    working_dir: str | None


class PostmanOutput(TypedDict, total=False):
    """Output schema for Postman executor."""
    status: str
    summary: dict | None
    results: dict | None
    error: str | None


class NewmanRunner:
    """Handles Newman CLI execution for Postman collections."""

    SUPPORTED_FORMATS = ["json", "html", "cli", "junit"]

    @staticmethod
    def validate_collection(collection_path: str) -> bool:
        """Validate that collection file exists and is valid JSON."""
        path = Path(collection_path)
        if not path.exists():
            raise FileNotFoundError(f"Collection not found: {collection_path}")
        try:
            with open(path, "r") as f:
                data = json.load(f)
                if "info" not in data or "item" not in data:
                    raise ValueError("Invalid Postman collection format")
            return True
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in collection: {e}")

    @staticmethod
    def validate_environment(environment_path: str | None) -> bool:
        """Validate that environment file exists and is valid JSON."""
        if not environment_path:
            return True
        path = Path(environment_path)
        if not path.exists():
            raise FileNotFoundError(f"Environment not found: {environment_path}")
        try:
            with open(path, "r") as f:
                data = json.load(f)
                if "values" not in data and "id" not in data:
                    raise ValueError("Invalid Postman environment format")
            return True
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in environment: {e}")

    @staticmethod
    def build_command(
        collection_path: str,
        environment_path: str | None = None,
        iteration_count: int | None = None,
        iteration_data: str | None = None,
        delay_request: int | None = None,
        report_format: str = "json",
        folder: str | None = None,
        export_path: str | None = None
    ) -> list[str]:
        """Build Newman command with all options."""
        cmd = ["newman", "run", collection_path]

        if environment_path:
            cmd.extend(["--environment", environment_path])

        if iteration_count is not None and iteration_count > 1:
            cmd.extend(["--iteration-count", str(iteration_count)])

        if iteration_data:
            cmd.extend(["--iteration-data", iteration_data])

        if delay_request is not None and delay_request > 0:
            cmd.extend(["--delay-request", str(delay_request)])

        if folder:
            cmd.extend(["--folder", folder])

        if report_format and report_format != "cli":
            output_format = report_format.lower()
            if output_format == "junit":
                output_format = "junit"
            if export_path:
                if output_format == "json":
                    cmd.extend(["--export-json", export_path])
                elif output_format == "html":
                    cmd.extend(["--export-html", export_path])
                elif output_format == "junit":
                    cmd.extend(["--export-junit", export_path])

        cmd.extend(["--reporters", report_format])

        return cmd


class CollectionRunner:
    """Manages Postman Collection Runner execution."""

    def __init__(self):
        self.results: dict[str, Any] = {}

    async def run_collection(
        self,
        collection: str,
        environment: str | None = None,
        iteration_count: int = 1,
        iteration_data: str | None = None,
        delay_request: int | None = None,
        report_format: str = "json",
        folder: str | None = None
    ) -> dict[str, Any]:
        """Execute a Postman collection."""
        NewmanRunner.validate_collection(collection)
        NewmanRunner.validate_environment(environment)

        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = None
            if report_format != "cli":
                ext = "xml" if report_format == "junit" else report_format
                export_path = os.path.join(tmpdir, f"results.{ext}")

            cmd = NewmanRunner.build_command(
                collection,
                environment,
                iteration_count,
                iteration_data,
                delay_request,
                report_format,
                folder,
                export_path
            )

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=tmpdir
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=3600
            )

            output = stdout.decode() if stdout else ""
            error = stderr.decode() if stderr else ""

            if process.returncode != 0 and "exec" not in error.lower():
                logger.error(f"Newman error: {error}")

            results = self._parse_output(output, export_path, tmpdir)
            return results

    def _parse_output(
        self,
        stdout: str,
        export_path: str | None,
        tmpdir: str
    ) -> dict[str, Any]:
        """Parse Newman output and results."""
        summary: dict[str, Any] = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }

        try:
            if export_path and Path(export_path).exists():
                with open(export_path, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        data = data[0]
                    summary = self._extract_summary(data)
        except Exception as e:
            logger.warning(f"Could not parse export file: {e}")

        if summary["total"] == 0:
            summary = self._parse_summary_from_output(stdout)

        return {
            "summary": summary,
            "raw_output": stdout
        }

    def _extract_summary(self, data: dict) -> dict[str, Any]:
        """Extract summary from Newman JSON output."""
        summary: dict[str, Any] = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }

        if "run" in data:
            run_data = data["run"]
            if "stats" in run_data:
                stats = run_data["stats"]
                summary["total"] = stats.get("requests", {}).get("total", 0)
                summary["passed"] = stats.get("requests", {}).get("started", 0) - stats.get("requests", {}).get("failed", 0)
                summary["failed"] = stats.get("requests", {}).get("failed", 0)

        return summary

    def _parse_summary_from_output(self, output: str) -> dict[str, Any]:
        """Parse summary from CLI output."""
        summary: dict[str, Any] = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }

        lines = output.split("\n")
        for line in lines:
            line = line.strip()
            if "iterations" in line.lower() and "total" in line.lower():
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.isdigit() and i > 0:
                        summary["total"] = int(part)
                        break
            elif "passed" in line.lower():
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.isdigit():
                        summary["passed"] = int(part)
                        break
            elif "failed" in line.lower():
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.isdigit():
                        summary["failed"] = int(part)
                        break

        return summary


class PostmanExecutor(SkillExecutor):
    """Execute Postman collections and API tests."""

    name = "postman-executor"
    version = "1.0.0"

    def __init__(self):
        super().__init__()
        self._newman_available: bool | None = None
        self.runner = CollectionRunner()

    async def execute(self, input_data: PostmanInput) -> PostmanOutput:
        """Execute a Postman collection.

        Args:
            input_data: Collection configuration with collection path,
                       environment, iterations, etc.

        Returns:
            PostmanOutput with execution results.
        """
        collection = input_data.get("collection", "")
        environment = input_data.get("environment")
        iteration_count = input_data.get("iteration_count", 1)
        iteration_data = input_data.get("iteration_data")
        delay_request = input_data.get("delay_request")
        report_format = input_data.get("report_format", "json")

        try:
            if not await self._check_newman_installed():
                return self._error_output(
                    "Newman is not installed. Install with: npm install -g newman"
                )

            if not collection:
                return self._error_output("Collection path is required")

            results = await self.runner.run_collection(
                collection=collection,
                environment=environment,
                iteration_count=iteration_count,
                iteration_data=iteration_data,
                delay_request=delay_request,
                report_format=report_format
            )

            return {
                "status": "success",
                "summary": results["summary"],
                "results": results,
                "error": None
            }

        except FileNotFoundError as e:
            return self._error_output(str(e))
        except ValueError as e:
            return self._error_output(str(e))
        except asyncio.TimeoutError:
            return self._error_output("Collection execution timed out")
        except Exception as e:
            logger.exception("Postman execution failed")
            return self._error_output(str(e))

    async def _check_newman_installed(self) -> bool:
        """Check if Newman CLI is installed."""
        if self._newman_available is not None:
            return self._newman_available

        try:
            result = subprocess.run(
                ["newman", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            self._newman_available = result.returncode == 0
        except Exception:
            self._newman_available = False

        return self._newman_available

    def _error_output(self, error: str) -> PostmanOutput:
        """Create standardized error output."""
        return {
            "status": "error",
            "summary": None,
            "results": None,
            "error": error
        }
