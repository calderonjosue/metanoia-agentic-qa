"""k6 executor for performance testing.

This skill provides performance testing capabilities using k6
for load generation, stress testing, and scalability analysis.
"""

import asyncio
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Any, TypedDict

from metanoia.skills.base import SkillExecutor, SkillInput, SkillOutput

logger = logging.getLogger(__name__)


class K6Input(TypedDict):
    """Input schema for k6 executor."""
    script: str
    vus: int
    duration: str
    thresholds: dict | None
    output_json: bool | None


class K6Output(TypedDict):
    """Output schema for k6 executor."""
    status: str
    metrics: dict | None
    summary: str | None
    error: str | None


class K6ScriptGenerator:
    """Generates k6 scripts from configuration."""

    @staticmethod
    def generate_from_endpoints(
        endpoints: list[dict],
        base_url: str,
        vus: int = 10,
        duration: str = "30s"
    ) -> str:
        """Generate a k6 script from endpoint configuration.
        
        Args:
            endpoints: List of endpoint configs with method, path, headers.
            base_url: Base URL for the API.
            vus: Number of virtual users.
            duration: Test duration.
            
        Returns:
            k6 script as string.
        """
        import_payloads = [
            'import http from "k6/http";',
            'import { check, sleep } from "k6";',
            'import { Rate, Trend } from "k6/metrics";'
        ]
        
        custom_metrics = [
            'const errorRate = new Rate("errors");',
            'const responseTime = new Trend("response_time");'
        ]
        
        options = f'''
export const options = {{
    vus: {vus},
    duration: "{duration}",
    thresholds: {{
        http_req_duration: ["p(95)<500"],
        errors: ["rate<0.1"]
    }}
}};
'''
        
        setup = '''
export function setup() {{
    return {{ baseURL: "__BASE_URL__" }};
}}
'''
        
        default_function = '''
export default function(data) {{
    // Test scenarios here
'''
        
        scenarios = []
        for i, endpoint in enumerate(endpoints):
            method = endpoint.get("method", "GET").upper()
            path = endpoint.get("path", "/")
            
            if method == "GET":
                scenarios.append(f'''
    const res_{i} = http.get(data.baseURL + "{path}");
    check(res_{i}, {{
        "status is 200": (r) => r.status === 200
    }});
    errorRate.add(res_{i}.status !== 200);
    responseTime.add(res_{i}.timings.duration);
''')
            elif method == "POST":
                body = json.dumps(endpoint.get("body", {}))
                scenarios.append(f'''
    const res_{i} = http.post(data.baseURL + "{path}", {body}, {{
        headers: {{ "Content-Type": "application/json" }}
    }});
    check(res_{i}, {{
        "status is 201": (r) => r.status === 201
    }});
    errorRate.add(res_{i}.status !== 201);
    responseTime.add(res_{i}.timings.duration);
''')
        
        default_function += "".join(scenarios)
        default_function += "\n    sleep(1);\n}"
        
        script = "\n".join(import_payloads + custom_metrics) + options + setup + default_function
        return script.replace('"__BASE_URL__"', '"' + base_url + '"')


class K6Executor(SkillExecutor):
    """Performance testing executor using k6."""

    name = "k6-executor"
    version = "1.0.0"

    def __init__(self):
        super().__init__()
        self._k6_available: bool | None = None

    async def execute(self, input_data: K6Input) -> K6Output:
        """Execute a k6 performance test.
        
        Args:
            input_data: Test configuration (script, vus, duration, etc.)
            
        Returns:
            K6Output with metrics and summary.
        """
        script = input_data.get("script", "")
        vus = input_data.get("vus", 10)
        duration = input_data.get("duration", "30s")
        output_json = input_data.get("output_json", True)
        
        try:
            if not await self._check_k6_installed():
                return self._error_output(
                    "k6 is not installed. Install from https://k6.io/docs/getting-started/installation/"
                )
            
            # If script looks like config rather than actual k6 script
            if script.startswith("{") or script.startswith("["):
                try:
                    config = json.loads(script)
                    if isinstance(config, list):
                        base_url = input_data.get("base_url", "http://localhost:3000")
                        script = K6ScriptGenerator.generate_from_endpoints(
                            config, base_url, vus, duration
                        )
                    elif isinstance(config, dict):
                        base_url = config.get("base_url", "http://localhost:3000")
                        endpoints = config.get("endpoints", [])
                        script = K6ScriptGenerator.generate_from_endpoints(
                            endpoints, base_url, vus, duration
                        )
                except json.JSONDecodeError:
                    return self._error_output("Invalid script configuration")
            
            result = await self._run_k6(script, output_json)
            return result
            
        except Exception as e:
            logger.exception("k6 execution failed")
            return self._error_output(str(e))

    async def _check_k6_installed(self) -> bool:
        """Check if k6 is installed."""
        if self._k6_available is not None:
            return self._k6_available
        
        try:
            result = subprocess.run(
                ["k6", "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            self._k6_available = result.returncode == 0
        except Exception:
            self._k6_available = False
        
        return self._k6_available

    async def _run_k6(self, script: str, output_json: bool) -> K6Output:
        """Run k6 with the given script."""
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.js',
            delete=False
        ) as f:
            f.write(script)
            script_path = f.name
        
        try:
            cmd = ["k6", "run"]
            if output_json:
                cmd.append("--out")
                cmd.append("json=results.json")
            cmd.extend(["--summary-export", "summary.json"])
            cmd.append(script_path)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=3600  # 1 hour max
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                return self._error_output(f"k6 failed: {error_msg}")
            
            # Parse results
            metrics = self._parse_results()
            summary = self._generate_summary(metrics)
            
            return {
                "status": "success",
                "metrics": metrics,
                "summary": summary,
                "error": None
            }
            
        finally:
            Path(script_path).unlink(missing_ok=True)

    def _parse_results(self) -> dict:
        """Parse k6 results from JSON output."""
        try:
            if Path("results.json").exists():
                with open("results.json", "r") as f:
                    return {"raw_output": "see results.json"}
        except Exception:
            pass
        
        try:
            if Path("summary.json").exists():
                with open("summary.json", "r") as f:
                    return json.load(f)
        except Exception:
            pass
        
        return {}

    def _generate_summary(self, metrics: dict) -> str:
        """Generate human-readable summary from metrics."""
        return f"""k6 Performance Test Results

Status: {'Passed' if metrics else 'Completed'}

Key Metrics:
- Virtual Users: Configured as specified
- Duration: As specified
- See detailed metrics in results.json
"""

    def _error_output(self, error: str) -> K6Output:
        """Create error output."""
        return {
            "status": "error",
            "metrics": None,
            "summary": None,
            "error": error
        }
