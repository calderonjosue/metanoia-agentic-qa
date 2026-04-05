"""
Android Test Example - AppiumExecutor

Run with: python android_test.py
Requires: Appium server running on port 4723
"""

import sys
import time
sys.path.insert(0, '..')
from executor import AppiumExecutor


class AndroidTest:
    def __init__(self):
        self.executor = AppiumExecutor(
            platform="android",
            app_path="/path/to/your/app.apk",
            device_name="Android_Emulator",
            port=4723,
            implicit_wait=10,
            explicit_wait=15
        )

    def run(self):
        try:
            self.executor.connect()
            print("Connected to Android device")

            self._test_login_flow()
            self._test_swipe_navigation()
            self._test_element_interactions()

            print("All tests passed!")

        except Exception as e:
            print(f"Test failed: {e}")
            self.executor.get_screenshot("/tmp/android_failure.png")
            raise

        finally:
            self.executor.disconnect()
            print("Disconnected")

    def _test_login_flow(self):
        print("Testing login flow...")

        if self.executor.wait_for_element("id", "com.example:id/username", timeout=10):
            self.executor.send_keys("id", "com.example:id/username", "testuser")
            self.executor.send_keys("id", "com.example:id/password", "password123")
            self.executor.click_element("id", "com.example:id/login_button")

            time.sleep(2)

            if self.executor.wait_for_element("accessibility", "welcome_message", timeout=15):
                print("  Login successful")
            else:
                print("  Login may have failed - continue anyway")

    def _test_swipe_navigation(self):
        print("Testing swipe navigation...")

        if self.executor.wait_for_element("class", "android.support.v4.view.ViewPager", timeout=5):
            self.executor.swipe(400, 800, 400, 200)
            print("  Swiped left on ViewPager")

        time.sleep(1)

    def _test_element_interactions(self):
        print("Testing element interactions...")

        button_exists = self.executor.is_element_present(
            "accessibility", "submit_button"
        )
        print(f"  Submit button present: {button_exists}")

        if button_exists:
            button_text = self.executor.get_text("accessibility", "submit_button")
            print(f"  Button text: {button_text}")

            button_enabled = self.executor.is_element_visible(
                "accessibility", "submit_button"
            )
            print(f"  Button visible: {button_enabled}")

            self.executor.click_element("accessibility", "submit_button")
            print("  Clicked submit button")

        self.executor.switch_to_webview()
        print("  Switched to WebView context")

        if self.executor.wait_for_element("xpath", "//input[@type='email']", timeout=5):
            self.executor.send_keys("xpath", "//input[@type='email']", "test@example.com")
            print("  Filled webview email field")

        self.executor.switch_to_native()
        print("  Switched back to native context")

    def _test_pinch_zoom(self):
        print("Testing pinch zoom...")
        self.executor.pinch(500, 500, scale=2.0)
        print("  Pinch zoom performed")


if __name__ == "__main__":
    test = AndroidTest()
    test.run()
