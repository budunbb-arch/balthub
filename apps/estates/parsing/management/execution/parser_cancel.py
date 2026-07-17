# /opt/balthub/apps/estates/parsing/management/execution/parser_cancel.py

import logging

logger = logging.getLogger(__name__)


class ParserCancelled(Exception):
    """Импорт остановлен пользователем."""
    pass


class ParserCancelChecker:

    def __init__(self, parser_run):
        self.parser_run = parser_run
        self.counter = 0

    def tick(self):

        self.counter += 1

        logger.warning(
            "tick %s (%s)",
            self.counter,
            self.parser_run.id,
        )

        self.counter = 0

        self.parser_run.refresh_from_db(
            fields=["cancel_requested"],
        )

        logger.warning(
            "cancel_requested=%s",
            self.parser_run.cancel_requested,
        )

        if self.parser_run.cancel_requested:
            raise ParserCancelled()