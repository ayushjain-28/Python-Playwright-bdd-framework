from playwright.sync_api import Locator

from config.settings import Settings
from pageobjects.BasePage import BasePage


class LoginPage(BasePage):
    def __init__(self, page, settings: Settings) -> None:
        super().__init__(page, settings)

    #region Locators

    def usernameTextbox(self) -> Locator:
        return self.page.locator("input[placeholder='Username']")

    def passwordTextbox(self) -> Locator:
        return self.page.locator("input[placeholder='Password']")

    def loginButton(self) -> Locator:
        return self.page.locator("//button[contains(@class,'orangehrm-login-button')]")

    def error_message(self) -> Locator:
        return self.page.locator(".oxd-alert-content-text")

    #endregion

    #region Methods

    def enterLoginDataAndClickLogin(self, username: str, password: str) -> None:
        
        self.fill(self.usernameTextbox(), username)
        self.fill(self.passwordTextbox(), password)
        self.click(self.loginButton())

    def get_error_message(self) -> str:
        return self.get_text(self.error_message())
    #endregion
