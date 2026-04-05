"""CI/CD pipeline orchestration for triggering and monitoring pipelines.

This module provides pipeline orchestration capabilities including
triggering pipelines, polling status, and retrieving artifacts.
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import httpx


class PipelineStatus(str, Enum):
    """Pipeline execution status values."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"
    SKIPPED = "skipped"


@dataclass
class PipelineRun:
    """Represents a CI pipeline run."""

    id: str
    status: PipelineStatus
    web_url: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    duration: Optional[int] = None


@dataclass
class ArtifactDownload:
    """Represents a downloaded artifact."""

    name: str
    path: str
    size_bytes: int


class PipelineOrchestrator:
    """CI/CD pipeline orchestration for GitHub Actions and GitLab CI.

    Provides methods to trigger pipelines, poll for completion,
    and retrieve test artifacts.

    Attributes:
        provider: CI provider ('github' or 'gitlab')
        token: API access token
        owner: Repository owner/organization
        repo: Repository name
    """

    def __init__(
        self,
        provider: str = "github",
        token: Optional[str] = None,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
    ):
        import os

        self.provider = provider.lower()
        self.token = token or os.getenv("CI_TOKEN") or os.getenv("GITHUB_TOKEN")
        self.owner = owner or os.getenv("CI_OWNER") or os.getenv("GITHUB_REPO_OWNER")
        self.repo = repo or os.getenv("CI_REPO") or os.getenv("GITHUB_REPO_NAME")

        if not self.token:
            raise ValueError("CI token is required. Set CI_TOKEN or GITHUB_TOKEN env var.")
        if not self.owner or not self.repo:
            raise ValueError("Owner and repo are required. Set CI_OWNER/CI_REPO env vars.")

        self._client = httpx.Client(timeout=30.0)

    def trigger_pipeline(
        self,
        branch: str,
        parameters: Optional[dict[str, Any]] = None,
    ) -> PipelineRun:
        """Start a CI pipeline for the specified branch.

        Args:
            branch: Git branch to run pipeline on
            parameters: Optional pipeline parameters (env vars, inputs, etc.)

        Returns:
            PipelineRun object with pipeline ID and status
        """
        if self.provider == "github":
            return self._trigger_github_workflow(branch, parameters)
        elif self.provider == "gitlab":
            return self._trigger_gitlab_pipeline(branch, parameters)
        else:
            raise ValueError(f"Unsupported CI provider: {self.provider}")

    def _trigger_github_workflow(
        self,
        branch: str,
        parameters: Optional[dict[str, Any]],
    ) -> PipelineRun:
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/actions/workflows/dispatch"

        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

        payload = {
            "ref": branch,
            "inputs": parameters or {},
        }

        response = self._client.post(url, headers=headers, json=payload)
        response.raise_for_status()

        workflow_runs_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/actions/runs"
        runs_response = self._client.get(workflow_runs_url, headers=headers)
        runs = runs_response.json().get("workflow_runs", [])

        if runs:
            latest = runs[0]
            return PipelineRun(
                id=str(latest["id"]),
                status=PipelineStatus(latest["status"]),
                web_url=latest["html_url"],
                started_at=latest.get("run_started_at"),
            )

        return PipelineRun(
            id="unknown",
            status=PipelineStatus.PENDING,
            web_url=f"https://github.com/{self.owner}/{self.repo}/actions",
        )

    def _trigger_gitlab_pipeline(
        self,
        branch: str,
        parameters: Optional[dict[str, Any]],
    ) -> PipelineRun:
        url = f"https://gitlab.com/api/v4/projects/{self.owner}%2F{self.repo}/pipeline"

        headers = {"PRIVATE-TOKEN": self.token}

        payload = {
            "ref": branch,
            "variables": [
                {"key": k, "value": str(v)}
                for k, v in (parameters or {}).items()
            ],
        }

        response = self._client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        return PipelineRun(
            id=str(data["id"]),
            status=PipelineStatus(data["status"]),
            web_url=data["web_url"],
            started_at=data.get("created_at"),
        )

    def poll_status(
        self,
        pipeline_id: str,
        timeout: int = 3600,
        poll_interval: int = 30,
    ) -> PipelineRun:
        """Wait for pipeline completion.

        Args:
            pipeline_id: The pipeline ID to wait for
            timeout: Maximum seconds to wait
            poll_interval: Seconds between status checks

        Returns:
            PipelineRun with final status
        """
        elapsed = 0

        while elapsed < timeout:
            status = self.get_pipeline_status(pipeline_id)

            if status.status in (
                PipelineStatus.SUCCESS,
                PipelineStatus.FAILED,
                PipelineStatus.CANCELED,
                PipelineStatus.SKIPPED,
            ):
                return status

            time.sleep(poll_interval)
            elapsed += poll_interval

        return status

    def get_pipeline_status(self, pipeline_id: str) -> PipelineRun:
        """Get current pipeline status.

        Args:
            pipeline_id: The pipeline ID

        Returns:
            PipelineRun with current status
        """
        if self.provider == "github":
            return self._get_github_workflow_status(pipeline_id)
        elif self.provider == "gitlab":
            return self._get_gitlab_pipeline_status(pipeline_id)
        else:
            raise ValueError(f"Unsupported CI provider: {self.provider}")

    def _get_github_workflow_status(self, pipeline_id: str) -> PipelineRun:
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/actions/runs/{pipeline_id}"

        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = self._client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        return PipelineRun(
            id=str(data["id"]),
            status=PipelineStatus(data["status"]),
            web_url=data["html_url"],
            started_at=data.get("run_started_at"),
            finished_at=data.get("updated_at"),
        )

    def _get_gitlab_pipeline_status(self, pipeline_id: str) -> PipelineRun:
        url = f"https://gitlab.com/api/v4/projects/{self.owner}%2F{self.repo}/pipelines/{pipeline_id}"

        headers = {"PRIVATE-TOKEN": self.token}

        response = self._client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        return PipelineRun(
            id=str(data["id"]),
            status=PipelineStatus(data["status"]),
            web_url=data["web_url"],
            started_at=data.get("created_at"),
            finished_at=data.get("finished_at"),
            duration=data.get("duration"),
        )

    def get_artifacts(
        self,
        pipeline_id: str,
        artifact_name: str,
        target_path: str = ".",
    ) -> ArtifactDownload:
        """Download test results or other artifacts.

        Args:
            pipeline_id: The pipeline ID
            artifact_name: Name of the artifact to download
            target_path: Local directory to save artifact

        Returns:
            ArtifactDownload with artifact details
        """
        if self.provider == "github":
            return self._get_github_artifacts(pipeline_id, artifact_name, target_path)
        elif self.provider == "gitlab":
            return self._get_gitlab_artifacts(pipeline_id, artifact_name, target_path)
        else:
            raise ValueError(f"Unsupported CI provider: {self.provider}")

    def _get_github_artifacts(
        self,
        pipeline_id: str,
        artifact_name: str,
        target_path: str,
    ) -> ArtifactDownload:
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/actions/runs/{pipeline_id}/artifacts"

        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = self._client.get(url, headers=headers)
        response.raise_for_status()
        artifacts = response.json().get("artifacts", [])

        for artifact in artifacts:
            if artifact["name"] == artifact_name:
                download_url = artifact["archive_download_url"]
                download_response = self._client.get(download_url, headers=headers)
                download_response.raise_for_status()

                import io
                import zipfile

                z = zipfile.ZipFile(io.BytesIO(download_response.content))
                z.extractall(target_path)

                return ArtifactDownload(
                    name=artifact["name"],
                    path=target_path,
                    size_bytes=artifact["size_in_bytes"],
                )

        raise ValueError(f"Artifact '{artifact_name}' not found in pipeline {pipeline_id}")

    def _get_gitlab_artifacts(
        self,
        pipeline_id: str,
        artifact_name: str,
        target_path: str,
    ) -> ArtifactDownload:
        import urllib.parse

        project_encoded = urllib.parse.quote(f"{self.owner}/{self.repo}", safe="")
        url = f"https://gitlab.com/api/v4/projects/{project_encoded}/pipelines/{pipeline_id}/jobs"

        headers = {"PRIVATE-TOKEN": self.token}

        response = self._client.get(url, headers=headers)
        response.raise_for_status()
        jobs = response.json()

        for job in jobs:
            if job["name"] == artifact_name or artifact_name in str(job.get("artifacts", [])):
                job_id = job["id"]
                artifact_url = f"https://gitlab.com/api/v4/projects/{project_encoded}/jobs/{job_id}/artifacts"

                artifact_response = self._client.get(artifact_url, headers=headers)

                import io
                import zipfile

                z = zipfile.ZipFile(io.BytesIO(artifact_response.content))
                z.extractall(target_path)

                return ArtifactDownload(
                    name=artifact_name,
                    path=target_path,
                    size_bytes=len(artifact_response.content),
                )

        raise ValueError(f"Artifact '{artifact_name}' not found in pipeline {pipeline_id}")
