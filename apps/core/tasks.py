# apps/core/tasks.py

from __future__ import annotations

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
from pathlib import Path
import requests

from apps.core.models import Parser
from apps.estates.parsing.services.registry import get_importer
from apps.estates.parsing.management.execution.parser_execution import (
    parser_lock,
    SameParserRunningError,
)
from apps.estates.parsing.management.execution.advisory_lock import ParserBusyError
from apps.estates.parsing.management.execution.parser_cancel import ParserCancelled


import traceback
import logging

logger = logging.getLogger(__name__)


@shared_task
def run_parser_task(parser_id: int):

    logger.info("Parser task received: %s", parser_id)

    try:

        with parser_lock(parser_id) as (parser, run):

            logger.info("Parser found: %s", parser.name)
            logger.info("Using importer: %s", parser.engine)

            Importer = get_importer(parser.engine)

            logger.info("Downloading feed...")

            feed_content, filename = download_feed(parser)

            logger.info(
                "Feed downloaded: %s (%d bytes)",
                filename,
                len(feed_content),
            )

            run.feed_file.save(
                filename,
                ContentFile(feed_content),
                save=False,
            )

            parser.last_file.save(
                filename,
                ContentFile(feed_content),
                save=False,
            )

            logger.info("Writing feed to %s", filename)

            feed_path = write_import_file(
                parser,
                filename,
                feed_content,
            )

            logger.info("Starting importer...")

            result = Importer(feed_path, run).run()

            logger.info(
                "Importer finished (%s objects)",
                result["items_processed"],
            )

            stats = result["stats"]

            run.items_processed = result["items_processed"]

            run.projects_created = stats["projects_created"]
            run.projects_updated = stats["projects_updated"]

            run.houses_created = stats["houses_created"]
            run.houses_updated = stats["houses_updated"]

            run.flats_created = stats["flats_created"]
            run.flats_updated = stats["flats_updated"]

            run.developers_created = stats["developers_created"]
            run.developers_updated = stats["developers_updated"]

            run.save(update_fields=[
                "items_processed",
                "projects_created",
                "projects_updated",
                "houses_created",
                "houses_updated",
                "flats_created",
                "flats_updated",
                "developers_created",
                "developers_updated",
                "message",
            ])

            logger.info("Parser %s finished successfully", parser.name)

            run.status = Parser.STATUS_SUCCESS
            run.finished_at = timezone.now()
            run.message = "ok"

            parser.last_status = Parser.STATUS_SUCCESS
            parser.last_message = "ok"

    except SameParserRunningError:

        logger.warning(
            "Parser %s already running",
            parser_id,
        )

        return "already_running"

    except ParserBusyError:

        logger.warning(
            "This parser is already running",
        )

        return "busy"
    
    except ParserCancelled:

        logger.info(
            "Parser %s cancelled by user",
            parser.name,
        )

        run.status = Parser.STATUS_CANCELLED
        run.finished_at = timezone.now()
        run.message = "Cancelled by user"

        run.cancel_requested = False

        parser.last_status = Parser.STATUS_CANCELLED
        parser.last_message = run.message

        run.save(
            update_fields=[
                "status",
                "finished_at",
                "message",
                "cancel_requested",
            ]
        )

        return "cancelled"


    except Exception as exc:

        run.status = Parser.STATUS_FAILED
        run.finished_at = timezone.now()
        run.message = str(exc)
        run.traceback = traceback.format_exc()

        run.save()

        raise

    except Exception:

        logger.exception(
            "Parser %s crashed",
            parser_id,
        )

        raise

    finally:

        if "parser" in locals():

            parser.last_run = timezone.now()

            parser.save(
                update_fields=[
                    "last_run",
                    "last_status",
                    "last_message",
                    "last_file",
                ]
            )

    return "success"


def download_feed(parser: Parser):
    if not parser.source_url:
        raise ValueError("Parser source_url is not set")

    auth = None
    if parser.auth_username and parser.auth_password:
        auth = (parser.auth_username, parser.auth_password)

    headers = parser.headers or {}
    response = requests.get(parser.source_url, headers=headers, auth=auth, timeout=120)
    response.raise_for_status()

    prefix = parser.slug or parser.engine
    filename = f"{prefix}-{timezone.now().strftime('%Y%m%d%H%M%S')}.xml"
    return response.content, filename


def write_import_file(parser, filename, content) -> Path:
    target_dir = Path(settings.FEEDS_DIR)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename
    target_path.write_bytes(content)
    return target_path
