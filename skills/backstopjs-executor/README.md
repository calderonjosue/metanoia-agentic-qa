# BackstopJS Executor

Visual regression testing with BackstopJS powered by Puppeteer rendering.

## Overview

This skill provides automated visual regression testing capabilities. It captures screenshots of web pages and compares them against reference images to detect unintended visual changes.

## Features

- **Puppeteer Rendering**: Headless Chrome with full CSS/JS support
- **Configurable Viewports**: Predefined mobile, tablet, desktop presets
- **Dynamic Content Handling**: Wait for elements, delays, custom scripts
- **HTML Reports**: Visual diff highlighting with heatmap
- **CI/CD Ready**: Exit codes for automated pipelines

## Installation

```bash
npm install -g backstopjs
```

## Quick Start

```bash
# Initialize BackstopJS
backstopjs init

# Run reference test
backstopjs reference

# Run visual test
backstopjs test
```

## Configuration

Create a `backstop.json` file:

```json
{
  "id": "my-project",
  "viewports": [
    { "name": "phone", "width": 375, "height": 667 },
    { "name": "desktop", "width": 1280, "height": 800 }
  ],
  "scenarios": [
    {
      "label": "Homepage",
      "url": "https://example.com",
      "delay": 1000,
      "hideSelectors": [".cookie-banner"],
      "removeSelectors": [".ad-overlay"]
    }
  ]
}
```

## Executor Usage

```python
import asyncio
from metanoia.skills.backstopjs_executor.executor import BackstopExecutor

async def run_test():
    executor = BackstopExecutor()
    
    result = await executor.execute({
        "action": "reference",
        "config": {
            "scenarios": [
                {
                    "label": "Homepage",
                    "url": "https://example.com",
                    "viewport": {"width": 1280, "height": 800}
                }
            ]
        }
    })
    
    print(f"Status: {result['status']}")
    return result

asyncio.run(run_test())
```

## Viewport Presets

| Preset | Width | Height |
|--------|-------|--------|
| phone | 375 | 667 |
| tablet | 768 | 1024 |
| desktop | 1280 | 800 |
| wide | 1920 | 1080 |

## Dynamic Content Options

| Option | Type | Description |
|--------|------|-------------|
| `delay` | number | Milliseconds to wait after load |
| `selector` | string | CSS selector to wait for |
| `onReadyScript` | string | Path to JS file to run before capture |
| `hideSelectors` | array | Selectors to set `visibility: hidden` |
| `removeSelectors` | array | Selectors to set `display: none` |

## CI/CD Integration

```yaml
# GitHub Actions example
- name: Visual Regression Test
  run: npx backstop test
- name: Upload Report
  if: failure()
  uses: actions/upload-artifact@v2
  with:
    name: backstop-report
    path: backstop_data
```

## Report Output

Reports are generated in `backstop_data/html_report/`:

- `index.html` - Main report with all scenarios
- Visual diffs with heatmap highlighting
- Pixel difference percentage
- Failed test screenshots

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All tests passed |
| 1 | Visual regressions detected |
| 2 | Configuration error |
