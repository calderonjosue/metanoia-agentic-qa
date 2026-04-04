"""GitHub integration module for PR status, comments, and merges."""

from src.github.integration import (
    GitHubIntegration,
    CommitStatus,
    MergeResult,
    PRComment,
)

__all__ = [
    "GitHubIntegration",
    "CommitStatus",
    "MergeResult",
    "PRComment",
]
