from dataclasses import dataclass


@dataclass(frozen=True)
class Login:
    username: str
    password: str
