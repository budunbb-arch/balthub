from contextlib import contextmanager

from django.db import connection


GLOBAL_PARSER_LOCK = 1
PARSER_LOCK_OFFSET = 1000


class ParserBusyError(Exception):
    pass


@contextmanager
def advisory_lock(lock_id: int):

    with connection.cursor() as cursor:

        cursor.execute(
            "SELECT pg_try_advisory_lock(%s)",
            [lock_id],
        )

        if not cursor.fetchone()[0]:
            raise ParserBusyError()

    try:
        yield

    finally:

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_advisory_unlock(%s)",
                [lock_id],
            )