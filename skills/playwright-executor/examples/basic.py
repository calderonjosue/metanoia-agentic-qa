# Playwright Executor Examples

## Basic Navigation

```python
from metanoia.skills.playwright_executor.executor import PlaywrightExecutor

async def test_navigation():
    executor = PlaywrightExecutor()
    result = await executor.execute({
        "action": "goto",
        "url": "https://example.com"
    })
    assert result["status"] == "success"
```

## Click with Self-Healing

```python
async def test_click():
    executor = PlaywrightExecutor()
    result = await executor.execute({
        "action": "click",
        "target": "#submit-button",
        "url": "https://example.com/form"
    })
    assert result["status"] == "success"
```

## Screenshot Capture

```python
async def test_screenshot():
    executor = PlaywrightExecutor()
    result = await executor.execute({
        "action": "screenshot",
        "url": "https://example.com"
    })
    assert result["status"] == "success"
    assert result["screenshot"] is not None
```
