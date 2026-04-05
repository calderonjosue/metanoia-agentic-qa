#!/usr/bin/env python3
"""
Datadog Test Metrics Reporter Executor

Submits test metrics to Datadog for monitoring and alerting.
"""

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

try:
    from datadog import api, initialize
except ImportError:
    print("Error: datadog package not installed. Run: pip install datadog")
    sys.exit(1)


@dataclass
class TestMetrics:
    suite: str
    passed: int
    failed: int
    skipped: int = 0
    duration: float = 0.0
    flaky: int = 0
    tags: Optional[list[str]] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = [f"suite:{self.suite}"]


class DatadogReporter:
    def __init__(self, api_key: Optional[str] = None, app_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("DATADOG_API_KEY")
        self.app_key = app_key or os.environ.get("DATADOG_APP_KEY")

        if not self.api_key or not self.app_key:
            raise ValueError("DATADOG_API_KEY and DATADOG_APP_KEY must be set")

        initialize(api_key=self.api_key, app_key=self.app_key)

    def submit_metrics(self, metrics: TestMetrics) -> dict:
        timestamp = int(datetime.now().timestamp())

        event_type = "test.results"
        tags = metrics.tags + ["metric_type:count"]

        api.Metric.send(
            metric=f"{event_type}.passed",
            points=((timestamp, metrics.passed)),
            tags=tags + ["status:passed"],
        )
        api.Metric.send(
            metric=f"{event_type}.failed",
            points=((timestamp, metrics.failed)),
            tags=tags + ["status:failed"],
        )
        api.Metric.send(
            metric=f"{event_type}.skipped",
            points=((timestamp, metrics.skipped)),
            tags=tags + ["status:skipped"],
        )

        if metrics.duration > 0:
            api.Metric.send(
                metric="test.duration",
                points=((timestamp, metrics.duration)),
                tags=tags,
            )

        if metrics.flaky > 0:
            flakiness_rate = (metrics.flaky / (metrics.passed + metrics.failed + metrics.flaky)) * 100
            api.Metric.send(
                metric="test.flakiness",
                points=((timestamp, flakiness_rate)),
                tags=tags,
            )

        return {"status": "success", "metrics": asdict(metrics)}


def submit_command(args):
    metrics = TestMetrics(
        suite=args.suite,
        passed=args.passed,
        failed=args.failed,
        skipped=args.skipped,
        duration=args.duration,
        flaky=args.flaky,
        tags=args.tags.split(",") if args.tags else None,
    )

    reporter = DatadogReporter()
    result = reporter.submit_metrics(metrics)
    print(json.dumps(result, indent=2))


def validate_command(args):
    schema_path = os.path.join(os.path.dirname(__file__), "schema.json")
    with open(schema_path, "r") as f:
        json.load(f)

    try:
        data = json.loads(args.payload)
        print("Payload is valid JSON")
        print(json.dumps(data, indent=2))
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        sys.exit(1)


def dashboards_command(args):
    dashboards_dir = os.path.join(os.path.dirname(__file__), "dashboards")
    if not os.path.exists(dashboards_dir):
        print("No dashboards directory found")
        return

    for filename in os.listdir(dashboards_dir):
        if filename.endswith(".json"):
            print(f"  - {filename}")


def alerts_command(args):
    alerts_dir = os.path.join(os.path.dirname(__file__), "alerts")
    if not os.path.exists(alerts_dir):
        print("No alerts directory found")
        return

    for filename in os.listdir(alerts_dir):
        if filename.endswith(".json"):
            print(f"  - {filename}")


def main():
    parser = argparse.ArgumentParser(description="Datadog Test Metrics Reporter")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    submit_parser = subparsers.add_parser("submit", help="Submit test metrics")
    submit_parser.add_argument("--suite", required=True, help="Test suite name")
    submit_parser.add_argument("--passed", type=int, required=True, help="Number of passed tests")
    submit_parser.add_argument("--failed", type=int, required=True, help="Number of failed tests")
    submit_parser.add_argument("--skipped", type=int, default=0, help="Number of skipped tests")
    submit_parser.add_argument("--duration", type=float, default=0.0, help="Test duration in seconds")
    submit_parser.add_argument("--flaky", type=int, default=0, help="Number of flaky tests")
    submit_parser.add_argument("--tags", default="", help="Comma-separated tags")

    validate_parser = subparsers.add_parser("validate", help="Validate metric payload")
    validate_parser.add_argument("--payload", required=True, help="JSON payload to validate")

    subparsers.add_parser("dashboards", help="List available dashboards")
    subparsers.add_parser("alerts", help="List available alert definitions")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "submit":
        submit_command(args)
    elif args.command == "validate":
        validate_command(args)
    elif args.command == "dashboards":
        dashboards_command(args)
    elif args.command == "alerts":
        alerts_command(args)


if __name__ == "__main__":
    main()
