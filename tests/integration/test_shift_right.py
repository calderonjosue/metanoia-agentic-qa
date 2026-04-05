"""End-to-end shift-right tests."""

import pytest
from unittest.mock import Mock

from metanoia.src.observability.telemetry import TelemetryCollector
from metanoia.src.chaos.abort_controller import AbortController
from metanoia.src.chaos.experiments import ChaosExperiment, AbortCondition


class TestShiftRightWorkflow:
    """Tests for full shift-right workflow."""

    @pytest.mark.asyncio
    async def test_shift_right_workflow(self):
        """Test full shift-right: APM -> chaos -> recovery."""
        mock_supabase = Mock()
        mock_table = Mock()
        mock_supabase.table = Mock(return_value=mock_table)
        mock_table.insert = Mock(return_value=mock_table)
        mock_table.execute = Mock()
        mock_table.delete = Mock(return_value=mock_table)
        mock_table.lt = Mock(return_value=mock_table)
        
        collector = TelemetryCollector(supabase_client=mock_supabase)
        
        experiment = ChaosExperiment(
            name="shift-right-test",
            description="Shift-right testing",
            target="service",
            action="latency_injection",
            duration_seconds=30,
            abort_conditions=[
                AbortCondition(condition_type="error_rate", threshold=0.5, comparison="gt")
            ]
        )
        
        controller = AbortController()
        
        metrics_buffer = []
        for i in range(5):
            metrics_buffer.append({
                "test_case_id": f"TEST-{i:03d}",
                "duration_seconds": 1.0 + i * 0.1,
                "passed": i < 4,
                "timestamp": "2024-01-15T10:30:00Z"
            })
        
        collector._metrics_buffer = metrics_buffer
        
        assert len(collector._metrics_buffer) == 5
        
        health_metrics = {"error_rate": 0.2}
        should_abort, reason = experiment.should_abort(health_metrics)
        
        assert should_abort is False
        
        experiment_id = "shift-right-exp-001"
        controller.trigger_abort(experiment_id)
        assert controller.is_aborted(experiment_id) is True
        
        controller.clear_abort(experiment_id)
        assert controller.is_aborted(experiment_id) is False

    @pytest.mark.asyncio
    async def test_shift_right_with_chaos_injection(self):
        """Test shift-right with chaos injection and abort."""
        mock_supabase = Mock()
        mock_table = Mock()
        mock_supabase.table = Mock(return_value=mock_table)
        mock_table.insert = Mock(return_value=mock_table)
        mock_table.execute = Mock()
        mock_table.delete = Mock(return_value=mock_table)
        mock_table.lt = Mock(return_value=mock_table)
        
        TelemetryCollector(supabase_client=mock_supabase)
        
        controller = AbortController(default_error_rate_threshold=0.3)
        
        ChaosExperiment(
            name="chaos-latency",
            description="Chaos latency injection",
            target="network",
            action="latency_injection",
            duration_seconds=45,
            abort_conditions=[
                AbortCondition(condition_type="error_rate", threshold=0.3, comparison="gt")
            ]
        )
        
        health_metrics = {"error_rate": 0.5, "latency_p99_ms": 2000.0}
        should_abort, reason = controller.should_abort(health_metrics)
        
        assert should_abort is True
        
        experiment_id = "chaos-exp-001"
        controller.trigger_abort(experiment_id)
        assert controller.is_aborted(experiment_id) is True
        
        abort_triggered, reason = controller.abort_if_health_checks_fail(
            health_metrics, experiment_id
        )
        assert abort_triggered is True

    @pytest.mark.asyncio
    async def test_shift_right_recovery_after_abort(self):
        """Test recovery after abort in shift-right."""
        mock_supabase = Mock()
        mock_table = Mock()
        mock_supabase.table = Mock(return_value=mock_table)
        mock_table.insert = Mock(return_value=mock_table)
        mock_table.execute = Mock()
        mock_table.delete = Mock(return_value=mock_table)
        mock_table.lt = Mock(return_value=mock_table)
        
        TelemetryCollector(supabase_client=mock_supabase)
        
        controller = AbortController()
        
        experiment_id = "recovery-exp-001"
        controller.trigger_abort(experiment_id)
        
        assert controller.is_aborted(experiment_id) is True
        
        abort_duration = controller.get_abort_duration(experiment_id)
        assert abort_duration is not None
        assert abort_duration >= 0
        
        controller.clear_abort(experiment_id)
        assert controller.is_aborted(experiment_id) is False
        
        health_metrics = {"error_rate": 0.05, "latency_p99_ms": 100.0}
        should_abort, reason = controller.should_abort(health_metrics)
        assert should_abort is False