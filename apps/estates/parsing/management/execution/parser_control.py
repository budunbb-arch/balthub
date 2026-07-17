from apps.core.models import ParserRun

from .parser_cancel import ParserCancelled


def check_cancel(run: ParserRun):

    run.refresh_from_db(
        fields=[
            "cancel_requested",
        ]
    )

    if run.cancel_requested:
        raise ParserCancelled(
            "Остановка запрошена пользователем."
        )