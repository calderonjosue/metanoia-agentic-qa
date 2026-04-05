---
name: selenium-executor
version: 1.0.0
author: Metanoia-QA Team
description: Selenium WebDriver test execution with page object model support
triggers:
  - selenium
  - webdriver
  - browser:automation
  - ui:test
  - page:object:model
---

# Selenium Executor Skill

UI automation skill using Selenium WebDriver with page object model (POM) support.

## Capabilities

- Cross-browser UI automation (Chrome, Firefox, Edge, Safari)
- Page object model (POM) pattern support
- Element locators with multiple strategies (ID, Name, CSS, XPath, etc.)
- Explicit and implicit waits
- Screenshot capture on failure
- Headless browser execution

## Architecture

```
SeleniumExecutor
├── WebDriver Manager
│   ├── Browser drivers (Chrome, Firefox, Edge, Safari)
│   └── Driver lifecycle management
├── Element Locator
│   ├── ID, Name, CSS, XPath, LinkText
│   └── Custom locators
├── Page Object Factory
│   ├── BasePage class
│   └── Dynamic page object creation
└── Executor
    ├── Navigation
    ├── Interaction
    └── Assertion
```

## Usage

```bash
# Install Selenium
pip install selenium

# Install browser drivers
webdriver-manager install
```

```python
from metanoia.skills.selenium_executor.executor import SeleniumExecutor

executor = SeleniumExecutor()
result = await executor.execute({
    "action": "click",
    "target": "#submit-button",
    "url": "https://example.com"
})
```

## Page Object Model

The skill supports the page object model pattern for maintainable test code:

```python
from metanoia.skills.selenium_executor.pom import BasePage, page_element

class LoginPage(BasePage):
    username = page_element(By.ID, "username")
    password = page_element(By.ID, "password")
    submit = page_element(By.CSS_SELECTOR, "button[type='submit']")
    
    def login(self, username, password):
        self.username.send_keys(username)
        self.password.send_keys(password)
        self.submit.click()
```
