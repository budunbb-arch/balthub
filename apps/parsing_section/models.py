from apps.core.models import Parser
from apps.core.models import ParserRun


class ParserProxy(Parser):

    class Meta:
        proxy = True
        app_label = "parsing_section"
        verbose_name = "Парсер"
        verbose_name_plural = "Парсеры"


class ParserRunProxy(ParserRun):

    class Meta:
        proxy = True
        app_label = "parsing_section"
        verbose_name = "Запуск парсера"
        verbose_name_plural = "Запуски парсеров"