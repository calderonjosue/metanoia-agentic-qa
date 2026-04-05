"""Skill executor engine for Skill Hub."""

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Any, TypedDict

from metanoia.skills.base import SkillExecutionError

if TYPE_CHECKING:
    from metanoia.src.skill_hub.base import SkillHubExecutor

logger = logging.getLogger(__name__)


class ExecutionResult(TypedDict):
    status: str
    data: dict[str, Any] | None
    error: str | None
    execution_time_ms: float | None


class HubExecutorEngine:
    """Engine for executing Skill Hub community skills."""

    def __init__(self, timeout_seconds: float = 300.0):
        self.timeout_seconds = timeout_seconds
        self._active_executions: dict[str, asyncio.Task] = {}

    async def execute(
        self,
        skill: "SkillHubExecutor",
        input_data: dict[str, Any]
    ) -> ExecutionResult:
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

            task = asyncio.create_task(skill.execute(input_data))
            self._active_executions[execution_id] = task

            try:
                result = await asyncio.wait_for(task, timeout=self.timeout_seconds)
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
        skills: list[tuple["SkillHubExecutor", dict[str, Any]]]
    ) -> list[ExecutionResult]:
        tasks = [self.execute(skill, input_data) for skill, input_data in skills]
        return await asyncio.gather(*tasks)

    def cancel_execution(self, execution_id: str) -> bool:
        task = self._active_executions.get(execution_id)
        if task and not task.done():
            task.cancel()
            return True
        return False

    def get_active_count(self) -> int:
        return len(self._active_executions)
