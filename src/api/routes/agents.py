"""Agent management routes.

This module provides endpoints for monitoring and controlling
the various agents in the STLC pipeline.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/v1/metanoia/agents", tags=["Agents"])


class AgentStatusResponse(BaseModel):
    """Agent status response."""
    agent_id: str
    agent_type: str
    status: str
    output: dict = Field(default_factory=dict)
    error: Optional[str] = None
    duration_seconds: Optional[float] = None


class AgentPauseResponse(BaseModel):
    """Response after pausing an agent."""
    agent_id: str
    message: str
    status: str
