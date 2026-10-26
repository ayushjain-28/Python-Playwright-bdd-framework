
import string

from playwright.sync_api import Locator, Page

from config.settings import Settings
from models.admin.AddUser import AddUser
from pageobjects.common.CommonPo import CommonPo
from utilities.PlaywrightHelper import PlaywrightHelper


class AddUserPage(CommonPo):
    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings)

    #region Locators

    def add_user_header_text(self) -> Locator:
        return self.page.get_by_role("heading", name="Add User", exact=True)

    def edit_user_header_text(self) -> Locator:
        return self.page.get_by_role("heading", name="Edit User", exact=True)

    def _form_group(self, label: str) -> Locator:
        return self.page.locator(".oxd-input-group").filter(
            has=self.page.get_by_text(label, exact=True)
        )

    def user_role_dropdown(self) -> Locator:
        return self._form_group("User Role").locator(".oxd-select-text")

    def user_role_options(self, role: str) -> Locator:
        return self.page.get_by_role("option", name=role, exact=True)

    def employee_name_textbox(self) -> Locator:
        return self.page.get_by_placeholder("Type for hints...", exact=True)

    def employee_name_options(self) -> Locator:
        return self.page.get_by_role("listbox").get_by_role("option")

    def employee_name_option(self, employee_name: str) -> Locator:
        return self.employee_name_options().filter(has_text=employee_name).first

    def status_dropdown(self) -> Locator:
        return self._form_group("Status").locator(".oxd-select-text")

    def status_options(self, status: str) -> Locator:
        return self.page.get_by_role("option", name=status, exact=True)

    def username_textbox(self) -> Locator:
        return self._form_group("Username").locator("input")

    def password_textbox(self) -> Locator:
        return self._form_group("Password").locator("input[type='password']")

    def confirm_password_textbox(self) -> Locator:
        return self._form_group("Confirm Password").locator("input[type='password']")

    def cancel_button(self) -> Locator:
        return self.page.get_by_role("button", name="Cancel", exact=True)

    def save_button(self) -> Locator:
        return self.page.get_by_role("button", name="Save", exact=True)

    #endregion

    #region Methods

    def _select_employee_name(self, user: AddUser) -> None:
        employee_options = self.employee_name_options()
        search_terms = dict.fromkeys((user.employee_name, *string.ascii_lowercase))

        for search_term in search_terms:
            self.fill(self.employee_name_textbox(), search_term)
            employee_name = self.get_employee_name(employee_options)
            if employee_name is not None:
                user.employee_name = employee_name
                self.click(self.employee_name_option(employee_name))
                return

        raise ValueError("No employees were found for any employee-name search.")

    def get_employee_name(self, options: Locator) -> str | None:
        options.filter(has_not_text="Searching....").first.wait_for(
            state="visible",
            timeout=self.settings.timeout,
        )
        option_elements = [
            option
            for option in options.all()
            if option.inner_text().strip()
            not in {"-- Select --", "Searching....", "No Records Found"}
        ]
        if not option_elements:
            return None
        return PlaywrightHelper.get_random_text_from_elements(option_elements)

    def enter_user_details_and_click_on_save_button(self, user: AddUser) -> None:
        self.click(self.user_role_dropdown())
        self.click(self.user_role_options(user.user_role))
        if self.edit_user_header_text().is_visible():
            user.employee_name = self.employee_name_textbox().input_value()
        else:
            self._select_employee_name(user)
        self.click(self.status_dropdown())
        self.click(self.status_options(user.status))
        self.fill(self.username_textbox(), user.username)
        if self.password_textbox().is_visible():
            self.fill(self.password_textbox(), user.password)
            self.fill(self.confirm_password_textbox(), user.password)
        self.click(self.save_button())

    #endregion