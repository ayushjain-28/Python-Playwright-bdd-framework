@smoke
Feature: OrangeHRM login

  @test_user_logs_in_with_valid_credentials
  Scenario: User logs in with valid credentials
    Given the user is on the OrangeHRM login page
    When the user logs in with valid credentials
    Then the dashboard page header is displayed
