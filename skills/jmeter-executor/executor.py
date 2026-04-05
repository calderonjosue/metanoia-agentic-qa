"""JMeter executor for performance testing.

This skill provides performance testing capabilities using Apache JMeter
for load generation, stress testing, and HTML report generation.
"""

import asyncio
import logging
import subprocess
from pathlib import Path
from typing import TypedDict

from metanoia.skills.base import SkillExecutor

logger = logging.getLogger(__name__)


class JMeterInput(TypedDict):
    """Input schema for JMeter executor."""
    jmx_file: str
    report_output: str | None
    results_file: str | None
    jmeter_properties: dict | None
    heap_size: str | None


class JMeterOutput(TypedDict):
    """Output schema for JMeter executor."""
    status: str
    report_path: str | None
    metrics: dict | None
    summary: str | None
    error: str | None


class JMeterExecutor(SkillExecutor):
    """Performance testing executor using Apache JMeter."""

    name = "jmeter-executor"
    version = "1.0.0"

    def __init__(self):
        super().__init__()
        self._jmeter_available: bool | None = None

    async def execute(self, input_data: JMeterInput) -> JMeterOutput:
        """Execute a JMeter performance test.
        
        Args:
            input_data: Test configuration (jmx_file, report_output, etc.)
            
        Returns:
            JMeterOutput with metrics and summary.
        """
        jmx_file = input_data.get("jmx_file", "")
        report_output = input_data.get("report_output", "")
        results_file = input_data.get("results_file", "results.jtl")
        jmeter_properties = input_data.get("jmeter_properties", {})
        heap_size = input_data.get("heap_size", "512m")
        
        try:
            if not await self._check_jmeter_installed():
                return self._error_output(
                    "JMeter is not installed. Install from https://jmeter.apache.org/download_jmeter.cgi"
                )
            
            if not jmx_file:
                return self._error_output("jmx_file is required")
            
            jmx_path = Path(jmx_file)
            if not jmx_path.exists():
                return self._error_output(f"JMX file not found: {jmx_file}")
            
            result = await self._run_jmeter(
                str(jmx_path.absolute()),
                report_output,
                results_file,
                jmeter_properties,
                heap_size
            )
            return result
            
        except Exception as e:
            logger.exception("JMeter execution failed")
            return self._error_output(str(e))

    async def _check_jmeter_installed(self) -> bool:
        """Check if JMeter is installed."""
        if self._jmeter_available is not None:
            return self._jmeter_available
        
        try:
            result = subprocess.run(
                ["jmeter", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            self._jmeter_available = result.returncode == 0
        except Exception:
            self._jmeter_available = False
        
        return self._jmeter_available

    async def _run_jmeter(
        self,
        jmx_path: str,
        report_output: str,
        results_file: str,
        jmeter_properties: dict,
        heap_size: str
    ) -> JMeterOutput:
        """Run JMeter with the given configuration."""
        cmd = [
            "jmeter",
            "-n",
            "-t", jmx_path,
            "-l", results_file,
        ]
        
        if report_output:
            report_dir = Path(report_output)
            report_dir.mkdir(parents=True, exist_ok=True)
            cmd.extend(["-e", "-o", str(report_dir.absolute())])
        
        for key, value in jmeter_properties.items():
            cmd.extend(["-J", f"{key}={value}"])
        
        if heap_size:
            cmd.extend(["-X", f"-JHEAP={heap_size}"])
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=3600
        )
        
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown error"
            return self._error_output(f"JMeter failed: {error_msg}")
        
        metrics = self._parse_results(results_file)
        summary = self._generate_summary(metrics, report_output)
        
        return {
            "status": "success",
            "report_path": report_output if report_output else None,
            "metrics": metrics,
            "summary": summary,
            "error": None
        }

    def _parse_results(self, results_file: str) -> dict:
        """Parse JMeter results from CSV/JSON output."""
        metrics = {}
        
        try:
            results_path = Path(results_file)
            if results_path.exists():
                metrics["results_file"] = results_file
                with open(results_path, "r") as f:
                    lines = f.readlines()
                    if len(lines) > 1:
                        metrics["total_samples"] = len(lines) - 1
        except Exception:
            pass
        
        return metrics

    def _generate_summary(self, metrics: dict, report_path: str | None) -> str:
        """Generate human-readable summary from metrics."""
        summary_parts = ["JMeter Performance Test Results", "", "Status: Completed"]
        
        if "total_samples" in metrics:
            summary_parts.append(f"Total Samples: {metrics['total_samples']}")
        
        if report_path:
            summary_parts.append(f"HTML Report: {report_path}")
        
        return "\n".join(summary_parts)

    def _error_output(self, error: str) -> JMeterOutput:
        """Create error output."""
        return {
            "status": "error",
            "report_path": None,
            "metrics": None,
            "summary": None,
            "error": error
        }
