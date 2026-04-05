"""Abort controller for cascade failure detection."""

import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class AbortController:
    """Cascade failure detection and abort controller.
    
    Monitors health metrics and triggers abort when conditions
    indicate cascading failure.
    
    Attributes:
        default_error_rate_threshold: Default error rate threshold (0.5 = 50%).
        default_latency_threshold_ms: Default latency threshold in milliseconds.
        abort_timeout_seconds: Maximum time to wait for graceful abort.
    """

    def __init__(
        self,
        default_error_rate_threshold: float = 0.5,
        default_latency_threshold_ms: float = 5000.0,
        abort_timeout_seconds: float = 30.0,
    ):
        """Initialize the abort controller.
        
        Args:
            default_error_rate_threshold: Default error rate threshold.
            default_latency_threshold_ms: Default latency threshold in ms.
            abort_timeout_seconds: Timeout for abort operations.
        """
        self.default_error_rate_threshold = default_error_rate_threshold
        self.default_latency_threshold_ms = default_latency_threshold_ms
        self.abort_timeout_seconds = abort_timeout_seconds
        self._active_aborts: dict[str, float] = {}

    def should_abort(self, health_metrics: dict) -> tuple[bool, str]:
        """Check if the chaos experiment should be aborted.
        
        Evaluates health metrics against configured thresholds
        to determine if cascade failure is occurring.
        
        Args:
            health_metrics: Dictionary of health metric name to value.
                Expected keys:
                - error_rate: float (0.0 to 1.0)
                - latency_p99_ms: float (milliseconds)
                - error_count: int
                - success_rate: float (0.0 to 1.0)
                
        Returns:
            Tuple of (should_abort, reason).
            should_abort is True if abort should be triggered.
            reason describes why abort was triggered.
        """
        error_rate = health_metrics.get("error_rate", 0.0)
        if error_rate > self.default_error_rate_threshold:
            return True, f"Error rate {error_rate:.2%} exceeds threshold {self.default_error_rate_threshold:.2%}"

        latency_p99 = health_metrics.get("latency_p99_ms", 0.0)
        if latency_p99 > self.default_latency_threshold_ms:
            return True, f"Latency P99 {latency_p99:.0f}ms exceeds threshold {self.default_latency_threshold_ms:.0f}ms"

        success_rate = health_metrics.get("success_rate", 1.0)
        if success_rate < (1.0 - self.default_error_rate_threshold):
            return True, f"Success rate {success_rate:.2%} below threshold {1.0 - self.default_error_rate_threshold:.2%}"

        error_count = health_metrics.get("error_count", 0)
        if error_count > 100:
            return True, f"Error count {error_count} exceeds threshold 100"

        return False, ""

    def trigger_abort(self, experiment_id: str) -> None:
        """Trigger immediate abort of a chaos experiment.
        
        Args:
            experiment_id: Unique identifier of the experiment to abort.
        """
        logger.warning(f"ABORT TRIGGERED for experiment: {experiment_id}")
        self._active_aborts[experiment_id] = time.time()

        logger.info(
            f"Experiment {experiment_id} abort initiated at {self._active_aborts[experiment_id]}"
        )

    def is_aborted(self, experiment_id: str) -> bool:
        """Check if an experiment has been aborted.
        
        Args:
            experiment_id: Unique identifier of the experiment.
            
        Returns:
            True if the experiment has been aborted.
        """
        return experiment_id in self._active_aborts

    def get_abort_duration(self, experiment_id: str) -> Optional[float]:
        """Get how long ago an abort was triggered.
        
        Args:
            experiment_id: Unique identifier of the experiment.
            
        Returns:
            Seconds since abort was triggered, or None if not aborted.
        """
        if experiment_id not in self._active_aborts:
            return None
        return time.time() - self._active_aborts[experiment_id]

    def clear_abort(self, experiment_id: str) -> None:
        """Clear abort state for an experiment.
        
        Args:
            experiment_id: Unique identifier of the experiment.
        """
        if experiment_id in self._active_aborts:
            del self._active_aborts[experiment_id]
            logger.info(f"Abort state cleared for experiment: {experiment_id}")

    def abort_if_health_checks_fail(
        self,
        health_metrics: dict,
        experiment_id: str,
    ) -> tuple[bool, str]:
        """Check health metrics and abort if failure is detected.
        
        Convenience method that combines should_abort and trigger_abort.
        
        Args:
            health_metrics: Dictionary of health metrics.
            experiment_id: Unique identifier of the experiment.
            
        Returns:
            Tuple of (abort_triggered, reason).
        """
        should_abort, reason = self.should_abort(health_metrics)
        if should_abort:
            self.trigger_abort(experiment_id)
        return should_abort, reason

    def abort_if_error_rate_exceeds(
        self,
        error_rate: float,
        experiment_id: str,
        threshold: Optional[float] = None,
    ) -> tuple[bool, str]:
        """Abort if error rate exceeds threshold.
        
        Args:
            error_rate: Current error rate (0.0 to 1.0).
            experiment_id: Unique identifier of the experiment.
            threshold: Optional custom threshold (uses default if None).
            
        Returns:
            Tuple of (abort_triggered, reason).
        """
        effective_threshold = threshold or self.default_error_rate_threshold
        if error_rate > effective_threshold:
            reason = f"Error rate {error_rate:.2%} exceeds threshold {effective_threshold:.2%}"
            self.trigger_abort(experiment_id)
            return True, reason
        return False, ""
