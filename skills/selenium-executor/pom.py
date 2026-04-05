"""Page Object Model (POM) support for Selenium executor.

This module provides utilities for creating maintainable page object models
following the POM pattern.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Callable, Optional, Any


class page_element:
    """Descriptor for defining page elements with locators.

    Usage:
        class LoginPage(BasePage):
            username = page_element(By.ID, "username")
            password = page_element(By.ID, "password")
            submit = page_element(By.CSS_SELECTOR, "button[type='submit']")
    """

    def __init__(self, by: By, locator: str, timeout: int = 10):
        self.by = by
        self.locator = locator
        self.timeout = timeout

    def __get__(self, obj: "BasePage", owner: type) -> "PageElement":
        return PageElement(obj.driver, self.by, self.locator, self.timeout)


class PageElement:
    """Represents a located page element with interaction methods."""

    def __init__(self, driver: WebDriver, by: By, locator: str, timeout: int = 10):
        self.driver = driver
        self.by = by
        self.locator = locator
        self.timeout = timeout

    def find(self) -> Any:
        """Find the element with explicit wait."""
        wait = WebDriverWait(self.driver, self.timeout)
        return wait.until(EC.presence_of_element_located((self.by, self.locator)))

    def find_clickable(self) -> Any:
        """Find element that is clickable."""
        wait = WebDriverWait(self.driver, self.timeout)
        return wait.until(EC.element_to_be_clickable((self.by, self.locator)))

    def send_keys(self, *args) -> None:
        """Send keys to element."""
        element = self.find()
        element.send_keys(*args)

    def click(self) -> None:
        """Click element."""
        element = self.find_clickable()
        element.click()

    def clear(self) -> None:
        """Clear element value."""
        element = self.find()
        element.clear()

    def submit(self) -> None:
        """Submit form."""
        element = self.find()
        element.submit()

    @property
    def text(self) -> str:
        """Get element text."""
        element = self.find()
        return element.text

    def get_attribute(self, name: str) -> Optional[str]:
        """Get element attribute."""
        element = self.find()
        return element.get_attribute(name)

    def is_displayed(self) -> bool:
        """Check if element is displayed."""
        try:
            element = self.find()
            return element.is_displayed()
        except Exception:
            return False


class BasePage:
    """Base class for page objects.

    Usage:
        class LoginPage(BasePage):
            username = page_element(By.ID, "username")
            password = page_element(By.ID, "password")
            submit = page_element(By.CSS_SELECTOR, "button[type='submit']")

            def login(self, username, password):
                self.username.send_keys(username)
                self.password.send_keys(password)
                self.submit.click()
    """

    def __init__(self, driver: WebDriver, timeout: int = 10):
        self.driver = driver
        self.timeout = timeout
        self._wait = WebDriverWait(driver, timeout)

    def open(self, url: str) -> None:
        """Navigate to URL."""
        self.driver.get(url)

    def wait_for_element(self, by: By, locator: str) -> Any:
        """Wait for element to be present."""
        return self._wait.until(EC.presence_of_element_located((by, locator)))

    def wait_for_clickable(self, by: By, locator: str) -> Any:
        """Wait for element to be clickable."""
        return self._wait.until(EC.element_to_be_clickable((by, locator)))

    def wait_for_url(self, url_pattern: str) -> bool:
        """Wait for URL to match pattern."""
        return self._wait.until(EC.url_to_be(url_pattern))

    def wait_for_title(self, title: str) -> bool:
        """Wait for page title."""
        return self._wait.until(EC.title_is(title))

    @property
    def title(self) -> str:
        """Get page title."""
        return self.driver.title

    @property
    def current_url(self) -> str:
        """Get current URL."""
        return self.driver.current_url

    def screenshot(self) -> str:
        """Capture screenshot as base64."""
        return self.driver.get_screenshot_as_base64()

    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript."""
        return self.driver.execute_script(script, *args)
