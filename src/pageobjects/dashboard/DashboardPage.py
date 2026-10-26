from playwright.sync_api import Locator, Page

from config.settings import Settings
from pageobjects.common.CommonPo import CommonPo


class DashboardPage(CommonPo):
    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings)

        #region Locators

    def dashboard_header(self) -> Locator:
        return self.page.locator("//h6[text()='Dashboard']")

    #endregion


    #region Methods

    #endregion