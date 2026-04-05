---
name: backstopjs-executor
version: 1.0.0
author: Metanoia-QA Team
description: Visual regression testing with BackstopJS using Puppeteer rendering
triggers:
  - visual:regression
  - backstopjs
  - visual:test
  - screenshot:diff
---

# BackstopJS Executor Skill

Visual regression testing skill powered by BackstopJS with Puppeteer rendering.

## Capabilities

- Puppeteer-based browser rendering
- Configurable viewport sizes (mobile, tablet, desktop)
- Dynamic content handling with delay and wait mechanisms
- HTML report generation with visual diffs
- CI/CD integration with exit codes
- Reference test configuration

## Architecture

```
BackstopExecutor
├── ConfigBuilder
│   ├── Viewport configuration
│   ├── Cookie/session handling
│   └── Dynamic content delays
├── TestRunner
│   ├── Reference capture
│   ├── Test execution
│   └── Diff generation
└── ReportGenerator
    ├── HTML reports
    └── CI/CD exit codes
```

## Usage

```bash
# Install BackstopJS
npm install -g backstopjs

# Initialize configuration
backstopjs init
```

```python
from metanoia.skills.backstopjs_executor.executor import BackstopExecutor

executor = BackstopExecutor()
result = await executor.execute({
    "action": "test",
    "config": "backstop.json",
    "scenarios": [...]
})
```

## Viewports

| Name | Width | Height |
|------|-------|--------|
| phone | 375 | 667 |
| tablet | 768 | 1024 |
| desktop | 1280 | 800 |

## Dynamic Content Handling

- `delay` - Wait time after page load (ms)
- `selector` - Wait for element before capture
- `onReadyScript` - Custom JavaScript before capture

## CI/CD Integration

Exit codes:
- `0` - All tests passed
- `1` - Tests failed
- `2` - Configuration error
