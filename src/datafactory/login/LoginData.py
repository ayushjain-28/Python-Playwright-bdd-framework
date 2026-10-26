from config.settings import Settings
from models.login.Login import Login


def get_valid_login_credentials(settings: Settings) -> Login:
    if not settings.username or not settings.password:
        raise ValueError(
            "Set APP_USERNAME and APP_PASSWORD before running the login scenario."
        )

    return Login(
        username=settings.username,
        password=settings.password,
    )
