"""New Relic APM integration for Metanoia-QA.

Provides metrics and trace collection via the New Relic API.
"""

import os
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MetricData(BaseModel):
    metric_name: str
    value: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tags: dict[str, str] = Field(default_factory=dict)


class TraceSpan(BaseModel):
    name: str
    service: str
    resource: str
    span_type: str = "custom"
    start_ms: int
    duration_ms: int
    tags: dict[str, str] = Field(default_factory=dict)
    error: bool = False
    error_message: Optional[str] = None


class NewRelicAPM:
    """New Relic APM client for metrics and trace collection.

    Requires NEW_RELIC_LICENSE_KEY environment variable.

    Attributes:
        license_key: New Relic license key
        account_id: New Relic account ID
    """

    def __init__(
        self,
        license_key: Optional[str] = None,
        account_id: Optional[str] = None,
    ):
        """Initialize the New Relic APM client.

        Args:
            license_key: New Relic license key (defaults to NEW_RELIC_LICENSE_KEY env var)
            account_id: New Relic account ID (defaults to NEW_RELIC_ACCOUNT_ID env var)
        """
        self.license_key = license_key or os.getenv("NEW_RELIC_LICENSE_KEY")
        self.account_id = account_id or os.getenv("NEW_RELIC_ACCOUNT_ID")

        if not self.license_key:
            raise ValueError(
                "New Relic license key is required. Set NEW_RELIC_LICENSE_KEY "
                "environment variable or pass license_key parameter."
            )

        self._metrics_endpoint = "https://metric-api.newrelic.com/metrics/v1"
        self._traces_endpoint = "https://trace-api.newrelic.com/trace/v1"

    def send_metric(self, metric: MetricData) -> bool:
        """Send a metric to New Relic.

        Args:
            metric: Metric data to send

        Returns:
            True if successful, False otherwise
        """
        try:
            import newrelic.agent

            if newrelic.agent.application():
                newrelic.agent.record_custom_metric(
                    metric.metric_name,
                    metric.value,
                    tags=metric.tags,
                )
                return True

        except ImportError:
            pass

        return self._send_metric_via_api(metric)

    def _send_metric_via_api(self, metric: MetricData) -> bool:
        """Send metric via New Relic REST API.

        Args:
            metric: Metric data to send

        Returns:
            True if successful, False otherwise
        """
        import requests  # type: ignore[import-untyped]

        headers = {
            "Content-Type": "application/json",
            "Api-Key": self.license_key,
        }

        metric_attrs = {
            **{k: str(v) for k, v in metric.tags.items()},
            "service": "metanoia-qa",
        }

        payload = {
            "metrics": [
                {
                    "name": metric.metric_name,
                    "type": "gauge",
                    "value": metric.value,
                    "timestamp": int(metric.timestamp.timestamp() * 1000),
                    "attributes": metric_attrs,
                }
            ]
        }

        try:
            response = requests.post(
                self._metrics_endpoint,
                headers=headers,
                json=payload,
                timeout=10,
            )
            return response.status_code in (200, 201, 202, 204)
        except Exception:
            return False

    def send_trace(self, span: TraceSpan) -> bool:
        """Send a trace span to New Relic.

        Args:
            span: Trace span data

        Returns:
            True if successful, False otherwise
        """
        import requests

        headers = {
            "Content-Type": "application/json",
            "Api-Key": self.license_key,
        }

        trace_payload = {
            "common": {
                "attributes": {
                    "service": span.service,
                    "env": os.getenv("NEW_RELIC_ENV", "production"),
                }
            },
            "spans": [
                {
                    "id": str(hash(f"{span.name}{span.resource}"))[:16],
                    "trace.id": str(hash(span.name))[:32],
                    "name": span.name,
                    "service.name": span.service,
                    "resource.name": span.resource,
                    "type": span.span_type,
                    "timestamp": span.start_ms,
                    "duration.ms": span.duration_ms,
                    "attributes": {
                        **{k: str(v) for k, v in span.tags.items()},
                    },
                    "error": span.error,
                }
            ],
        }

        if span.error and span.error_message:
            trace_payload["spans"][0]["error.message"] = span.error_message  # type: ignore[index]

        try:
            response = requests.post(
                self._traces_endpoint,
                headers=headers,
                json=trace_payload,
                timeout=10,
            )
            return response.status_code in (200, 201, 202, 204)
        except Exception:
            return False

    def send_metrics_batch(self, metrics: list[MetricData]) -> int:
        """Send multiple metrics in a batch.

        Args:
            metrics: List of metrics to send

        Returns:
            Number of successfully sent metrics
        """
        success_count = 0
        for metric in metrics:
            if self.send_metric(metric):
                success_count += 1
        return success_count

    def send_traces_batch(self, spans: list[TraceSpan]) -> int:
        """Send multiple trace spans in a batch.

        Args:
            spans: List of trace spans to send

        Returns:
            Number of successfully sent spans
        """
        success_count = 0
        for span in spans:
            if self.send_trace(span):
                success_count += 1
        return success_count

    def create_transaction(
        self,
        name: str,
        group: Optional[str] = None,
    ):
        """Create a New Relic transaction context.

        Args:
            name: Transaction name
            group: Optional transaction group

        Returns:
            Transaction context manager
        """
        try:
            import newrelic.agent
            return newrelic.agent.BackgroundTask(
                newrelic.agent.application(),
                name=name,
                group=group or "Custom",
            )
        except ImportError:
            from contextlib import nullcontext
            return nullcontext()
