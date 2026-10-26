
from playwright.sync_api import Locator, Page

from config.settings import Settings
from pageobjects.common.CommonPo import CommonPo


class AdminPage(CommonPo):
    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings)

    #region Locators

    def admin_header_text(self) -> Locator:
        return self.page.get_by_role("heading", name="Admin", exact=True)

    def add_user_button(self) -> Locator:
        return self.page.get_by_role("button", name="Add")

    def username_search_textbox(self) -> Locator:
        return self.page.locator(".oxd-input-group").filter(
            has=self.page.get_by_text("Username", exact=True)
        ).locator("input")

    def search_button(self) -> Locator:
        return self.page.get_by_role("button", name="Search", exact=True)

    def user_row(self, username: str) -> Locator:
        return self.page.locator(
            "//div[@role='row'][.//div[@role='cell']"
            f"[normalize-space()='{username}']]"
        )

    def edit_user_button(self, username: str) -> Locator:
        return self.user_row(username).locator(
            ".oxd-table-cell-actions button:has(.bi-pencil-fill)"
        )

    def user_checkbox(self, username: str) -> Locator:
        return self.user_row(username).locator(".oxd-checkbox-input")

    def delete_selected_button(self) -> Locator:
        return self.page.get_by_role("button", name="Delete Selected")

    def confirm_delete_button(self) -> Locator:
        return self.page.get_by_role("button", name="Yes, Delete")

    #endregion

    #region Methods

    def get_admin_header_text(self) -> str:
        return self.get_text(self.admin_header_text())

    def click_on_add_button(self) -> None:
        self.click(self.add_user_button())

    def search_user(self, username: str) -> None:
        self.page.wait_for_url(
            "**/admin/viewSystemUsers",
            timeout=self.settings.timeout,
        )
        self.fill(self.username_search_textbox(), username)
        self.click(self.search_button())

    def get_user_details_from_table(self, username: str) -> dict[str, str]:
        row = self.user_row(username)
        row.wait_for(state="visible", timeout=self.settings.timeout)
        cells = row.get_by_role("cell").all_inner_texts()
        return {
            "username": cells[1],
            "user_role": cells[2],
            "employee_name": cells[3],
            "status": cells[4],
        }

    def click_edit_user(self, username: str) -> None:
        self.click(self.edit_user_button(username))

    def delete_user(self, username: str) -> None:
        self.click(self.user_checkbox(username))
        self.click(self.delete_selected_button())
        self.click(self.confirm_delete_button())

    #endregion
    