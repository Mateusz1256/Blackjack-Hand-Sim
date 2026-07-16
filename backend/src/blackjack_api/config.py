"""Backend application settings."""

from dataclasses import dataclass
from os import getenv

DEFAULT_APP_NAME = "Blackjack Simulator API"
DEFAULT_VERSION = "0.1.0"
DEFAULT_ENVIRONMENT = "local"
DEFAULT_API_PREFIX = "/api/v1"


@dataclass(frozen=True, slots=True)
class BackendSettings:
    app_name: str = DEFAULT_APP_NAME
    version: str = DEFAULT_VERSION
    environment: str = DEFAULT_ENVIRONMENT
    api_prefix: str = DEFAULT_API_PREFIX


def get_settings() -> BackendSettings:
    return BackendSettings(
        app_name=getenv("BLACKJACK_API_NAME", DEFAULT_APP_NAME),
        version=getenv("BLACKJACK_API_VERSION", DEFAULT_VERSION),
        environment=getenv(
            "BLACKJACK_API_ENVIRONMENT",
            DEFAULT_ENVIRONMENT,
        ),
        api_prefix=getenv("BLACKJACK_API_PREFIX", DEFAULT_API_PREFIX),
    )
