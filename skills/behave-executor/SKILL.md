---
name: behave-executor
version: 1.0.0
author: Metanoia-QA Team
description: BDD testing skill using Behave (Python BDD framework). Trigger: bdd, behave, gherkin, given-when-then, behavior:testing
---

# Behave Executor Skill

BDD testing skill using Behave, the Python BDD framework.

## Capabilities

- Run `.feature` files with Gherkin syntax
- Support Given-When-Then step definitions
- Table-driven scenarios (Scenario Outline)
- Tags filtering (`@tag`, `@wip`, etc.)
- Background steps per feature
- Hooks for setup/teardown

## Architecture

```
BehaveExecutor
├── FeatureLoader
│   ├── Parses .feature files
│   └── Resolves step implementations
├── StepRegistry
│   ├── Registers Given/When/Then steps
│   └── Maps step text to functions
├── TagFilter
│   └── Filters scenarios by tags
└── Runner
    ├── Executes Behave
    └── Returns results
```

## Usage

```bash
# Install Behave
pip install behave

# Run all features
behave

# Run with specific tags
behave --tags=@smoke
behave --tags="not @wip"
behave --tags="@auth and @smoke"
```

```python
from metanoia.skills.behave_executor.executor import BehaveExecutor

executor = BehaveExecutor()
result = await executor.execute({
    "features": ["features/login.feature"],
    "tags": ["@smoke"],
    "steps_module": "features.steps"
})
```
