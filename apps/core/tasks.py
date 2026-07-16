# apps/core/tasks.py

from __future__ import annotations

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
from pathlib import Path
import requests

from apps.core.models import Parser, ParserRun
from django.core.management import call_command
from apps.estates.parsing.services.registry import get_importer


import traceback
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def run_parser_task(self, parser_id: int):

    logger.info("Parser task started: %s", parser_id)

    parser = Parser.objects.filter(pk=parser_id).first()

    logger.info("Parser found: %s", parser)

    if not parser:
        return "parser_not_found"

    logger.info("Using importer: %s", parser.engine)
    Importer = get_importer(parser.engine)

    run = ParserRun.objects.create(
        parser=parser,
        status=Parser.STATUS_STARTED,
        started_at=timezone.now(),
    )

    try:
        logger.info("Downloading feed...")
        feed_content, filename = download_feed(parser)
        logger.info("Feed downloaded: %s", filename)

        run.feed_file.save(filename, ContentFile(feed_content), save=False)
        parser.last_file.save(filename, ContentFile(feed_content), save=False)

        feed_path = write_import_file(
            parser,
            filename,
            feed_content,
        )

        logger.info("Running import_xml...")

        result = Importer(feed_path).run()

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

        logger.info("Import finished.")

        run.status = Parser.STATUS_SUCCESS
        run.finished_at = timezone.now()
        run.items_processed = result.get("items_processed")
        run.message = "ok"
        parser.last_status = run.status
        parser.last_message = run.message
    except Exception as exc:
        logger.exception(
            "Parser %s failed",
            parser.pk,
        )
        run.status = Parser.STATUS_FAILED
        run.finished_at = timezone.now()

        tb = traceback.format_exc()

        run.message = str(exc)
        run.traceback = tb
        parser.last_status = Parser.STATUS_FAILED
        parser.last_message = str(exc)
    finally:
        run.save()
        parser.last_run = run.finished_at or timezone.now()
        parser.save(update_fields=["last_run", "last_status", "last_message", "last_file"])  # type: ignore

    return run.status


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
