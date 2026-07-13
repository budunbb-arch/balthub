# /opt/balthub/apps/estates/parsing/management/commands/import_xml.py

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from apps.estates.parsing.services import FeedImporter

class Command(BaseCommand):
    help = "Import XML feed"

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str, default="test.xml")

    def handle(self, *args, **kwargs):
        feed_path = Path(settings.FEEDS_DIR) / kwargs["file"]

        result = FeedImporter(feed_path).run()

        self.stdout.write(
            self.style.SUCCESS(result["message"])
        )

            
