#!/usr/bin/env python3
"""
Example: Datadog Test Metrics Reporter

This script demonstrates how to submit test metrics to Datadog.
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from executor import DatadogReporter, TestMetrics


def basic_example():
    """Submit basic test metrics."""
    reporter = DatadogReporter()

    metrics = TestMetrics(
        suite="api-integration-tests",
        passed=145,
        failed=3,
        skipped=2,
        duration=89.5,
        flaky=1,
    )

    result = reporter.submit_metrics(metrics)
    print(f"Submitted metrics: {result}")


def ci_cd_example():
    """Example for CI/CD pipeline integration."""
    api_key = os.environ.get("DATADOG_API_KEY")
    app_key = os.environ.get("DATADOG_APP_KEY")

    if not api_key or not app_key:
        print("Error: DATADOG_API_KEY and DATADOG_APP_KEY must be set")
        sys.exit(1)

    reporter = DatadogReporter(api_key=api_key, app_key=app_key)

    passed = int(os.environ.get("TEST_PASSED", 0))
    failed = int(os.environ.get("TEST_FAILED", 0))
    skipped = int(os.environ.get("TEST_SKIPPED", 0))
    duration = float(os.environ.get("TEST_DURATION", 0))
    suite = os.environ.get("TEST_SUITE", "unknown")

    metrics = TestMetrics(
        suite=suite,
        passed=passed,
        failed=failed,
        skipped=skipped,
        duration=duration,
        tags=[
            f"environment:{os.environ.get('CI_ENVIRONMENT', 'unknown')}",
            f"branch:{os.environ.get('GIT_BRANCH', 'unknown')}",
        ],
    )

    result = reporter.submit_metrics(metrics)
    print(f"CI/CD metrics submitted: {result}")


def pytest_example():
    """Example parsing pytest output."""
    reporter = DatadogReporter()

    test_results = {
        "passed": ["test_login", "test_logout", "test_search"],
        "failed": ["test_checkout"],
        "skipped": ["test_legacy"],
    }

    passed = len(test_results["passed"])
    failed = len(test_results["failed"])
    skipped = len(test_results["skipped"])

    metrics = TestMetrics(
        suite="e2e-tests",
        passed=passed,
        failed=failed,
        skipped=skipped,
        duration=45.2,
        flaky=0,
        tags=["framework:pytest", "browser:chromium"],
    )

    result = reporter.submit_metrics(metrics)
    print(f"Pytest metrics submitted: {result}")


def main():
    print("=== Datadog Test Metrics Reporter Examples ===\n")

    print("1. Basic Example")
    print("-" * 40)
    try:
        basic_example()
    except Exception as e:
        print(f"Error: {e}")
        print("(This is expected if Datadog credentials are not configured)\n")

    print("\n2. Pytest Example")
    print("-" * 40)
    try:
        pytest_example()
    except Exception as e:
        print(f"Error: {e}")
        print("(This is expected if Datadog credentials are not configured)\n")

    print("\n3. CI/CD Example")
    print("-" * 40)
    print("Set DATADOG_API_KEY and DATADOG_APP_KEY to run this example")


if __name__ == "__main__":
    main()
