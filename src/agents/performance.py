"""Performance Test Engineer agent for Metanoia-QA.

Executes k6 load tests and analyzes performance metrics.
"""

import asyncio
import logging
import re
from typing import Optional

from pydantic import BaseModel

from skill_runtime.loader import SkillLoader
from skill_runtime.executor import SkillExecutorEngine, create_executor

logger = logging.getLogger(__name__)


class PerformanceMetrics(BaseModel):
    """Performance test metrics."""
    response_time_p95: float
    response_time_p99: Optional[float] = None
    throughput_rps: float
    error_rate: float
    duration: float
    vus: int


class TestResult(BaseModel):
    """Result of test execution."""
    passed: int
    failed: int
    skipped: int
    duration: float
    report_url: Optional[str] = None
    metrics: Optional[PerformanceMetrics] = None
    regressions: list[dict] = []


class PerformanceEngineer:
    """Performance Test Engineer that executes k6 load tests.
    
    Responsibilities:
    - Identify bottleneck endpoints from code changes
    - Generate k6 load scripts using k6-executor skill
    - Execute performance tests
    - Analyze results (response time, throughput)
    - Flag performance regressions
    """

    name = "performance-engineer"
    version = "1.0.0"

    THRESHolds = {
        "http_req_duration_p95": 500,
        "http_req_duration_p99": 1000,
        "error_rate": 0.05,
        "throughput_min": 10
    }

    def __init__(self):
        self._skill_loader = SkillLoader()
        self._executor_engine = create_executor(timeout_seconds=3600.0)
        self._k6_executor = None
        self._baseline_metrics: dict = {}

    async def execute(self, test_cases: list[dict], context: dict) -> TestResult:
        """Execute performance tests and return results.
        
        Args:
            test_cases: List of endpoint configurations.
            context: Execution context with base_url, vus, duration.
            
        Returns:
            TestResult with metrics and regression flags.
        """
        k6_executor = self._get_k6_executor()
        if k6_executor is None:
            logger.error("k6 executor not available")
            return TestResult(
                passed=0,
                failed=len(test_cases),
                skipped=0,
                duration=0.0,
                regressions=[{"error": "k6 executor not available"}]
            )

        endpoints = self._extract_endpoints(test_cases)
        base_url = context.get("base_url", "http://localhost:3000")
        vus = context.get("vus", 10)
        duration = context.get("duration", "30s")

        input_data = {
            "endpoints": endpoints,
            "base_url": base_url,
            "vus": vus,
            "duration": duration,
            "output_json": True
        }

        try:
            result = await self._executor_engine.execute(k6_executor, input_data)
            
            if result["status"] == "error":
                return TestResult(
                    passed=0,
                    failed=1,
                    skipped=0,
                    duration=0.0,
                    regressions=[{"error": result.get("error", "Unknown error")}]
                )

            data = result.get("data", {})
            metrics = self._parse_metrics(data)
            regressions = self._detect_regressions(metrics)

            return TestResult(
                passed=1 if not regressions else 0,
                failed=len(regressions),
                skipped=0,
                duration=result.get("execution_time_ms", 0) / 1000,
                metrics=metrics,
                regressions=regressions
            )

        except Exception as e:
            logger.exception("Performance test execution failed")
            return TestResult(
                passed=0,
                failed=1,
                skipped=0,
                duration=0.0,
                regressions=[{"error": str(e)}]
            )

    async def heal(self, failure: dict) -> dict:
        """Attempt to address performance issues.
        
        Args:
            failure: Failure information with endpoint, metric, value.
            
        Returns:
            Analysis result with recommendations.
        """
        endpoint = failure.get("endpoint", "")
        slow_metric = failure.get("metric", "")
        value = failure.get("value", 0)

        recommendations = []

        if "p95" in slow_metric or "p99" in slow_metric:
            recommendations.append({
                "type": "timeout",
                "suggestion": f"Consider increasing timeout for {endpoint}",
                "severity": "medium"
            })
            
        if value > self.THRESHolds.get("http_req_duration_p99", 1000):
            recommendations.append({
                "type": "bottleneck",
                "suggestion": f"Possible bottleneck at {endpoint} - consider optimization",
                "severity": "high"
            })

        return {
            "status": "analyzed",
            "endpoint": endpoint,
            "metric": slow_metric,
            "value": value,
            "recommendations": recommendations
        }

    def identify_bottlenecks(self, code_changes: list[dict]) -> list[str]:
        """Identify potential bottleneck endpoints from code changes.
        
        Args:
            code_changes: List of code change dictionaries.
            
        Returns:
            List of potentially affected endpoints.
        """
        bottlenecks = []
        
        slow_patterns = [
            r"database",
            r"query",
            r"loop.*select",
            r"for.*each",
            r"sleep",
            r"wait.*for",
            r"aiohttp",
            r"requests\.get",
            r"fetch\(",
        ]
        
        for change in code_changes:
            file_path = change.get("file", "")
            diff = change.get("diff", "")
            
            for pattern in slow_patterns:
                if re.search(pattern, diff, re.IGNORECASE):
                    endpoint = self._infer_endpoint(file_path)
                    if endpoint and endpoint not in bottlenecks:
                        bottlenecks.append(endpoint)

        return bottlenecks

    def generate_load_script(
        self,
        endpoints: list[dict],
        base_url: str,
        vus: int = 10,
        duration: str = "30s"
    ) -> str:
        """Generate k6 load script from endpoint configuration.
        
        Args:
            endpoints: List of endpoint configs.
            base_url: Base URL for the API.
            vus: Number of virtual users.
            duration: Test duration.
            
        Returns:
            k6 script as string.
        """
        k6_executor = self._get_k6_executor()
        if k6_executor is None:
            return ""

        from metanoia.skills.k6_executor.executor import K6ScriptGenerator
        return str(K6ScriptGenerator.generate_from_endpoints(endpoints, base_url, vus, duration))

    def set_baseline(self, metrics: dict) -> None:
        """Set baseline metrics for regression comparison.
        
        Args:
            metrics: Baseline performance metrics.
        """
        self._baseline_metrics = metrics.copy()

    def get_baseline(self) -> dict:
        """Get current baseline metrics."""
        return self._baseline_metrics.copy()

    def _get_k6_executor(self):
        """Get or create k6 executor instance."""
        if self._k6_executor is None:
            executor_class = self._skill_loader.load_skill("k6-executor")
            if executor_class:
                self._k6_executor = executor_class()
        return self._k6_executor

    def _extract_endpoints(self, test_cases: list[dict]) -> list[dict]:
        """Extract endpoint configurations from test cases."""
        endpoints = []
        
        for tc in test_cases:
            if "endpoint" in tc:
                endpoints.append({
                    "method": tc.get("method", "GET").upper(),
                    "path": tc["endpoint"],
                    "headers": tc.get("headers", {}),
                    "body": tc.get("body")
                })
            elif "url" in tc:
                path = tc["url"]
                if path.startswith("http"):
                    path = path.split(tc.get("base_url", ""), 1)[-1] if "base_url" in tc else path
                endpoints.append({
                    "method": tc.get("method", "GET").upper(),
                    "path": path,
                    "headers": tc.get("headers", {}),
                    "body": tc.get("body")
                })
        
        return endpoints

    def _parse_metrics(self, data: dict) -> Optional[PerformanceMetrics]:
        """Parse k6 output into PerformanceMetrics."""
        try:
            metrics = data.get("metrics", {})
            
            http_duration = metrics.get("http_req_duration", {})
            p95 = http_duration.get("p(95)", 0) if isinstance(http_duration, dict) else 0
            p99 = http_duration.get("p(99)", 0) if isinstance(http_duration, dict) else 0
            
            throughput = metrics.get("http_reqs", {})
            rps = throughput.get("rate", 0) if isinstance(throughput, dict) else 0
            
            errors = metrics.get("errors", {})
            error_rate = errors.get("rate", 0) if isinstance(errors, dict) else 0
            
            return PerformanceMetrics(
                response_time_p95=p95,
                response_time_p99=p99,
                throughput_rps=rps,
                error_rate=error_rate,
                duration=data.get("duration", 0),
                vus=data.get("vus", 0)
            )
        except Exception as e:
            logger.warning(f"Failed to parse metrics: {e}")
            return None

    def _detect_regressions(self, metrics: Optional[PerformanceMetrics]) -> list[dict]:
        """Detect performance regressions against thresholds or baseline."""
        regressions = []
        
        if metrics is None:
            return [{"type": "parse_error", "message": "Could not parse metrics"}]

        if metrics.response_time_p95 > self.THRESHolds["http_req_duration_p95"]:
            regressions.append({
                "type": "latency",
                "metric": "p95_response_time",
                "value": metrics.response_time_p95,
                "threshold": self.THRESHolds["http_req_duration_p95"],
                "severity": "high" if metrics.response_time_p95 > self.THRESHolds["http_req_duration_p99"] else "medium"
            })

        if metrics.response_time_p99 and metrics.response_time_p99 > self.THRESHolds["http_req_duration_p99"]:
            regressions.append({
                "type": "latency",
                "metric": "p99_response_time",
                "value": metrics.response_time_p99,
                "threshold": self.THRESHolds["http_req_duration_p99"],
                "severity": "high"
            })

        if metrics.error_rate > self.THRESHolds["error_rate"]:
            regressions.append({
                "type": "reliability",
                "metric": "error_rate",
                "value": metrics.error_rate,
                "threshold": self.THRESHolds["error_rate"],
                "severity": "high" if metrics.error_rate > 0.1 else "medium"
            })

        if self._baseline_metrics:
            baseline = self._baseline_metrics
            p95_delta = metrics.response_time_p95 - baseline.get("p95", 0)
            if p95_delta > 0.1 * baseline.get("p95", 1):
                regressions.append({
                    "type": "regression",
                    "metric": "p95_delta",
                    "value": p95_delta,
                    "baseline": baseline.get("p95", 0),
                    "severity": "medium"
                })

        return regressions

    def _infer_endpoint(self, file_path: str) -> str:
        """Infer endpoint from file path."""
        path = file_path.lower()
        
        if "api" in path or "routes" in path or "endpoints" in path:
            parts = file_path.split("/")
            for i, part in enumerate(parts):
                if part in ("api", "routes", "endpoints") and i + 1 < len(parts):
                    return f"/{parts[i + 1].replace('.py', '')}"
        
        return ""
