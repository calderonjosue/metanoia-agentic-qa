# Cypress Executor Skill

End-to-end testing with Cypress.

## Features

- **Cross-browser**: Chrome, Firefox, Electron support
- **Auto-waiting**: Automatic retries and waits
- **Real DOM**: Real browser execution
- **Time-travel**: Debug with snapshots

## Quick Start

```python
from metanoia.skills.cypress_executor.executor import CypressExecutor

executor = CypressExecutor()
result = await executor.execute({
    "command": "visit",
    "url": "https://example.com"
})
```

## Supported Commands

| Command | Description |
|---------|-------------|
| `visit` | Navigate to a URL |
| `click` | Click an element |
| `type` | Type text into an input |
| `contains` | Find element by text |
| `get` | Get element by selector |
