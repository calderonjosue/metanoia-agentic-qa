"""Pytest configuration for integration tests."""

import pytest


def pytest_configure(config):
    """Register custom markers for integration tests."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may require external services)"
    )
