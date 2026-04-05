# A11y Tester

Accessibility testing skill using axe-core for WCAG 2.1 and Section 508 compliance.

## Installation

```bash
pip install axe-core playwright
playwright install chromium
```

## Usage

```python
from metanoia.skills.a11y_tester.executor import A11yTesterExecutor

async def main():
    executor = A11yTesterExecutor()
    result = await executor.execute({
        "url": "https://example.com",
        "standards": ["wcag21aa"],
        "include_html": True
    })
    print(f"Violations: {result['violation_count']}")

asyncio.run(main())
```

## Files

| File | Description |
|------|-------------|
| `SKILL.md` | Skill definition with frontmatter |
| `executor.py` | A11yTesterExecutor implementation |
| `schema.json` | Input/output contract |
| `examples/page_audit.py` | Example accessibility audit |
| `README.md` | This file |

## Command Line

```bash
python -m metanoia.skills.a11y_tester.executor --url https://example.com --output report.json
```

## Integration

### CI/CD Pipeline

```python
# GitHub Actions
- uses: actions/checkout@v3
- name: Run A11y Tests
  run: python -m metanoia.skills.a11y_tester --url ${{ env.URL }}
```

### Integration with Test Suites

```python
import pytest
from metanoia.skills.a11y_tester.executor import A11yTesterExecutor

@pytest.mark.asyncio
async def test_login_page_a11y():
    executor = A11yTesterExecutor()
    result = await executor.execute({"url": "/login"})
    assert result["violation_count"] == 0, result["violations"]
```

## Standards

- WCAG 2.1 (A, AA, AAA)
- Section 508
- axe-core best practices

## Exit Codes

- `0`: Success, no violations
- `1`: Violations found
- `2`: Scan error
