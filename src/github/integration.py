"""GitHub API client for PR operations, commit status, and merging.

This module provides a high-level interface for GitHub operations
required by the CI/CD orchestrator, using PyGithub or ghapi.
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

try:
    from github import Github
    from github.GithubException import GithubException
except ImportError:
    Github = None
    GithubException = None


class CommitStatus(str, Enum):
    """CI commit status values."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"


@dataclass
class PRComment:
    """Represents a PR comment."""

    id: int
    body: str
    author: str
    created_at: str


@dataclass
class MergeResult:
    """Result of a merge operation."""

    merged: bool
    sha: Optional[str] = None
    message: str = ""


class GitHubIntegration:
    """GitHub API client for PR and commit operations.

    Provides methods for checking PR status, posting comments,
    merging PRs, and checking CI commit status.

    Attributes:
        token: GitHub personal access token
        repo: Repository name in format 'owner/repo'
    """

    def __init__(
        self,
        token: Optional[str] = None,
        repo: Optional[str] = None,
    ):
        if Github is None:
            raise ImportError("PyGithub is required. Install with: pip install PyGithub")

        self.token = token or os.getenv("GITHUB_TOKEN")
        self.repo = repo or os.getenv("GITHUB_REPO")

        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN env var.")
        if not self.repo:
            raise ValueError("GitHub repo is required. Set GITHUB_REPO env var.")

        self._client = Github(self.token)
        self._repo = self._client.get_repo(self.repo)

    def check_pr_status(self, pr_number: int) -> dict[str, Any]:
        """Get the current state of a pull request.

        Args:
            pr_number: The PR number

        Returns:
            Dictionary containing PR state, title, head sha, and mergeability
        """
        pr = self._repo.get_pull(pr_number)

        return {
            "number": pr.number,
            "state": pr.state,
            "title": pr.title,
            "body": pr.body,
            "head_sha": pr.head.sha,
            "mergeable": pr.mergeable,
            "merged": pr.merged,
            "additions": pr.additions,
            "deletions": pr.deletions,
            "changed_files": pr.changed_files,
        }

    def post_comment(self, pr_number: int, body: str) -> PRComment:
        """Post a comment on a pull request.

        Args:
            pr_number: The PR number
            body: Comment body text

        Returns:
            PRComment object with comment details
        """
        pr = self._repo.get_pull(pr_number)
        comment = pr.create_issue_comment(body)

        return PRComment(
            id=comment.id,
            body=comment.body,
            author=comment.user.login,
            created_at=comment.created_at.isoformat(),
        )

    def merge_pr(
        self,
        pr_number: int,
        commit_title: Optional[str] = None,
        commit_message: Optional[str] = None,
    ) -> MergeResult:
        """Merge a pull request if quality gate passes.

        Args:
            pr_number: The PR number
            commit_title: Optional merge commit title
            commit_message: Optional merge commit message

        Returns:
            MergeResult indicating success/failure and details
        """
        pr = self._repo.get_pull(pr_number)

        if pr.is_cross_repository():
            return MergeResult(merged=False, message="Cross-repository PRs cannot be merged via API")

        if pr.state != "open":
            return MergeResult(merged=False, message=f"PR is not open: {pr.state}")

        if not pr.mergeable:
            return MergeResult(merged=False, message="PR is not mergeable (conflicts or failed checks)")

        try:
            merge_result = pr.merge(
                commit_title=commit_title or f"Merge PR #{pr_number}",
                commit_message=commit_message or "Merged via Metanoia-QA",
            )
            return MergeResult(
                merged=True,
                sha=merge_result.sha,
                message="Successfully merged",
            )
        except GithubException as e:
            return MergeResult(merged=False, message=f"Merge failed: {e.data.get('message', str(e))}")

    def get_commit_status(self, sha: str) -> dict[str, Any]:
        """Get the combined CI status for a commit.

        Args:
            sha: The commit SHA

        Returns:
            Dictionary with combined status, state, and individual statuses
        """
        commit = self._repo.get_commit(sha)
        combined = commit.get_combined_status()

        statuses = []
        for status in combined.statuses:
            statuses.append({
                "context": status.context,
                "state": status.state,
                "description": status.description,
                "target_url": status.target_url,
            })

        return {
            "sha": sha,
            "state": combined.state,
            "total_count": combined.total_count,
            "statuses": statuses,
        }

    def get_pr_checks(self, pr_number: int) -> list[dict[str, Any]]:
        """Get all check runs for a PR's head commit.

        Args:
            pr_number: The PR number

        Returns:
            List of check run dictionaries
        """
        pr = self._repo.get_pull(pr_number)
        check_runs = self._repo.get_commit(pr.head.sha).get_check_runs()

        return [
            {
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "details_url": run.html_url,
            }
            for run in check_runs
        ]
