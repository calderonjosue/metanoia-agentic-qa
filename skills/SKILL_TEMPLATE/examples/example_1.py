# Skill Template Examples

This directory contains example usage of the skill template.

## Example 1: Basic Skill Usage

```python
"""Example: Using a skill executor."""
import asyncio
from my_skill.executor import MySkillExecutor


async def main():
    executor = MySkillExecutor()
    
    input_data = {
        "param1": "hello",
        "param2": 42
    }
    
    result = await executor.execute(input_data)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

## Example 2: Creating a Custom Skill

```python
"""Example: Creating a custom skill."""
from metanoia.skills.base import SkillExecutor, SkillInput, SkillOutput


class HelloWorldExecutor(SkillExecutor):
    name = "hello-world"
    version = "1.0.0"

    async def execute(self, input_data: SkillInput) -> SkillOutput:
        name = input_data.get("name", "World")
        return {
            "status": "success",
            "message": f"Hello, {name}!"
        }


# Usage
async def demo():
    executor = HelloWorldExecutor()
    result = await executor.execute({"name": "Metanoia"})
    assert result["status"] == "success"
    assert result["message"] == "Hello, Metanoia!"
```
