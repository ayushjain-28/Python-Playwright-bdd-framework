from playwright.sync_api import Locator, Page, expect

from config.settings import Settings


class BasePage:

    def __init__(self, page: Page, settings: Settings) -> None:
        self.page = page
        self.settings = settings
        self.base_url = settings.base_url.rstrip("/")

    def navigate_to(self, path: str = "") -> None:
        """Navigate to a path relative to the configured base URL."""
        normalized_path = path.lstrip("/")
        url = f"{self.base_url}/{normalized_path}" if normalized_path else self.base_url
        self.page.goto(url, wait_until="commit")

    def click(self, locator: Locator) -> None:
        """Wait for a locator to be usable, then click it."""
        expect(locator).to_be_visible(timeout=self.settings.timeout)
        locator.click()

    def fill(self, locator: Locator, value: str) -> None:
        """Wait for a field to be visible, then replace its value."""
        expect(locator).to_be_visible(timeout=self.settings.timeout)
        locator.fill(value)

    def get_text(self, locator: Locator) -> str:
        """Return the visible text for a locator."""
        expect(locator).to_be_visible(timeout=self.settings.timeout)
        return locator.inner_text().strip()