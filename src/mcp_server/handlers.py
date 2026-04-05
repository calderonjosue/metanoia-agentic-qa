"""MCP request handlers."""
import logging

logger = logging.getLogger(__name__)


class MCPHandlers:
    """Handles MCP protocol requests."""

    def __init__(self, registry):
        self.registry = registry

    async def handle_sprint_start(self, params: dict) -> dict:
        """Handle sprint start request."""
        sprint_id = params.get("sprint_id", "")
        goals = params.get("goals", [])
        logger.info(f"Starting sprint {sprint_id} with goals: {goals}")
        return {
            "status": "started",
            "sprint_id": sprint_id,
            "goals": goals
        }

    async def handle_sprint_status(self, params: dict) -> dict:
        """Handle sprint status request."""
        sprint_id = params.get("sprint_id", "")
        return {
            "sprint_id": sprint_id,
            "status": "active",
            "progress": 0.0
        }

    async def handle_agent_execute(self, params: dict) -> dict:
        """Handle agent execution request."""
        agent_name = params.get("agent_name", "")
        task = params.get("task", {})
        logger.info(f"Executing agent {agent_name} with task {task}")
        return {
            "status": "executed",
            "agent": agent_name,
            "result": {}
        }
