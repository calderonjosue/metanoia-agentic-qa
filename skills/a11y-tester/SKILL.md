---
name: a11y-tester
version: 1.0.0
author: Metanoia-QA Team
description: Accessibility testing skill using axe-core for WCAG 2.1 and Section 508 compliance
triggers:
  - a11y
  - accessibility
  - wcag
  - section508
  - axe-core
  - accessibility-audit
  - accessibility-test
---

# A11y Tester Skill

Accessibility testing using axe-core engine for automated WCAG 2.1 and Section 508 compliance checking.

## Features

- **WCAG 2.1 Compliance**: Full support for Levels A, AA, and AAA
- **Section 508 Compliance**: Validates against US federal accessibility requirements
- **Automated Scans**: Run comprehensive accessibility audits on any URL
- **CI/CD Integration**: Exit codes and JSON reports for automation pipelines
- **Detailed Violation Reports**: Actionable remediation guidance for each issue

## Quick Start

```python
from metanoia.skills.a11y_tester.executor import A11yTesterExecutor

executor = A11yTesterExecutor()
result = await executor.execute({
    "url": "https://example.com",
    "standards": ["wcag21aa", "section508"],
    "verbose": True
})
```

## Standards Supported

| Standard | Description |
|----------|-------------|
| `wcag21a` | WCAG 2.1 Level A |
| `wcag21aa` | WCAG 2.1 Level AA |
| `wcag21aaa` | WCAG 2.1 Level AAA |
| `section508` | Section 508 (US federal) |
| `bestpractice` | Axe-core best practices |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No violations found |
| 1 | Violations found |
| 2 | Scan error occurred |

## Report Formats

- **JSON**: Machine-readable for CI/CD integration
- **HTML**: Human-readable with remediation guidance
- **Sarif**: Standard format for CI systems

## CI/CD Example

```yaml
# GitHub Actions
- name: Run Accessibility Audit
  run: |
    python -m metanoia.skills.a11y_tester \
      --url ${{ env.URL }} \
      --output results.json \
      --format json
```

## Violation Categories

- **Critical**: Must fix immediately (e.g., missing alt text)
- **Serious**: Should fix (e.g., low contrast)
- **Moderate**: Should consider fixing
- **Minor**: Nice to fix

## Remediation

Each violation includes:
- `help`: What the issue is
- `helpUrl`: Documentation link
- `nodes`: Affected DOM elements
- `impact`: Severity level
- `tags`: Related WCAG criteria
