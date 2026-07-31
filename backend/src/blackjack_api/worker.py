"""Deployment worker entry point for local Docker Compose."""

from __future__ import annotations

import logging
import signal
from threading import Event

from blackjack_api.config import get_settings
from blackjack_api.services import open_database

LOGGER = logging.getLogger("blackjack_api.worker")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    settings = get_settings()
    stop_event = Event()

    def stop(_signum: int, _frame: object) -> None:
        stop_event.set()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    connection = open_database(settings.database_path)
    connection.close()
    LOGGER.info(
        "worker container ready with local queue mode; API process owns queued jobs",
    )
    stop_event.wait()
    LOGGER.info("worker container stopped")


if __name__ == "__main__":
    main()
