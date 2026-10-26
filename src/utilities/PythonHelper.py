import secrets
import string
from collections.abc import Sequence
from datetime import datetime
from random import choice
from typing import TypeVar

T = TypeVar("T")


class PythonHelper:
    @staticmethod
    def random_option(options: Sequence[T]) -> T:
        if not options:
            raise ValueError("options cannot be empty")
        return choice(options)

    @staticmethod
    def timestamp_hhmmss() -> str:
        return datetime.now().strftime("%H%M%S")

    @staticmethod
    def get_random_alphabet() -> str:
        """Return one randomly selected uppercase or lowercase English letter."""
        return secrets.choice(string.ascii_letters)