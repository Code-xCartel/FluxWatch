import re
from functools import cached_property

from starlette.config import Config

_config = Config(".env")


def get_env(name: str, default=None):
    return _config.get(name, default=default)


class AppConfig:
    API_PREFIX = get_env("API_PREFIX", "/api/v1")

    PG_URL = get_env("PG_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
    REDIS_URL = get_env("REDIS_URL", "redis://localhost:6379/0")

    FWES_SENDER_MAIL = get_env("FWES_SENDER_MAIL", "mail@mail.com")
    FWES_SENDER_PASS = get_env("FWES_SENDER_PASS", "password")
    FWES_SMTP_SERVER = get_env("FWES_SMTP_SERVER", "smtp")
    FWES_SMTP_PORT = get_env("FWES_SMTP_PORT", 465)

    PLATFORM_LINK = get_env("PLATFORM_LINK", "http://localhost:8000")

    API_KEY_TTL_DAYS = get_env("API_KEY_TTL_DAYS", 30)
    API_KEY_DAILY_LIMIT = get_env("API_KEY_DAILY_LIMIT", 86400)

    @cached_property
    def skip_auth_routes(self):
        return (
            re.compile(r"^/favicon.ico"),
            re.compile(rf"^{self.API_PREFIX}/$"),
            re.compile(rf"^{self.API_PREFIX}/version$"),
            re.compile(rf"^{self.API_PREFIX}/info$"),
            re.compile(rf"^{self.API_PREFIX}/docs$"),
            re.compile(rf"^{self.API_PREFIX}/redoc$"),
            re.compile(rf"^{self.API_PREFIX}/openapi.json$"),
            # Auth
            re.compile(rf"^{self.API_PREFIX}/auth/sign-up$"),
            re.compile(rf"^{self.API_PREFIX}/auth/sign-in$"),
            re.compile(rf"^{self.API_PREFIX}/auth/activate$"),
            re.compile(rf"^{self.API_PREFIX}/auth/resend-email$"),
            re.compile(rf"^{self.API_PREFIX}/auth/forgot-password$"),
        )

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {"format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"},
            "simple": {"format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"},
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
            "simple": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
        },
        "loggers": {
            "app": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False,
            },
            "flux_watch_api": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False,
            },
            "uvicorn": {"handlers": ["simple"], "level": "INFO", "propagate": False},
        },
        "root": {"handlers": ["console"], "level": "DEBUG"},
    }
