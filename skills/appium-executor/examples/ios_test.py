"""
iOS Test Example - AppiumExecutor

Run with: python ios_test.py
Requires: Appium server running on port 4723 with WebDriverAgent configured
"""

import sys
import time
sys.path.insert(0, '..')
from executor import AppiumExecutor


class iOSTest:
    def __init__(self):
        self.executor = AppiumExecutor(
            platform="ios",
            app_path="/path/to/your/app.app",
            bundle_id="com.example.myapp",
            device_name="iPhone 14",
            platform_version="16.0",
            port=4723,
            implicit_wait=10,
            explicit_wait=15
        )

    def run(self):
        try:
            self.executor.connect()
            print("Connected to iOS device")

            self._test_native_interactions()
            self._test_webview_testing()
            self._test_gestures()

            print("All tests passed!")

        except Exception as e:
            print(f"Test failed: {e}")
            self.executor.get_screenshot("/tmp/ios_failure.png")
            raise

        finally:
            self.executor.disconnect()
            print("Disconnected")

    def _test_native_interactions(self):
        print("Testing native interactions...")

        if self.executor.wait_for_element("accessibility", "SettingsButton", timeout=10):
            self.executor.click_element("accessibility", "SettingsButton")
            print("  Clicked settings button")

            time.sleep(1)

        self.executor.hide_keyboard()

        nav_items = self.executor.find_elements(
            "class", "XCUIElementTypeCell"
        )
        print(f"  Found {len(nav_items)} navigation items")

    def _test_webview_testing(self):
        print("Testing WebView...")

        contexts = self.executor.get_contexts()
        print(f"  Available contexts: {contexts}")

        if len(contexts) > 1:
            self.executor.switch_to_webview()
            print("  Switched to WebView")

            time.sleep(1)

            search_box = self.executor.find_element("css", "input[type='search']")
            if search_box:
                search_box.click()
                self.executor.send_keys("css", "input[type='search']", "test query")
                print("  Filled search box in WebView")

            self.executor.switch_to_native()
            print("  Back to native context")

    def _test_gestures(self):
        print("Testing gestures...")

        self.executor.tap(200, 400)
        print("  Tapped at (200, 400)")

        self.executor.long_press(200, 400, duration=1500)
        print("  Long pressed at (200, 400)")

        self.executor.swipe(400, 800, 400, 200, duration=800)
        print("  Swiped up")

        table_exists = self.executor.is_element_present(
            "class", "XCUIElementTypeTableView"
        )
        if table_exists:
            self.executor.scroll("class", "XCUIElementTypeTableView", "down")
            print("  Scrolled table down")

    def _test_element_attributes(self):
        print("Testing element attributes...")

        if self.executor.wait_for_element("id", "mainButton", timeout=5):
            is_enabled = self.executor.get_attribute(
                "id", "mainButton", "enabled"
            )
            print(f"  Button enabled: {is_enabled}")

            element_type = self.executor.get_attribute(
                "id", "mainButton", "type"
            )
            print(f"  Element type: {element_type}")

            label = self.executor.get_attribute(
                "id", "mainButton", "label"
            )
            print(f"  Element label: {label}")

    def _test_page_source(self):
        print("Testing page source retrieval...")
        source = self.executor.get_page_source()
        print(f"  Page source length: {len(source)} chars")


if __name__ == "__main__":
    test = iOSTest()
    test.run()
