Feature: Login
  User authentication and session management

  @smoke @auth
  Scenario: Successful login with valid credentials
    Given I am on the login page
    When I fill in "username" with "admin"
    And I fill in "password" with "secret123"
    And I press "Login"
    Then I should see "Welcome, admin"
    And the page title should be "Dashboard"

  @smoke @auth
  Scenario: Failed login with invalid password
    Given I am on the login page
    When I fill in "username" with "admin"
    And I fill in "password" with "wrongpassword"
    And I press "Login"
    Then I should see "Invalid credentials"
    And I should not see "Dashboard"

  @auth
  Scenario Outline: Login attempts with different user roles
    Given I am on the login page
    When I fill in "username" with "<username>"
    And I fill in "password" with "<password>"
    And I press "Login"
    Then I should see "<expected_message>"

    Examples: Admin Users
      | username | password    | expected_message      |
      | admin    | admin123    | Welcome, admin        |
      | super    | super123    | Welcome, super        |

    Examples: Regular Users
      | username | password  | expected_message        |
      | user1    | pass123   | Welcome, user1           |
      | user2    | pass456   | Welcome, user2           |

  @wip
  Scenario: Password reset flow
    Given I am on the login page
    When I click "Forgot Password"
    Then I should see "Reset Password"
    And I fill in "email" with "user@example.com"
    And I press "Send Reset Link"
    Then I should see "Check your email"

  @auth @regression
  Scenario: Session timeout warning
    Given I am logged in as "admin"
    When I wait for "1900" seconds
    Then I should see "Session expiring soon"
