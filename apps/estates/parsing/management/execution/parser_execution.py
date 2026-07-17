# /opt/balthub/apps/estates/parsing/management/execution/parser_execution.py

from contextlib import contextmanager
from datetime import timedelta

from django.utils import timezone

from apps.core.models import Parser
from apps.core.models import ParserRun

from .advisory_lock import (
    advisory_lock,
    PARSER_LOCK_OFFSET,
)


class SameParserRunningError(Exception):
    """Этот парсер уже выполняется."""


class ParserBusyError(Exception):
    pass


@contextmanager
def parser_lock(parser_id: int):

    ParserRun.objects.filter(
        status="running",
        started_at__lt=timezone.now() - timedelta(hours=12),
    ).update(
        status="failed",
        finished_at=timezone.now(),
        message="Automatically terminated (stale run)",
    )

    parser = Parser.objects.get(pk=parser_id)

    parser_lock_id = PARSER_LOCK_OFFSET + parser.id

    with advisory_lock(parser_lock_id):

        run = ParserRun.objects.create(
            parser=parser,
            status=Parser.STATUS_STARTED,
            started_at=timezone.now(),
        )

        try:

            yield parser, run

            if run.status == Parser.STATUS_STARTED:
                run.status = Parser.STATUS_SUCCESS

            if run.finished_at is None:
                run.finished_at = timezone.now()

            run.save()

        finally:

            if run.finished_at is None:
                run.finished_at = timezone.now()

            run.save()