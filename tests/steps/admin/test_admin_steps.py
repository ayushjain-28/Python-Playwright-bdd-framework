import pytest
from playwright.sync_api import Page, expect
from pytest_bdd import given, scenario, then, when

from config.settings import settings
from constants import Constants
from datafactory.admin import AddUserData
from datafactory.admin.AddUserData import get_edit_admin_data, get_new_admin_data
from pageobjects.admin.adduser.AddUserPage import AddUserPage
from pageobjects.admin.AdminPage import AdminPage
from pageobjects.dashboard.DashboardPage import DashboardPage

@scenario("admin/admin.feature", "Create, update, and delete an admin user")
def test_admin_user_lifecycle() -> None:
    pass


@given("the user is logged in to OrangeHRM")
def user_is_logged_in(page: Page) -> None:
    global dashboard_page, admin_page, add_user_page, create_admin_user_data, edit_admin_user_data
    dashboard_page = DashboardPage(page, settings)
    admin_page = AdminPage(page, settings)
    add_user_page = AddUserPage(page, settings)
    create_admin_user_data = AddUserData.get_new_admin_data()
    edit_admin_user_data = AddUserData.get_edit_admin_data()
    expect(dashboard_page.dashboard_header()).to_be_visible()


@when("the user opens the Admin module")
def user_opens_admin_module() -> None:
    dashboard_page.click_sidebar_menu_option("viewAdminModule")


@then("the Admin page is displayed")
def admin_page_is_displayed() -> None:
    assert admin_page.get_admin_header_text() == "Admin"


@when("the user opens the Add User form")
def user_opens_add_user_form() -> None:
    admin_page.click_on_add_button()


@then("the Add User form is displayed")
def add_user_form_is_displayed() -> None:
    expect(add_user_page.add_user_header_text()).to_be_visible()

@when("the user enters generated admin details and saves the user")
def user_enters_admin_details_and_saves() -> None:
    add_user_page.enter_user_details_and_click_on_save_button(create_admin_user_data)


@then("a success notification confirms the admin was created")
def admin_creation_success_notification_is_displayed() -> None:
    assert (admin_page.get_toaster_message_title_text()== Constants.SUCCESS_TOASTER_MESSAGE_TITLE)
    assert (admin_page.get_toaster_message_text()== Constants.SUCCESS_TOASTER_MESSAGE_TEXT)


@when("the user searches for the created admin by username")
def user_searches_created_admin_by_username() -> None:
    admin_page.search_user(create_admin_user_data.username)


@then("the admin table shows the created user's details")
def created_admin_details_are_correct() -> None:
    user_details = admin_page.get_user_details_from_table(create_admin_user_data.username)
    employee_name_parts = create_admin_user_data.employee_name.split()
    employee_name = " ".join((employee_name_parts[0], employee_name_parts[-1]))
    assert user_details["username"] == create_admin_user_data.username
    assert user_details["user_role"] == create_admin_user_data.user_role
    assert user_details["employee_name"] == employee_name
    assert user_details["status"] == create_admin_user_data.status


@then("the Edit User form is displayed")
def edit_user_form_is_displayed() -> None:
    admin_page.click_edit_user(create_admin_user_data.username)
    expect(add_user_page.edit_user_header_text()).to_be_visible()


@when("the user edits the admin and saves the updated details")
def user_updates_admin_details() -> None:
    add_user_page.enter_user_details_and_click_on_save_button(edit_admin_user_data)


@when("the user searches for the updated admin by username")
def user_searches_updated_admin_by_username() -> None:
    admin_page.search_user(edit_admin_user_data.username)


@then("the admin table shows the updated user's details")
def updated_admin_details_are_correct() -> None:
    user_details = admin_page.get_user_details_from_table(edit_admin_user_data.username)
    employee_name_parts = edit_admin_user_data.employee_name.split()
    employee_name = " ".join((employee_name_parts[0], employee_name_parts[-1]))
    assert user_details["username"] == edit_admin_user_data.username
    assert user_details["user_role"] == edit_admin_user_data.user_role
    assert user_details["employee_name"] == employee_name
    assert user_details["status"] == edit_admin_user_data.status


@when("the user selects and deletes the updated admin")
def user_selects_and_deletes_updated_admin() -> None:
    admin_page.delete_user(edit_admin_user_data.username)


@when("the user searches for the deleted admin by username")
def user_searches_deleted_admin_by_username() -> None:
    admin_page.search_user(edit_admin_user_data.username)


@then("the deleted admin is not displayed in the results")
def deleted_admin_is_absent_from_results() -> None:
    expect(admin_page.user_row(edit_admin_user_data.username)).to_have_count(0)
