"""Dynamic skill loader for Metanoia-QA.

Loads skills from the skills directory and makes them available for execution.
"""

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any

from metanoia.skills.base import SkillExecutor


class SkillLoader:
    """Dynamic skill loader that discovers and loads skills at runtime."""

    def __init__(self, skills_path: Path | None = None):
        """Initialize the skill loader.
        
        Args:
            skills_path: Path to the skills directory. 
                        Defaults to metanoia/skills/
        """
        if skills_path is None:
            self.skills_path = Path(__file__).parent.parent.parent / "skills"
        else:
            self.skills_path = Path(skills_path)
        
        self._loaded_skills: dict[str, type[SkillExecutor]] = {}

    def discover_skills(self) -> list[str]:
        """Discover all available skills in the skills directory.
        
        Returns:
            List of skill directory names.
        """
        if not self.skills_path.exists():
            return []
        
        skills = []
        for item in self.skills_path.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                skill_md = item / "SKILL.md"
                executor_py = item / "executor.py"
                if skill_md.exists() or executor_py.exists():
                    skills.append(item.name)
        
        return sorted(skills)

    def load_skill(self, skill_name: str) -> type[SkillExecutor] | None:
        """Load a specific skill by name.
        
        Args:
            skill_name: Name of the skill directory.
            
        Returns:
            The skill's executor class, or None if not found.
        """
        if skill_name in self._loaded_skills:
            return self._loaded_skills[skill_name]
        
        skill_path = self.skills_path / skill_name
        if not skill_path.exists():
            return None
        
        executor_path = skill_path / "executor.py"
        if not executor_path.exists():
            return None
        
        try:
            spec = importlib.util.spec_from_file_location(
                f"metanoia.skills.{skill_name}.executor",
                executor_path
            )
            if spec is None or spec.loader is None:
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"metanoia.skills.{skill_name}.executor"] = module
            spec.loader.exec_module(module)
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type) 
                    and issubclass(attr, SkillExecutor) 
                    and attr is not SkillExecutor
                ):
                    attr.name = skill_name  # type: ignore[attr-defined]
                    self._loaded_skills[skill_name] = attr
                    return attr
            
            return None
        except Exception:
            return None

    def load_all_skills(self) -> dict[str, type[SkillExecutor]]:
        """Load all discovered skills.
        
        Returns:
            Dictionary mapping skill names to executor classes.
        """
        skill_names = self.discover_skills()
        for name in skill_names:
            self.load_skill(name)
        
        return self._loaded_skills.copy()

    def get_skill(self, skill_name: str) -> type[SkillExecutor] | None:
        """Get a loaded skill by name.
        
        Args:
            skill_name: Name of the skill.
            
        Returns:
            The executor class, or None if not loaded.
        """
        return self._loaded_skills.get(skill_name)

    def get_skill_metadata(self, skill_name: str) -> dict[str, Any] | None:
        """Get metadata for a skill.
        
        Args:
            skill_name: Name of the skill.
            
        Returns:
            Dictionary with name, version, etc., or None.
        """
        skill_class = self.get_skill(skill_name)
        if skill_class is None:
            skill_class = self.load_skill(skill_name)
        
        if skill_class is None:
            return None
        
        return {
            "name": getattr(skill_class, "name", skill_name),
            "version": getattr(skill_class, "version", "1.0.0"),
        }

    def reload_skill(self, skill_name: str) -> type[SkillExecutor] | None:
        """Reload a skill (useful after updates).
        
        Args:
            skill_name: Name of the skill to reload.
            
        Returns:
            The reloaded executor class, or None.
        """
        if skill_name in self._loaded_skills:
            del self._loaded_skills[skill_name]
        
        module_key = f"metanoia.skills.{skill_name}.executor"
        if module_key in sys.modules:
            del sys.modules[module_key]
        
        return self.load_skill(skill_name)


_global_loader: SkillLoader | None = None


def get_loader() -> SkillLoader:
    """Get the global skill loader instance."""
    global _global_loader
    if _global_loader is None:
        _global_loader = SkillLoader()
    return _global_loader


def load_skill(skill_name: str) -> type[SkillExecutor] | None:
    """Convenience function to load a skill."""
    return get_loader().load_skill(skill_name)


def discover_skills() -> list[str]:
    """Convenience function to discover skills."""
    return get_loader().discover_skills()
