---
name: visual-healing
version: 1.0.0
author: Metanoia-QA Team
description: Self-healing using Gemini Vision - automatic repair of broken UI elements
triggers:
  - visual:healing
  - self:heal
  - vision:repair
  - selector:repair
---

# Visual Healing Skill

Self-healing capability using Gemini Vision to automatically
repair broken UI selectors and elements.

## Overview

When traditional selectors fail due to DOM changes, visual healing
uses AI vision to analyze the page and propose working alternatives.

## Capabilities

- Analyze screenshots to find elements
- Generate robust selectors from visual cues
- Handle dynamic DOM changes
- Learn from past repairs
- Multi-language element identification

## Usage

```python
from metanoia.skills.visual_healing.executor import VisualHealingExecutor

healer = VisualHealingExecutor()
result = await healer.heal({
    "screenshot": screenshot_bytes,
    "failed_selector": "#old-button",
    "action_intent": "click"
})
```
