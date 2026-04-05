"""Reporting routes.

This module provides endpoints for generating and retrieving
various reports from the STLC execution.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/v1/metanoia/reports", tags=["Reports"])


class SummaryReport(BaseModel):
    """Summary report across all sprints."""
    total_sprints: int
    certified_sprints: int
    rejected_sprints: int
    total_test_cases: int
    total_tests_executed: int
    sprints: list[dict]


class DetailedReport(BaseModel):
    """Detailed report for a specific sprint."""
    sprint_id: str
    metrics: dict
    agent_results: list[dict]
    test_cases: list[dict]
