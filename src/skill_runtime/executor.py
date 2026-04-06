"""Skill execution engine for Metanoia-QA.

Manages the lifecycle of skill execution including validation,
execution, error handling, and cleanup.
"""

import asyncio
import logging
from typing import Any, TypedDict

from metanoia.skills.base import SkillExecutionError, SkillExecutor

logger = logging.getLogger(__name__)


class ExecutionResult(TypedDict):
    """Result of skill execution."""
    status: str
    data: dict[str, Any] | None
    error: str | None
    execution_time_ms: float | None


class SkillExecutorEngine:
    """Engine for executing skills with lifecycle management."""

    def __init__(self, timeout_seconds: float = 300.0):
        """Initialize the execution engine.

        Args:
            timeout_seconds: Maximum time for skill execution.
        """
        self.timeout_seconds = timeout_seconds
        self._active_executions: dict[str, asyncio.Task] = {}

    async def execute(
        self,
        skill: SkillExecutor,
        input_data: dict[str, Any]
    ) -> ExecutionResult:
        """Execute a skill with the given input.

        Args:
            skill: The skill executor instance.
            input_data: Input data for the skill.

        Returns:
            ExecutionResult with status, data, and timing.
        """
        import time
        start_time = time.time()
        execution_id = f"{skill.name}-{start_time}"

        try:
            if not await skill.validate_input(input_data):
                return {
                    "status": "error",
                    "data": None,
                    "error": "Invalid input data",
                    "execution_time_ms": None
                }

            task = asyncio.create_task(
                skill.execute(input_data)  # type: ignore[arg-type]
            )
            self._active_executions[execution_id] = task

            try:
                result = await asyncio.wait_for(
                    task,
                    timeout=self.timeout_seconds
                )
                execution_time_ms = (time.time() - start_time) * 1000

                return {
                    "status": str(result.get("status", "success")),
                    "data": dict(result),
                    "error": str(result.get("error")) if result.get("error") else None,
                    "execution_time_ms": execution_time_ms
                }
            except asyncio.TimeoutError:
                task.cancel()
                logger.error(f"Skill {skill.name} timed out after {self.timeout_seconds}s")
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Execution timed out after {self.timeout_seconds}s",
                    "execution_time_ms": self.timeout_seconds * 1000
                }
            finally:
                self._active_executions.pop(execution_id, None)

        except SkillExecutionError as e:
            execution_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Skill execution error in {skill.name}: {e}")
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "execution_time_ms": execution_time_ms
            }
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            logger.exception(f"Unexpected error executing {skill.name}")
            return {
                "status": "error",
                "data": None,
                "error": f"Unexpected error: {str(e)}",
                "execution_time_ms": execution_time_ms
            }
        finally:
            try:
                await skill.cleanup()
            except Exception as e:
                logger.warning(f"Cleanup error for {skill.name}: {e}")

    async def execute_batch(
        self,
        skills: list[tuple[SkillExecutor, dict[str, Any]]]
    ) -> list[ExecutionResult]:
        """Execute multiple skills in parallel.

        Args:
            skills: List of (skill, input_data) tuples.

        Returns:
            List of ExecutionResults in same order as input.
        """
        tasks = [
            self.execute(skill, input_data)
            for skill, input_data in skills
        ]
        return await asyncio.gather(*tasks)

    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel an active execution.

        Args:
            execution_id: ID of the execution to cancel.

        Returns:
            True if cancelled, False if not found.
        """
        task = self._active_executions.get(execution_id)
        if task and not task.done():
            task.cancel()
            return True
        return False

    def get_active_count(self) -> int:
        """Get number of currently active executions."""
        return len(self._active_executions)


class SkillExecutionContext:
    """Context manager for skill execution with setup/teardown."""

    def __init__(self, engine: SkillExecutorEngine):
        self.engine = engine
        self.results: list[ExecutionResult] = []

    async def __aenter__(self) -> "SkillExecutionContext":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def run(self, skill: SkillExecutor, input_data: dict[str, Any]) -> ExecutionResult:
        """Run a skill and store the result."""
        result = await self.engine.execute(skill, input_data)
        self.results.append(result)
        return result


def create_executor(timeout_seconds: float = 300.0) -> SkillExecutorEngine:
    """Factory function to create an executor engine."""
    return SkillExecutorEngine(timeout_seconds=timeout_seconds)
