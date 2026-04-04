"""Pytest configuration and fixtures for Metanoia-QA tests."""

import pytest
from unittest.mock import Mock, AsyncMock


@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client."""
    client = Mock()
    client.table = Mock()
    client.rpc = AsyncMock()
    return client


@pytest.fixture
def mock_gemini():
    """Create a mock Gemini client."""
    return AsyncMock()


@pytest.fixture
def sample_sprint_context():
    """Create a sample sprint context for testing."""
    return {
        "sprint_id": "SP-45",
        "sprint_goal": "Implement checkout flow",
        "risk_tolerance": "Low",
        "historical_lookback_sprints": 3
    }


@pytest.fixture
def mock_context_analysis_result():
    """Create a mock context analysis result."""
    return {
        "risk_level": "medium",
        "risk_score": 0.45,
        "similar_sprints": [
            {
                "sprint_id": "SP-40",
                "sprint_name": "Checkout Refactor",
                "similarity_score": 0.75,
                "shared_modules": ["payment", "cart"],
                "shared_features": ["payment_processing"],
                "defect_density": 0.3,
                "test_effectiveness": 0.85
            }
        ],
        "flaky_tests": [
            {
                "test_id": "TEST-001",
                "test_name": "Payment Gateway Test",
                "module": "payment",
                "failure_rate": 0.15,
                "last_failure": "2024-01-15T10:30:00Z",
                "root_cause": None
            }
        ],
        "module_risks": [
            {
                "module_name": "payment",
                "defect_density": 0.35,
                "change_frequency": 0.6,
                "test_coverage": 0.7,
                "risk_level": "high",
                "recommendations": [
                    "Increase regression test coverage",
                    "Schedule additional security testing"
                ]
            }
        ],
        "recommendations": [
            "Review 1 flaky tests before sprint start",
            "Focus on 1 high-risk module(s) with elevated defect density"
        ],
        "effort_multiplier": 1.225
    }


@pytest.fixture
def mock_agent_result():
    """Create a mock agent execution result."""
    return {
        "agent_name": "test-agent",
        "passed": 38,
        "failed": 2,
        "skipped": 2,
        "duration": 245.5,
        "status": "completed",
        "metadata": {}
    }
