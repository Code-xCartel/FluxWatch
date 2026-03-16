from starlette.config import Config

_config = Config(".env")


def get_env(name: str, default=None):
    return _config.get(name, default=default)


class AppConfig:
    API_PREFIX = get_env("API_PREFIX", "/api/v1")
    PG_URL = get_env("PG_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
    REDIS_URL = get_env("REDIS_URL", "redis://localhost:6379/0")

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
