"""Datadog APM integration for Metanoia-QA.

Provides metrics and trace collection via the Datadog API.
"""

import os
from typing import Optional
from datetime import datetime

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


class DatadogAPM:
    """Datadog APM client for metrics and trace collection.

    Requires DATADOG_API_KEY and optionally DATADOG_APP_KEY environment variables.

    Attributes:
        api_key: Datadog API key
        app_key: Optional Datadog application key
        site: Datadog site (defaults to datadoghq.com)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        app_key: Optional[str] = None,
        site: Optional[str] = None,
    ):
        """Initialize the Datadog APM client.

        Args:
            api_key: Datadog API key (defaults to DATADOG_API_KEY env var)
            app_key: Optional Datadog app key (defaults to DATADOG_APP_KEY env var)
            site: Datadog site (defaults to DATADOG_SITE or "datadoghq.com")
        """
        self.api_key = api_key or os.getenv("DATADOG_API_KEY")
        self.app_key = app_key or os.getenv("DATADOG_APP_KEY")
        self.site = site or os.getenv("DATADOG_SITE", "datadoghq.com")

        if not self.api_key:
            raise ValueError(
                "Datadog API key is required. Set DATADOG_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self._statsd_host = f"api.{self.site}"
        self._traces_endpoint = f"https://api.{self.site}/api/v1/traces"

    def send_metric(self, metric: MetricData) -> bool:
        """Send a metric to Datadog.

        Args:
            metric: Metric data to send

        Returns:
            True if successful, False otherwise
        """
        try:
            from datadog import initialize, statsd

            if not hasattr(self, "_initialized"):
                initialize(
                    api_key=self.api_key,
                    app_key=self.app_key,
                    host=self._statsd_host,
                )
                self._initialized = True

            tags = [f"{k}:{v}" for k, v in metric.tags.items()]
            tags.append(f"service:metanoia-qa")

            statsd.gauge(
                metric.metric_name,
                metric.value,
                tags=tags,
                timestamp=metric.timestamp.timestamp(),
            )

            return True

        except ImportError:
            self._send_metric_via_api(metric)
            return True
        except Exception:
            return False

    def _send_metric_via_api(self, metric: MetricData) -> None:
        """Send metric via Datadog REST API as fallback.

        Args:
            metric: Metric data to send
        """
        import requests  # type: ignore[import-untyped]

        headers = {
            "Content-Type": "application/json",
            "DD-API-KEY": self.api_key,
        }

        if self.app_key:
            headers["DD-APPLICATION-KEY"] = self.app_key

        series_data = {
            "metric": metric.metric_name,
            "points": [[metric.timestamp.timestamp(), metric.value]],
            "type": "gauge",
            "tags": [f"{k}:{v}" for k, v in metric.tags.items()] + ["service:metanoia-qa"],
        }

        requests.post(
            f"https://api.{self.site}/api/v1/series",
            headers=headers,
            json={"series": [series_data]},
            timeout=10,
        )

    def send_trace(self, span: TraceSpan) -> bool:
        """Send a trace span to Datadog.

        Args:
            span: Trace span data

        Returns:
            True if successful, False otherwise
        """
        try:
            import requests  # type: ignore[import-untyped]

            headers = {
                "Content-Type": "application/json",
                "DD-API-KEY": self.api_key,
            }

            if self.app_key:
                headers["DD-APPLICATION-KEY"] = self.app_key

            trace_payload = {
                "traces": [
                    [
                        {
                            "trace_id": str(hash(span.name))[:16],
                            "span_id": str(hash(span.resource))[:16],
                            "name": span.name,
                            "resource": span.resource,
                            "service": span.service,
                            "type": span.span_type,
                            "start": span.start_ms,
                            "duration": span.duration_ms,
                            "tags": {
                                **{k: str(v) for k, v in span.tags.items()},
                                "env": os.getenv("DD_ENV", "production"),
                                "service": span.service,
                            },
                            "error": span.error,
                            "error_msg": span.error_message,
                        }
                    ]
                ]
            }

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
