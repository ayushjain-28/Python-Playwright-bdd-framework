from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse


_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


def _read_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    normalized = value.strip().lower()

    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False

    raise ValueError(f"{name} must be a boolean value; received {value!r}.")


def _read_int(name: str, default: int) -> int:
    value = os.getenv(name)

    if value is None:
        return default

    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer; received {value!r}.") from exc


@dataclass(frozen=True)
class Settings:
    base_url: str = field(
        default_factory=lambda: os.getenv(
            "BASE_URL", "https://opensource-demo.orangehrmlive.com"
        ).strip()
    )
    browser_name: str = field(
        default_factory=lambda: os.getenv("BROWSER", "chromium").strip().lower()
    )
    headless: bool = field(default_factory=lambda: _read_bool("HEADLESS", True))
    timeout: int = field(
        default_factory=lambda: _read_int("PLAYWRIGHT_TIMEOUT", 30_000)
    )
    artifact_dir: Path = field(
        default_factory=lambda: Path(os.getenv("ARTIFACT_DIR", "artifacts"))
    )
    username: str = field(default_factory=lambda: os.getenv("APP_USERNAME", ""))
    password: str = field(default_factory=lambda: os.getenv("APP_PASSWORD", ""))
    screenshot_on_failure: bool = field(
        default_factory=lambda: _read_bool("SCREENSHOT_ON_FAILURE", True)
    )
    trace_on_failure: bool = field(
        default_factory=lambda: _read_bool("TRACE_ON_FAILURE", True)
    )
    video_on_failure: bool = field(
        default_factory=lambda: _read_bool("VIDEO_ON_FAILURE", True)
    )

    @classmethod
    def from_env(cls) -> Settings:
        settings = cls()
        settings.validate()
        return settings

    def validate(self) -> None:
        parsed = urlparse(self.base_url)

        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(
                "BASE_URL must be a valid URL starting with http:// or https://."
            )

        if self.browser_name not in {"chromium", "firefox", "webkit"}:
            raise ValueError(
                f"Unsupported browser {self.browser_name!r}. "
                "Use chromium, firefox, or webkit."
            )

        if self.timeout <= 0:
            raise ValueError("PLAYWRIGHT_TIMEOUT must be greater than zero.")


settings = Settings.from_env()