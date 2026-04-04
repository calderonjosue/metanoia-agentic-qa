# Visual Healing Examples

## Basic Healing

```python
from metanoia.skills.visual_healing.executor import VisualHealingExecutor

async def heal_selector():
    healer = VisualHealingExecutor()
    result = await healer.execute({
        "screenshot": base64_screenshot,
        "failed_selector": "#submit-btn-v2",
        "action_intent": "click"
    })
    print(f"Healed selector: {result['healed_selector']}")
```

## Using the Orchestrator

```python
from metanoia.skills.visual_healing.executor import SelfHealingOrchestrator

async def full_healing():
    orchestrator = SelfHealingOrchestrator()
    result = await orchestrator.heal(
        broken_selector="#old-button",
        screenshot=screenshot_bytes,
        action="click"
    )
    print(f"Status: {result['status']}")
    if result['healed_selector']:
        print(f"Use: {result['healed_selector']}")
```

## Without Screenshot (Heuristics Only)

```python
async def heuristic_healing():
    healer = VisualHealingExecutor()
    result = await healer.execute({
        "failed_selector": ".dynamic-class-12345",
        "action_intent": "click"
    })
    print(f"Alternatives: {result['alternative_selectors']}")
```
