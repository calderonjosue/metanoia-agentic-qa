"""Telemetry collection for Metanoia-QA metrics.

Collects and stores test duration, pass/fail rates, and agent performance
metrics using Supabase for storage with 30-day retention.
"""

from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

from pydantic import BaseModel, Field

from src.knowledge.client import get_supabase_client


class MetricPoint(BaseModel):
    timestamp: datetime
    metric_name: str
    value: float
    tags: dict[str, str] = Field(default_factory=dict)


class TestMetrics(BaseModel):
    test_case_id: str
    duration_seconds: float
    passed: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: Optional[str] = None
    sprint_id: Optional[str] = None
    module: Optional[str] = None


class AgentPerformance(BaseModel):
    agent_id: str
    agent_type: str
    duration_seconds: float
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    output_size: int = 0
    error_message: Optional[str] = None


@dataclass
class TelemetryConfig:
    retention_days: int = 30
    batch_size: int = 100
    flush_interval_seconds: float = 60.0


class TelemetryCollector:
    """Collects and stores telemetry data for the STLC pipeline.

    Attributes:
        supabase: Supabase client for storage
        config: Telemetry configuration
        _metrics_buffer: In-memory buffer for metrics pending flush
    """

    def __init__(
        self,
        supabase_client=None,
        config: Optional[TelemetryConfig] = None,
    ):
        """Initialize the telemetry collector.

        Args:
            supabase_client: Optional Supabase client (uses default if not provided)
            config: Telemetry configuration
        """
        self.supabase = supabase_client or get_supabase_client()
        self.config = config or TelemetryConfig()
        self._metrics_buffer: list[dict] = []
        self._last_flush = datetime.utcnow()

    async def record_test_metrics(self, metrics: TestMetrics) -> None:
        """Record test execution metrics.

        Args:
            metrics: Test metrics to record
        """
        record = {
            "test_case_id": metrics.test_case_id,
            "duration_seconds": metrics.duration_seconds,
            "passed": metrics.passed,
            "timestamp": metrics.timestamp.isoformat(),
            "agent_id": metrics.agent_id,
            "sprint_id": metrics.sprint_id,
            "module": metrics.module,
        }
        self._metrics_buffer.append(record)

        if len(self._metrics_buffer) >= self.config.batch_size:
            await self._flush()

    async def record_agent_performance(self, performance: AgentPerformance) -> None:
        """Record agent execution performance.

        Args:
            performance: Agent performance data
        """
        record = {
            "agent_id": performance.agent_id,
            "agent_type": performance.agent_type,
            "duration_seconds": performance.duration_seconds,
            "status": performance.status,
            "timestamp": performance.timestamp.isoformat(),
            "output_size": performance.output_size,
            "error_message": performance.error_message,
        }
        self._metrics_buffer.append(record)

        if len(self._metrics_buffer) >= self.config.batch_size:
            await self._flush()

    async def record_metric(
        self,
        metric_name: str,
        value: float,
        tags: Optional[dict[str, str]] = None,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Record a generic metric point.

        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags/labels
            timestamp: Optional timestamp (defaults to now)
        """
        record = {
            "metric_name": metric_name,
            "value": value,
            "timestamp": (timestamp or datetime.utcnow()).isoformat(),
            "tags": tags or {},
        }
        self._metrics_buffer.append(record)

        if len(self._metrics_buffer) >= self.config.batch_size:
            await self._flush()

    async def _flush(self) -> None:
        """Flush buffered metrics to Supabase."""
        if not self._metrics_buffer:
            return

        cutoff = datetime.utcnow() - timedelta(days=self.config.retention_days)
        cutoff_str = cutoff.isoformat()

        self.supabase.table("telemetry_metrics").insert(self._metrics_buffer).execute()

        self.supabase.table("telemetry_metrics").delete().lt(
            "timestamp", cutoff_str
        ).execute()

        self._metrics_buffer = []
        self._last_flush = datetime.utcnow()

    async def get_test_duration_stats(
        self,
        sprint_id: Optional[str] = None,
        module: Optional[str] = None,
        days: int = 30,
    ) -> dict:
        """Get test duration statistics.

        Args:
            sprint_id: Optional sprint filter
            module: Optional module filter
            days: Number of days to look back

        Returns:
            Dictionary with duration statistics
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()

        query = self.supabase.table("telemetry_metrics").select(
            "duration_seconds"
        ).gte("timestamp", cutoff_str).eq("metric_type", "test")

        if sprint_id:
            query = query.eq("sprint_id", sprint_id)
        if module:
            query = query.eq("module", module)

        response = query.execute()

        if not response.data:
            return {"count": 0, "mean": 0, "p50": 0, "p95": 0, "p99": 0}

        durations: list[float] = [float(r["duration_seconds"]) for r in response.data if isinstance(r, dict) and "duration_seconds" in r]
        sorted_durations = sorted(durations)

        return {
            "count": len(durations),
            "mean": sum(durations) / len(durations),
            "p50": sorted_durations[len(sorted_durations) // 2],
            "p95": sorted_durations[int(len(sorted_durations) * 0.95)],
            "p99": sorted_durations[int(len(sorted_durations) * 0.99)],
        }

    async def get_pass_fail_rates(
        self,
        sprint_id: Optional[str] = None,
        days: int = 30,
    ) -> dict:
        """Get pass/fail rates.

        Args:
            sprint_id: Optional sprint filter
            days: Number of days to look back

        Returns:
            Dictionary with pass/fail counts and rates
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()

        query = self.supabase.table("telemetry_metrics").select(
            "passed"
        ).gte("timestamp", cutoff_str).eq("metric_type", "test")

        if sprint_id:
            query = query.eq("sprint_id", sprint_id)

        response = query.execute()

        if not response.data:
            return {"total": 0, "passed": 0, "failed": 0, "pass_rate": 0.0}

        total = len(response.data)
        passed = sum(1 for r in response.data if isinstance(r, dict) and r.get("passed", False))

        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total > 0 else 0.0,
        }

    async def get_agent_performance_stats(
        self,
        agent_type: Optional[str] = None,
        days: int = 30,
    ) -> dict:
        """Get agent performance statistics.

        Args:
            agent_type: Optional agent type filter
            days: Number of days to look back

        Returns:
            Dictionary with agent performance stats
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()

        query = self.supabase.table("telemetry_metrics").select(
            "agent_id", "agent_type", "duration_seconds", "status"
        ).gte("timestamp", cutoff_str).eq("metric_type", "agent")

        if agent_type:
            query = query.eq("agent_type", agent_type)

        response = query.execute()

        if not response.data:
            return {"total_executions": 0, "success_rate": 0.0, "avg_duration": 0.0}

        total = len(response.data)
        successful = sum(1 for r in response.data if isinstance(r, dict) and r.get("status") == "completed")
        durations: list[float] = [float(r["duration_seconds"]) for r in response.data if isinstance(r, dict) and "duration_seconds" in r]

        return {
            "total_executions": total,
            "success_rate": successful / total if total > 0 else 0.0,
            "avg_duration": sum(durations) / len(durations) if durations else 0.0,
        }
