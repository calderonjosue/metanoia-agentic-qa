"""Example step definitions for Behave BDD tests."""

from behave import given, when, then, step


@given('I am on the login page')
def step_i_am_on_login_page(context):
    """Navigate to the login page."""
    context.browser.get("https://example.com/login")


@given('I am logged in as "{username}"')
def step_logged_in_as(context, username):
    """Log in as a specific user."""
    context.browser.get("https://example.com/login")
    context.browser.find_element("name", "username").send_keys(username)
    context.browser.find_element("name", "password").send_keys("password")
    context.browser.find_element("name", "login").click()
    context.current_user = username


@given('the following users exist')
def step_users_exist(context):
    """Create users from table data."""
    context.users = {}
    for row in context.table:
        context.users[row["username"]] = {
            "password": row["password"],
            "role": row.get("role", "user")
        }


@when('I fill in "{field}" with "{value}"')
def step_fill_field(context, field, value):
    """Fill an input field with value."""
    elem = context.browser.find_element("name", field)
    elem.clear()
    elem.send_keys(value)


@when('I press "{button}"')
def step_press_button(context, button):
    """Click a button by name or text."""
    elem = context.browser.find_element("name", button)
    elem.click()


@when('I click "{text}"')
def step_click_text(context, text):
    """Click an element containing text."""
    context.browser.find_element("partial link text", text).click()


@when('I wait for "{seconds}" seconds')
def step_wait(context, seconds):
    """Wait for specified seconds."""
    import time
    time.sleep(int(seconds))


@then('I should see "{text}"')
def step_should_see(context, text):
    """Assert text is visible on page."""
    assert text in context.browser.page_source, f"Expected '{text}' not found"


@then('I should not see "{text}"')
def step_should_not_see(context, text):
    """Assert text is not visible on page."""
    assert text not in context.browser.page_source, f"Unexpected '{text}' found"


@then('the page title should be "{title}"')
def step_page_title(context, title):
    """Assert page title matches."""
    actual = context.browser.title
    assert actual == title, f"Expected title '{title}', got '{actual}'"


@step('I enter the following credentials')
def step_credentials(context):
    """Enter credentials from table."""
    for row in context.table:
        field = row["field"]
        value = row["value"]
        context.browser.find_element("name", field).send_keys(value)
