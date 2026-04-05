"""MCP Server implementation."""
import logging

from .handlers import MCPHandlers
from .models import MCPResponse

logger = logging.getLogger(__name__)


class MCPServer:
    """MCP server for Metanoia-QA."""
    
    def __init__(self, skill_registry=None):
        from skill_runtime.registry import SkillRegistry
        self.registry = skill_registry or SkillRegistry()
        self.handlers = MCPHandlers(self.registry)
        self.running = False
        
    async def start(self):
        """Start the MCP server."""
        self.running = True
        logger.info("MCP Server started")
        
    async def stop(self):
        """Stop the MCP server."""
        self.running = False
        logger.info("MCP Server stopped")
        
    async def handle_request(self, method: str, params: dict, request_id: str | None = None) -> MCPResponse:
        """Handle incoming MCP request."""
        handlers = {
            "sprint/start": self.handlers.handle_sprint_start,
            "sprint/status": self.handlers.handle_sprint_status,
            "agent/execute": self.handlers.handle_agent_execute,
        }
        
        handler = handlers.get(method)
        if handler:
            try:
                result = await handler(params)
                return MCPResponse(result=result, id=request_id)
            except Exception as e:
                logger.exception(f"Handler error for {method}")
                return MCPResponse(
                    error={"code": -32603, "message": str(e)},
                    id=request_id
                )
        return MCPResponse(
            error={"code": -32601, "message": f"Unknown method: {method}"},
            id=request_id
        )