# Creating Skills for Metanoia-QA

Guide to creating, testing, and contributing new skills to the Metanoia-QA framework.

## Table of Contents

1. [Overview](#overview)
2. [Skill Anatomy](#skill-anatomy)
3. [Creating a New Skill](#creating-a-new-skill)
4. [Testing Your Skill](#testing-your-skill)
5. [Submitting to the Community](#submitting-to-the-community)

---

## Overview

Skills are the fundamental units of functionality in Metanoia-QA. Each skill encapsulates a specific capability—UI automation, performance testing, security scanning—that can be invoked by agents in the framework.

### When to Create a Skill

- You need to integrate a new testing tool
- You have reusable logic other agents can benefit from
- You want to share functionality with the community

---

## Skill Anatomy

Every skill follows a standardized structure:

```
skill-name/
├── SKILL.md          # Frontmatter metadata + documentation
├── executor.py       # Main implementation class
├── schema.json       # Input/output contract (JSON Schema)
├── examples/         # Usage examples
│   └── example_1.py
└── README.md         # Quick reference
```

### Frontmatter (SKILL.md)

```yaml
---
name: my-skill
version: 1.0.0
author: Your Name
description: What this skill does
triggers:
  - keyword1
  - keyword2
---

# My Skill

Documentation in Markdown follows...
```

### Executor Class

```python
from metanoia.skills.base import SkillExecutor, SkillInput, SkillOutput

class MySkillExecutor(SkillExecutor):
    name = "my-skill"
    version = "1.0.0"

    async def execute(self, input_data: SkillInput) -> SkillOutput:
        # Implementation
        return {"status": "success", "result": data}
```

### Schema (schema.json)

Defines valid inputs and outputs using JSON Schema:

```json
{
  "input": {
    "type": "object",
    "properties": {
      "target": {"type": "string"}
    },
    "required": ["target"]
  },
  "output": {
    "type": "object", 
    "properties": {
      "status": {"type": "string"},
      "result": {"type": "object"}
    }
  }
}
```

---

## Creating a New Skill

### Step 1: Use the Template

```bash
cp -r metanoia/skills/SKILL_TEMPLATE metanoia/skills/your-skill-name
```

### Step 2: Fill in Frontmatter

Edit `SKILL.md` with:

- `name`: Unique identifier (kebab-case, no spaces)
- `version`: Semantic version (1.0.0)
- `author`: Your name or organization
- `description`: Clear description of functionality
- `triggers`: Keywords that should activate this skill

### Step 3: Implement the Executor

Edit `executor.py`:

1. Import base class: `from metanoia.skills.base import SkillExecutor`
2. Subclass `SkillExecutor`
3. Set `name` and `version` class attributes
4. Implement `async def execute(self, input_data: SkillInput) -> SkillOutput`

```python
from typing import Any
from metanoia.skills.base import SkillExecutor, SkillInput, SkillOutput

class MySkillExecutor(SkillExecutor):
    name = "my-skill"
    version = "1.0.0"

    async def execute(self, input_data: SkillInput) -> SkillOutput:
        target = input_data.get("target")
        
        try:
            # Your logic here
            result = await some_async_operation(target)
            return {
                "status": "success",
                "data": result
            }
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e)
            }
```

### Step 4: Define the Schema

Edit `schema.json` to document your input/output contract:

```json
{
  "input": {
    "type": "object",
    "properties": {
      "target": {
        "type": "string",
        "description": "URL or path to target"
      },
      "options": {
        "type": "object",
        "description": "Optional configuration"
      }
    },
    "required": ["target"]
  },
  "output": {
    "type": "object",
    "properties": {
      "status": {
        "type": "string",
        "enum": ["success", "error"]
      },
      "data": {},
      "error": {
        "type": "string"
      }
    }
  }
}
```

### Step 5: Add Examples

Create `examples/your_example.py` with working code:

```python
"""Example: Using my-skill."""
import asyncio
from metanoia.skills.my_skill.executor import MySkillExecutor

async def main():
    executor = MySkillExecutor()
    result = await executor.execute({
        "target": "https://example.com"
    })
    print(result)

asyncio.run(main())
```

### Step 6: Write README

Document:
- What the skill does
- How to install/configure
- Basic usage
- Configuration options

---

## Testing Your Skill

### Unit Testing

```python
import pytest
import asyncio
from metanoia.skills.my_skill.executor import MySkillExecutor

@pytest.fixture
def executor():
    return MySkillExecutor()

@pytest.mark.asyncio
async def test_execute_success(executor):
    result = await executor.execute({"target": "https://example.com"})
    assert result["status"] == "success"

@pytest.mark.asyncio
async def test_execute_error(executor):
    result = await executor.execute({"target": "invalid"})
    assert result["status"] == "error"
```

### Integration Testing

For skills that interact with external systems:

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_with_real_system():
    executor = MySkillExecutor()
    result = await executor.execute({
        "target": "https://staging.example.com",
        "api_key": os.getenv("TEST_API_KEY")
    })
    assert result["status"] == "success"
```

### Running Tests

```bash
# All tests
pytest tests/

# Specific skill tests
pytest tests/skills/test_my_skill.py

# With coverage
pytest --cov=metanoia/skills/my_skill tests/
```

---

## Submitting to the Community

### Prerequisites

1. Your skill is in `metanoia/skills/<your-skill>/`
2. Tests pass locally
3. Documentation is complete
4. You have permission to open-source the code

### Submission Process

1. **Fork** the repository
2. **Create** a branch: `git checkout -b skill/<your-skill>`
3. **Add** your skill following the directory structure
4. **Commit** your changes
5. **Push** to your fork
6. **Open** a Pull Request with description

### PR Template

```markdown
## Skill: <your-skill-name>

**Description**: Brief description of what the skill does

**Author**: Your Name

**Capabilities**:
- Capability 1
- Capability 2

**Example**:
```python
executor = MySkillExecutor()
result = await executor.execute({"target": "..."})
```

**Testing**: How was this tested?

**Dependencies**: Any external dependencies required?
```

### Review Criteria

- Code follows existing patterns
- Tests are included and pass
- Documentation is complete
- No security vulnerabilities
- No hardcoded secrets

---

## Best Practices

### Error Handling

```python
async def execute(self, input_data: SkillInput) -> SkillOutput:
    try:
        result = await risky_operation(input_data)
        return {"status": "success", "data": result}
    except SpecificError as e:
        return {"status": "error", "error": f"Specific error: {e}"}
    except Exception as e:
        return {"status": "error", "error": "Unexpected error"}
```

### Cleanup

```python
async def execute(self, input_data: SkillInput) -> SkillOutput:
    try:
        # Setup
        resource = await acquire_resource()
        # ... use resource ...
        return {"status": "success"}
    finally:
        await self.cleanup()

async def cleanup(self):
    # Release resources
    pass
```

### Validation

```python
async def validate_input(self, input_data: dict) -> bool:
    required = ["target", "timeout"]
    return all(k in input_data for k in required)
```

---

## Getting Help

- GitHub Issues: Report bugs or request features
- Discord: Join the Metanoia-QA community
- Documentation: Check the main docs folder

---

*Last updated: 2026-04-04*
