# /opt/balthub/apps/estates/parsing/management/commands/import_xml.py

import logging
import sys
from pathlib import Path

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Parser, ParserRun
from apps.estates.parsing.services.nmarket.importer import NMarketImporter


class Command(BaseCommand):
    help = "Import XML feed"

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str, default="test.xml")
        parser.add_argument(
            "--parser-id",
            type=int,
            help="ID парсера (Parser) для создания ParserRun",
            required=False,
        )

    def handle(self, *args, **kwargs):
        feed_path = Path(settings.FEEDS_DIR) / kwargs["file"]

        # Создаём временный ParserRun
        parser_id = kwargs.get("parser_id")
        if parser_id:
            parser = Parser.objects.get(pk=parser_id)
        else:
            parser, _ = Parser.objects.get_or_create(
                name="Console Import",
                slug="console-import",
                engine=Parser.ENGINE_NMARKET,
                is_active=False,
            )

        parser_run = ParserRun.objects.create(
            parser=parser,
            status=Parser.STATUS_STARTED,
            started_at=timezone.now(),
            flats_deactivated=0,
        )

        result = NMarketImporter(feed_path, parser_run).run()

        parser_run.status = Parser.STATUS_SUCCESS
        parser_run.finished_at = timezone.now()
        parser_run.message = result["message"]
        parser_run.items_processed = result["items_processed"]
        parser_run.save()

        self.stdout.write(self.style.SUCCESS(result["message"]))