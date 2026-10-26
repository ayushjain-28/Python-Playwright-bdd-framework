
from playwright.sync_api import Locator, Page

from config.settings import Settings
from pageobjects.BasePage import BasePage


class CommonPo(BasePage):
    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings)

    #region Locators

    def sidebar_menu_options(self, option: str) -> Locator:
        return self.page.locator(f"//li//a[contains(@href, '{option}')]")

    def toaster_message_title(self) -> Locator:
        return self.page.locator("//p[contains(@class,'oxd-text--toast-title')]")

    def toaster_message_text(self) -> Locator:
        return self.page.locator("//p[contains(@class, 'oxd-text--toast-message')]")

    #endregion

    #region Methods

    def click_sidebar_menu_option(self, option: str) -> None:
        self.click(self.sidebar_menu_options(option))

    def get_toaster_message_title_text(self) -> str:
        return self.get_text(self.toaster_message_title())

    def get_toaster_message_text(self) -> str:
        return self.get_text(self.toaster_message_text())
    

    #endregion
