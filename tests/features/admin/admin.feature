@e2e
Feature: OrangeHRM admin user management

@test_Create_a_new_admin_user
  Scenario: Create, update, and delete an admin user
    Given the user is logged in to OrangeHRM
    When the user opens the Admin module
    Then the Admin page is displayed
    When the user opens the Add User form
    Then the Add User form is displayed
    When the user enters generated admin details and saves the user
    Then a success notification confirms the admin was created
    When the user searches for the created admin by username
    Then the admin table shows the created user's details
    Then the Edit User form is displayed
    When the user edits the admin and saves the updated details
    When the user searches for the updated admin by username
    Then the admin table shows the updated user's details
    When the user selects and deletes the updated admin
    When the user searches for the deleted admin by username
    Then the deleted admin is not displayed in the results