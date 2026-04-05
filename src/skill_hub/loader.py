"""Skill loader for Skill Hub."""

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from metanoia.src.skill_hub.base import SkillHubExecutor


class HubSkillLoader:
    """Dynamic skill loader for Skill Hub community skills."""

    def __init__(self, skills_path: Path | None = None):
        if skills_path is None:
            self.skills_path = Path(__file__).parent.parent.parent / "skills"
        else:
            self.skills_path = Path(skills_path)

        self._loaded_skills: dict[str, type["SkillHubExecutor"]] = {}

    def discover_skills(self) -> list[str]:
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

    def load_skill(self, skill_name: str) -> type["SkillHubExecutor"] | None:
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
                    and issubclass(attr, SkillHubExecutor)
                    and attr is not SkillHubExecutor
                ):
                    attr.name = skill_name
                    self._loaded_skills[skill_name] = attr
                    return attr

            return None
        except Exception:
            return None

    def load_all_skills(self) -> dict[str, type["SkillHubExecutor"]]:
        skill_names = self.discover_skills()
        for name in skill_names:
            self.load_skill(name)

        return self._loaded_skills.copy()

    def get_skill(self, skill_name: str) -> type["SkillHubExecutor"] | None:
        return self._loaded_skills.get(skill_name)


_global_loader: HubSkillLoader | None = None


def get_loader() -> HubSkillLoader:
    global _global_loader
    if _global_loader is None:
        _global_loader = HubSkillLoader()
    return _global_loader


def load_from_registry(skill_name: str) -> type["SkillHubExecutor"] | None:
    return get_loader().load_skill(skill_name)
