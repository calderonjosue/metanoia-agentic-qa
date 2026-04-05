"""GitLab integration module for MR status, comments, and merges."""

from src.gitlab.integration import (
    GitLabIntegration,
    MergeResult,
    MRState,
)

__all__ = [
    "GitLabIntegration",
    "MRState",
    "MergeResult",
]
