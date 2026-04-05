---
name: cypress-executor
version: 1.0.0
author: Metanoia-QA Team
description: End-to-end testing with Cypress
triggers:
  - cypress
  - e2e:test
  - ui:test
  - e2e:automation
---

# Cypress Executor Skill

End-to-end testing skill using Cypress.

## Capabilities

- `cy.visit()` - Navigate to URLs
- `cy.click()` - Click elements
- `cy.type()` - Type text into inputs
- `cy.contains()` - Find elements by text content
- `cy.get()` - Get elements by selector

## Architecture

```
CypressExecutor
├── BrowserManager
│   ├── Chrome/Firefox/Electron
│   └── Headless mode
├── CommandBuilder
│   ├── visit()
│   ├── click()
│   ├── type()
│   ├── contains()
│   └── get()
└── TestRunner
    ├── Spec execution
    └── Result aggregation
```

## Usage

```bash
# Install Cypress
npm install cypress --save-dev
npx cypress install
```

```python
from metanoia.skills.cypress_executor.executor import CypressExecutor

executor = CypressExecutor()
result = await executor.execute({
    "command": "visit",
    "url": "https://example.com"
})
```
