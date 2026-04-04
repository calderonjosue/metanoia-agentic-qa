"""GitLab API client for MR operations and merging.

This module provides a high-level interface for GitLab operations
required by the CI/CD orchestrator, using python-gitlab.
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

try:
    import gitlab
except ImportError:
    gitlab = None


class MRState(str, Enum):
    """Merge request state values."""

    OPENED = "opened"
    CLOSED = "closed"
    MERGED = "merged"
    LOCKED = "locked"


@dataclass
class MergeResult:
    """Result of a merge operation."""

    merged: bool
    iid: Optional[int] = None
    message: str = ""


class GitLabIntegration:
    """GitLab API client for MR and project operations.

    Provides methods for checking MR status, posting comments,
    and merging MRs.

    Attributes:
        token: GitLab personal access token
        project_id: GitLab project ID or path (namespace/project)
    """

    def __init__(
        self,
        token: Optional[str] = None,
        project_id: Optional[str] = None,
        url: Optional[str] = None,
    ):
        if gitlab is None:
            raise ImportError("python-gitlab is required. Install with: pip install python-gitlab")

        self.token = token or os.getenv("GITLAB_TOKEN")
        self.project_id = project_id or os.getenv("GITLAB_PROJECT_ID")
        self.url = url or os.getenv("GITLAB_URL", "https://gitlab.com")

        if not self.token:
            raise ValueError("GitLab token is required. Set GITLAB_TOKEN env var.")
        if not self.project_id:
            raise ValueError("GitLab project ID is required. Set GITLAB_PROJECT_ID env var.")

        self._client = gitlab.Gitlab(self.url, private_token=self.token)
        self._project = self._client.projects.get(self.project_id)

    def check_mr_status(self, mr_iid: int) -> dict[str, Any]:
        """Get the current state of a merge request.

        Args:
            mr_iid: The MR IID (internal ID)

        Returns:
            Dictionary containing MR state, title, source branch, and mergeability
        """
        mr = self._project.mergerequests.get(mr_iid)

        return {
            "iid": mr.iid,
            "state": mr.state,
            "title": mr.title,
            "description": mr.description,
            "source_branch": mr.source_branch,
            "target_branch": mr.target_branch,
            "merge_status": mr.merge_status,
            "merged": mr.state == "merged",
            "has_conflicts": mr.merge_status == "cannot_be_merged",
            "detailed_merge_status": getattr(mr, "detailed_merge_status", None),
        }

    def post_comment(self, mr_iid: int, body: str) -> dict[str, Any]:
        """Post a comment on a merge request.

        Args:
            mr_iid: The MR IID
            body: Comment body text

        Returns:
            Dictionary with comment details
        """
        mr = self._project.mergerequests.get(mr_iid)
        note = mr.notes.create({"body": body})

        return {
            "id": note.id,
            "body": note.body,
            "author": note.author["username"],
            "created_at": note.created_at,
        }

    def merge_mr(
        self,
        mr_iid: int,
        should_remove_source_branch: bool = True,
        merge_commit_message: Optional[str] = None,
    ) -> MergeResult:
        """Merge a merge request if quality gate passes.

        Args:
            mr_iid: The MR IID
            should_remove_source_branch: Whether to delete source branch after merge
            merge_commit_message: Optional custom merge commit message

        Returns:
            MergeResult indicating success/failure and details
        """
        mr = self._project.mergerequests.get(mr_iid)

        if mr.state != "opened":
            return MergeResult(merged=False, message=f"MR is not open: {mr.state}")

        if mr.merge_status in ("cannot_be_merged", "cannot_be_merged_rechecking"):
            return MergeResult(merged=False, message="MR cannot be merged (conflicts or failed checks)")

        try:
            options = {
                "should_remove_source_branch": should_remove_source_branch,
            }
            if merge_commit_message:
                options["merge_commit_message"] = merge_commit_message

            mr.merge(**options)

            return MergeResult(
                merged=True,
                iid=mr_iid,
                message="Successfully merged",
            )
        except gitlab.GitLabMRClosedError:
            return MergeResult(merged=False, message="MR is closed")
        except gitlab.GitLabMRNotOpenError:
            return MergeResult(merged=False, message="MR is not open")
        except Exception as e:
            return MergeResult(merged=False, message=f"Merge failed: {str(e)}")

    def get_mr_changes(self, mr_iid: int) -> dict[str, Any]:
        """Get the changes (diff) of a merge request.

        Args:
            mr_iid: The MR IID

        Returns:
            Dictionary with MR changes including diffs
        """
        mr = self._project.mergerequests.get(mr_iid, lazy=False)
        changes = mr.changes()

        return {
            "iid": mr.iid,
            "state": mr.state,
            "changes": changes.get("changes", []),
            "diff_refs": changes.get("diff_refs"),
        }
