"""Declarative chaos experiment definitions."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ExperimentTarget(str, Enum):
    """Chaos experiment target types."""
    DATABASE = "database"
    NETWORK = "network"
    SERVICE = "service"
    INFRASTRUCTURE = "infrastructure"


class ExperimentAction(str, Enum):
    """Chaos experiment action types."""
    LATENCY_INJECTION = "latency_injection"
    NODE_FAILURE = "node_failure"
    NETWORK_PARTITION = "network_partition"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    PACKET_LOSS = "packet_loss"
    SERVICE_TERMINATION = "service_termination"


@dataclass
class AbortCondition:
    """Abort condition for a chaos experiment.

    Attributes:
        condition_type: Type of condition (e.g., "error_rate", "latency").
        threshold: Threshold value that triggers abort.
        comparison: Comparison operator ("gt", "lt", "gte", "lte").
    """
    condition_type: str
    threshold: float
    comparison: str = "gt"

    def evaluate(self, value: float) -> bool:
        """Evaluate if the condition is met.

        Args:
            value: The current metric value.

        Returns:
            True if the condition should trigger abort.
        """
        if self.comparison == "gt":
            return value > self.threshold
        elif self.comparison == "gte":
            return value >= self.threshold
        elif self.comparison == "lt":
            return value < self.threshold
        elif self.comparison == "lte":
            return value <= self.threshold
        return False


@dataclass
class ChaosExperiment:
    """Declarative chaos experiment definition.

    Attributes:
        name: Unique experiment name.
        description: Human-readable description.
        target: Target of the experiment (e.g., "database", "network").
        action: Action to perform (e.g., "latency_injection").
        duration_seconds: How long the experiment should run.
        abort_conditions: List of abort conditions.
        enabled: Whether the experiment is enabled.
        intensity: Experiment intensity (0.0 to 1.0).
        tags: Optional tags for categorization.
    """
    name: str
    description: str
    target: str
    action: str
    duration_seconds: int
    abort_conditions: list[AbortCondition] = field(default_factory=list)
    enabled: bool = True
    intensity: float = 0.5
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def should_abort(self, health_metrics: dict) -> tuple[bool, Optional[str]]:
        """Check if any abort condition is met.

        Args:
            health_metrics: Current health metrics dictionary.

        Returns:
            Tuple of (should_abort, reason_if_abort).
        """
        for condition in self.abort_conditions:
            metric_value = health_metrics.get(condition.condition_type)
            if metric_value is not None and condition.evaluate(metric_value):
                return True, f"Abort triggered: {condition.condition_type}={metric_value} (threshold: {condition.threshold})"
        return False, None

    @classmethod
    def from_dict(cls, data: dict) -> "ChaosExperiment":
        """Create a ChaosExperiment from a dictionary.

        Args:
            data: Dictionary with experiment configuration.

        Returns:
            ChaosExperiment instance.
        """
        abort_conditions = [
            AbortCondition(**ac) if isinstance(ac, dict) else ac
            for ac in data.get("abort_conditions", [])
        ]
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            target=data["target"],
            action=data["action"],
            duration_seconds=data["duration_seconds"],
            abort_conditions=abort_conditions,
            enabled=data.get("enabled", True),
            intensity=data.get("intensity", 0.5),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict:
        """Convert experiment to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "name": self.name,
            "description": self.description,
            "target": self.target,
            "action": self.action,
            "duration_seconds": self.duration_seconds,
            "abort_conditions": [
                {
                    "condition_type": ac.condition_type,
                    "threshold": ac.threshold,
                    "comparison": ac.comparison,
                }
                for ac in self.abort_conditions
            ],
            "enabled": self.enabled,
            "intensity": self.intensity,
            "tags": self.tags,
            "metadata": self.metadata,
        }
