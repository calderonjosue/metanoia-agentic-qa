"""Behave executor for BDD testing.

This skill provides BDD testing capabilities using Behave,
the Python BDD framework.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, TypedDict

from behave.__main__ import main as behave_main

logger = logging.getLogger(__name__)


class BehaveInput(TypedDict):
    """Input schema for Behave executor."""
    features: list[str]
    tags: list[str] | None
    steps_module: str | None
    format: str | None
    define: dict[str, str] | None
    userdata: dict[str, str] | None


class BehaveOutput(TypedDict):
    """Output schema for Behave executor."""
    status: str
    passed: int
    failed: int
    skipped: int
    results: str | None
    error: str | None


class BehaveExecutor:
    """BDD testing executor using Behave framework."""

    name = "behave-executor"
    version = "1.0.0"

    def __init__(self):
        self._results: dict[str, Any] | None = None

    async def execute(self, input_data: BehaveInput) -> BehaveOutput:
        """Execute Behave BDD tests.

        Args:
            input_data: Configuration for Behave execution.
                - features: List of feature file paths or directories.
                - tags: Optional list of tags to filter scenarios.
                - steps_module: Optional module path for step definitions.
                - format: Output format (json, plain, etc.).
                - define: User-defined attributes (key=value pairs).
                - userdata: Additional user data.

        Returns:
            BehaveOutput with status and test results.
        """
        features = input_data.get("features", [])
        tags = input_data.get("tags")
        steps_module = input_data.get("steps_module")
        output_format = input_data.get("format", "json")
        define_vars = input_data.get("define", {})
        userdata = input_data.get("userdata", {})

        if not features:
            return self._error_output("No features specified")

        try:
            return await self._run_behave(
                features=features,
                tags=tags,
                steps_module=steps_module,
                output_format=output_format,
                define_vars=define_vars,
                userdata=userdata
            )
        except Exception as e:
            logger.exception("Behave execution failed")
            return self._error_output(str(e))

    async def _run_behave(
        self,
        features: list[str],
        tags: list[str] | None,
        steps_module: str | None,
        output_format: str,
        define_vars: dict[str, str],
        userdata: dict[str, str]
    ) -> BehaveOutput:
        """Run Behave with specified configuration."""
        if steps_module:
            if steps_module not in sys.path:
                sys.path.insert(0, os.getcwd())

        cmd_args = []

        for feature in features:
            if os.path.isdir(feature):
                cmd_args.append(feature)
            elif os.path.isfile(feature):
                cmd_args.append(feature)
            else:
                cmd_args.append(feature)

        if tags:
            tag_expression = self._build_tag_expression(tags)
            cmd_args.extend(["--tags", tag_expression])

        if output_format == "json":
            cmd_args.extend(["--format", "json"])
            cmd_args.extend(["--outfile", "behave.json"])

        for key, value in define_vars.items():
            cmd_args.extend(["--define", f"{key}={value}"])

        for key, value in userdata.items():
            cmd_args.extend(["--userdata", f"{key}={value}"])

        cmd_args.append("--no-color")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._execute_behave,
            cmd_args
        )

        return self._parse_results(result)

    def _execute_behave(self, cmd_args: list[str]) -> int:
        """Execute Behave CLI and return exit code."""
        logger.info(f"Running Behave with args: {' '.join(cmd_args)}")

        original_cwd = os.getcwd()
        try:
            return behave_main(cmd_args)
        finally:
            os.chdir(original_cwd)

    def _build_tag_expression(self, tags: list[str]) -> str:
        """Build Behave tag expression from tag list."""
        return ",".join(tags)

    def _parse_results(self, exit_code: int) -> BehaveOutput:
        """Parse Behave execution results."""
        passed = 0
        failed = 0
        skipped = 0
        results_json: str | None = None

        if os.path.exists("behave.json"):
            try:
                with open("behave.json", "r") as f:
                    data = json.load(f)
                    for feature in data:
                        for scenario in feature.get("elements", []):
                            status = scenario.get("status", "skipped")
                            if status == "passed":
                                passed += 1
                            elif status == "failed":
                                failed += 1
                            elif status == "skipped":
                                skipped += 1
                    results_json = json.dumps(data, indent=2)
            except Exception as e:
                logger.warning(f"Failed to parse behave.json: {e}")

        status = "success" if exit_code == 0 and failed == 0 else "error"

        return {
            "status": status,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "results": results_json,
            "error": None if status == "success" else "Tests failed"
        }

    def _error_output(self, error: str) -> BehaveOutput:
        """Create error output."""
        return {
            "status": "error",
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "results": None,
            "error": error
        }

    async def cleanup(self) -> None:
        """Cleanup temporary files."""
        if os.path.exists("behave.json"):
            try:
                os.remove("behave.json")
            except Exception:
                pass
