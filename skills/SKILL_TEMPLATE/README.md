# SKILL_TEMPLATE

Template for creating new Metanoia-QA skills.

## Quick Start

1. Copy this directory to `metanoia/skills/<your-skill>/`
2. Customize the files for your skill
3. Register the skill in the skill registry

## Files

| File | Description |
|------|-------------|
| `SKILL.md` | Skill definition with frontmatter |
| `executor.py` | Abstract executor class |
| `schema.json` | Input/output contract |
| `examples/` | Example usage |
| `README.md` | This file |

## Creating a New Skill

```bash
# 1. Copy template
cp -r skills/SKILL_TEMPLATE skills/my-new-skill

# 2. Edit SKILL.md with your frontmatter
cd skills/my-new-skill
$EDITOR SKILL.md

# 3. Implement executor.py
$EDITOR executor.py

# 4. Define schema
$EDITOR schema.json

# 5. Add examples
mkdir -p examples
$EDITOR examples/my_example.py
```

## Skill Anatomy

### SKILL.md
Contains frontmatter metadata and documentation:
- `name`: Unique identifier (kebab-case)
- `version`: Semantic version
- `author`: Who created it
- `description`: What it does
- `triggers`: Keywords that activate the skill

### executor.py
The main logic. Subclass `SkillExecutor` and implement `execute()`.

### schema.json
JSON Schema defining valid inputs and outputs.

## Testing Your Skill

```python
import asyncio
from my_skill.executor import MySkillExecutor

async def test():
    executor = MySkillExecutor()
    result = await executor.execute({"param1": "value"})
    assert result["status"] == "success"

asyncio.run(test())
```

## Registering Your Skill

Add to `metanoia/skills/__init__.py`:

```python
from .my_new_skill.executor import MySkillExecutor

__all__ = ["MySkillExecutor"]
```

## Contributing

See `docs/CREATING_SKILLS.md` for full guide.
