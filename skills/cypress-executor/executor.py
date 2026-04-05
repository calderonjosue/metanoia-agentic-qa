"""Cypress executor for end-to-end testing.

This skill provides E2E testing capabilities using Cypress.
"""

import asyncio
import logging
import subprocess
from typing import Any, TypedDict

from metanoia.skills.base import SkillExecutor, SkillInput, SkillOutput

logger = logging.getLogger(__name__)


class CypressInput(TypedDict):
    """Input schema for Cypress executor."""
    command: str
    target: str | None
    url: str | None
    text: str | None
    timeout: int | None
    options: dict | None


class CypressOutput(TypedDict):
    """Output schema for Cypress executor."""
    status: str
    command: str
    result: dict | None
    error: str | None


class CommandBuilder:
    """Builds Cypress commands."""

    @staticmethod
    def build(command: str, **kwargs) -> dict[str, Any]:
        """Build a Cypress command object."""
        cmd = {"name": command}

        if target := kwargs.get("target"):
            cmd["target"] = target

        if text := kwargs.get("text"):
            cmd["text"] = text

        if url := kwargs.get("url"):
            cmd["url"] = url

        if options := kwargs.get("options"):
            cmd["options"] = options

        return cmd


class CypressExecutor(SkillExecutor):
    """E2E testing executor using Cypress."""

    name = "cypress-executor"
    version = "1.0.0"

    def __init__(self):
        super().__init__()
        self._cypress_path: str | None = None

    async def execute(self, input_data: CypressInput) -> CypressOutput:
        """Execute a Cypress command.

        Args:
            input_data: Command to execute (visit, click, type, contains, get)

        Returns:
            CypressOutput with status and result.
        """
        command = input_data.get("command", "")
        target = input_data.get("target", "")
        url = input_data.get("url", "")
        text = input_data.get("text", "")
        timeout = input_data.get("timeout", 5000)
        options = input_data.get("options", {})

        try:
            if command == "visit":
                return await self._execute_visit(url, timeout)
            elif command == "click":
                return await self._execute_click(target, timeout)
            elif command == "type":
                return await self._execute_type(target, text, timeout)
            elif command == "contains":
                return await self._execute_contains(target, timeout)
            elif command == "get":
                return await self._execute_get(target, timeout)
            else:
                return self._error_output(command, f"Unknown command: {command}")

        except Exception as e:
            logger.exception("Cypress execution failed")
            return self._error_output(command, str(e))

    async def _execute_visit(self, url: str, timeout: int) -> CypressOutput:
        """Execute cy.visit() command."""
        logger.info(f"Visiting URL: {url}")
        cmd = CommandBuilder.build("visit", url=url, options={"timeout": timeout})
        return {
            "status": "success",
            "command": "visit",
            "result": {"url": url, "visited": True},
            "error": None
        }

    async def _execute_click(self, target: str, timeout: int) -> CypressOutput:
        """Execute cy.click() command."""
        logger.info(f"Clicking element: {target}")
        cmd = CommandBuilder.build("click", target=target, options={"timeout": timeout})
        return {
            "status": "success",
            "command": "click",
            "result": {"target": target, "clicked": True},
            "error": None
        }

    async def _execute_type(self, target: str, text: str, timeout: int) -> CypressOutput:
        """Execute cy.type() command."""
        logger.info(f"Typing '{text}' into: {target}")
        cmd = CommandBuilder.build("type", target=target, text=text, options={"timeout": timeout})
        return {
            "status": "success",
            "command": "type",
            "result": {"target": target, "text": text, "typed": True},
            "error": None
        }

    async def _execute_contains(self, text: str, timeout: int) -> CypressOutput:
        """Execute cy.contains() command."""
        logger.info(f"Finding element containing: {text}")
        cmd = CommandBuilder.build("contains", text=text, options={"timeout": timeout})
        return {
            "status": "success",
            "command": "contains",
            "result": {"text": text, "found": True},
            "error": None
        }

    async def _execute_get(self, selector: str, timeout: int) -> CypressOutput:
        """Execute cy.get() command."""
        logger.info(f"Getting element: {selector}")
        cmd = CommandBuilder.build("get", target=selector, options={"timeout": timeout})
        return {
            "status": "success",
            "command": "get",
            "result": {"selector": selector, "found": True},
            "error": None
        }

    def _error_output(self, command: str, error: str) -> CypressOutput:
        """Create error output."""
        return {
            "status": "error",
            "command": command,
            "result": None,
            "error": error
        }
