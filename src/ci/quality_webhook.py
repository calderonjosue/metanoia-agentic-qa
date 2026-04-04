"""Webhook handler for GitHub and GitLab CI events.

This module processes incoming webhooks from GitHub and GitLab
for quality gate evaluation and pipeline status updates.
"""

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from typing import Any, Optional

import httpx


@dataclass
class WebhookEvent:
    """Parsed webhook event data.

    Attributes:
        event_type: Type of event (e.g., 'push', 'pull_request', 'merge_request')
        repository: Repository name in format 'owner/repo'
        branch: Branch name
        commit_sha: Commit SHA
        payload: Raw webhook payload
    """

    event_type: str
    repository: str
    branch: str
    commit_sha: str
    payload: dict[str, Any]


@dataclass
class QualityPayload:
    """Quality gate evaluation payload.

    Attributes:
        pr_id: Pull request or merge request ID
        repository: Repository name
        score: Quality score (0.0 to 1.0)
        analysis_output: Detailed analysis results
        build_status: CI build status ('passed' or 'failed')
    """

    pr_id: str
    repository: str
    score: float
    analysis_output: dict[str, Any]
    build_status: str


def _verify_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature.

    Args:
        payload: Raw request body
        signature: X-Hub-Signature-256 header value
        secret: Webhook secret token

    Returns:
        True if signature is valid
    """
    if not signature.startswith("sha256="):
        return False

    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(f"sha256={expected}", signature)


def _verify_gitlab_token(token: str, secret: Optional[str] = None) -> bool:
    """Verify GitLab webhook token.

    Args:
        token: X-Gitlab-Token header value
        secret: Expected secret token

    Returns:
        True if token is valid
    """
    expected = secret or os.getenv("GITLAB_WEBHOOK_SECRET", "")
    return hmac.compare_digest(expected, token)


def handle_github_webhook(
    payload: bytes,
    headers: dict[str, str],
    secret: Optional[str] = None,
) -> WebhookEvent:
    """Process GitHub webhook payload.

    Args:
        payload: Raw request body
        headers: Request headers
        secret: Webhook secret for signature verification

    Returns:
        WebhookEvent with parsed event data

    Raises:
        ValueError: If signature verification fails or payload is invalid
    """
    secret = secret or os.getenv("GITHUB_WEBHOOK_SECRET", "")

    signature = headers.get("X-Hub-Signature-256", "")
    if secret and not _verify_github_signature(payload, signature, secret):
        raise ValueError("Invalid GitHub webhook signature")

    event_type = headers.get("X-GitHub-Event", "unknown")
    data = json.loads(payload)

    repository = data.get("repository", {}).get("full_name", "")
    branch = ""
    commit_sha = ""

    if event_type == "push":
        branch = data.get("ref", "").replace("refs/heads/", "")
        commit_sha = data.get("after", "")
    elif event_type in ("pull_request", "pull_request_target"):
        pr = data.get("pull_request", {})
        branch = pr.get("head", {}).get("ref", "")
        commit_sha = pr.get("head", {}).get("sha", "")
    elif event_type == "check_run" or event_type == "check_suite":
        check = data.get("check_run", data.get("check_suite", {}))
        branch = check.get("head_branch", "")
        commit_sha = check.get("head_sha", "")

    return WebhookEvent(
        event_type=event_type,
        repository=repository,
        branch=branch,
        commit_sha=commit_sha,
        payload=data,
    )


def handle_gitlab_webhook(
    payload: bytes,
    headers: dict[str, str],
    secret: Optional[str] = None,
) -> WebhookEvent:
    """Process GitLab webhook payload.

    Args:
        payload: Raw request body
        headers: Request headers
        secret: Webhook secret for token verification

    Returns:
        WebhookEvent with parsed event data

    Raises:
        ValueError: If token verification fails or payload is invalid
    """
    secret = secret or os.getenv("GITLAB_WEBHOOK_SECRET", "")

    token = headers.get("X-Gitlab-Token", "")
    if secret and not _verify_gitlab_token(token, secret):
        raise ValueError("Invalid GitLab webhook token")

    data = json.loads(payload)

    event_type = data.get("object_kind", "unknown")
    repository = data.get("project", {}).get("path_with_namespace", "")
    branch = ""
    commit_sha = ""

    if event_type == "push":
        branch = data.get("ref", "").replace("refs/heads/", "")
        commit_sha = data.get("after", "")
    elif event_type == "merge_request":
        mr = data.get("object_attributes", {})
        branch = mr.get("source_branch", "")
        commit_sha = mr.get("last_commit", {}).get("id", "")

    return WebhookEvent(
        event_type=event_type,
        repository=repository,
        branch=branch,
        commit_sha=commit_sha,
        payload=data,
    )


async def forward_to_orchestrator(
    webhook_event: WebhookEvent,
    orchestrator_url: str,
) -> dict[str, Any]:
    """Forward webhook event to the pipeline orchestrator.

    Args:
        webhook_event: Parsed webhook event
        orchestrator_url: URL of the orchestrator service

    Returns:
        Response from the orchestrator
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{orchestrator_url}/webhook/quality",
            json={
                "event_type": webhook_event.event_type,
                "repository": webhook_event.repository,
                "branch": webhook_event.branch,
                "commit_sha": webhook_event.commit_sha,
                "payload": webhook_event.payload,
            },
        )
        response.raise_for_status()
        return response.json()
