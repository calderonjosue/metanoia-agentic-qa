"""Sprint management routes.

This module provides endpoints for starting, monitoring, and
managing quality missions (sprints) in the STLC pipeline.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/v1/metanoia/sprint", tags=["Sprint"])


class SprintStartRequest(BaseModel):
    """Request to start a new sprint."""
    sprint_id: str = Field(..., description="Unique sprint identifier")
    sprint_goal: str = Field(..., description="Quality mission/goal")
    run_async: bool = Field(default=False, description="Run graph asynchronously")


class SprintStatusResponse(BaseModel):
    """Sprint status response."""
    sprint_id: str
    sprint_goal: str
    current_phase: str
    iteration_count: int
    context_analysis: Optional[dict] = None
    test_plan: Optional[dict] = None
    test_case_count: int = 0
    execution_results: dict
    release_certification: Optional[dict] = None
    started_at: str
    updated_at: str


class TestPlanResponse(BaseModel):
    """Test plan response."""
    sprint_id: str
    test_plan: dict
    test_cases: list


class CertificationResponse(BaseModel):
    """Release certification response."""
    sprint_id: str
    certified: bool
    confidence_score: float
    blockers: list[str]
    recommendations: list[str]
    summary: str
    certified_at: str
