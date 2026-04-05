# Selenium Executor

Selenium WebDriver test execution skill with page object model support.

## Quick Start

```python
from metanoia.skills.selenium_executor.executor import SeleniumExecutor

async def main():
    executor = SeleniumExecutor()
    result = await executor.execute({
        "action": "goto",
        "url": "https://example.com"
    })
    print(result)
```

## Files

| File | Description |
|------|-------------|
| `SKILL.md` | Skill definition with frontmatter |
| `executor.py` | Main Selenium WebDriver executor |
| `pom.py` | Page object model support |
| `schema.json` | Input/output contract |
| `examples/` | Example usage |

## Supported Browsers

- Chrome
- Firefox
- Edge
- Safari

## Supported Actions

- `goto` - Navigate to URL
- `click` - Click element
- `send_keys` - Type text into element
- `clear` - Clear element value
- `submit` - Submit form
- `get_text` - Get element text
- `get_attribute` - Get element attribute
- `is_displayed` - Check element visibility
- `screenshot` - Capture page screenshot

## Locator Strategies

- `ID` - Element by ID attribute
- `NAME` - Element by name attribute
- `CSS_SELECTOR` - CSS selector
- `XPATH` - XPath expression
- `LINK_TEXT` - Link by exact text
- `PARTIAL_LINK_TEXT` - Link by partial text
- `TAG_NAME` - Element by tag name
- `CLASS_NAME` - Element by class name

## Page Object Model

The POM module provides:

- `BasePage` - Base class for page objects
- `page_element` - Decorator for element locators
- `PageObjectMeta` - Metaclass for page objects

## Testing Your Skill

```bash
# Run examples
python examples/basic.py

# Run with pytest
pytest tests/selenium_executor/
```
