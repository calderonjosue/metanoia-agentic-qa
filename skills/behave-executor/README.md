# Behave Executor Skill

BDD testing using Behave, the Python BDD framework.

## Features

- **Gherkin Support**: Write scenarios in plain English
- **Step Definitions**: Python implementations for Given-When-Then
- **Tags Filtering**: Run subsets via `@tag` annotations
- **Table-Driven**: Scenario Outline with examples
- **Hooks**: Setup/teardown via environment.py

## Quick Start

### 1. Install Behave

```bash
pip install behave
```

### 2. Create Feature File

```gherkin
# features/login.feature
Feature: Login
  @smoke
  Scenario: Successful login
    Given I am on the login page
    When I fill in "username" with "admin"
    And I fill in "password" with "secret"
    And I press "Login"
    Then I should see "Welcome"
```

### 3. Create Step Definitions

```python
# features/steps/login_steps.py
from behave import given, when, then

@given('I am on the login page')
def step_impl(context):
    context.browser.get("https://example.com/login")

@when('I fill in "{field}" with "{value}"')
def step_impl(context, field, value):
    elem = context.browser.find_element_by_name(field)
    elem.send_keys(value)

@when('I press "{button}"')
def step_impl(context, button):
    context.browser.find_element_by_name(button).click()

@then('I should see "{text}"')
def step_impl(context, text):
    assert text in context.browser.page_source
```

### 4. Run Tests

```bash
behave features/
behave --tags=@smoke
behave --tags="not @wip"
```

## Executor Usage

```python
from metanoia.skills.behave_executor.executor import BehaveExecutor

executor = BehaveExecutor()
result = await executor.execute({
    "features": ["features/login.feature"],
    "tags": ["@smoke"],
    "steps_module": "features.steps",
    "format": "json"
})
```

## Tags

| Tag | Description |
|-----|-------------|
| `@smoke` | Smoke tests |
| `@regression` | Regression tests |
| `@wip` | Work in progress |
| `@auth` | Authentication tests |

Combine with `and`, `or`, `not`:
- `behave --tags="@smoke and @auth"`
- `behave --tags="not @wip"`
- `behave --tags="@smoke or @regression"`
