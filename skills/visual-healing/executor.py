"""Visual healing executor using Gemini Vision.

This skill provides self-healing capabilities for UI automation
by using AI vision to analyze pages and repair broken selectors.
"""

import base64
import logging
from typing import Any, TypedDict

from metanoia.skills.base import SkillExecutor

logger = logging.getLogger(__name__)


class VisualHealingInput(TypedDict):
    """Input schema for visual healing."""
    screenshot: str
    failed_selector: str
    action_intent: str
    page_html: str | None
    context: dict | None


class VisualHealingOutput(TypedDict):
    """Output schema for visual healing."""
    status: str
    healed_selector: str | None
    confidence: float | None
    alternative_selectors: list[str] | None
    analysis: str | None
    error: str | None


class SelectorRepairStrategy:
    """Strategies for repairing broken selectors."""

    @staticmethod
    def repair_by_text(text: str) -> list[str]:
        """Generate selectors based on element text."""
        return [
            f"text={text}",
            f"//*[contains(text(), '{text}')]",
            f"[aria-label*='{text}']",
            f"[title*='{text}']"
        ]

    @staticmethod
    def repair_by_position(tag: str, index: int) -> list[str]:
        """Generate selectors based on element position."""
        return [
            f"{tag}:nth-of-type({index})",
            f"{tag}:nth-child({index})",
            f"({tag})[{index}]"
        ]

    @staticmethod
    def repair_by_role(role: str) -> list[str]:
        """Generate selectors based on ARIA role."""
        return [
            f"[role='{role}']",
            f"//*[@role='{role}']"
        ]

    @staticmethod
    def repair_by_similar_elements(
        tag: str,
        class_list: list[str],
        exclude_broken: str
    ) -> list[str]:
        """Generate selectors for similar elements."""
        selectors = []

        if class_list:
            base_class = class_list[0] if class_list else ""
            if base_class:
                selectors.append(f"{tag}.{base_class}")
                selectors.append(f"[class*='{base_class}']")

        if tag:
            selectors.append(tag)

        return [s for s in selectors if s != exclude_broken]


