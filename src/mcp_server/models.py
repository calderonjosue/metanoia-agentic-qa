"""MCP data models."""
from typing import Any, Optional
from pydantic import BaseModel


class MCPRequest(BaseModel):
    """Incoming MCP request."""
    method: str
    params: dict = {}
    id: Optional[str] = None


class MCPResponse(BaseModel):
    """Outgoing MCP response."""
    result: Optional[Any] = None
    error: Optional[dict] = None
    id: Optional[str] = None


class SprintStartParams(BaseModel):
    """Parameters for sprint start."""
    sprint_id: str
    goals: list[str] = []


class AgentExecuteParams(BaseModel):
    """Parameters for agent execution."""
    agent_name: str
    task: dict