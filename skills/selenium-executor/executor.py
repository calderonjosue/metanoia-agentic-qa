"""Selenium executor with page object model support.

This skill provides UI automation capabilities using Selenium WebDriver
with built-in support for the page object model (POM) pattern.
"""

import logging
from typing import Any, TypedDict

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from metanoia.skills.base import SkillExecutor

logger = logging.getLogger(__name__)


class SeleniumInput(TypedDict):
    """Input schema for Selenium executor."""
    action: str
    target: str | None
    url: str | None
    value: str | None
    timeout: int | None
    locator_strategy: str | None
    browser: str | None


class SeleniumOutput(TypedDict):
    """Output schema for Selenium executor."""
    status: str
    screenshot: str | None
    healed_selector: str | None
    error: str | None
    result: Any | None


class LocatorStrategy:
    """Maps string locator strategy to Selenium By constants."""

    STRATEGY_MAP = {
        "ID": By.ID,
        "NAME": By.NAME,
        "CSS_SELECTOR": By.CSS_SELECTOR,
        "XPATH": By.XPATH,
        "LINK_TEXT": By.LINK_TEXT,
        "PARTIAL_LINK_TEXT": By.PARTIAL_LINK_TEXT,
        "TAG_NAME": By.TAG_NAME,
        "CLASS_NAME": By.CLASS_NAME,
    }

    @classmethod
    def get_by(cls, strategy: str) -> By:
        """Convert string strategy to Selenium By constant."""
        return cls.STRATEGY_MAP.get(strategy.upper(), By.CSS_SELECTOR)


class ElementLocator:
    """Handles element location with fallback strategies."""

    def __init__(self, driver: WebDriver, timeout: int = 10):
        self.driver = driver
        self.timeout = timeout

    def find_element(
        self,
        target: str,
        strategy: str = "CSS_SELECTOR"
    ) -> WebElement | None:
        """Find element with given strategy and timeout."""
        try:
            by = LocatorStrategy.get_by(strategy)
            wait = WebDriverWait(self.driver, self.timeout)
            element = wait.until(EC.presence_of_element_located((by, target)))
            return element
        except (TimeoutException, NoSuchElementException):
            logger.warning(f"Element not found: {target} ({strategy})")
            return None

    def find_clickable(
        self,
        target: str,
        strategy: str = "CSS_SELECTOR"
    ) -> WebElement | None:
        """Find element that is clickable."""
        try:
            by = LocatorStrategy.get_by(strategy)
            wait = WebDriverWait(self.driver, self.timeout)
            element = wait.until(EC.element_to_be_clickable((by, target)))
            return element
        except (TimeoutException, NoSuchElementException):
            logger.warning(f"Clickable element not found: {target}")
            return None


class SeleniumExecutor(SkillExecutor):
    """UI automation executor using Selenium WebDriver."""

    name = "selenium-executor"
    version = "1.0.0"

    def __init__(self, browser: str = "chrome", headless: bool = True):
        super().__init__()
        self._browser = browser.lower()
        self._headless = headless
        self._driver: WebDriver | None = None
        self._locator: ElementLocator | None = None

    async def execute(self, input_data: SeleniumInput) -> SeleniumOutput:
        """Execute a Selenium action.

        Args:
            input_data: Action to perform (action, target, url, etc.)

        Returns:
            SeleniumOutput with status and result.
        """
        action = input_data.get("action", "goto")
        target = input_data.get("target", "")
        url = input_data.get("url", "about:blank")
        value = input_data.get("value", "")
        input_data.get("timeout", 30)
        strategy = input_data.get("locator_strategy", "CSS_SELECTOR")
        browser = input_data.get("browser", self._browser)

        try:
            await self._ensure_driver(browser)

            if action == "goto":
                self._driver.get(url)
                return self._success_output(result={"url": url})

            elif action == "click":
                element = self._locator.find_clickable(target, strategy)
                if element:
                    element.click()
                    return self._success_output(result={"clicked": target})
                return self._error_output(f"Element not clickable: {target}")

            elif action == "send_keys":
                element = self._locator.find_element(target, strategy)
                if element:
                    element.send_keys(value)
                    return self._success_output(result={"sent_keys": value, "target": target})
                return self._error_output(f"Element not found: {target}")

            elif action == "clear":
                element = self._locator.find_element(target, strategy)
                if element:
                    element.clear()
                    return self._success_output(result={"cleared": target})
                return self._error_output(f"Element not found: {target}")

            elif action == "submit":
                element = self._locator.find_element(target, strategy)
                if element:
                    element.submit()
                    return self._success_output(result={"submitted": target})
                return self._error_output(f"Element not found: {target}")

            elif action == "get_text":
                element = self._locator.find_element(target, strategy)
                if element:
                    text = element.text
                    return self._success_output(result={"text": text, "target": target})
                return self._error_output(f"Element not found: {target}")

            elif action == "get_attribute":
                attr_name = value or "value"
                element = self._locator.find_element(target, strategy)
                if element:
                    attr_value = element.get_attribute(attr_name)
                    return self._success_output(result={"attribute": attr_name, "value": attr_value})
                return self._error_output(f"Element not found: {target}")

            elif action == "is_displayed":
                element = self._locator.find_element(target, strategy)
                if element:
                    visible = element.is_displayed()
                    return self._success_output(result={"displayed": visible, "target": target})
                return self._error_output(f"Element not found: {target}")

            elif action == "screenshot":
                if url and url != "about:blank":
                    self._driver.get(url)
                screenshot_bytes = self._driver.get_screenshot_as_base64()
                return self._success_output(
                    screenshot=screenshot_bytes,
                    result={"screenshot_captured": True}
                )

            else:
                return self._error_output(f"Unknown action: {action}")

        except Exception as e:
            logger.exception("Selenium execution failed")
            return self._error_output(str(e))
        finally:
            await self.cleanup()

    async def _ensure_driver(self, browser: str) -> None:
        """Ensure WebDriver is initialized."""
        if self._driver is None:
            options = getattr(webdriver, browser.title())().options
            if self._headless:
                options.add_argument("--headless")
            self._driver = getattr(webdriver, browser)()
            self._locator = ElementLocator(self._driver)

    async def cleanup(self) -> None:
        """Cleanup driver resources."""
        if self._driver:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None
            self._locator = None

    def _success_output(
        self,
        screenshot: str | None = None,
        result: Any | None = None
    ) -> SeleniumOutput:
        """Create success output."""
        return {
            "status": "success",
            "screenshot": screenshot,
            "healed_selector": None,
            "error": None,
            "result": result
        }

    def _error_output(self, error: str) -> SeleniumOutput:
        """Create error output."""
        return {
            "status": "error",
            "screenshot": None,
            "healed_selector": None,
            "error": error,
            "result": None
        }

    def get_metadata(self) -> dict[str, str]:
        """Return skill metadata."""
        return {
            "name": self.name,
            "version": self.version,
            "browser": self._browser,
            "headless": str(self._headless)
        }
