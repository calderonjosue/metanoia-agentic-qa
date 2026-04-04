"""Metanoia-QA FastAPI Application.

This module provides the REST API for the autonomous QA system,
managing sprints, agent coordination, and release certification.
"""

import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google.genai import Client as GeminiClient

from src.orchestrator.graph import MetanoiaGraph, create_graph
from src.orchestrator.state import MetanoiaState, AgentType, AgentStatus
from src.orchestrator.checkpointing import PostgresCheckpointSaver, get_checkpointer
from src.knowledge.rag import MetanoiaRAG, AgentLessonsLearned

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    logger.info("Starting Metanoia-QA API...")
    yield
    logger.info("Shutting down Metanoia-QA API...")


app = FastAPI(
    title="Metanoia-QA API",
    description="Autonomous Agentic STLC Framework",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SprintStartRequest(BaseModel):
    """Request model for starting a new sprint."""
    sprint_id: str = Field(..., description="Unique sprint identifier")
    sprint_goal: str = Field(..., description="Quality mission/goal for the sprint")
    run_async: bool = Field(default=False, description="Run graph asynchronously")


class SprintStatusResponse(BaseModel):
    """Response model for sprint status."""
    sprint_id: str
    sprint_goal: str
    current_phase: str
    iteration_count: int
    context_analysis: Optional[dict] = None
    test_plan: Optional[dict] = None
    test_case_count: int = 0
    execution_results: dict = Field(default_factory=dict)
    release_certification: Optional[dict] = None
    started_at: str
    updated_at: str


class TestPlanResponse(BaseModel):
    """Response model for test plan."""
    sprint_id: str
    test_plan: dict
    test_cases: list


class CertificationResponse(BaseModel):
    """Response model for release certification."""
    sprint_id: str
    certified: bool
    confidence_score: float
    blockers: list[str]
    recommendations: list[str]
    summary: str
    certified_at: str


class AgentStatusResponse(BaseModel):
    """Response model for agent status."""
    agent_id: str
    agent_type: str
    status: str
    output: dict = Field(default_factory=dict)
    error: Optional[str] = None
    duration_seconds: Optional[float] = None


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    timestamp: str
    supabase_connected: bool


_active_graphs: dict[str, MetanoiaGraph] = {}
_active_states: dict[str, MetanoiaState] = {}


def get_graph() -> MetanoiaGraph:
    """Get or create the MetanoiaGraph instance."""
    if "default" not in _active_graphs:
        checkpointer = None
        if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
            try:
                checkpointer = get_checkpointer()
            except Exception as e:
                logger.warning(f"Could not initialize checkpointer: {e}")

        _active_graphs["default"] = create_graph(checkpointer=checkpointer)

    return _active_graphs["default"]


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check API and dependency health."""
    from src.knowledge.client import get_supabase_client

    supabase_connected = False
    try:
        client = get_supabase_client()
        supabase_connected = client.table("pg_stat_activity").select("pid").limit(1).execute().data is not None
    except Exception:
        pass

    return HealthResponse(
        status="healthy" if supabase_connected else "degraded",
        version="0.1.0",
        timestamp=datetime.utcnow().isoformat(),
        supabase_connected=supabase_connected,
    )


@app.post("/v1/metanoia/sprint/start", response_model=SprintStatusResponse, tags=["Sprint"])
async def start_sprint(request: SprintStartRequest, background_tasks: BackgroundTasks):
    """Start a new quality mission (sprint processing).

    This endpoint initiates the STLC pipeline by creating a new
    MetanoiaState and triggering the LangGraph execution.

    Args:
        request: Sprint start request with ID and goal

    Returns:
        Initial sprint status with state
    """
    logger.info(f"Starting sprint: {request.sprint_id}")

    state = MetanoiaState(
        sprint_id=request.sprint_id,
        sprint_goal=request.sprint_goal,
    )

    graph = get_graph()

    if request.run_async:
        _active_states[request.sprint_id] = state

        async def run_graph_async():
            async for _ in graph.run_async(state, thread_id=request.sprint_id):
                _active_states[request.sprint_id] = graph.graph.get_state(
                    {"configurable": {"thread_id": request.sprint_id}}
                ).values

        background_tasks.add_task(run_graph_async)

        return SprintStatusResponse(
            sprint_id=state.sprint_id,
            sprint_goal=state.sprint_goal,
            current_phase=state.current_phase,
            iteration_count=state.iteration_count,
            test_case_count=len(state.test_cases),
            started_at=state.started_at.isoformat(),
            updated_at=state.updated_at.isoformat(),
        )
    else:
        result = graph.run(state, thread_id=request.sprint_id)

        return SprintStatusResponse(
            sprint_id=result.sprint_id,
            sprint_goal=result.sprint_goal,
            current_phase=result.current_phase,
            iteration_count=result.iteration_count,
            context_analysis=result.context_analysis,
            test_plan=result.test_plan,
            test_case_count=len(result.test_cases),
            execution_results={
                agent_id: {
                    "status": r.status.value,
                    "output": r.output,
                }
                for agent_id, r in result.execution_results.items()
            },
            release_certification=result.release_certification.model_dump() if result.release_certification else None,
            started_at=result.started_at.isoformat(),
            updated_at=result.updated_at.isoformat(),
        )


@app.get("/v1/metanoia/sprint/{sprint_id}/status", response_model=SprintStatusResponse, tags=["Sprint"])
async def get_sprint_status(sprint_id: str):
    """Get current status of a sprint.

    Args:
        sprint_id: Sprint identifier

    Returns:
        Current sprint status
    """
    if sprint_id in _active_states:
        state = _active_states[sprint_id]
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sprint {sprint_id} not found"
        )

    return SprintStatusResponse(
        sprint_id=state.sprint_id,
        sprint_goal=state.sprint_goal,
        current_phase=state.current_phase,
        iteration_count=state.iteration_count,
        context_analysis=state.context_analysis,
        test_plan=state.test_plan,
        test_case_count=len(state.test_cases),
        execution_results={
            agent_id: {
                "status": r.status.value,
                "output": r.output,
            }
            for agent_id, r in state.execution_results.items()
        },
        release_certification=state.release_certification.model_dump() if state.release_certification else None,
        started_at=state.started_at.isoformat(),
        updated_at=state.updated_at.isoformat(),
    )


@app.get("/v1/metanoia/sprint/{sprint_id}/test-plan", response_model=TestPlanResponse, tags=["Sprint"])
async def get_test_plan(sprint_id: str):
    """Get the test plan for a sprint.

    Args:
        sprint_id: Sprint identifier

    Returns:
        Test plan with detailed test cases
    """
    if sprint_id not in _active_states:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sprint {sprint_id} not found"
        )

    state = _active_states[sprint_id]

    if not state.test_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test plan not yet generated"
        )

    return TestPlanResponse(
        sprint_id=state.sprint_id,
        test_plan=state.test_plan,
        test_cases=[tc.model_dump() for tc in state.test_cases],
    )


@app.get("/v1/metanoia/sprint/{sprint_id}/certification", response_model=CertificationResponse, tags=["Sprint"])
async def get_certification(sprint_id: str):
    """Get release certification for a sprint.

    Args:
        sprint_id: Sprint identifier

    Returns:
        Release certification decision
    """
    if sprint_id not in _active_states:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sprint {sprint_id} not found"
        )

    state = _active_states[sprint_id]

    if not state.release_certification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification not yet available"
        )

    cert = state.release_certification

    return CertificationResponse(
        sprint_id=cert.sprint_id,
        certified=cert.certified,
        confidence_score=cert.confidence_score,
        blockers=cert.blockers,
        recommendations=cert.recommendations,
        summary=cert.summary,
        certified_at=cert.certified_at.isoformat(),
    )


@app.get("/v1/metanoia/agents/status", response_model=list[AgentStatusResponse], tags=["Agents"])
async def get_all_agents_status():
    """Get status of all active agents.

    Returns:
        List of agent statuses
    """
    statuses = []

    for sprint_id, state in _active_states.items():
        for agent_id, result in state.execution_results.items():
            statuses.append(AgentStatusResponse(
                agent_id=result.agent_id,
                agent_type=result.agent_type.value,
                status=result.status.value,
                output=result.output,
                error=result.error,
                duration_seconds=result.duration_seconds,
            ))

    return statuses


@app.post("/v1/metanoia/agents/{agent_id}/pause", response_model=AgentStatusResponse, tags=["Agents"])
async def pause_agent(agent_id: str):
    """Pause a running agent.

    Args:
        agent_id: Agent identifier

    Returns:
        Updated agent status
    """
    for state in _active_states.values():
        if agent_id in state.execution_results:
            result = state.execution_results[agent_id]
            result.status = AgentStatus.PAUSED

            return AgentStatusResponse(
                agent_id=result.agent_id,
                agent_type=result.agent_type.value,
                status=result.status.value,
                output=result.output,
                error=result.error,
                duration_seconds=result.duration_seconds,
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Agent {agent_id} not found"
    )


@app.post("/v1/metanoia/agents/{agent_id}/resume", response_model=AgentStatusResponse, tags=["Agents"])
async def resume_agent(agent_id: str):
    """Resume a paused agent.

    Args:
        agent_id: Agent identifier

    Returns:
        Updated agent status
    """
    for state in _active_states.values():
        if agent_id in state.execution_results:
            result = state.execution_results[agent_id]

            if result.status != AgentStatus.PAUSED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Agent {agent_id} is not paused"
                )

            result.status = AgentStatus.RUNNING

            return AgentStatusResponse(
                agent_id=result.agent_id,
                agent_type=result.agent_type.value,
                status=result.status.value,
                output=result.output,
                error=result.error,
                duration_seconds=result.duration_seconds,
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Agent {agent_id} not found"
    )


@app.get("/v1/metanoia/reports/summary", tags=["Reports"])
async def get_summary_report():
    """Get a summary report of all sprints.

    Returns:
        Summary report with aggregated metrics
    """
    total_sprints = len(_active_states)
    certified_count = sum(
        1 for s in _active_states.values()
        if s.release_certification and s.release_certification.certified
    )

    total_test_cases = sum(len(s.test_cases) for s in _active_states.values())
    total_executed = sum(
        r.output.get("tests_passed", 0) + r.output.get("tests_failed", 0)
        for s in _active_states.values()
        for r in s.execution_results.values()
    )

    return {
        "total_sprints": total_sprints,
        "certified_sprints": certified_count,
        "rejected_sprints": total_sprints - certified_count,
        "total_test_cases": total_test_cases,
        "total_tests_executed": total_executed,
        "sprints": [
            {
                "sprint_id": s.sprint_id,
                "phase": s.current_phase,
                "certified": s.release_certification.certified if s.release_certification else None,
            }
            for s in _active_states.values()
        ],
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true",
    )
