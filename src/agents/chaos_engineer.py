"""Chaos Engineer agent for Metanoia-QA.

Orchestrates chaos experiments with advanced abort triggers.
"""

import logging
from typing import Any, Optional

from src.agents.base import AgentConfig, AgentResponse, AgentStatus
from src.agents.types import AgentType
from src.agents.chaos_agent import ChaosAgent, ChaosExperimentResult
from src.chaos.experiments import ChaosExperiment, AbortCondition
from src.chaos.abort_controller import AbortController

logger = logging.getLogger(__name__)


class ChaosEngineer(ChaosAgent):
    """Chaos Engineer that orchestrates experiments with abort triggers.
    
    Extends ChaosAgent with advanced cascade failure detection
    and automated abort capabilities.
    
    Responsibilities:
    - Define and orchestrate chaos experiments
    - Monitor for cascade failure conditions
    - Trigger automated aborts when thresholds exceeded
    - Validate experiment safety
    """
    
    name = "chaos-engineer"
    version = "1.0.0"
    
    def __init__(self, config: AgentConfig):
        """Initialize the Chaos Engineer.
        
        Args:
            config: Agent configuration.
        """
        super().__init__(config)
        self._abort_conditions: list[AbortCondition] = []
        self._cascade_failure_detected = False
    
    def add_abort_condition(self, condition: AbortCondition) -> None:
        """Add an abort condition to the engineer.
        
        Args:
            condition: AbortCondition to add.
        """
        self._abort_conditions.append(condition)
        logger.info(f"Added abort condition: {condition.condition_type} {condition.comparison} {condition.threshold}")
    
    def clear_abort_conditions(self) -> None:
        """Clear all abort conditions."""
        self._abort_conditions.clear()
        logger.info("Cleared all abort conditions")
    
    def abort_if_health_checks_fail(
        self,
        health_metrics: dict,
        experiment_id: str,
    ) -> tuple[bool, str]:
        """Abort experiment if health checks fail.
        
        Checks all configured abort conditions against current
        health metrics and triggers abort if any condition is met.
        
        Args:
            health_metrics: Current health metrics dictionary.
            experiment_id: ID of the running experiment.
            
        Returns:
            Tuple of (abort_triggered, reason).
        """
        for condition in self._abort_conditions:
            metric_value = health_metrics.get(condition.condition_type)
            if metric_value is not None:
                if condition.evaluate(metric_value):
                    reason = f"Health check failed: {condition.condition_type}={metric_value} (threshold: {condition.threshold})"
                    self._abort_controller.trigger_abort(experiment_id)
                    self._cascade_failure_detected = True
                    logger.warning(f"CASCADE FAILURE DETECTED: {reason}")
                    return True, reason
        
        should_abort, reason = self._abort_controller.should_abort(health_metrics)
        if should_abort:
            self._abort_controller.trigger_abort(experiment_id)
            self._cascade_failure_detected = True
            logger.warning(f"CASCADE FAILURE DETECTED: {reason}")
        
        return should_abort, reason
    
    def abort_if_error_rate_exceeds(
        self,
        error_rate: float,
        experiment_id: str,
        threshold: Optional[float] = None,
    ) -> tuple[bool, str]:
        """Abort if error rate exceeds threshold.
        
        Specialized abort trigger for error rate monitoring.
        
        Args:
            error_rate: Current error rate (0.0 to 1.0).
            experiment_id: ID of the running experiment.
            threshold: Custom threshold (uses default 0.5 if None).
            
        Returns:
            Tuple of (abort_triggered, reason).
        """
        effective_threshold = threshold if threshold is not None else 0.5
        if error_rate > effective_threshold:
            reason = f"Error rate {error_rate:.2%} exceeds threshold {effective_threshold:.2%}"
            self._abort_controller.trigger_abort(experiment_id)
            self._cascade_failure_detected = True
            logger.warning(f"CASCADE FAILURE DETECTED: {reason}")
            return True, reason
        return False, ""
    
    def is_cascade_failure_detected(self) -> bool:
        """Check if cascade failure has been detected.
        
        Returns:
            True if cascade failure was detected during execution.
        """
        return self._cascade_failure_detected
    
    def reset_cascade_failure(self) -> None:
        """Reset cascade failure detection state."""
        self._cascade_failure_detected = False
        logger.info("Cascade failure detection reset")
    
    def execute(self, state: dict[str, Any]) -> AgentResponse:
        """Execute chaos engineering workflow.
        
        Args:
            state: Pipeline state with experiment definitions.
            
        Returns:
            AgentResponse with orchestration results.
        """
        self._cascade_failure_detected = False
        
        response = super().execute(state)
        
        response.output["cascade_failure_detected"] = self._cascade_failure_detected
        response.output["abort_conditions_configured"] = len(self._abort_conditions)
        
        if self._cascade_failure_detected:
            response.output["status_message"] = "Experiments completed with cascade failure detection"
        else:
            response.output["status_message"] = "All experiments completed safely"
        
        return response
    
    def validate_experiment_safety(self, experiment: ChaosExperiment) -> tuple[bool, list[str]]:
        """Validate that an experiment has proper safety controls.
        
        Args:
            experiment: The experiment to validate.
            
        Returns:
            Tuple of (is_safe, list of warnings).
        """
        warnings = []
        is_safe = True
        
        if not experiment.abort_conditions:
            warnings.append(f"Experiment {experiment.name} has no abort conditions")
            is_safe = False
        
        if experiment.duration_seconds > 300:
            warnings.append(f"Experiment {experiment.name} duration exceeds 5 minutes")
        
        if experiment.intensity > 0.8:
            warnings.append(f"Experiment {experiment.name} has high intensity ({experiment.intensity})")
            is_safe = False
        
        return is_safe, warnings
