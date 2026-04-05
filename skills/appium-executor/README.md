# Appium Executor Skill

Mobile testing skill for iOS and Android using Appium with Python.

## Overview

The Appium Executor skill provides a Python-based automation framework for testing native mobile applications and webviews on Android and iOS devices.

## Installation

```bash
pip install appium python-appium-client
```

## Usage

```python
from appium_executor import AppiumExecutor

executor = AppiumExecutor(
    platform="android",
    app_path="path/to/app.apk",
    device_name="Pixel_6"
)

executor.connect()

# Find and interact with elements
element = executor.find_element("accessibility", "login_button")
element.click()

# Perform gestures
executor.tap(100, 200)
executor.swipe(500, 1000, 500, 100)  # swipe down
executor.pinch(500, 500, 2)

# Switch to WebView
executor.switch_to_webview()
executor.find_element("xpath", "//button[text()='Submit']").click()

executor.disconnect()
```

## Platform-Specific Notes

### Android

- Use `app_path` with `.apk` file
- Supports UIAutomator2 driver
- Element locators: id, xpath, accessibility, class

### iOS

- Use `bundle_id` or `app_path` with `.app` file
- Uses XCUITest driver
- Requires WebDriverAgent setup
- Element locators: id, xpath, accessibility, class

## API Reference

### Connection

- `connect()` - Initialize Appium session
- `disconnect()` - Close Appium session
- `switch_to_webview()` - Switch to WebView context
- `switch_to_native()` - Switch back to native context

### Element Finding

- `find_element(strategy, value)` - Find single element
- `find_elements(strategy, value)` - Find multiple elements

### Gestures

- `tap(x, y)` - Tap at coordinates
- `long_press(x, y, duration)` - Long press
- `swipe(start_x, start_y, end_x, end_y)` - Swipe gesture
- `pinch(x, y, scale)` - Pinch zoom
- `scroll(element, direction)` - Scroll within element

### Waits

- `wait_for_element(strategy, value, timeout)` - Explicit wait
- `set_implicit_wait(seconds)` - Set implicit wait
