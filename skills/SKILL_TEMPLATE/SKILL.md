---
name: skill-template
version: 1.0.0
author: Metanoia-QA Team
description: Template for creating new Metanoia-QA skills
triggers:
  - skill:create
  - skill:new
  - skill:bootstrap
---

# Skill Template

This is a template for creating new Metanoia-QA skills.

## Structure

```
skill-name/
├── SKILL.md          # Skill definition with frontmatter
├── executor.py       # Abstract executor class
├── schema.json       # Input/output contract
├── examples/         # Example usage
│   └── example_1.py
└── README.md         # Documentation
```

## Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique skill identifier (kebab-case) |
| `version` | Yes | Semantic version (1.0.0) |
| `author` | Yes | Skill author |
| `description` | Yes | What the skill does |
| `triggers` | No | Keywords that trigger this skill |

## Creating a New Skill

1. Copy this template to `metanoia/skills/<skill-name>/`
2. Update `SKILL.md` with your skill's frontmatter and documentation
3. Implement `executor.py` by subclassing `SkillExecutor`
4. Define input/output schema in `schema.json`
5. Add examples to `examples/`
6. Update this README with usage instructions

## Executor Pattern

```python
from metanoia.skills.base import SkillExecutor

class MySkillExecutor(SkillExecutor):
    async def execute(self, input_data: dict) -> dict:
        # Your implementation here
        pass
```

## Input/Output Contract

Define your skill's interface in `schema.json`:

```json
{
  "input": {
    "type": "object",
    "properties": {
      "param1": {"type": "string", "description": "..."}
    },
    "required": ["param1"]
  },
  "output": {
    "type": "object",
    "properties": {
      "result": {"type": "boolean"}
    }
  }
}
```
