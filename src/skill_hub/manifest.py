"""Manifest schema validation for Skill Hub."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class SkillEntry(BaseModel):
    name: str = Field(..., min_length=1)
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    description: str
    path: str


class SkillManifest(BaseModel):
    name: str = Field(..., min_length=1)
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    description: str
    author: str
    skills: list[SkillEntry] = Field(default_factory=list)
    runtime_version: str = Field(default=">=2.0")

    @field_validator("runtime_version")
    @classmethod
    def validate_runtime_version(cls, v: str) -> str:
        if not v.startswith(">="):
            raise ValueError("runtime_version must start with '>='")
        return v


def validate_manifest(data: dict[str, Any]) -> bool:
    try:
        SkillManifest(**data)
        return True
    except Exception:
        return False


def parse_manifest(data: dict[str, Any]) -> SkillManifest | None:
    try:
        return SkillManifest(**data)
    except Exception:
        return None
