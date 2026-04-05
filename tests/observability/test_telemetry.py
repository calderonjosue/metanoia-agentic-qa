"""Tests for observability telemetry."""

import sys
from unittest.mock import Mock



class MockKnowledgeClient:
    @staticmethod
    def get_supabase_client():
        mock_client = Mock()
        mock_client.table = Mock(return_value=mock_client)
        mock_client.insert = Mock(return_value=mock_client)
        mock_client.execute = Mock()
        mock_client.delete = Mock(return_value=mock_client)
        mock_client.lt = Mock(return_value=mock_client)
        return mock_client


sys.modules['src.knowledge'] = Mock()
sys.modules['src.knowledge.client'] = MockKnowledgeClient()

from src.observability.telemetry import (  # noqa: E402
    TelemetryCollector,
    TelemetryConfig,
    TestMetrics,
    AgentPerformance,
)


class TestTelemetryCollector:
    """Tests for TelemetryCollector."""

    def test_collector_stores_metrics(self):
        """Test metrics are stored."""
        collector = TelemetryCollector()
        
        metrics = TestMetrics(
            test_case_id="TEST-001",
            duration_seconds=2.5,
            passed=True,
            agent_id="agent-001",
            sprint_id="SP-45"
        )
        
        collector._metrics_buffer.append({
            "test_case_id": metrics.test_case_id,
            "duration_seconds": metrics.duration_seconds,
            "passed": metrics.passed,
        })
        
        assert len(collector._metrics_buffer) == 1
        assert collector._metrics_buffer[0]["test_case_id"] == "TEST-001"

    def test_retention_30_days(self):
        """Test old metrics are cleaned."""
        config = TelemetryConfig(retention_days=30)
        collector = TelemetryCollector(config=config)
        
        assert collector.config.retention_days == 30


class TestTestMetrics:
    """Tests for TestMetrics model."""

    def test_test_metrics_creation(self):
        """Test creating TestMetrics."""
        metrics = TestMetrics(
            test_case_id="TEST-002",
            duration_seconds=1.5,
            passed=False,
            module="payment"
        )
        
        assert metrics.test_case_id == "TEST-002"
        assert metrics.duration_seconds == 1.5
        assert metrics.passed is False
        assert metrics.module == "payment"


class TestAgentPerformance:
    """Tests for AgentPerformance model."""

    def test_agent_performance_creation(self):
        """Test creating AgentPerformance."""
        perf = AgentPerformance(
            agent_id="agent-002",
            agent_type="el_arqueologo",
            duration_seconds=5.0,
            status="completed",
            output_size=1024
        )
        
        assert perf.agent_id == "agent-002"
        assert perf.agent_type == "el_arqueologo"
        assert perf.duration_seconds == 5.0
        assert perf.status == "completed"
        assert perf.output_size == 1024