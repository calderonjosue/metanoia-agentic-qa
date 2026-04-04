"""Agent type definitions."""

from enum import Enum


class AgentType(str, Enum):
    """Agent type enumeration - corporate role names."""
    CONTEXT_ANALYST = "context_analyst"
    STRATEGY_MANAGER = "strategy_manager"
    TEST_DESIGN_LEAD = "test_design_lead"
    UI_AUTOMATION_ENGINEER = "ui_automation_engineer"
    PERFORMANCE_ENGINEER = "performance_engineer"
    SECURITY_ENGINEER = "security_engineer"
    INTEGRATION_ENGINEER = "integration_engineer"
    RELEASE_ANALYST = "release_analyst"
