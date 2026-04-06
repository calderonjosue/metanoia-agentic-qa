"""Chaos Agent for Metanoia-QA.

Executes chaos experiments and reports results.
"""

import logging
from typing import Any, Optional

from pydantic import BaseModel

from src.agents.base import AgentConfig, AgentResponse, AgentStatus, BaseAgent
from src.agents.types import AgentType
from src.chaos.abort_controller import AbortController
from src.chaos.experiments import ChaosExperiment

logger = logging.getLogger(__name__)


class ChaosExperimentResult(BaseModel):
    """Result from a chaos experiment execution."""
    experiment_name: str
    status: str
    duration_seconds: float
    target: str
    action: str
    error_injected: bool = False
    abort_triggered: bool = False
    abort_reason: Optional[str] = None
    health_metrics: dict = {}
    report_url: Optional[str] = None
    metadata: dict = {}


class ChaosAgent(BaseAgent):
    """Chaos Agent that executes declarative chaos experiments.

    Responsibilities:
    - Execute chaos experiments with controlled failure injection
    - Monitor system health during experiments
    - Report experiment results
    - Integrate with APM for observability
    """

    name = "chaos-agent"
    version = "1.0.0"

    def __init__(self, config: AgentConfig):
        """Initialize the Chaos Agent.

        Args:
            config: Agent configuration.
        """
        super().__init__(config)
        self._abort_controller = AbortController()
        self._active_experiments: dict[str, ChaosExperiment] = {}

    def execute(self, state: dict[str, Any]) -> AgentResponse:
        """Execute chaos experiments.

        Args:
            state: Pipeline state containing experiment definitions
                   and execution context.

        Returns:
            AgentResponse with experiment results.
        """
        experiments = state.get("chaos_experiments", [])
        results = []

        for experiment_def in experiments:
            if isinstance(experiment_def, dict):
                experiment = ChaosExperiment.from_dict(experiment_def)
            else:
                experiment = experiment_def

            if not experiment.enabled:
                logger.info(f"Skipping disabled experiment: {experiment.name}")
                continue

            logger.info(f"Executing chaos experiment: {experiment.name}")
            result = self._execute_experiment(experiment)
            results.append(result)

        return AgentResponse(
            agent_id=self.config.agent_id,
            agent_type=AgentType.CONTEXT_ANALYST,
            status=AgentStatus.COMPLETED,
            output={
                "experiments_executed": len(results),
                "results": [r.model_dump() for r in results],
            },
        )

    def _execute_experiment(self, experiment: ChaosExperiment) -> ChaosExperimentResult:
        """Execute a single chaos experiment.

        Args:
            experiment: The experiment to execute.

        Returns:
            ChaosExperimentResult with execution details.
        """
        import time

        start_time = time.time()
        self._active_experiments[experiment.name] = experiment

        try:
            health_metrics = self._run_experiment_loop(experiment)
            duration = time.time() - start_time

            abort_triggered, abort_reason = experiment.should_abort(health_metrics)

            return ChaosExperimentResult(
                experiment_name=experiment.name,
                status="completed",
                duration_seconds=duration,
                target=experiment.target,
                action=experiment.action,
                error_injected=True,
                abort_triggered=abort_triggered,
                abort_reason=abort_reason,
                health_metrics=health_metrics,
            )

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Experiment {experiment.name} failed: {e}")
            return ChaosExperimentResult(
                experiment_name=experiment.name,
                status="failed",
                duration_seconds=duration,
                target=experiment.target,
                action=experiment.action,
                error_injected=False,
                abort_triggered=True,
                abort_reason=str(e),
            )
        finally:
            if experiment.name in self._active_experiments:
                del self._active_experiments[experiment.name]

    def _run_experiment_loop(self, experiment: ChaosExperiment) -> dict:
        """Run the experiment loop monitoring health metrics.

        Args:
            experiment: The experiment being executed.

        Returns:
            Final health metrics dictionary.
        """
        import time

        health_metrics = {
            "error_rate": 0.0,
            "latency_p99_ms": 100.0,
            "success_rate": 1.0,
            "error_count": 0,
        }

        end_time = time.time() + experiment.duration_seconds

        while time.time() < end_time:
            current_metrics = self._collect_health_metrics(experiment)
            health_metrics.update(current_metrics)

            should_abort, _ = experiment.should_abort(health_metrics)
            if should_abort:
                break

            time.sleep(1)

        return health_metrics

    def _collect_health_metrics(self, experiment: ChaosExperiment) -> dict:
        """Collect current health metrics.

        In a real implementation, this would integrate with APM
        and monitoring systems.

        Args:
            experiment: The experiment being executed.

        Returns:
            Current health metrics.
        """
        import random

        base_error_rate = 0.01 * experiment.intensity
        error_rate = min(1.0, base_error_rate + random.random() * 0.05)

        return {
            "error_rate": error_rate,
            "latency_p99_ms": 100 + (200 * experiment.intensity * random.random()),
            "success_rate": 1.0 - error_rate,
            "error_count": int(error_rate * 1000),
        }

    def abort_experiment(self, experiment_id: str) -> bool:
        """Abort a running experiment.

        Args:
            experiment_id: Name/ID of the experiment to abort.

        Returns:
            True if the experiment was found and aborted.
        """
        if experiment_id in self._active_experiments:
            self._abort_controller.trigger_abort(experiment_id)
            del self._active_experiments[experiment_id]
            logger.info(f"Experiment {experiment_id} aborted")
            return True
        return False

    def get_active_experiments(self) -> list[str]:
        """Get list of currently running experiments.

        Returns:
            List of active experiment IDs.
        """
        return list(self._active_experiments.keys())
