---
name: playwright-executor
version: 1.0.0
author: Metanoia-QA Team
description: UI automation with vision-based self-healing using Playwright and Gemini Vision
triggers:
  - ui:automation
  - playwright
  - visual:healing
  - ui:test
---

# Playwright Executor Skill

UI automation skill with vision-based self-healing capabilities.

## Capabilities

- Cross-browser UI automation (Chromium, Firefox, WebKit)
- Vision-based element detection and healing
- Automatic selector repair when DOM changes
- Screenshot diffing and visual regression
- Smart waits with ML-predicted load times

## Architecture

```
PlaywrightAgent
├── VisionHealer (Gemini Vision)
│   ├── Detects broken selectors via screenshots
│   └── Proposes修复 (repair) alternatives
├── SelectorEngine
│   ├── CSS/XPath generation
│   └── Fallback strategies
└── Executor
    ├── Navigation
    ├── Interaction
    └── Assertion
```

## Usage

```bash
# Install browsers
playwright install

# Install with dependencies
playwright install --with-deps
```

```python
from metanoia.skills.playwright_executor.executor import PlaywrightExecutor

executor = PlaywrightExecutor()
result = await executor.execute({
    "action": "click",
    "target": "#submit-button",
    "url": "https://example.com"
})
```
