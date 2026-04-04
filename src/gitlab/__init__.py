"""GitLab integration module for MR status, comments, and merges."""

from src.gitlab.integration import (
    GitLabIntegration,
    MRState,
    MergeResult,
)

__all__ = [
    "GitLabIntegration",
    "MRState",
    "MergeResult",
]
