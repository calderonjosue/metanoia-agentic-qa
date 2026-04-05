---
name: appium-executor
description: Mobile testing skill for iOS and Android using Appium. Trigger: When testing mobile apps, automating iOS/Android native or webview testing, or performing mobile gesture automation.
base: /Users/calderonjosue_/metanoia/skills/appium-executor
files:
  - executor.py
  - schema.json
  - examples/android_test.py
  - examples/ios_test.py
---

# Appium Executor Skill

Execute mobile automation tests for Android and iOS using Appium with Python.

## Quick Start

```python
from executor import AppiumExecutor

# Initialize executor
executor = AppiumExecutor(
    platform="android",
    app_path="/path/to/app.apk",
    port=4723
)

# Connect and test
executor.connect()
executor.find_element("id", "com.example:id/button").click()
executor.swipe(500, 500, 100, 500)  # swipe up
executor.disconnect()
```

## Features

- Android and iOS native app testing
- WebView context switching and testing
- Gesture support: tap, swipe, pinch, zoom
- Element finding by ID, XPath, accessibility ID, class name
- Screenshot capture on failure
- Implicit/explicit wait strategies

## Configuration

See `schema.json` for full configuration options.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| platform | string | Yes | "android" or "ios" |
| app_path | string | Yes | Path to .apk or .app |
| port | integer | No | Appium server port (default: 4723) |
| device_name | string | No | Target device name |
| bundle_id | string | iOS | iOS app bundle ID |
