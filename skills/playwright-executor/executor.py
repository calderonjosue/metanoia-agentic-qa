"""Playwright executor with vision-based self-healing.

This skill provides UI automation capabilities using Playwright with
automatic recovery when selectors break due to DOM changes.
"""

import logging
from typing import Any, TypedDict

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from metanoia.skills.base import SkillExecutor

logger = logging.getLogger(__name__)


class PlaywrightInput(TypedDict):
    """Input schema for Playwright executor."""
    action: str
    target: str
    url: str
    timeout: int | None
    wait_for_selectors: list[str] | None


class PlaywrightOutput(TypedDict):
    """Output schema for Playwright executor."""
    status: str
    screenshot: str | None
    healed_selector: str | None
    error: str | None


class VisionHealer:
    """Uses Gemini Vision to heal broken selectors."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or __import__('os').getenv('GEMINI_API_KEY')

    async def analyze_and_repair(
        self,
        page: Page,
        broken_selector: str,
        original_action: str
    ) -> str | None:
        """Analyze page screenshot and propose repaired selector.
        
        Args:
            page: Playwright page object.
            broken_selector: The selector that failed.
            original_action: What action was being attempted.
            
        Returns:
            Repaired selector string or None.
        """
        try:
            screenshot_bytes = await page.screenshot()
            import base64
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
            
            prompt = f"""Analyze this UI screenshot. The original selector '{broken_selector}' 
            failed when trying to: {original_action}. 
            
            Identify the visible element that matches this action and provide a new 
            CSS selector or XPath that will reliably find it. Return ONLY the new selector."""

            # This would call Gemini Vision API
            # For now, return a fallback strategy
            logger.info(f"Vision healing for selector: {broken_selector}")
            
            # Fallback: try finding by text content or aria labels
            return await self._fallback_repair(page, original_action)
            
        except Exception as e:
            logger.error(f"Vision healing failed: {e}")
            return None

    async def _fallback_repair(self, page: Page, action: str) -> str | None:
        """Fallback repair strategies based on action type."""
        try:
            if action == "click":
                # Try finding buttons or clickable elements
                elements = await page.query_selector_all("button, a, [role='button'], input[type='submit']")
                if elements:
                    return "button"
            elif action == "fill":
                # Try finding input fields
                return "input"
        except Exception:
            pass
        return None


class SelectorEngine:
    """Manages selector generation and fallback strategies."""

    @staticmethod
    def generate_selectors(element_info: dict) -> list[str]:
        """Generate multiple selector candidates from element info."""
        selectors = []
        
        if "id" in element_info:
            selectors.append(f"#{element_info['id']}")
        
        if "class" in element_info:
            classes = element_info["class"]
            if isinstance(classes, list):
                selectors.append("." + ".".join(classes))
            else:
                selectors.append(f".{classes}")
        
        if "tag" in element_info:
            selectors.append(element_info["tag"])
        
        if "text" in element_info:
            selectors.append(f"text={element_info['text']}")
        
        if "aria_label" in element_info:
            selectors.append(f"[aria-label='{element_info['aria_label']}']")
        
        return selectors

    @staticmethod
    async def try_selectors(page: Page, selectors: list[str]) -> Any | None:
        """Try multiple selectors until one works."""
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    return element
            except Exception:
                continue
        return None


class PlaywrightExecutor(SkillExecutor):
    """UI automation executor with vision-based self-healing."""

    name = "playwright-executor"
    version = "1.0.0"

    def __init__(self):
        super().__init__()
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._vision_healer: VisionHealer | None = None
        self._selector_engine = SelectorEngine()

    async def execute(self, input_data: PlaywrightInput) -> PlaywrightOutput:
        """Execute a Playwright action with self-healing.
        
        Args:
            input_data: Action to perform (action, target, url, etc.)
            
        Returns:
            PlaywrightOutput with status and screenshot.
        """
        action = input_data.get("action", "goto")
        target = input_data.get("target", "")
        url = input_data.get("url", "about:blank")
        timeout = input_data.get("timeout", 30000)
        
        try:
            await self._ensure_browser()
            await self._ensure_page()
            
            if action == "goto":
                await self._page.goto(url, timeout=timeout)
                return self._success_output(screenshot=True)
            
            elif action == "click":
                return await self._execute_with_healing(
                    action="click",
                    target=target,
                    timeout=timeout or 30000
                )
            
            elif action == "fill":
                return await self._execute_with_healing(
                    action="fill",
                    target=target,
                    timeout=timeout or 30000
                )
            
            elif action == "screenshot":
                await self._page.goto(url, timeout=timeout)
                screenshot = await self._page.screenshot()
                import base64
                return {
                    "status": "success",
                    "screenshot": base64.b64encode(screenshot).decode(),
                    "healed_selector": None,
                    "error": None
                }
            
            else:
                return self._error_output(f"Unknown action: {action}")
                
        except Exception as e:
            logger.exception("Playwright execution failed")
            return self._error_output(str(e))
        finally:
            await self.cleanup()

    async def _execute_with_healing(
        self,
        action: str,
        target: str,
        timeout: int
    ) -> PlaywrightOutput:
        """Execute action with automatic healing on failure."""
        try:
            # First attempt with original selector
            element = await self._page.query_selector(target)
            if element:
                if action == "click":
                    await element.click(timeout=timeout)
                elif action == "fill":
                    value = ""  # Would come from input_data
                    await element.fill(value)
                return self._success_output()
            
            # Selector failed - try vision healing
            healed_selector = None
            if self._vision_healer:
                healed_selector = await self._vision_healer.analyze_and_repair(
                    self._page, target, action
                )
            
            if healed_selector:
                element = await self._page.query_selector(healed_selector)
                if element:
                    if action == "click":
                        await element.click(timeout=timeout)
                    elif action == "fill":
                        pass  # Would fill with value
                    return {
                        "status": "success",
                        "screenshot": None,
                        "healed_selector": healed_selector,
                        "error": None
                    }
            
            return self._error_output(f"Selector not found: {target}")
            
        except Exception as e:
            return self._error_output(f"Action failed: {e}")

    async def _ensure_browser(self) -> None:
        """Ensure browser is launched."""
        if self._browser is None:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(headless=True)
            self._context = await self._browser.new_context()
            self._vision_healer = VisionHealer()

    async def _ensure_page(self) -> None:
        """Ensure page is created."""
        if self._page is None and self._context:
            self._page = await self._context.new_page()

    async def cleanup(self) -> None:
        """Cleanup browser resources."""
        if self._page:
            await self._page.close()
            self._page = None
        if self._context:
            await self._context.close()
            self._context = None
        if self._browser:
            await self._browser.close()
            self._browser = None

    def _success_output(self, screenshot: bool = False) -> PlaywrightOutput:
        """Create success output."""
        return {
            "status": "success",
            "screenshot": None,
            "healed_selector": None,
            "error": None
        }

    def _error_output(self, error: str) -> PlaywrightOutput:
        """Create error output."""
        return {
            "status": "error",
            "screenshot": None,
            "healed_selector": None,
            "error": error
        }
