

from random import choice

from playwright.sync_api import Locator


class PlaywrightHelper:
    @staticmethod
    def get_random_text_from_elements(elements: list[Locator]) -> str:
        """Return visible text from one randomly selected locator in a list."""
        element_texts = [
            element.inner_text().strip()
            for element in elements
            if element.is_visible()
        ]
        non_empty_texts = [text for text in element_texts if text]
        if not non_empty_texts:
            raise ValueError("Cannot select text: no visible elements contain text.")

        return choice(non_empty_texts)