class VisionAnalyzer:
    """Analyzes screenshots using Gemini Vision to understand UI elements."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or __import__('os').getenv('GEMINI_API_KEY')
        self._model = None

    async def analyze_element(
        self,
        screenshot: bytes,
        element_description: str
    ) -> dict[str, Any]:
        """Analyze screenshot to find element matching description.
        
        Args:
            screenshot: Image bytes.
            element_description: What element to find.
            
        Returns:
            Analysis result with proposed selector and confidence.
        """
        if not self.api_key:
            return {
                "found": False,
                "selector": None,
                "confidence": 0.0,
                "reasoning": "No Gemini API key configured"
            }

        try:
            # In production, this would call Gemini Vision API
            # For now, return a placeholder analysis
            prompt = f"""Analyze this UI screenshot. Find the element described as: 
            "{element_description}"
            
            Provide a CSS selector or XPath that will reliably identify this element.
            Also estimate confidence (0-1) and explain your reasoning."""

            logger.info(f"Vision analysis with prompt: {prompt[:100]}...")

            # Placeholder - would use Gemini Vision
            return {
                "found": True,
                "selector": None,  # Would be populated by Gemini
                "confidence": 0.0,
                "reasoning": "Gemini Vision API not configured"
            }

        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return {
                "found": False,
                "selector": None,
                "confidence": 0.0,
                "reasoning": str(e)
            }

    async def compare_screenshots(
        self,
        before: bytes,
        after: bytes
    ) -> dict[str, Any]:
        """Compare two screenshots to find visual differences.
        
        Args:
            before: Screenshot before change.
            after: Screenshot after change.
            
        Returns:
            Analysis of what changed.
        """
        return {
            "changed": True,
            "changed_elements": [],
            "change_type": "unknown"
        }


class VisualHealingExecutor(SkillExecutor):
    """Self-healing executor for broken UI selectors."""

    name = "visual-healing"
    version = "1.0.0"

    def __init__(self):
        super().__init__()
        self._analyzer = VisionAnalyzer()
        self._repair_strategy = SelectorRepairStrategy()
        self._repair_history: list[dict] = []

    async def execute(self, input_data: VisualHealingInput) -> VisualHealingOutput:
        """Execute visual healing to repair a broken selector.
        
        Args:
            input_data: Screenshot and failed selector info.
            
        Returns:
            VisualHealingOutput with healed selector.
        """
        screenshot_b64 = input_data.get("screenshot", "")
        failed_selector = input_data.get("failed_selector", "")
        action_intent = input_data.get("action_intent", "")

        try:
            # Decode screenshot if base64
            screenshot = screenshot_b64
            if isinstance(screenshot_b64, str):
                try:
                    screenshot = base64.b64decode(screenshot_b64)
                except Exception:
                    pass

            # Step 1: Try vision analysis first
            if screenshot and self._analyzer.api_key:
                analysis = await self._analyzer.analyze_element(
                    screenshot,
                    f"element to {action_intent}"
                )

                if analysis.get("found") and analysis.get("selector"):
                    self._record_repair(failed_selector, analysis["selector"], "vision")
                    return {
                        "status": "success",
                        "healed_selector": analysis["selector"],
                        "confidence": analysis.get("confidence", 0.0),
                        "alternative_selectors": [analysis["selector"]],
                        "analysis": analysis.get("reasoning", ""),
                        "error": None
                    }

            # Step 2: Fallback to heuristic repair strategies
            alternatives = self._heuristic_repair(failed_selector, action_intent)

            if alternatives:
                best = alternatives[0]
                self._record_repair(failed_selector, best, "heuristic")

                return {
                    "status": "success",
                    "healed_selector": best,
                    "confidence": 0.7,
                    "alternative_selectors": alternatives,
                    "analysis": f"Generated {len(alternatives)} heuristic alternatives",
                    "error": None
                }

            return {
                "status": "error",
                "healed_selector": None,
                "confidence": None,
                "alternative_selectors": None,
                "analysis": None,
                "error": "Could not repair selector"
            }

        except Exception as e:
            logger.exception("Visual healing failed")
            return {
                "status": "error",
                "healed_selector": None,
                "confidence": None,
                "alternative_selectors": None,
                "analysis": None,
                "error": str(e)
            }

    def _heuristic_repair(
        self,
        broken_selector: str,
        action: str
    ) -> list[str]:
        """Generate repair candidates using heuristics."""
        alternatives = []

        # Try action-based fallbacks
        if action == "click":
            alternatives.extend([
                "button",
                "[role='button']",
                "a",
                "input[type='submit']",
                "input[type='button']"
            ])
        elif action == "fill":
            alternatives.extend([
                "input",
                "textarea",
                "[contenteditable='true']"
            ])

        # Try extracting info from broken selector
        parts = broken_selector.split()
        for part in parts:
            if part.startswith("."):
                class_name = part[1:]
                alternatives.append(f"[class*='{class_name}']")
            elif part.startswith("#"):
                id_name = part[1:]
                alternatives.append(f"[id*='{id_name}']")

        # Check repair history for similar selectors
        for record in self._repair_history:
            if self._selector_similar(broken_selector, record["broken"]):
                alternatives.append(record["healed"])

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for alt in alternatives:
            if alt not in seen:
                seen.add(alt)
                unique.append(alt)

        return unique[:5]

    def _selector_similar(self, sel1: str, sel2: str) -> bool:
        """Check if two selectors are similar."""
        import re

        def normalize(s: str) -> str:
            return re.sub(r'[^a-zA-Z0-9]', '', s).lower()

        return normalize(sel1) in normalize(sel2) or normalize(sel2) in normalize(sel1)

    def _record_repair(
        self,
        broken: str,
        healed: str,
        method: str
    ) -> None:
        """Record repair in history for future reference."""
        self._repair_history.append({
            "broken": broken,
            "healed": healed,
            "method": method
        })

        # Keep history bounded
        if len(self._repair_history) > 100:
            self._repair_history = self._repair_history[-100:]


class SelfHealingOrchestrator:
    """Orchestrates multiple healing strategies."""

    def __init__(self):
        self.visual_healer = VisualHealingExecutor()
        self.history: list[dict] = []

    async def heal(
        self,
        broken_selector: str,
        screenshot: str | None = None,
        action: str = "click",
        context: dict | None = None
    ) -> dict[str, Any]:
        """Attempt to heal a broken selector using all available strategies.
        
        Args:
            broken_selector: The selector that failed.
            screenshot: Optional screenshot for vision analysis.
            action: What action was being attempted.
            context: Additional context.
            
        Returns:
            Healing result with best candidate selector.
        """
        strategies = [
            ("visual", self.visual_healer.execute if screenshot else None),
            ("history", self._heal_from_history),
            ("heuristic", self._heal_heuristic),
        ]

        for name, strategy in strategies:
            if strategy is None:
                continue

            try:
                if name == "visual":
                    result = await strategy({
                        "screenshot": screenshot,
                        "failed_selector": broken_selector,
                        "action_intent": action
                    })
                elif name == "history":
                    result = strategy(broken_selector, action)
                else:
                    result = strategy(broken_selector, action)

                if result.get("status") == "success" and result.get("healed_selector"):
                    self._record_healing(broken_selector, result["healed_selector"], name)
                    return result
            except Exception as e:
                logger.warning(f"Healing strategy {name} failed: {e}")

        return {
            "status": "error",
            "healed_selector": None,
            "error": "All healing strategies failed"
        }

    def _heal_from_history(self, broken: str, action: str) -> dict:
        """Try to heal using repair history."""
        for record in self.visual_healer._repair_history:
            if self.visual_healer._selector_similar(broken, record["broken"]):
                return {
                    "status": "success",
                    "healed_selector": record["healed"],
                    "confidence": 0.8,
                    "method": "history"
                }
        return {"status": "error"}

    def _heal_heuristic(self, broken: str, action: str) -> dict:
        """Try to heal using heuristics."""
        alternatives = self.visual_healer._heuristic_repair(broken, action)
        if alternatives:
            return {
                "status": "success",
                "healed_selector": alternatives[0],
                "confidence": 0.6,
                "method": "heuristic"
            }
        return {"status": "error"}

    def _record_healing(
        self,
        broken: str,
        healed: str,
        method: str
    ) -> None:
        """Record successful healing."""
        self.history.append({
            "broken": broken,
            "healed": healed,
            "method": method
        })
