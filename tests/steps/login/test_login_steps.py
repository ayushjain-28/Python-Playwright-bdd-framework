import pytest
from playwright.sync_api import Page, expect
from pytest_bdd import given, scenario, then, when

from config.settings import settings
from datafactory.login.LoginData import get_valid_login_credentials
from pageobjects.dashboard.DashboardPage import DashboardPage
from pageobjects.login.LoginPage import LoginPage

login_page: LoginPage
dashboard_page: DashboardPage


@pytest.mark.handles_login
@scenario("login/login.feature", "User logs in with valid credentials")
def test_user_logs_in_with_valid_credentials() -> None:
    pass


@given("the user is on the OrangeHRM login page")
def user_is_on_login_page(page: Page) -> None:
    global login_page, dashboard_page
    login_page = LoginPage(page, settings)
    dashboard_page = DashboardPage(page, settings)
    login_page.navigate_to()


@when("the user logs in with valid credentials")
def user_logs_in_with_valid_credentials() -> None:
    login = get_valid_login_credentials(settings)
    login_page.enterLoginDataAndClickLogin(login.username, login.password)


@then("the dashboard page header is displayed")
def dashboard_header_is_displayed() -> None:
    expect(dashboard_page.dashboard_header()).to_be_visible()
