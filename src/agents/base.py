"""Base agent classes for Metanoia-QA.

This module provides the base classes and interfaces that all
specialized agents must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from src.agents.types import AgentType  # Re-export for backward compatibility


class AgentStatus(str, Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class AgentConfig:
    """Configuration for an agent instance.

    Attributes:
        agent_type: Type of the agent
        agent_id: Unique identifier for this instance
        model: LLM model to use
        temperature: Sampling temperature
        max_retries: Maximum retry attempts
        timeout_seconds: Execution timeout
    """
    agent_type: AgentType
    agent_id: str
    model: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_retries: int = 3
    timeout_seconds: int = 300
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentResponse(BaseModel):
    """Standard response from agent execution.

    Attributes:
        agent_id: ID of the agent that produced this response
        agent_type: Type of the agent
        status: Execution status
        output: Agent's output data
        error: Error message if failed
        started_at: When execution started
        completed_at: When execution completed
        duration_seconds: Total execution time
        metadata: Additional metadata
    """
    agent_id: str
    agent_type: AgentType
    status: AgentStatus
    output: dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    """Abstract base class for all Metanoia-QA agents.

    All specialized agents must inherit from this class and implement
    the execute method.

    Attributes:
        config: Agent configuration
        status: Current agent status
    """

    def __init__(self, config: AgentConfig):
        """Initialize the agent.

        Args:
            config: Agent configuration
        """
        self.config = config
        self.status = AgentStatus.IDLE

    @abstractmethod
    def execute(self, state: dict[str, Any]) -> AgentResponse:
        """Execute the agent's primary logic.

        This method must be implemented by all agent subclasses.

        Args:
            state: Current pipeline state

        Returns:
            AgentResponse with execution results
        """
        pass

    def run(self, state: dict[str, Any]) -> AgentResponse:
        """Run the agent with error handling and timing.

        Args:
            state: Current pipeline state

        Returns:
            AgentResponse with execution results
        """
        from datetime import datetime

        self.status = AgentStatus.RUNNING
        started_at = datetime.utcnow()

        try:
            response = self.execute(state)
            response.status = AgentStatus.COMPLETED
            return response

        except Exception as e:
            self.status = AgentStatus.FAILED
            return AgentResponse(
                agent_id=self.config.agent_id,
                agent_type=self.config.agent_type,
                status=AgentStatus.FAILED,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow(),
                duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
            )

        finally:
            if self.status == AgentStatus.RUNNING:
                self.status = AgentStatus.IDLE

