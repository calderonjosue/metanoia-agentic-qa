"""Abstract base class for Metanoia-QA skill executors."""

from abc import ABC, abstractmethod
from typing import Any, TypedDict


class SkillInput(TypedDict):
    """Base type for skill inputs."""
    pass


class SkillOutput(TypedDict):
    """Base type for skill outputs."""
    pass


class SkillExecutor(ABC):
    """Abstract base class for all Metanoia-QA skill executors.
    
    Subclass this to create a new skill. Implement the execute method
    to define your skill's behavior.
    
    Example:
        class MySkillExecutor(SkillExecutor):
            async def execute(self, input_data: SkillInput) -> SkillOutput:
                # Process input and return output
                return {"status": "success", "data": input_data.get("value")}
    """

    name: str = "base-skill"
    version: str = "1.0.0"

    @abstractmethod
    async def execute(self, input_data: SkillInput) -> SkillOutput:
        """Execute the skill with the given input.
        
        Args:
            input_data: Dictionary containing skill-specific input parameters.
            
        Returns:
            Dictionary containing skill execution results.
            
        Raises:
            SkillExecutionError: If execution fails.
        """
        pass

    async def validate_input(self, input_data: dict) -> bool:
        """Validate input data before execution.
        
        Args:
            input_data: The input data to validate.
            
        Returns:
            True if valid, False otherwise.
        """
        return True

    async def cleanup(self) -> None:
        """Cleanup resources after execution.
        
        Override this method if your skill needs to clean up
        resources (connections, files, etc.) after execution.
        """
        pass

    def get_metadata(self) -> dict[str, str]:
        """Return skill metadata.
        
        Returns:
            Dictionary containing name, version, and other metadata.
        """
        return {
            "name": self.name,
            "version": self.version,
        }


class SkillExecutionError(Exception):
    """Exception raised when skill execution fails."""

    def __init__(self, message: str, skill_name: str = "unknown", details: dict | None = None):
        super().__init__(message)
        self.skill_name = skill_name
        self.details = details or {}
