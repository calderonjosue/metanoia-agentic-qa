# Visual Healing Skill

Self-healing UI selectors using Gemini Vision AI.

## Overview

When DOM changes break traditional CSS/XPath selectors, visual healing
uses AI to analyze the page and generate robust alternatives.

## Features

- **Vision Analysis**: Gemini Vision powered element detection
- **Heuristic Repair**: Fallback strategies without API calls
- **History Learning**: Improves over time from past repairs
- **Multi-Strategy**: Combines multiple healing approaches

## How It Works

```
1. Selector fails (DOM change, element moved)
        ↓
2. Capture screenshot of current page
        ↓
3. Gemini Vision analyzes visual layout
        ↓
4. Proposes修复 (repair) selector alternatives
        ↓
5. Test proposed selectors
        ↓
6. Return best match with confidence
```

## Quick Start

```python
from metanoia.skills.visual_healing.executor import VisualHealingExecutor

healer = VisualHealingExecutor()
result = await healer.execute({
    "screenshot": base64_screenshot,
    "failed_selector": "#old-button",
    "action_intent": "click"
})

print(f"Healed: {result['healed_selector']}")
```

## Configuration

Set `GEMINI_API_KEY` environment variable for AI vision analysis.
Without the API key, heuristic strategies are used.

## Confidence Levels

| Confidence | Meaning |
|------------|---------|
| 0.9+ | Vision-verified, high certainty |
| 0.7-0.9 | Vision analysis, good certainty |
| 0.5-0.7 | Heuristic, moderate certainty |
| <0.5 | Best effort, may need review |
