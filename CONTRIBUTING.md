# Contributing to Metanoia-QA

Thank you for your interest in contributing to Metanoia-QA!

This document provides guidelines and instructions for contributing.

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Running Tests](#running-tests)
4. [Coding Standards](#coding-standards)
5. [Submitting Changes](#submitting-changes)
6. [Skill Development](#skill-development)

---

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/metanoia-qa.git
   cd metanoia-qa
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/metanoia-qa/metanoia-qa.git
   ```

---

## Development Setup

### Prerequisites

- Python 3.12+
- Git
- (Optional) Docker for containerized development

### Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Required for full functionality:
# - GEMINI_API_KEY
# - SUPABASE_URL
# - SUPABASE_SERVICE_KEY
```

### Verify Setup

```bash
# Run the application
uvicorn src.api.main:app --reload

# Run tests to verify everything works
pytest tests/ -v
```

---

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Suites

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# With coverage report
pytest tests/ --cov=src --cov-report=html
```

### Test Categories

| Tag | Description |
|-----|-------------|
| `unit` | Fast unit tests, no external dependencies |
| `integration` | Tests requiring external services |
| `slow` | Tests taking > 10 seconds |

### Writing Tests

```python
import pytest
from metanoia.src.agents.example import ExampleAgent

class TestExampleAgent:
    """Tests for ExampleAgent."""

    @pytest.fixture
    def agent(self):
        return ExampleAgent()

    @pytest.mark.asyncio
    async def test_execute_success(self, agent):
        result = await agent.execute({"input": "test"})
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_execute_error(self, agent):
        result = await agent.execute({"invalid": "data"})
        assert result["status"] == "error"
```

---

## Coding Standards

### Python Style

- Follow **PEP 8** guidelines
- Use **type hints** for all function signatures
- Maximum line length: **100 characters**
- Use **async/await** for I/O operations

### Import Organization

```python
# Standard library
import json
from pathlib import Path

# Third-party
from pydantic import BaseModel

# Local application
from metanoia.src.agents.base import AgentBase
```

### Docstring Format

```python
async def execute(self, input_data: dict) -> dict:
    """Execute the agent with given input.
    
    Args:
        input_data: Dictionary containing execution parameters.
        
    Returns:
        Dictionary with execution results.
        
    Raises:
        ExecutionError: If execution fails.
    """
    pass
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Modules | snake_case | `context_analyst.py` |
| Classes | PascalCase | `ContextAnalyst` |
| Functions | snake_case | `analyze_context()` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |
| Variables | snake_case | `result_data` |

### Pre-commit Hooks

We use pre-commit to enforce standards:

```bash
# Run all hooks manually
pre-commit run --all-files

# Skip hooks (not recommended)
git commit --no-verify
```

---

## Submitting Changes

### Branch Naming

```
feature/description      # New features
bugfix/description       # Bug fixes
docs/description         # Documentation updates
skill/description        # New skill modules
```

### Commit Messages

```
type(scope): description

Types: feat, fix, docs, style, refactor, test, chore

Examples:
- feat(agents): add context analyzer with memory
- fix(playwright): repair selector healing logic
- docs: update API documentation
```

### Pull Request Process

1. **Create a feature branch** from `develop`:
   ```bash
   git checkout develop
   git pull upstream develop
   git checkout -b feature/my-feature
   ```

2. **Make your changes** following the coding standards

3. **Run tests locally**:
   ```bash
   pytest tests/ -v
   ruff check .
   mypy src/
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/my-feature
   ```

6. **Open a Pull Request** on GitHub with:
   - Clear title and description
   - Reference to related issues
   - Screenshots for UI changes

### PR Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No hardcoded secrets
```

---

## Skill Development

### Creating a New Skill

1. Copy the template:
   ```bash
   cp -r skills/SKILL_TEMPLATE skills/my-new-skill
   ```

2. Implement the executor:
   ```python
   from metanoia.skills.base import SkillExecutor
   
   class MySkillExecutor(SkillExecutor):
       name = "my-new-skill"
       version = "1.0.0"
       
       async def execute(self, input_data):
           # Your implementation
           pass
   ```

3. Add tests in `tests/skills/`

4. Document in `skills/my-new-skill/README.md`

### Skill Structure

```
skills/
└── my-new-skill/
    ├── SKILL.md          # Frontmatter + docs
    ├── executor.py       # Implementation
    ├── schema.json       # I/O contract
    ├── examples/         # Usage examples
    └── README.md         # Quick reference
```

---

## Code of Conduct

Please be respectful and constructive. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## Questions?

- GitHub Issues: For bug reports and feature requests
- Discussions: For questions and community support

---

*Last updated: 2026-04-04*
