"""
AppiumExecutor - Mobile testing automation for Android and iOS.
"""

from typing import Optional, List, Dict, Any
from appium import webdriver
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class AppiumExecutor:
    PLATFORM_ANDROID = "android"
    PLATFORM_IOS = "ios"

    def __init__(
        self,
        platform: str,
        app_path: Optional[str] = None,
        bundle_id: Optional[str] = None,
        port: int = 4723,
        device_name: Optional[str] = None,
        platform_version: Optional[str] = None,
        implicit_wait: float = 10,
        explicit_wait: float = 20,
    ):
        self.platform = platform.lower()
        self.app_path = app_path
        self.bundle_id = bundle_id
        self.port = port
        self.device_name = device_name or (f"{self.platform}_device")
        self.platform_version = platform_version
        self.implicit_wait = implicit_wait
        self.explicit_wait = explicit_wait
        self.driver: Optional[WebDriver] = None
        self._current_context = None

    def connect(self) -> None:
        """Establish connection to Appium server and initialize driver."""
        capabilities = self._build_capabilities()
        self.driver = webdriver.Remote(
            f"http://localhost:{self.port}/wd/hub",
            capabilities
        )
        self.driver.implicitly_wait(self.implicit_wait)

    def disconnect(self) -> None:
        """Close the Appium session and disconnect."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def _build_capabilities(self) -> Dict[str, Any]:
        """Build Appium capabilities based on platform."""
        if self.platform == self.PLATFORM_ANDROID:
            return self._android_capabilities()
        elif self.platform == self.PLATFORM_IOS:
            return self._ios_capabilities()
        else:
            raise ValueError(f"Unsupported platform: {self.platform}")

    def _android_capabilities(self) -> Dict[str, Any]:
        caps = {
            "platformName": "Android",
            "deviceName": self.device_name,
            "automationName": "UIAutomator2",
        }
        if self.app_path:
            caps["app"] = self.app_path
        if self.platform_version:
            caps["platformVersion"] = self.platform_version
        return caps

    def _ios_capabilities(self) -> Dict[str, Any]:
        caps = {
            "platformName": "iOS",
            "deviceName": self.device_name,
            "automationName": "XCUITest",
        }
        if self.app_path:
            caps["app"] = self.app_path
        if self.bundle_id:
            caps["bundleId"] = self.bundle_id
        if self.platform_version:
            caps["platformVersion"] = self.platform_version
        return caps

    def find_element(
        self, strategy: str, value: str, timeout: Optional[float] = None
    ):
        """Find a single element using the specified strategy."""
        by = self._get_by_strategy(strategy)
        wait_time = timeout if timeout is not None else self.explicit_wait
        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            raise NoSuchElementException(
                f"Element not found: {strategy}={value}"
            )

    def find_elements(self, strategy: str, value: str) -> List:
        """Find multiple elements using the specified strategy."""
        by = self._get_by_strategy(strategy)
        return self.driver.find_elements(by, value)

    def click_element(self, strategy: str, value: str) -> None:
        """Find and click an element."""
        element = self.find_element(strategy, value)
        element.click()

    def send_keys(self, strategy: str, value: str, text: str, clear_first: bool = True) -> None:
        """Find an element and send keys to it."""
        element = self.find_element(strategy, value)
        if clear_first:
            element.clear()
        element.send_keys(text)

    def tap(self, x: int, y: int) -> None:
        """Perform a tap at the specified coordinates."""
        action = webdriver.TouchAction(self.driver)
        action.tap(x=x, y=y).perform()

    def long_press(self, x: int, y: int, duration: int = 1000) -> None:
        """Perform a long press at the specified coordinates."""
        action = webdriver.TouchAction(self.driver)
        action.long_press(x=x, y=y, duration=duration).release().perform()

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 500) -> None:
        """Perform a swipe gesture from start to end coordinates."""
        action = webdriver.TouchAction(self.driver)
        action.press(x=start_x, y=start_y)
        action.wait(duration)
        action.move_to(x=end_x, y=end_y)
        action.release().perform()

    def pinch(self, x: int, y: int, scale: float = 2.0) -> None:
        """Perform a pinch gesture at coordinates with given scale."""
        action = webdriver.TouchAction(self.driver)
        action.zoom(element=None, x=x, y=y, scale=scale).perform()

    def scroll(self, strategy: str, value: str, direction: str = "down") -> None:
        """Scroll within an element. Direction: up, down, left, right."""
        element = self.find_element(strategy, value)
        if direction == "down":
            action = webdriver.TouchAction(self.driver)
            action.scroll(element, 0, -200).perform()
        elif direction == "up":
            action = webdriver.TouchAction(self.driver)
            action.scroll(element, 0, 200).perform()

    def get_contexts(self) -> List[str]:
        """Get all available contexts (native, webview)."""
        return self.driver.contexts

    def switch_to_webview(self, name: Optional[str] = None) -> None:
        """Switch to WebView context."""
        contexts = self.get_contexts()
        if name:
            self.driver.switch_to.context(name)
            self._current_context = name
        else:
            webview_context = next(
                (c for c in contexts if "WEBVIEW" in c or "webview" in c),
                None
            )
            if webview_context:
                self.driver.switch_to.context(webview_context)
                self._current_context = webview_context

    def switch_to_native(self) -> None:
        """Switch back to native app context."""
        self.driver.switch_to.context("NATIVE_APP")
        self._current_context = "NATIVE_APP"

    def get_page_source(self) -> str:
        """Get the current page XML source."""
        return self.driver.page_source

    def get_screenshot(self, filepath: str) -> None:
        """Save screenshot to the specified filepath."""
        self.driver.save_screenshot(filepath)

    def get_screenshot_base64(self) -> str:
        """Get screenshot as base64 encoded string."""
        return self.driver.get_screenshot_as_base64()

    def wait_for_element(
        self, strategy: str, value: str, timeout: Optional[float] = None, state: str = "visible"
    ) -> bool:
        """Wait for element to reach specified state."""
        by = self._get_by_strategy(strategy)
        wait_time = timeout if timeout is not None else self.explicit_wait
        try:
            if state == "visible":
                WebDriverWait(self.driver, wait_time).until(
                    EC.visibility_of_element_located((by, value))
                )
            elif state == "clickable":
                WebDriverWait(self.driver, wait_time).until(
                    EC.element_to_be_clickable((by, value))
                )
            elif state == "present":
                WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_element_located((by, value))
                )
            return True
        except TimeoutException:
            return False

    def set_implicit_wait(self, seconds: float) -> None:
        """Set implicit wait timeout."""
        self.implicit_wait = seconds
        if self.driver:
            self.driver.implicitly_wait(seconds)

    def is_element_present(self, strategy: str, value: str) -> bool:
        """Check if element is present."""
        return len(self.find_elements(strategy, value)) > 0

    def is_element_visible(self, strategy: str, value: str) -> bool:
        """Check if element is visible."""
        try:
            element = self.find_element(strategy, value)
            return element.is_displayed()
        except NoSuchElementException:
            return False

    def get_text(self, strategy: str, value: str) -> Optional[str]:
        """Get text content of an element."""
        element = self.find_element(strategy, value)
        return element.text

    def get_attribute(self, strategy: str, value: str, attribute: str) -> Optional[str]:
        """Get an attribute value from an element."""
        element = self.find_element(strategy, value)
        return element.get_attribute(attribute)

    def hide_keyboard(self) -> None:
        """Hide the soft keyboard if visible."""
        try:
            self.driver.hide_keyboard()
        except Exception:
            pass

    def _get_by_strategy(self, strategy: str):
        """Map strategy string to AppiumBy locator."""
        mapping = {
            "id": AppiumBy.ID,
            "xpath": AppiumBy.XPATH,
            "accessibility": AppiumBy.ACCESSIBILITY_ID,
            "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
            "class": AppiumBy.CLASS_NAME,
            "class_name": AppiumBy.CLASS_NAME,
            "name": AppiumBy.NAME,
            "css": AppiumBy.CSS_SELECTOR,
            "android_uiautomator": AppiumBy.ANDROID_UIAUTOMATOR,
            "ios_uiautomation": AppiumBy.IOS_UIAUTOMATION,
            "tag": AppiumBy.TAG_NAME,
        }
        normalized = strategy.lower().replace("-", "_")
        return mapping.get(normalized, AppiumBy.ID)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False
