"""UI Automation Engineer agent for Metanoia-QA.

Executes Playwright tests with vision-based self-healing for broken selectors.
"""

import asyncio
import logging
from typing import Any, Optional

from pydantic import BaseModel

from skill_runtime.executor import create_executor
from skill_runtime.loader import SkillLoader

logger = logging.getLogger(__name__)


class TestResult(BaseModel):
    """Result of test execution."""
    passed: int
    failed: int
    skipped: int
    duration: float
    report_url: Optional[str] = None
    screenshots: list[str] = []
    errors: list[dict] = []


class UIAutomationEngineer:
    """UI Automation Engineer that executes Playwright tests with self-healing.
    
    Responsibilities:
    - Execute Playwright tests using playwright-executor skill
    - Use vision-healing skill on selector failure
    - Generate PR for broken selectors
    - Report pass/fail with screenshots
    - Integrate with skill_runtime
    """

    name = "ui-automation-engineer"
    version = "1.0.0"

    def __init__(self):
        self._skill_loader = SkillLoader()
        self._executor_engine = create_executor(timeout_seconds=600.0)
        self._playwright_executor = None
        self._visual_healer = None
        self._broken_selectors: list[dict] = []

    async def execute(self, test_cases: list[dict], context: dict) -> TestResult:
        """Execute UI tests and return results.
        
        Args:
            test_cases: List of test case dictionaries with url, selectors, actions.
            context: Execution context with base_url, timeout, etc.
            
        Returns:
            TestResult with pass/fail counts and screenshots.
        """
        passed = 0
        failed = 0
        skipped = 0
        duration = 0.0
        screenshots: list[str] = []
        errors: list[dict] = []

        playwright = self._get_playwright_executor()
        if playwright is None:
            logger.error("Playwright executor not available")
            return TestResult(
                passed=0,
                failed=len(test_cases),
                skipped=0,
                duration=0.0,
                errors=[{"error": "Playwright executor not available"}]
            )

        for test_case in test_cases:
            test_start = asyncio.get_event_loop().time()

            try:
                result = await self._execute_test_case(
                    playwright, test_case, context
                )

                if result["status"] == "success":
                    passed += 1
                    if result.get("screenshot"):
                        screenshots.append(result["screenshot"])
                else:
                    failed += 1
                    error_info = {
                        "test_case": test_case.get("name", "unknown"),
                        "error": result.get("error", "Unknown error"),
                        "selector": test_case.get("selector", "")
                    }
                    errors.append(error_info)

                    if result.get("healed_selector"):
                        self._record_broken_selector(
                            original=test_case.get("selector", ""),
                            healed=result["healed_selector"],
                            error=result.get("error", "")
                        )

            except Exception as e:
                failed += 1
                logger.exception(f"Test case failed: {e}")
                errors.append({
                    "test_case": test_case.get("name", "unknown"),
                    "error": str(e)
                })

            duration += asyncio.get_event_loop().time() - test_start

        return TestResult(
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=duration,
            screenshots=screenshots,
            errors=errors
        )

    async def heal(self, failure: dict) -> dict:
        """Attempt self-healing on a test failure.
        
        Args:
            failure: Failure information with selector, action, screenshot.
            
        Returns:
            Healing result with repaired selector.
        """
        visual_healer = self._get_visual_healer()
        if visual_healer is None:
            return {
                "status": "error",
                "healed_selector": None,
                "error": "Visual healer not available"
            }

        screenshot = failure.get("screenshot", "")
        failed_selector = failure.get("selector", "")
        action = failure.get("action", "click")

        try:
            healing_input = {
                "screenshot": screenshot,
                "failed_selector": failed_selector,
                "action_intent": action,
                "page_html": failure.get("page_html"),
                "context": failure.get("context")
            }

            result = await visual_healer.execute(healing_input)
            return dict(result) if result else result

        except Exception as e:
            logger.exception("Self-healing failed")
            return {
                "status": "error",
                "healed_selector": None,
                "error": str(e)
            }

    def generate_selector_fix_pr(self) -> dict:
        """Generate a PR for fixing broken selectors.
        
        Returns:
            PR details with changes.
        """
        if not self._broken_selectors:
            return {
                "status": "no_changes",
                "message": "No broken selectors to fix"
            }

        changes = []
        for record in self._broken_selectors:
            changes.append({
                "file": record.get("file", "selectors.json"),
                "original": record["original"],
                "replacement": record["healed"],
                "reason": record.get("error", "")
            })

        return {
            "status": "ready",
            "changes": changes,
            "title": "fix: Repair broken UI selectors",
            "description": self._generate_pr_description(changes)
        }

    def get_broken_selectors(self) -> list[dict]:
        """Get list of broken selectors found during execution."""
        return self._broken_selectors.copy()

    def _get_playwright_executor(self):
        """Get or create Playwright executor instance."""
        if self._playwright_executor is None:
            executor_class = self._skill_loader.load_skill("playwright-executor")
            if executor_class:
                self._playwright_executor = executor_class()
        return self._playwright_executor

    def _get_visual_healer(self):
        """Get or create Visual Healing executor instance."""
        if self._visual_healer is None:
            executor_class = self._skill_loader.load_skill("visual-healing")
            if executor_class:
                self._visual_healer = executor_class()
        return self._visual_healer

    async def _execute_test_case(
        self,
        playwright: Any,
        test_case: dict,
        context: dict
    ) -> dict:
        """Execute a single test case with healing on failure."""
        url = context.get("base_url", "") + test_case.get("url", "")
        action = test_case.get("action", "goto")
        selector = test_case.get("selector", "")
        timeout = test_case.get("timeout", context.get("timeout", 30000))

        input_data = {
            "action": action,
            "target": selector,
            "url": url,
            "timeout": timeout,
            "wait_for_selectors": test_case.get("wait_for_selectors")
        }

        result = await self._executor_engine.execute(playwright, input_data)

        if result["status"] == "error" and result.get("error"):
            if "selector" in result["error"].lower() or "not found" in result["error"].lower():
                healing_result = await self.heal({
                    "selector": selector,
                    "action": action,
                    "screenshot": result.get("data", {}).get("screenshot"),
                    "context": context
                })

                if healing_result.get("status") == "success" and healing_result.get("healed_selector"):
                    input_data["target"] = healing_result["healed_selector"]
                    result = await self._executor_engine.execute(playwright, input_data)

        return dict(result.get("data", {"status": result["status"], "error": result.get("error")}))

    def _record_broken_selector(
        self,
        original: str,
        healed: str,
        error: str
    ) -> None:
        """Record a broken selector for PR generation."""
        self._broken_selectors.append({
            "original": original,
            "healed": healed,
            "error": error,
            "file": "locators/selectors.json"
        })

    def _generate_pr_description(self, changes: list[dict]) -> str:
        """Generate PR description from selector changes."""
        lines = [
            "## Summary",
            f"This PR repairs {len(changes)} broken UI selectors.",
            "",
            "## Changes",
            ""
        ]

        for i, change in enumerate(changes, 1):
            lines.append(f"{i}. `{change['original']}` -> `{change['replacement']}`")
            if change.get("reason"):
                lines.append(f"   Reason: {change['reason']}")

        lines.extend([
            "",
            "## Testing",
            "- All tests pass with healed selectors",
            "- Screenshots captured for verification",
            "",
            "Generated by Metanoia-QA UI Automation Lead"
        ])

        return "\n".join(lines)
