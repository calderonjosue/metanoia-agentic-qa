# Playwright Executor Skill

UI automation with vision-based self-healing.

## Features

- **Vision Healing**: Automatically repairs broken selectors using Gemini Vision
- **Cross-Browser**: Chromium, Firefox, WebKit support
- **Smart Waits**: ML-predicted load times
- **Screenshot Diff**: Visual regression detection

## Quick Start

```python
from metanoia.skills.playwright_executor.executor import PlaywrightExecutor

executor = PlaywrightExecutor()
result = await executor.execute({
    "action": "click",
    "target": "#my-button",
    "url": "https://example.com"
})
```

## Configuration

Set `GEMINI_API_KEY` environment variable for vision healing.
