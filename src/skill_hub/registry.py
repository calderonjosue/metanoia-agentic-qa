"""Community skill registry for Skill Hub.

Local cache of skill manifests and GitHub-based registry lookup.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path

import yaml

from metanoia.src.skill_hub.manifest import SkillManifest, validate_manifest

logger = logging.getLogger(__name__)

CACHE_DIR = Path.home() / ".metanoia" / "skill_cache"
DEFAULT_REGISTRY_URL = "https://api.github.com/repos/metanoia-qa/skills/contents"


@dataclass
class SkillEntry:
    name: str
    version: str
    description: str
    path: str


@dataclass
class CachedSkill:
    manifest: SkillManifest
    local_path: Path | None = None
    is_installed: bool = False


class CommunitySkillRegistry:
    """Community skill registry with local cache and GitHub lookup."""

    def __init__(self, cache_dir: Path | None = None, registry_url: str | None = None):
        self.cache_dir = cache_dir or CACHE_DIR
        self.registry_url = registry_url or DEFAULT_REGISTRY_URL
        self._cache: dict[str, CachedSkill] = {}
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        manifest_file = self.cache_dir / "registry_manifest.json"
        if manifest_file.exists():
            try:
                with open(manifest_file) as f:
                    data = json.load(f)
                    for name, info in data.items():
                        self._cache[name] = CachedSkill(
                            manifest=SkillManifest(**info["manifest"]),
                            local_path=Path(info["local_path"]) if info.get("local_path") else None,
                            is_installed=info.get("is_installed", False)
                        )
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")

    def _save_cache(self) -> None:
        manifest_file = self.cache_dir / "registry_manifest.json"
        data = {}
        for name, cached in self._cache.items():
            data[name] = {
                "manifest": cached.manifest.model_dump(),
                "local_path": str(cached.local_path) if cached.local_path else None,
                "is_installed": cached.is_installed
            }
        with open(manifest_file, "w") as f:
            json.dump(data, f, indent=2)

    async def fetch_manifest(self, skill_name: str) -> SkillManifest | None:
        import httpx

        url = f"https://raw.githubusercontent.com/metanoia-qa/skills/main/{skill_name}/skill-manifest.yaml"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                if response.status_code == 200:
                    manifest_data = yaml.safe_load(response.text)
                    if validate_manifest(manifest_data):
                        return SkillManifest(**manifest_data)
        except Exception as e:
            logger.error(f"Failed to fetch manifest for {skill_name}: {e}")
        return None

    async def search(self, query: str) -> list[SkillManifest]:
        manifests = []
        for cached in self._cache.values():
            if query.lower() in cached.manifest.name.lower() or query.lower() in cached.manifest.description.lower():
                manifests.append(cached.manifest)
        return manifests

    async def install(self, skill_name: str) -> bool:
        manifest = await self.fetch_manifest(skill_name)
        if manifest is None:
            return False

        install_path = self.cache_dir / skill_name
        install_path.mkdir(parents=True, exist_ok=True)

        manifest_path = install_path / "skill-manifest.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(manifest.model_dump(), f)

        self._cache[skill_name] = CachedSkill(
            manifest=manifest,
            local_path=install_path,
            is_installed=True
        )
        self._save_cache()
        return True

    def uninstall(self, skill_name: str) -> bool:
        if skill_name not in self._cache:
            return False

        cached = self._cache[skill_name]
        if cached.local_path and cached.local_path.exists():
            import shutil
            shutil.rmtree(cached.local_path)

        del self._cache[skill_name]
        self._save_cache()
        return True

    def list_installed(self) -> list[SkillManifest]:
        return [c.manifest for c in self._cache.values() if c.is_installed]

    def get_local_manifest(self, skill_name: str) -> SkillManifest | None:
        cached = self._cache.get(skill_name)
        return cached.manifest if cached else None


_global_registry: CommunitySkillRegistry | None = None


def get_hub_registry() -> CommunitySkillRegistry:
    global _global_registry
    if _global_registry is None:
        _global_registry = CommunitySkillRegistry()
    return _global_registry
