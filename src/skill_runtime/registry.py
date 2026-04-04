"""Skill registry for Metanoia-QA.

Central registry for all skills with metadata, versioning,
and dependency management.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from metanoia.skills.base import SkillExecutor

logger = logging.getLogger(__name__)


@dataclass
class SkillMetadata:
    """Metadata for a registered skill."""
    name: str
    version: str
    author: str
    description: str
    triggers: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    file_path: Path | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "triggers": self.triggers,
            "dependencies": self.dependencies,
        }


class SkillRegistry:
    """Central registry for all Metanoia-QA skills."""

    def __init__(self):
        """Initialize the registry."""
        self._skills: dict[str, SkillMetadata] = {}
        self._executors: dict[str, type[SkillExecutor]] = {}

    def register(
        self,
        name: str,
        executor_class: type[SkillExecutor],
        metadata: SkillMetadata | None = None
    ) -> None:
        """Register a skill.
        
        Args:
            name: Unique skill name.
            executor_class: The executor class.
            metadata: Optional metadata.
        """
        if metadata is None:
            metadata = SkillMetadata(
                name=name,
                version=getattr(executor_class, "version", "1.0.0"),
                author=getattr(executor_class, "author", "Unknown"),
                description=getattr(executor_class, "description", ""),
            )
        
        self._skills[name] = metadata
        self._executors[name] = executor_class
        logger.info(f"Registered skill: {name} v{metadata.version}")

    def unregister(self, name: str) -> bool:
        """Unregister a skill.
        
        Args:
            name: Name of the skill to unregister.
            
        Returns:
            True if unregistered, False if not found.
        """
        if name in self._skills:
            del self._skills[name]
            del self._executors[name]
            logger.info(f"Unregistered skill: {name}")
            return True
        return False

    def get_metadata(self, name: str) -> SkillMetadata | None:
        """Get metadata for a skill.
        
        Args:
            name: Skill name.
            
        Returns:
            SkillMetadata or None if not found.
        """
        return self._skills.get(name)

    def get_executor(self, name: str) -> type[SkillExecutor] | None:
        """Get the executor class for a skill.
        
        Args:
            name: Skill name.
            
        Returns:
            Executor class or None.
        """
        return self._executors.get(name)

    def create_executor(self, name: str) -> SkillExecutor | None:
        """Create an instance of a skill's executor.
        
        Args:
            name: Skill name.
            
        Returns:
            Executor instance or None.
        """
        executor_class = self._executors.get(name)
        if executor_class is None:
            return None
        return executor_class()

    def list_skills(self) -> list[str]:
        """List all registered skill names."""
        return sorted(self._skills.keys())

    def list_triggers(self) -> dict[str, list[str]]:
        """Get all skills mapped by trigger word."""
        trigger_map: dict[str, list[str]] = {}
        for name, metadata in self._skills.items():
            for trigger in metadata.triggers:
                if trigger not in trigger_map:
                    trigger_map[trigger] = []
                trigger_map[trigger].append(name)
        return trigger_map

    def find_by_trigger(self, trigger: str) -> list[str]:
        """Find skills that match a trigger.
        
        Args:
            trigger: Trigger keyword.
            
        Returns:
            List of matching skill names.
        """
        return self.list_triggers().get(trigger, [])

    def find_by_prefix(self, prefix: str) -> list[str]:
        """Find skills whose names start with prefix.
        
        Args:
            prefix: Name prefix to search.
            
        Returns:
            List of matching skill names.
        """
        return [name for name in self._skills if name.startswith(prefix)]

    def get_all_metadata(self) -> list[dict[str, Any]]:
        """Get metadata for all registered skills."""
        return [m.to_dict() for m in self._skills.values()]

    def clear(self) -> None:
        """Clear all registered skills."""
        self._skills.clear()
        self._executors.clear()
        logger.info("Cleared all registered skills")


_global_registry: SkillRegistry | None = None


def get_registry() -> SkillRegistry:
    """Get the global skill registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = SkillRegistry()
    return _global_registry


def register_skill(
    name: str,
    executor_class: type[SkillExecutor],
    metadata: SkillMetadata | None = None
) -> None:
    """Convenience function to register a skill."""
    get_registry().register(name, executor_class, metadata)


def get_skill(name: str) -> SkillExecutor | None:
    """Convenience function to get a skill executor instance."""
    return get_registry().create_executor(name)


def list_all_skills() -> list[str]:
    """Convenience function to list all skills."""
    return get_registry().list_skills()
