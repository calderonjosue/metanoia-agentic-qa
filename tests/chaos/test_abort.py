"""Tests for abort controller."""


from src.chaos.abort_controller import AbortController
from src.chaos.experiments import ChaosExperiment, AbortCondition


class TestAbortController:
    """Tests for AbortController."""

    def test_should_abort_when_health_fails(self):
        """Test abort triggers on health check failure."""
        controller = AbortController(
            default_error_rate_threshold=0.5,
            default_latency_threshold_ms=5000.0
        )
        
        health_metrics = {
            "error_rate": 0.75,
            "latency_p99_ms": 3000.0,
            "error_count": 50,
            "success_rate": 0.25
        }
        
        should_abort, reason = controller.should_abort(health_metrics)
        
        assert should_abort is True
        assert "error_rate" in reason.lower() or "exceeds" in reason.lower()

    def test_trigger_abort_stops_experiment(self):
        """Test abort stops running experiment."""
        controller = AbortController()
        
        experiment_id = "exp-001"
        
        controller.trigger_abort(experiment_id)
        
        assert controller.is_aborted(experiment_id) is True
        
        duration = controller.get_abort_duration(experiment_id)
        assert duration is not None
        assert duration >= 0.0

    def test_should_not_abort_when_healthy(self):
        """Test abort does not trigger when healthy."""
        controller = AbortController(
            default_error_rate_threshold=0.5,
            default_latency_threshold_ms=5000.0
        )
        
        health_metrics = {
            "error_rate": 0.1,
            "latency_p99_ms": 100.0,
            "error_count": 5,
            "success_rate": 0.9
        }
        
        should_abort, reason = controller.should_abort(health_metrics)
        
        assert should_abort is False
        assert reason == ""

    def test_clear_abort(self):
        """Test clearing abort state."""
        controller = AbortController()
        
        experiment_id = "exp-002"
        controller.trigger_abort(experiment_id)
        
        assert controller.is_aborted(experiment_id) is True
        
        controller.clear_abort(experiment_id)
        
        assert controller.is_aborted(experiment_id) is False

    def test_abort_if_health_checks_fail(self):
        """Test abort_if_health_checks_fail method."""
        controller = AbortController()
        
        health_metrics = {"error_rate": 0.6}
        experiment_id = "exp-003"
        
        abort_triggered, reason = controller.abort_if_health_checks_fail(
            health_metrics, experiment_id
        )
        
        assert abort_triggered is True
        assert controller.is_aborted(experiment_id) is True


class TestChaosExperimentAbort:
    """Tests for ChaosExperiment abort conditions."""

    def test_experiment_should_abort_on_condition_met(self):
        """Test experiment aborts when condition is met."""
        experiment = ChaosExperiment(
            name="latency-test",
            description="Test latency injection",
            target="service",
            action="latency_injection",
            duration_seconds=60,
            abort_conditions=[
                AbortCondition(condition_type="error_rate", threshold=0.5, comparison="gt")
            ]
        )
        
        health_metrics = {"error_rate": 0.6}
        
        should_abort, reason = experiment.should_abort(health_metrics)
        
        assert should_abort is True
        assert reason is not None

    def test_experiment_should_not_abort_on_condition_not_met(self):
        """Test experiment does not abort when condition not met."""
        experiment = ChaosExperiment(
            name="latency-test",
            description="Test latency injection",
            target="service",
            action="latency_injection",
            duration_seconds=60,
            abort_conditions=[
                AbortCondition(condition_type="error_rate", threshold=0.5, comparison="gt")
            ]
        )
        
        health_metrics = {"error_rate": 0.3}
        
        should_abort, reason = experiment.should_abort(health_metrics)
        
        assert should_abort is False
        assert reason is None