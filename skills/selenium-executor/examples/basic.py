# Selenium Executor Examples

## Basic Navigation

```python
from metanoia.skills.selenium_executor.executor import SeleniumExecutor

async def test_navigation():
    executor = SeleniumExecutor()
    result = await executor.execute({
        "action": "goto",
        "url": "https://example.com"
    })
    assert result["status"] == "success"
```

## Click Element

```python
async def test_click():
    executor = SeleniumExecutor()
    result = await executor.execute({
        "action": "click",
        "target": "#submit-button",
        "url": "https://example.com/form",
        "locator_strategy": "CSS_SELECTOR"
    })
    assert result["status"] == "success"
```

## Send Keys

```python
async def test_send_keys():
    executor = SeleniumExecutor()
    result = await executor.execute({
        "action": "send_keys",
        "target": "input[name='username']",
        "value": "testuser",
        "url": "https://example.com/login",
        "locator_strategy": "NAME"
    })
    assert result["status"] == "success"
```

## Page Object Model Example

```python
"""Example: Using Page Object Model with SeleniumExecutor."""
from selenium import webdriver
from selenium.webdriver.common.by import By
from metanoia.skills.selenium_executor.pom import BasePage, page_element


class LoginPage(BasePage):
    username = page_element(By.ID, "username")
    password = page_element(By.ID, "password")
    submit = page_element(By.CSS_SELECTOR, "button[type='submit']")
    error_message = page_element(By.CLASS_NAME, "error-message")

    def login(self, username: str, password: str) -> bool:
        self.username.send_keys(username)
        self.password.send_keys(password)
        self.submit.click()
        return not self.error_message.is_displayed()


class DashboardPage(BasePage):
    welcome_message = page_element(By.TAG_NAME, "h1")
    logout_button = page_element(By.ID, "logout")

    def get_welcome(self) -> str:
        return self.welcome_message.text


async def test_login_with_pom():
    driver = webdriver.Chrome()
    driver.get("https://example.com/login")

    login_page = LoginPage(driver)
    success = login_page.login("testuser", "password123")

    assert success, "Login should succeed"
    assert "Welcome" in login_page.driver.title

    driver.quit()
```

## Complete Test Flow

```python
"""Complete test flow example with assertions."""
import asyncio
from metanoia.skills.selenium_executor.executor import SeleniumExecutor


async def run_test_flow():
    executor = SeleniumExecutor()

    # Step 1: Open login page
    result = await executor.execute({
        "action": "goto",
        "url": "https://example.com/login"
    })
    assert result["status"] == "success"

    # Step 2: Enter username
    result = await executor.execute({
        "action": "send_keys",
        "target": "#username",
        "value": "testuser",
        "locator_strategy": "CSS_SELECTOR"
    })
    assert result["status"] == "success"

    # Step 3: Enter password
    result = await executor.execute({
        "action": "send_keys",
        "target": "#password",
        "value": "password123",
        "locator_strategy": "CSS_SELECTOR"
    })
    assert result["status"] == "success"

    # Step 4: Click submit
    result = await executor.execute({
        "action": "click",
        "target": "button[type='submit']",
        "locator_strategy": "CSS_SELECTOR"
    })
    assert result["status"] == "success"

    # Step 5: Verify dashboard loads
    result = await executor.execute({
        "action": "get_text",
        "target": "h1.welcome",
        "locator_strategy": "CSS_SELECTOR"
    })
    assert result["status"] == "success"
    assert "Welcome" in result["result"]["text"]

    # Step 6: Take screenshot
    result = await executor.execute({
        "action": "screenshot"
    })
    assert result["status"] == "success"
    assert result["screenshot"] is not None

    print("All tests passed!")


if __name__ == "__main__":
    asyncio.run(run_test_flow())
```
