"""Base skill executor for Skill Hub."""

from abc import abstractmethod
from typing import Any, TypedDict

from metanoia.skills.base import SkillExecutor as BaseSkillExecutor


class SkillHubInput(TypedDict):
    pass


class SkillHubOutput(TypedDict):
    pass


class SkillHubExecutor(BaseSkillExecutor):
    """Base class for Skill Hub community skills.

    Community skills extend the base SkillExecutor with additional
    capabilities for registry discovery, version checking, and
    community features.
    """

    name: str = "hub-base-skill"
    version: str = "1.0.0"
    author: str = "community"
    registry_url: str | None = None

    @abstractmethod
    async def execute(self, input_data: SkillHubInput) -> SkillHubOutput:
        pass

    async def validate_input(self, input_data: dict) -> bool:
        return True

    async def cleanup(self) -> None:
        pass

    def get_metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "registry_url": self.registry_url,
        }
