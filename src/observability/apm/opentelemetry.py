"""OpenTelemetry exporter for Metanoia-QA.

Provides OTLP (OpenTelemetry Protocol) export for metrics and traces.
Configured via OTEL_EXPORTER_OTLP_ENDPOINT and related environment variables.
"""

import os
from typing import Optional
from datetime import datetime
from contextlib import contextmanager

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


class OpenTelemetryExporter:
    """OpenTelemetry OTLP exporter for metrics and traces.

    Supports configuration via environment variables:
    - OTEL_EXPORTER_OTLP_ENDPOINT: OTLP endpoint (default: http://localhost:4317)
    - OTEL_EXPORTER_OTLP_PROTOCOL: Protocol (grpc or http/protobuf)
    - OTEL_EXPORTER_OTLP_HEADERS: Comma-separated headers
    - OTEL_SERVICE_NAME: Service name (default: metanoia-qa)

    Attributes:
        endpoint: OTLP endpoint URL
        protocol: OTLP protocol (grpc or http/protobuf)
        service_name: Name of the service
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        protocol: Optional[str] = None,
        service_name: Optional[str] = None,
    ):
        """Initialize the OpenTelemetry exporter.

        Args:
            endpoint: OTLP endpoint (defaults to OTEL_EXPORTER_OTLP_ENDPOINT or localhost:4317)
            protocol: OTLP protocol (defaults to OTEL_EXPORTER_OTLP_PROTOCOL or grpc)
            service_name: Service name (defaults to OTEL_SERVICE_NAME or metanoia-qa)
        """
        self.endpoint = endpoint or os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"
        )
        self.protocol = protocol or os.getenv(
            "OTEL_EXPORTER_OTLP_PROTOCOL", "grpc"
        )
        self.service_name = service_name or os.getenv(
            "OTEL_SERVICE_NAME", "metanoia-qa"
        )
        self._headers = self._parse_headers(
            os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")
        )
        self._initialized = False

    def _parse_headers(self, headers_str: str) -> dict[str, str]:
        """Parse comma-separated headers string.

        Args:
            headers_str: Headers in format "key1=value1,key2=value2"

        Returns:
            Dictionary of headers
        """
        if not headers_str:
            return {}

        headers = {}
        for pair in headers_str.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                headers[key.strip()] = value.strip()
        return headers

    def _ensure_initialized(self) -> None:
        """Initialize OpenTelemetry if not already done."""
        if self._initialized:
            return

        try:
            from opentelemetry import trace, metrics
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )
            from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
                OTLPMetricExporter,
            )
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.sdk.metrics import MeterProvider
            from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
            from opentelemetry.sdk.resources import Resource, SERVICE_NAME


            resource = Resource.create({SERVICE_NAME: self.service_name})

            trace_provider = TracerProvider(resource=resource)
            trace_exporter = OTLPSpanExporter(
                endpoint=self.endpoint,
                headers=self._headers,
                insecure=self.protocol == "grpc",
            )
            trace_provider.add_span_processor(
                BatchSpanProcessor(trace_exporter)
            )
            trace.set_tracer_provider(trace_provider)

            metric_exporter = OTLPMetricExporter(
                endpoint=self.endpoint,
                headers=self._headers,
                insecure=self.protocol == "grpc",
            )
            metric_reader = PeriodicExportingMetricReader(metric_exporter)
            meter_provider = MeterProvider(
                resource=resource,
                metric_readers=[metric_reader],
            )
            metrics.set_meter_provider(meter_provider)

            self._initialized = True

        except ImportError:
            self._initialized = True

    def send_metric(self, metric: MetricData) -> bool:
        """Send a metric to the OTLP endpoint.

        Args:
            metric: Metric data to send

        Returns:
            True if successful, False otherwise
        """
        try:
            self._ensure_initialized()

            from opentelemetry import metrics

            meter = metrics.get_meter(self.service_name)

            value_counter = meter.create_counter(name=metric.metric_name)
            value_counter.add(
                metric.value,
                attributes=metric.tags,
            )

            return True

        except ImportError:
            return self._send_metric_fallback(metric)
        except Exception:
            return False

    def _send_metric_fallback(self, metric: MetricData) -> bool:
        """Fallback metric sending via direct OTLP HTTP.

        Args:
            metric: Metric data to send

        Returns:
            True if successful, False otherwise
        """
        import requests  # type: ignore[import-untyped]

        metric_definition = {
            "name": metric.metric_name,
            "description": "",
            "gauge": {
                "data_points": [
                    {
                        "as_int": int(metric.value),
                        "time_unix_nano": int(metric.timestamp.timestamp() * 1e9),
                        "attributes": [
                            {"key": k, "value": {"string_value": v}}
                            for k, v in metric.tags.items()
                        ],
                    }
                ]
            },
        }

        resource_metrics = [
            {
                "resource": {
                    "attributes": [
                        {
                            "key": "service.name",
                            "value": {"string_value": self.service_name},
                        }
                    ]
                },
                "scope_metrics": [
                    {
                        "scope": {"name": "metanoia-qa"},
                        "metrics": [metric_definition],
                    }
                ],
            }
        ]

        try:
            endpoint = self.endpoint.replace("grpc", "http") if self.endpoint else "http://localhost:4318"
            if not endpoint.endswith("/v1/metrics"):
                endpoint = f"{endpoint}/v1/metrics"

            response = requests.post(
                endpoint,
                json={"resource_metrics": resource_metrics},
                headers={
                    "Content-Type": "application/json",
                    **self._headers,
                },
                timeout=10,
            )
            return response.status_code in (200, 201, 202, 204)
        except Exception:
            return False

    def send_trace(self, span: TraceSpan) -> bool:
        """Send a trace span to the OTLP endpoint.

        Args:
            span: Trace span data

        Returns:
            True if successful, False otherwise
        """
        try:
            self._ensure_initialized()

            from opentelemetry import trace
            from opentelemetry.trace import Status, StatusCode

            tracer = trace.get_tracer(self.service_name)

            span_obj = tracer.start_span(
                name=span.name,
                attributes={
                    **span.tags,
                    "service.name": span.service,
                    "resource.name": span.resource,
                },
            )

            if span.error:
                span_obj.set_status(
                    Status(StatusCode.ERROR, span.error_message or "")
                )

            span_obj.end()

            return True

        except ImportError:
            return self._send_trace_fallback(span)
        except Exception:
            return False

    def _send_trace_fallback(self, span: TraceSpan) -> bool:
        """Fallback trace sending via direct OTLP HTTP.

        Args:
            span: Trace span data

        Returns:
            True if successful, False otherwise
        """
        import requests

        trace_data = {
            "resource_spans": [
                {
                    "resource": {
                        "attributes": [
                            {
                                "key": "service.name",
                                "value": {"string_value": span.service},
                            }
                        ]
                    },
                    "scope_spans": [
                        {
                            "scope": {"name": "metanoia-qa"},
                            "spans": [
                                {
                                    "trace_id": str(hash(span.name))[:32].ljust(32, "0"),
                                    "span_id": str(hash(span.resource))[:16].ljust(16, "0"),
                                    "name": span.name,
                                    "kind": 1,
                                    "start_time_unix_nano": span.start_ms * 1e6,
                                    "end_time_unix_nano": (span.start_ms + span.duration_ms) * 1e6,
                                    "attributes": [
                                        {"key": k, "value": {"string_value": str(v)}}
                                        for k, v in span.tags.items()
                                    ],
                                    "status": {
                                        "code": 2 if span.error else 1,
                                        "message": span.error_message or "",
                                    },
                                }
                            ],
                        }
                    ],
                }
            ]
        }

        try:
            endpoint = self.endpoint.replace("grpc", "http") if self.endpoint else "http://localhost:4318"
            if not endpoint.endswith("/v1/traces"):
                endpoint = f"{endpoint}/v1/traces"

            response = requests.post(
                endpoint,
                json=trace_data,
                headers={
                    "Content-Type": "application/json",
                    **self._headers,
                },
                timeout=10,
            )
            return response.status_code in (200, 201, 202, 204)
        except Exception:
            return False

    @contextmanager
    def span(self, name: str, attributes: Optional[dict] = None):
        """Context manager for creating a span.

        Args:
            name: Span name
            attributes: Optional span attributes

        Yields:
            The created span
        """
        try:
            self._ensure_initialized()

            from opentelemetry import trace

            tracer = trace.get_tracer(self.service_name)
            with tracer.start_as_current_span(name, attributes=attributes or {}) as s:
                yield s

        except ImportError:
            yield None

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
