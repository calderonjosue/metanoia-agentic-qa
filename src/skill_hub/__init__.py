"""Skill Hub - Community skill registry and management.

Provides skill discovery, installation, publishing, and lifecycle management
for the Metanoia-QA framework.
"""

from metanoia.src.skill_hub.base import SkillHubExecutor
from metanoia.src.skill_hub.executor import ExecutionResult, HubExecutorEngine
from metanoia.src.skill_hub.loader import HubSkillLoader, load_from_registry
from metanoia.src.skill_hub.manifest import parse_manifest, validate_manifest
from metanoia.src.skill_hub.registry import CommunitySkillRegistry, SkillManifest

__all__ = [
    "SkillHubExecutor",
    "HubSkillLoader",
    "load_from_registry",
    "HubExecutorEngine",
    "ExecutionResult",
    "CommunitySkillRegistry",
    "SkillManifest",
    "validate_manifest",
    "parse_manifest",
]
